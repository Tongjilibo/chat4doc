'''
以fast_api方式来部署大模型
'''

from bert4torch.pipelines import ChatGlm2OpenaiApi
from bert4torch.snippets import JsonConfig
import re


config = JsonConfig('./config.json')
llm_model_path = config.llm_model_path
llm_url = config.llm_url
host = re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', llm_url)[0]
port = int(re.findall(':[0-9]+', llm_url)[0][1:])


generation_config  = {'mode':'random_sample',
                      'maxlen':2048, 
                      'default_rtype':'logits', 
                      'use_states':True
                      }

chat = ChatGlm2OpenaiApi(llm_model_path, **generation_config)
chat.run(host=host, port=port)