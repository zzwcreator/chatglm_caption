import requests as requests
# 在这里配置您在本站的API_KEY
api_key = "**"
headers = {
    "Authorization": 'Bearer ' + api_key,
}

def get_chat(prompt, mode):
    params = {
    "messages": [
        {
            "role": 'user',
            "content": prompt
        }
    ],
    # 如果需要切换模型，在这里修改
    "model": mode
    # "model": 'gpt-4'
    }
    response = requests.post(
        "https://aigptx.top/v1/chat/completions",
        headers=headers,
        json=params,
        stream=False
    )
    res = response.json()
    res_content = res['choices'][0]['message']['content']
    return res_content


def get_res(prompt):
    return get_chat(prompt, 'gpt-3.5-turbo')

# while 1:
#     question = input("输入您的问题\n")
#     print(get_chat(question, 'gpt-3.5-turbo'))
