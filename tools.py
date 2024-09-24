import os
from langchain_community.tools.tavily_search import TavilySearchResults
import json

def _get_work_root():
    return os.environ.get("WORK_ROOT", "./data/llm_result")

WORK_ROOT = _get_work_root()

def read_file(filename):
    filename = os.path.join(WORK_ROOT, filename)
    if not os.path.exists(filename):
        return f"{filename} not exits, pls make sure file exits before reading."

    with open(filename,"r") as f:
        return "\n".join(f.readlines())


def append2file(filename, content):
    filename = os.path.join(WORK_ROOT, filename)
    if not os.path.exists(filename):
        return f"{filename} not exits, pls make sure file exits before write to it."

    with open(filename, 'a') as f:
        f.write(content)

    return f"Append content to {filename} success."


def write2file(filename, content):
    filename = os.path.join(WORK_ROOT, filename)
    with open(filename, "w") as f:
        f.write(content)

    return f"Write content to {filename} success"


def search(query):
    tool = TavilySearchResults(max_results = 5)
    try:
        '''
        res:
        [
        {
            "content":"",
            "url":""
        }
        ]
        '''
        res = tool.invoke(query)
        content_list = [ item["content"] for item in res]
        return "\n".join(content_list)
    except Exception as err:
        return f"Search erro: {err}"


tools_info = [
    {
        "name": "read_file",
        "description": "read file form agent generate, should write file before read",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "description": "read file name"
            }
        ]
    },
    {
        "name": "append2file",
        "description": "append llm content to file, should write file before read",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "description": "file name"
            },
            {
                "name": "content",
                "type": "string",
                "description": "append to file content"
            }
        ]
    },
{
        "name": "write2file",
        "description": "write llm content to file",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "description": "file name"
            },
            {
                "name": "content",
                "type": "string",
                "description": "write to file content"
            }
        ]
    },
{
        "name": "finish",
        "description": "finish user's task",
        "args": [
            {
                "name": "answer",
                "type": "string",
                "description": "the finial result"
            }
        ]
    },
    {
        "name": "search",
        "description": "a search engine, you can gain additional knowledge though this search engine "
                       "when you are unsure of large model return",
        "args": [
            {
                "name": "query",
                "type": "string",
                "description": "search query to look up"
            }
        ]
    }
]

tools_map = {
    "read_file": read_file,
    "append2file": append2file,
    "write2file": write2file,
    "search": search
}

"""
生成工具描述
:return:
"""
def gen_tools_desc():
    tools_desc = []
    for idx, t in enumerate(tools_info):
        args_desc = []
        for info in t["args"]:
            args_desc.append({
                "name": info["name"],
                "description": info["description"],
                "type": info["type"]
            })
        args_desc = json.dumps(args_desc, ensure_ascii=False)
        tool_desc = f"{idx + 1}.{t['name']}:{t['description']}, args: {args_desc}"
        tools_desc.append(tool_desc)
    tools_prompt = "\n".join(tools_desc)
    return tools_prompt