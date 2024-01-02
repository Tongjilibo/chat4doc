import os
from sanic import Sanic, response
import jinja2
import requests
from bert4torch.snippets import JsonConfig
import re


config = JsonConfig('../config.json')
webui_url = config.webui_url
route_ = webui_url.split('/')[-1]
text2vec_url = config.server_url + config.server_route_text2vec

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


async def call_api(request, save_path, api_url):
    '''上传并解析pdf得到对应结果'''
    # 把file拷贝到指定的文件位置
    file = request.files.get('file')
    file_name = file.name.split('.')[0].replace(' ', '')
    upload_path = os.path.join(save_path, file_name, file.name)  # 保存文件地址
    os.makedirs(os.path.join(save_path, file_name), exist_ok=True)
    with open(upload_path, 'wb') as f:
        f.write(file.body)

    data = {'file': file}  # {'file': open('C:/Users/user/Desktop/资料概要.pdf', 'rb')}
    headers = {"Content-type": "application/json"}
    response = requests.post(url=api_url, headers=headers, files=data)
    return file_name, response.json()


# =======================chat4doc=======================
@app.route(route_, methods=['GET', 'POST'])
async def chat4doc_upload(request):
    if request.method == 'GET':
        return template('./upload.html')
    if request.method == 'POST':
        if 'analysis' in request.form:
            save_path = await get_user_path(request)
            file = request.files.get('file')
            file_name = file.name.split('.')[0].replace(' ', '')
            upload_path = os.path.join(save_path, file_name, file.name)  # 保存文件地址
            os.makedirs(os.path.join(save_path, file_name), exist_ok=True)
            with open(upload_path, 'wb') as f:
                f.write(file.body)

            data = {'file': file}  # {'file': open('C:/Users/user/Desktop/资料概要.pdf', 'rb')}
            requests.post(url=text2vec_url, files=data)
            return response.redirect(app.url_for('chat4doc_show', file=file_name))


@app.route(route_+'/show/<file>', methods=['GET', 'POST'])
async def chat4doc_show(request, file):
    import urllib.parse
    file = urllib.parse.unquote(file)
    user_url = await get_user_path(request, url=True)
    pdf = user_url + f'/{file}/{file}.pdf'  # pdf用于展示的url
    if request.method == 'POST':
        if 'show_all' in request.form.keys():
            return template('./runtime.html', pdf=pdf+'#toolbar=0', file=file)
        elif 'upload' in request.form.keys():
            return response.redirect(app.url_for('chat4doc_upload'))
        elif 'show_text' in request.form.keys():
            return template('./runtime.html', pdf=pdf+f'#toolbar=0', file=file)

    if request.method == 'GET':
        return template('./runtime.html', pdf=pdf, file=file)


def get_keys_map(pages_results):
    keys_map = {}
    for item in pages_results:
        label = item['label']
        page = item['page']
        context = item.get('context')
        keys_map[label] = keys_map.get(label, [])
        keys_map[label].append([[context], page])
    return pages_results, keys_map


if __name__ == '__main__':
    host = re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', webui_url)[0]
    port = int(re.findall(':[0-9]+', webui_url)[0][1:])

    app.run(host, port=port, debug=True, auto_reload=True)
