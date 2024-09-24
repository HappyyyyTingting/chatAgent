import time

from tools import tools_map
from prompt import gen_prompt
from model_provider import ModelProvider
from dotenv import load_dotenv

load_dotenv()
mp = ModelProvider()

def parse_thoughts(response):
    '''
       response:{
           'action':{
               'name':'action_name',
               'args':{
                   'arg name':'arg value'
               }
           },
           'thoughts':{
               'text':'thought',
               'plan':'plan',
               'criticism':'criticism',
               'speak':'current stage return to user',
               'reasoning':""
           }
       }
    '''
    try:
        thoughts = response.get("thoughts")
        plan = thoughts.get("plan")
        criticism = thoughts.get("criticism")
        observation = thoughts.get("speak")
        reasoning = thoughts.get("reasoning")
        prompt = f"paln:{plan} \n reasoning:{reasoning} \n criticism :{criticism} \n obervation:{observation}"
        return prompt
    except Exception as err:
        print("Parse thoughts err:{}".format(err))
        return "".format(err)



def agent_execute(query, max_request_times):
    chat_history = []
    cur_request_time = 0
    agent_scratch = ""
    while cur_request_time < max_request_times:
        cur_request_time += 1

        prompt = gen_prompt(query, agent_scratch)
        '''
        prompt 包含：
            1.任务描述
            2.调用工具描述
            3.用户输入：user_mgs
            4.assistant mgs
            5.结果限制
            6.更好实践描述
        '''
        start_time = time.time()
        print("================{}.Begin to call llm.================".format(cur_request_time))
        # response = call_llm()
        response = mp.chat(prompt, chat_history)

        end_time = time.time()
        print("================{}End to call llm, time spent {}". format(cur_request_time, end_time - start_time))

        if not response or not isinstance(response, dict):
            print("Call llm error, begin to retry.....", response)
            continue
        '''
        response:{
            'action':{
                'name':'action_name',
                'args':{
                    'arg name':'arg value'
                }
            },
            'thoughts':{
                'text':'thought',
                'plan':'plan',
                'criticism':'criticism',
                'speak':'current stage return to user',
                'reasoning':""
            }
        }
        '''
        action_info = response.get("action")
        action_name = action_info.get("name")
        action_args = action_info.get("args")
        print("Current action:{}, and its args:{}", action_name, action_args)

        if action_name == "finish":
            final_answer = action_args.get("answer")
            print("final answer:", final_answer)
            break

        observation = response.get("thoughts").get("speak")
        try:
            # tools_map = {} #mapping from action_name to func -> {"action_name":func}
            func = tools_map.get(action_name)
            observation = func(**action_args)

        except Exception as err:
            print("Failed to call tools:", err)

        agent_scratch = agent_scratch + "\n" + observation

        user_msg = "decide which tool to user"
        assistant_msg = parse_thoughts(response)
        chat_history.append([user_msg, assistant_msg])







def main(max_request_times = 10):
    while True:
        query = input("Pls input your question.")
        if query == "exit":
            return

        agent_execute(query, max_request_times)


if __name__ == "__main__":
    main()