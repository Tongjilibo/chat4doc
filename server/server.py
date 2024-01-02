'''向量的存储，查询，检索模块
'''
from fastapi import FastAPI, UploadFile, File, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from bert4vector import BertVector
import json
import aiohttp
import torch
from bert4torch.snippets import JsonConfig
import re


config = JsonConfig('./config.json')
llm_url = config.llm_url.replace('0.0.0.0', '127.0.0.1')
server_url = config.server_url
embedding_model_path = config.embedding_model_path
server_route_text2vec = config.server_route_text2vec
server_route_search = config.server_route_search
server_route_summary = config.server_route_summary
prompt_system = config.prompt_system
prompt_system_summary = config.prompt_system_summary

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] , #这里可以填写["*"]，表示允许任意ip
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
bertvec = BertVector(embedding_model_path, device=device)


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


@app.post(server_route_text2vec)
async def text2vec(file: UploadFile = File(...)):
    '''把text转为向量，上传文件的时候使用'''
    content = await extract_text_from_pdf(file=file)
    # 调用vector的接口，把文字转为向量
    bertvec.add_corpus(content)
    return content


@app.post(server_route_summary)
async def summary():
    '''根据预料来总结文档'''

    message = '请总结下述短文：'
    id_ = 0
    while (len(message) < 512) and (id_ < len(bertvec.corpus)):
        message += bertvec.corpus[id_]
        id_ += 1
        
    content = await call_llm(prompt_system_summary, message)
    resp = {'content': content}
    return JSONResponse(content=resp, status_code=status.HTTP_200_OK)


@app.post(server_route_search)
async def search(request: Request):
    '''找出topk的结果，并调用相应的大模型来结合知识库回答问题，点击发送按钮时候调用'''
    # 检索对应的文档
    data = await request.body()
    data = json.loads(jsonable_encoder(data))
    queries = data['query']
    resp = bertvec.search(queries, topk=5)[queries]

    reference = []
    for i, item in enumerate(resp, start=1):
        reference.append(f"[{i}]. {item['text']}")
    message = '\n'.join(reference) + f'根据上述材料回答：{queries}'
    content = await call_llm(prompt_system, message)
    
    resp = {'content': content, 'reference': '\n'.join(reference)}
    return JSONResponse(content=resp, status_code=status.HTTP_200_OK)


async def call_llm(system, message):
    '''调用大模型'''
    data = {
        "messages": [
            {
                "content": system,
                "role": "system"
            },
            {
                "content": message,
                "role": "user"
            }
        ],
        "model": "default",
        "stream": False
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(llm_url, json=data) as response:
            content = await response.json()
            content = content['choices'][0]['message']['content']
    return content


if __name__ == '__main__':
    host = re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', server_url)[0]
    port = int(re.findall(':[0-9]+', server_url)[0][1:])
    uvicorn.run(app='server:app', host=host, port=port, reload=True)