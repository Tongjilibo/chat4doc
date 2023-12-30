'''向量的存储，查询，检索模块
'''
from fastapi import FastAPI, UploadFile, File, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import uvicorn
from bert4vector import BertVector
import json
import aiohttp


app = FastAPI()
bertvec = BertVector('E:\pretrain_ckpt\embedding\moka-ai@m3e-base', device='cuda')


async def extract_text_from_pdf(file_path:str=None, file: UploadFile = File(...)):
    import PyPDF2
    contents = []
    if file_path is not None:
        pdf_reader = PyPDF2.PdfReader(open(file_path, 'rb'))
    elif file is not None:
        pdf_reader = PyPDF2.PdfReader(file.file._file)

    for page in pdf_reader.pages:
        page_text = page.extract_text().strip()
        raw_text = [text.strip() for text in page_text.splitlines() if text.strip()]
        new_text = ''
        for text in raw_text:
            new_text += text
            if text[-1] in ['.', '!', '?', '。', '！', '？', '…', ';', '；', ':', '：', '”', '’', '）', '】', '》', '」',
                            '』', '〕', '〉', '》', '〗', '〞', '〟', '»', '"', "'", ')', ']', '}']:
                contents.append(new_text)
                new_text = ''
        if new_text:
            contents.append(new_text)
    return contents


@app.post('/text2vec')
async def text2vec(file: UploadFile = File(...)):
    '''把text转为向量'''
    content = await extract_text_from_pdf(file=file)
    # 调用vector的接口，把文字转为向量
    bertvec.add_corpus(content)
    return content


@app.post('/search')
async def search(request: Request):
    '''找出topk的结果'''

    # 检索对应的文档
    data = await request.body()
    data = json.loads(jsonable_encoder(data))
    queries = data['query']
    resp = bertvec.search(queries, topk=5)[queries]

    message = ''
    for i, item in enumerate(resp, start=1):
        message += f"参考材料{i}: {item['text']}\n"
    message += f'根据上述材料回答：{queries}'

    system = '你是一个文档问答助手，请根据下述的问题和参考材料进行回复，如果问题在参考材料中找不到，请回复不知道，不允许随意编造答案。'
    data = {
        "messages": [
            {
                "content": message,
                "role": "user"
            },
            {
                "content": system,
                "role": "system"
            }
        ],
        "model": "default",
        "stream": False
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8000/chat', json=data) as response:
            resp = await response.text()
    print(resp)
    return JSONResponse(content=resp, status_code=status.HTTP_200_OK)

if __name__ == '__main__':
    uvicorn.run(app='server:app', host='0.0.0.0', port=8100, reload=True, workers=1)