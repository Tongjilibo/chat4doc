'''
以fast_api方式来部署大模型
'''

from bert4torch.chat import OpenaiApiChatglm2

model_path = "E:/pretrain_ckpt/glm/chatglm2-6B"
generation_config  = {'mode':'random_sample',
                      'maxlen':2048, 
                      'default_rtype':'logits', 
                      'use_states':True
                      }

chat = OpenaiApiChatglm2(model_path, **generation_config)
chat.run()