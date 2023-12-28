'''向量的存储，查询，检索模块
'''
from fastapi import FastAPI
import uvicorn
from bert4vector import BertVector

app = FastAPI()
bertvec = BertVector('E:/pretrain_ckpt/simbert/sushen@simbert_chinese_tiny')

@app.post('/add_corpus')
async def add_corpus(request):
    '''把text转为向量'''
    pass

@app.post('/search')
async def search(request):
    '''找出topk的结果'''
    pass

async def extract_text_from_pdf(file_path: str):
    import PyPDF2
    contents = []
    with open(file_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
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
async def text2vec(request):
    '''把text转为向量'''
    content = await extract_text_from_pdf()
    # 调用vector的接口，把文字转为向量


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8100)