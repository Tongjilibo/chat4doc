import os
from sanic import Sanic, response
import jinja2
import json
from utils import load_config
import requests
import argparse


# 参数解析
parser = argparse.ArgumentParser(description='webui')
parser.add_argument('--port', default=8083)
args = parser.parse_args()
port = int(args.port)

app = Sanic('default')
env = jinja2.Environment(loader=jinja2.FileSystemLoader('./templates'))
app.static('/static', './static')
app.ctx.static_folder='./static'
USER_DATA_CENTER = os.path.join(os.getcwd(), "static/user_data")  # 用户的目录地址
USER_DATA_URL = '/static/user_data'  # 用户的目录url


async def get_user_path(request, url=False):
    '''获取该用户文件缓存地址'''
    ip = request.client_ip
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(':')[0]
    elif request.headers.get('x-real-ip'):
        ip = request.headers.get('x-real-ip').split(':')[0]
    elif request.headers.get('Host'):
        ip = request.headers.get('Host').split(':')[0]
    else:
        ip = '127.0.0.1'
    app.config.update({"IP":ip})
    ip = app.config.IP
    if url:
        save_path = os.path.join(USER_DATA_URL, ip)
    else:
        save_path = os.path.join(USER_DATA_CENTER, ip)
        os.makedirs(save_path, exist_ok=True)
    return save_path


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return response.html(template.render(kwargs))


async def call_api(request, save_path, api_url, method='only_file_path'):
    '''上传并解析pdf得到对应结果'''
    # 把file拷贝到指定的文件位置
    file = request.files.get('file')
    file_name = file.name.split('.')[0].replace(' ', '')
    upload_path = os.path.join(save_path, file_name, file.name)  # 保存文件地址
    os.makedirs(os.path.join(save_path, file_name), exist_ok=True)
    with open(upload_path, 'wb') as f:
        f.write(file.body)

    # 发送http请求
    if method == 'only_file_path':
        data = {'file_path': upload_path} # 文件的绝对路径, 以.docx|.pdf结尾
    else:
        # 文件的绝对路径，其中file_path是文件夹地址，file_name是以.docx|.pdf结尾
        data = {'file_path': os.path.join(save_path, file_name), 'file_name': file.name}

    headers = {"Content-type": "application/json"}
    response = requests.post(url=api_url, headers=headers, data=json.dumps(data))
    return file_name, response.json()


# =======================pdf_extract=======================
@app.route(load_config('webui', 'pdf_extract'), methods=['GET', 'POST'])
async def pdf_extract_upload(request):
    if request.method == 'GET':
        return template('./pdf_extract/upload.html')
    if request.method == 'POST':
        if 'analysis' in request.form:
            save_path = await get_user_path(request)
            global result
            file_name, result = await call_api(request, save_path, load_config('api', 'pdf_extract'), method='both')
            return response.redirect(app.url_for('pdf_extract_show', file=file_name))


@app.route(load_config('webui', 'pdf_extract')+'/show/<file>', methods=['GET', 'POST'])
async def pdf_extract_show(request, file):
    import urllib.parse
    file = urllib.parse.unquote(file)
    user_path = await get_user_path(request)
    result_json = result
    user_url = await get_user_path(request, url=True)
    xlsx = user_url + f'/{file}/{file}.xlsx'  # pdf解析的xlsx下载url 
    pdf = user_url + f'/{file}/{file}_highlight.pdf'  # pdf用于展示的url
    if request.method == 'POST':
        if 'show_all' in request.form.keys():
            pages_results, keys_map = get_keys_map(result_json)
            return template('./pdf_extract/runtime.html', keys_map=keys_map, pdf=pdf+'#toolbar=0', xlsx=xlsx, file=file)
        elif 'upload' in request.form.keys():
            return response.redirect(app.url_for('pdf_extract_upload'))
        elif 'show_text' in request.form.keys():
            # 显示对应页面中提取的信息
            label = request.form.get('show_text')
            if '#' in label:
                label, page = label.split('#')
            pages_results, keys_map = get_keys_map(result_json)
            pages = [ent for ent in pages_results if ent['label']==label]
            if 'page' not in vars():
                page = pages[0]['page']
            return template('./pdf_extract/runtime.html', keys_map=keys_map, pdf=pdf+f'#page={page}#toolbar=0', xlsx=xlsx, file=file)

    if request.method == 'GET':
        _, keys_map = get_keys_map(result_json)
        return template('./pdf_extract/runtime.html', keys_map=keys_map, pdf=pdf+'#toolbar=0', xlsx=xlsx, file=file)


def get_keys_map(pages_results):
    keys_map = {}
    for item in pages_results:
        label = item['label']
        page = item['page']
        context = item.get('context')
        keys_map[label] = keys_map.get(label, [])
        keys_map[label].append([[context], page])
    return pages_results, keys_map


# =======================word2word=======================
@app.route(load_config('webui', 'word2word'), methods=['GET', 'POST'])
async def word2word_upload(request):
    if request.method == 'GET':
        return template('./word2word/upload.html')
    if request.method == 'POST':
        if 'analysis' in request.form:
            save_path = await get_user_path(request)
            global result
            file_name, result = await call_api(request, save_path, load_config('api', 'word2word'))
            return response.redirect(app.url_for('word2word_show', file=file_name))


@app.route(load_config('webui', 'word2word')+'/show/<file>', methods=['GET', 'POST'])
async def word2word_show(request, file):
    import urllib.parse
    file = urllib.parse.unquote(file)
    result_src_docx_json = result['result_src_docx_json']
    result_tgt_docx_json = result['result_tgt_docx_json']
    tgt_docx = result['tgt_docx'].replace(os.getcwd(), '').replace('\\', '/')
    src_pdf = result['src_pdf'].replace(os.getcwd(), '').replace('\\', '/')
    tgt_pdf = result['tgt_pdf'].replace(os.getcwd(), '').replace('\\', '/')

    if request.method == 'POST':
        if 'show_all' in request.form.keys():
            # pages_results, keys_map = get_keys_map(json_path)
            # 把识别结果中涉及到的页面pdf高亮出来
            # highlight_pdf(upload_path, pages_results)
            return template('./word2word/runtime.html', keys_map={}, src_pdf=src_pdf, tgt_pdf=tgt_pdf, file=file)
        elif 'upload' in request.form.keys():
            return response.redirect(app.url_for('word2word_upload'))
        elif 'show_text' in request.form.keys():
            # 显示对应页面中提取的信息
            label = request.form.get('show_text')
            if '#' in label:
                label, src_page = label.split('#')
            # src_page
            pages_results, keys_map = get_keys_map(result_src_docx_json)
            pages = [ent for ent in pages_results if ent['label']==label]
            if 'src_page' not in vars():
                src_page = pages[0]['page']
            # tgt_page
            pages_results, _ = get_keys_map(result_tgt_docx_json)
            pages = [ent for ent in pages_results if ent['label']==label]
            if 'tgt_page' not in vars():
                tgt_page = pages[0]['page']

            return template('./word2word/runtime.html', keys_map=keys_map, src_pdf=src_pdf+f'#page={src_page}', 
                            tgt_pdf=tgt_pdf+f'#page={tgt_page}', docx=tgt_docx, file=file)

    if request.method == 'GET':
        _, keys_map = get_keys_map(result_src_docx_json)
        return template('./word2word/runtime.html', keys_map=keys_map, src_pdf=src_pdf, tgt_pdf=tgt_pdf, docx=tgt_docx, file=file)


# =======================lifecycle======================
@app.route(load_config('webui', 'lifecycle'), methods=['GET', 'POST'])
async def lifecycle_upload(request):
    if request.method == 'GET':
        return template('./lifecycle/upload.html')
    if request.method == 'POST':
        if 'analysis' in request.form:
            save_path = await get_user_path(request)
            global result
            file_name, result = await call_api(request, save_path, load_config('api', 'lifecycle'))
            return response.redirect(app.url_for('lifecycle_show', file=file_name))


@app.route(load_config('webui', 'lifecycle')+'/show/<file>', methods=['GET', 'POST'])
async def lifecycle_show(request, file):
    import urllib.parse
    file = urllib.parse.unquote(file)
    result_json = result['result_json']
    json_path = result['result_json']  # pdf解析的结果地址
    xlsx = result['xlsx_path']  # pdf解析的xlsx下载url
    pdf = result['pdf_path'].replace(os.getcwd(), '').replace('\\', '/')

    if request.method == 'POST':
        if 'show_all' in request.form.keys():
            pages_results, keys_map = get_keys_map(result_json)
            return template('./lifecycle/runtime.html', keys_map=keys_map, pdf=pdf+'#toolbar=0', xlsx=xlsx, file=file)
        elif 'upload' in request.form.keys():
            return response.redirect(app.url_for('lifecycle_upload'))
        elif 'show_text' in request.form.keys():
            # 显示对应页面中提取的信息
            label = request.form.get('show_text')
            if '#' in label:
                label, page = label.split('#')
            pages_results, keys_map = get_keys_map(result_json)
            pages = [ent for ent in pages_results if ent['label']==label]
            if 'page' not in vars():
                page = pages[0]['page']
            return template('./lifecycle/runtime.html', keys_map=keys_map, pdf=pdf+f'#page={page}#toolbar=0', xlsx=xlsx, file=file)

    if request.method == 'GET':
        _, keys_map = get_keys_map(result_json)
        return template('./lifecycle/runtime.html', keys_map=keys_map, pdf=pdf+'#toolbar=0', xlsx=xlsx, file=file)


# =======================checkreport======================
@app.route(load_config('webui', 'checkreport'), methods=['GET', 'POST'])
async def checkreport_upload(request):
    if request.method == 'GET':
        return template('./checkreport/upload.html')
    if request.method == 'POST':
        if 'analysis' in request.form:
            save_path = await get_user_path(request)
            global result
            file_name, result = await call_api(request, save_path, load_config('api', 'checkreport'))
            return response.redirect(app.url_for('checkreport_show', file=file_name))


@app.route(load_config('webui', 'checkreport')+'/show/<file>', methods=['GET', 'POST'])
async def checkreport_show(request, file):
    import urllib.parse
    file = urllib.parse.unquote(file)
    result_json = result['result_json']
    json_path = result['result_json']  # pdf解析的结果地址
    xlsx = result['xlsx_path']  # pdf解析的xlsx下载url
    pdf = result['pdf_path'].replace(os.getcwd(), '').replace('\\', '/')

    if request.method == 'POST':
        if 'show_all' in request.form.keys():
            pages_results, keys_map = get_keys_map(result_json)
            return template('./checkreport/runtime.html', keys_map=keys_map, pdf=pdf+'#toolbar=0', xlsx=xlsx, file=file)
        elif 'upload' in request.form.keys():
            return response.redirect(app.url_for('checkreport_upload'))
        elif 'show_text' in request.form.keys():
            # 显示对应页面中提取的信息
            label = request.form.get('show_text')
            if '#' in label:
                label, page = label.split('#')
            pages_results, keys_map = get_keys_map(result_json)
            pages = [ent for ent in pages_results if ent['label']==label]
            if 'page' not in vars():
                page = pages[0]['page']
            return template('./checkreport/runtime.html', keys_map=keys_map, pdf=pdf+f'#page={page}#toolbar=0', xlsx=xlsx, file=file)

    if request.method == 'GET':
        _, keys_map = get_keys_map(result_json)
        return template('./checkreport/runtime.html', keys_map=keys_map, pdf=pdf+'#toolbar=0', xlsx=xlsx, file=file)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True, auto_reload=True)
