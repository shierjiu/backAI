# AiEvaluationy/chat_cozi.py
import requests
import json
def chat_cozi(query):
    # cozi参数
    token = "pat_7Kg91MXdAdOtLK4x5UUHGHVrww7JCDXjlWdRzJKlhovfT6P5cw4fVpIxaBcqpM04"
    bot_id = "7497790981790728204"
    user_id = "123"  # 固定的任意字符串即可

    url =  "https://api.coze.cn/v3/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "bot_id": bot_id,
        "user_id": user_id,
        "stream": True,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": query,
                "content_type": "text"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body, stream=True)
    answer = ""
    expecting_data = False  # 标记下一行是否是期待的data

    for line in response.iter_lines():
        if line:
            line_decode = line.decode('utf-8')
            if expecting_data:
                data = line_decode.split("data:", 1)[1].strip()
                json_data = json.loads(data)
                if json_data.get("type") == "answer":
                    answer = json_data["content"]
                    break
            if "event:conversation.message.completed" in line_decode:
                expecting_data = True

    print(answer)
    return answer


chat_cozi("你是谁")


