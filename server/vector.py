'''向量的存储，查询，检索模块
'''
from fastapi import FastAPI, UploadFile, File, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import uvicorn
from bert4vector import BertVector
import json


app = FastAPI()
bertvec = BertVector('E:\pretrain_ckpt\embedding\moka-ai@m3e-base')

@app.post('/search')
async def search(request: Request):
    '''找出topk的结果'''
    data = await request.body()
    data = json.loads(jsonable_encoder(data))
    queries = data['query']
    resp = bertvec.search(queries, topk=5)
    return JSONResponse(content=resp, status_code=status.HTTP_200_OK)


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


if __name__ == '__main__':
    uvicorn.run(app='vector:app', host='0.0.0.0', port=8100, reload=True)