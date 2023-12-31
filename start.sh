# 大模型接口
python ./server/llm.py  --port 8000 &

# 后台服务器接口
python ./server/server.py --port 8100 &

# 前端界面接口
cd client_py
python ./webui.py --port 8083 &