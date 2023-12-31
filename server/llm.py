'''
以fast_api方式来部署大模型
'''

from bert4torch.pipelines import ChatGlm2OpenaiApi
import argparse

parser = argparse.ArgumentParser(description='llm')
parser.add_argument('--port', default=8000)
args = parser.parse_args()
port = int(args.port)

model_path = "E:/pretrain_ckpt/glm/chatglm2-6B"
generation_config  = {'mode':'random_sample',
                      'maxlen':2048, 
                      'default_rtype':'logits', 
                      'use_states':True
                      }

chat = ChatGlm2OpenaiApi(model_path, **generation_config)
chat.run(port=port)