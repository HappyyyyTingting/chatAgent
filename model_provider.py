import json
import os

from zhipu import ZhipuAI
from prompt import user_prompt

class ModelProvider(object):

    def __init__(self):
        self.api_key = os.environ.get("API_KEY")
        self.model_name = os.environ.get("MODEL_NAME")
        self._client = ZhipuAI(api_key=self.api_key)
        self.max_retry_time = 3

    def chat(self, prompt, chat_history):
        cur_retry_time = 0
        while cur_retry_time < self.max_retry_time:
            cur_retry_time += 1
            try:
                messages = [
                    {"role":"system", "content":prompt}
                ]
                for history in chat_history:
                    messages.append({"role":"user", "content":history[0]})
                    messages.append({"role":"assistant", "content": history[1]})

                # 最后1条信息是用户的输入
                messages.append({"role":"user", "content":user_prompt})

                response = self._client.chat.completions.create(
                    model = self.model_name,
                    messages = messages
                )
                print(response.choices[0].message.content)
                content = json.loads(response.choices[0].message.content)
                # content = json.loads(response.choices[0].message.content)

                return content
            except Exception as err:
                print("Failed to call LLM: {}".format(err))


        return {}