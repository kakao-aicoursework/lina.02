import chromadb
import pandas as pd
import openai
import json


def init_data():
    tmp = []
    info = []
    # file_name = "./data/project_data_카카오톡채널.txt"
    f = open("./data/project_data_카카오톡채널.txt", 'r')
    lines = f.read().splitlines()
    for line in lines:
        tmp.append(line)
    f.close()

    for index, value in enumerate(tmp):
        if value.startswith("#"):
            text = ''
            i = 1
            while True:
                # TODO : '#'전까지로 변경 필요
                if tmp[index + i] == '':
                    break
                text = text + tmp[index + i]
                i = i + 1

            info.append({
                "title": value,
                "content": text
            })

    return json.dumps(info)


def get_chanel_info():
    return init_data()


def send_gpt(messages, temperature=1.5, max_tokens=2048):
    openai.api_key = "sk-"
    functions = [
        {
            "name": "get_chanel_info",
            "description": "카카오톡 채널에 대한 정보를 json으로 전달해줍니다.",
            "parameters": {
                "type": "object",
                "properties": {
                },
            },
        }
    ]
    messages.append(
          {
              "role": "system",
              "content": "당신은 상담사 입니다. 친절하게 얘기해주세요. "
          }
      )
    # print(messages)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        functions=functions,
        function_call="auto",
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return completion


def main(messages):
    completion = send_gpt(messages)
    response_message = completion["choices"][0]["message"]

    # print(response_message)

    if response_message.get("function_call"):
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_chanel_info": get_chanel_info,
        }
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        # function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call()
        messages.append(response_message)
        messages.append(
            {
                "role": "function",
                "name": "get_chanel_info",
                "content": str(function_response),
            }
        )

        r2 = send_gpt(messages)
        f_response = r2["choices"][0]["message"]
    else:
        f_response = response_message

    print(f_response.content)
    return f_response


if __name__ == '__main__':
    main([
        {
              "role": "user",
              "content": "카카오톡 채널이 뭐야?"
          }
    ])
