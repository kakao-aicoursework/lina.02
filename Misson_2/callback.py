from dto import ChatbotRequest
from samples import list_card
import aiohttp
import time
import logging
import openai
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import SystemMessage
import os
import requests
from dotenv import load_dotenv

# 환경 변수 처리 필요!
load_dotenv()
openai.api_key = os.environ.get('api_key')
os.environ["OPENAI_API_KEY"] = os.environ.get('api_key')
logger = logging.getLogger("Callback")

RAW_DATA = "/Users/lina/PycharmProjects/kakaochattest_guide/data/project_data_카카오싱크.txt"


async def callback_handler(request: ChatbotRequest) -> dict:

    raw_data = init_data()
    # print(raw_data)

    writer_llm = ChatOpenAI(temperature=0.1, max_tokens=300, model="gpt-3.5-turbo-16k")
    summarizer = build_summarizer(writer_llm)

    anwser = summarizer.run(text=raw_data, ask=request.userRequest.utterance)

    print(anwser)

   # 참고링크 통해 payload 구조 확인 가능
    payload = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": anwser
                    }
                }
            ]
        }
    }
    # ===================== end =================================
    # 참고링크1 : https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/ai_chatbot_callback_guide
    # 참고링크1 : https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/answer_json_format

    time.sleep(5.0)

    url = request.userRequest.callbackUrl
    print(url)
    requests.post(url=url, json=payload)
    # if url:
    #     async with aiohttp.ClientSession() as session:
    #         async with session.post(url=url, json=payload, ssl=False) as resp:
    #             await resp.json()


def init_data():
    tmp = []
    info = {}
    f = open(RAW_DATA, 'r')
    lines = f.read().splitlines()
    for line in lines:
        tmp.append(line)
    f.close()

    start = False
    for index, value in enumerate(tmp):
        if value.startswith("#") and not start:
            start = True
            title = value
            text = ''
        elif start:
            text = text + value

        if len(tmp) < index + 2:
            break
        else:
            if tmp[index + 1].startswith('#') and start:
                start = False
                info[title.replace(" ", "").replace("#", "")] = text.replace(" ", "")
                # info.append({
                #     "title": title.replace(" ", ""),
                #     "content": text.replace(" ", "")
                # })
    # print(info)
    return info


def build_summarizer(llm):
    system_message = "As a Kakao sink counselor, you have to respond kindly to people's questions. The contents of Kakao sink are as follows\n {text} \n You always answer in Korean. 200자 이재로 답해줘"
    system_message_prompt = SystemMessage(content=system_message)

    human_template = "\n\n{ask}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                    human_message_prompt])

    chain = LLMChain(llm=llm, prompt=chat_prompt)
    return chain
