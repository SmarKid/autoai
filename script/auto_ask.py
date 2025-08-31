import requests
import json
from logger import logger


def chat_with_openai(prompt, model="gpt-3.5-turbo", server_url="https://localhost:8000/v1"):
    # 请求头，可能需要根据实际情况调整
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY'  # 替换为你的实际API密钥
    }

    # 请求数据
    data = {
        'model': model,
        'messages': [
            {'role': 'user', 'content': prompt}
        ]
    }

    try:
        # 发送POST请求
        response = requests.post(f"{server_url}/chat/completions", headers=headers, json=data)

        # 检查响应状态码
        response.raise_for_status()

        # 返回响应中的内容，假设是JSON格式
        return response.json()['choices'][0]['message']['content']

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


def chat_with_ollama(prompt, model="qwen2.5:7b", server_url="http://localhost:11434"):
    """
    与Ollama模型进行对话
    
    Args:
        prompt (str): 用户输入的提示文本
        model (str): 要使用的模型名称，默认为qwen2.5:7b
        server_url (str): Ollama服务器地址，默认为http://localhost:11434
        
    Returns:
        str: 模型的回复
    """
    url = f"{server_url}/api/generate"

    # 准备请求数据
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        # 发送POST请求到Ollama API
        response = requests.post(url, json=data)
        response.raise_for_status()  # 检查请求是否成功

        # 解析响应
        result = response.json()
        return result.get('response', '')

    except requests.exceptions.RequestException as e:
        error_msg = f"调用Ollama API时发生错误: {e}"
        logger.error(error_msg)
        return None


def read_file_by_lines(file_path):
    """
    从文件中逐行读取内容，跳过空行
    
    Args:
        file_path (str): 文件路径
        
    Yields:
        str: 每一行的内容（去除首尾空白字符）
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # 去除首尾空白字符并检查是否为空行
                cleaned_line = line.strip()
                if cleaned_line:  # 如果不是空行
                    yield cleaned_line
    except FileNotFoundError:
        error_msg = f"错误：找不到文件 '{file_path}'"
        logger.error(error_msg)
    except Exception as e:
        error_msg = f"读取文件时发生错误: {e}"
        logger.error(error_msg)


def readFile(file_path):
    file = open(file_path, "r", encoding='utf-8')
    content = file.read()
    file.close()
    return content


def main():
    file_path = "E:\学习资料\哲学\西方哲学\西方哲学原文材料\逻辑学-导论原文.txt"
    write_file_path = "E:\学习资料\哲学\西方哲学\西方哲学原文材料\逻辑学-导论-ai导读.txt"
    model = "gemma3:12b"

    prompt_template = readFile("template/summarize.txt")
    translation_result_template = readFile("template/summarize_result.txt")
    times = 10
    with open(write_file_path, "a", encoding='utf-8') as file:
        for line in read_file_by_lines(file_path):
            if (times <= 0):
                break
            # times -= 1
            if (len(line)) > 20:
                original_text = line
                prompt = prompt_template.replace("{original_text}", original_text)
                translation_text = chat_with_ollama(prompt, model)
                result = translation_result_template.replace("{original_text}", original_text).replace(
                    "{translation_text}", translation_text)
                print(result)
                file.write(result)
            else:
                file.write(line + "\n")


if __name__ == "__main__":
    print("开始")
