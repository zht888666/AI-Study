# 定义后台 API 的 URL
import json
# 转发 Gradio 临时文件给 FastAPI 时，需要保留上传文件名。
import os
import requests

chat_with_agent_url = "http://127.0.0.1:6605/chat/agent_chat"
chat_url = "http://127.0.0.1:6605/chat/chat"


def get_file_path(file):
    # 新版本 Gradio 可能把上传文件传成字典，而不是普通路径字符串。
    if isinstance(file, dict):
        return file.get("path") or file.get("name")
    return file


def parse_prompt(prompt):
    # ChatInterface 可能传入多模态字典，也可能只传入纯文本。
    if isinstance(prompt, dict):
        return prompt.get("text", ""), prompt.get("files", [])
    return str(prompt), []


def chat_with_agent(prompt, history, sys_prompt, history_len, temperature, max_tokens, stream, session_id):
    # 构建文件和表单数据
    # 构建文件和表单数据，旧版本
    # files = [('files', (open(file_path, 'rb'))) for file_path in prompt["files"]]
    # 对应新版本
    # 从prompt中获得files 打开文件后使用元组接收进行存储，可以上传很多同时处理
    # files = [('files', (open(file_path['path'], 'rb'))) for file_path in prompt["files"]]
    prompt_text, prompt_files = parse_prompt(prompt)
    # 打开本地临时文件前，先统一 Gradio 上传文件对象的格式。
    file_paths = [get_file_path(file) for file in prompt_files]
    # 同时发送文件名和文件句柄，保证 FastAPI 能正确拿到 UploadFile.filename。
    files = [('files', (os.path.basename(file_path), open(file_path, 'rb'))) for file_path in file_paths if file_path]
    if prompt_files != []:
        # 提取文件路径并拼接到 query 中
        # 把上传后的临时文件路径放进 query，方便后端把文件和当前问题关联起来。
        query = f'{prompt_text}\n' + "".join(file_paths[0])
    else:
        query = f'{prompt_text}\n'
    # 构建请求数据
    data = {
        "query": query,
        "sys_prompt": sys_prompt,
        "history_len": history_len,
        "history": [str(h) for h in history],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "session_id": session_id,
    }

    # 发送请求到 FastAPI 后端
    try:
        response = requests.post(chat_with_agent_url, files=files, data=data, stream=True)
        if response.status_code == 200:
            chunks = ""
            if stream:
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        data = json.loads(chunk)
                        chunks += data.get('answer', '')
                        yield chunks

            else:
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    data = json.loads(chunk)
                    chunks += data.get('answer', '')

                yield chunks

        else:
            yield "请求失败，请检查后台服务器是否正常运行。"
    except Exception as e:
        yield f"发生错误：{e}"
