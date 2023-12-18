from Misson_3.dto.dto import ChatbotRequest
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
import json

# 환경 변수 처리 필요!
load_dotenv()
openai.api_key = os.environ.get('api_key')
os.environ["OPENAI_API_KEY"] = os.environ.get('api_key')
logger = logging.getLogger("Callback")

RAW_DATA = "./data/project_data_카카오싱크.txt"


def callback_handler(request: ChatbotRequest) -> dict:


    # 참고 링크 통해 payload 구조 확인 가능
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

    time.sleep(3.0)

    url = request.userRequest.callbackUrl
    if url:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        resp = requests.post(url, data=json.dumps(payload), headers=headers)
        print(resp.json())


def build_summarizer(llm):
    system_message = "As a Kakao sink counselor, you have to respond kindly to people's questions. The contents of Kakao sink are as follows\n " \
                     "{text} \n " \
                     "You always answer in Korean. Answer me in 200 characters"
    system_message_prompt = SystemMessage(content=system_message)

    human_template = "\n\n{ask}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                    human_message_prompt])

    chain = LLMChain(llm=llm, prompt=chat_prompt)
    return chain
