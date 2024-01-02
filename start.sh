# 大模型接口
python ./server/llm.py &

# 后台服务器接口
python ./server/server.py &

# 前端界面接口
cd client_py
python ./webui.py &