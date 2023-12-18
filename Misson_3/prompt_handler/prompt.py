import json

from langchain.chains import ConversationChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper

from Misson_3.conf import API_KEY
from Misson_3.db_handler.vector_handler import Vector
from Misson_3.prompt_handler.history import History
import os

os.environ["OPENAI_API_KEY"] = API_KEY


class Prompt:
    def __init__(self):
        llm = ChatOpenAI(temperature=0.1, max_tokens=200, model="gpt-3.5-turbo-16k")
        self.parse_intent_chain = self.create_chain(
            llm=llm,
            template_path="/Users/lina/PycharmProjects/lina.02/Misson_3/prompt_handler/prompt_txt/parse_intent.txt",
            output_key="intent",
        )

        self.check_the_questions = self.create_chain(
            llm=llm,
            template_path="/Users/lina/PycharmProjects/lina.02/Misson_3/prompt_handler/prompt_txt/check_the_questions.txt",
            output_key="the_question",
        )

        # response
        self.default_chain = self.create_chain(
            llm=llm,
            template_path="/Users/lina/PycharmProjects/lina.02/Misson_3/prompt_handler/prompt_txt/response_default.txt",
            output_key="answer",
        )
        self.response_with_web = self.create_chain(
            llm=llm,
            template_path="/Users/lina/PycharmProjects/lina.02/Misson_3/prompt_handler/prompt_txt/response_with_web.txt",
            output_key="answer",
        )
        self.response_final = self.create_chain(
            llm=llm,
            template_path="/Users/lina/PycharmProjects/lina.02/Misson_3/prompt_handler/prompt_txt/response_final.txt",
            output_key="answer",
        )

        # search prompt
        self.search_value_check_chain = self.create_chain(
            llm=llm,
            template_path="/Users/lina/PycharmProjects/lina.02/Misson_3/prompt_handler/prompt_txt/search_value_check.txt",
            output_key="related_web_search_results",
        )
        self.search_compression_chain = self.create_chain(
            llm=llm,
            template_path="/Users/lina/PycharmProjects/lina.02/Misson_3/prompt_handler/prompt_txt/search_compression_chain.txt",
            output_key="output",
        )

    def search_info(self, user_message):
        search = GoogleSearchAPIWrapper(
            google_api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyCvwJTlkKe0gW6ZEVcxl8uRYEX61k2t2Ek"),
            google_cse_id=os.getenv("GOOGLE_CSE_ID", "06cc9133f435c4908")
        )

        search_tool = Tool(
            name="Google Search",
            description="Search Google for recent results in detail.",
            func=search.run,
        )

        context = {"user_message": user_message,
                   "related_web_search_results": search_tool.run(user_message)
                   }

        has_value = self.search_value_check_chain.run(context)

        print(has_value)
        if has_value == "Y":
            answer = self.search_compression_chain.run(context)
            return answer
        else:
            return ""

    @staticmethod
    def read_prompt_template(file_path: str) -> str:
        with open(file_path, "r") as f:
            prompt_template = f.read()
        return prompt_template

    def create_chain(self, llm, template_path, output_key):
        return LLMChain(
            llm=llm,
            prompt=ChatPromptTemplate.from_template(
                template=self.read_prompt_template(template_path)
            ),
            output_key=output_key,
            verbose=True,
        )


def gernerate(user_message, is_new, conversation_id: str) -> dict[str, str]:
    INTENT_LIST_TXT = "prompt_txt/intent_list.txt"
    vc = Vector()
    pt = Prompt()
    ht = History()

    # 히스토리 가져오기
    history_file = ht.load_conversation_history(conversation_id)

    context = dict(user_message=user_message)
    context["input"] = context["user_message"]
    context["intent_list"] = pt.read_prompt_template(INTENT_LIST_TXT)
    context["related_documents"] = ""

    # 새로운 대화인지 아닌지 체크
    if is_new is False:
        context['chat_history'] = ht.get_chat_history(conversation_id)
    else:
        context['chat_history'] = ""
    context['substance'] = ''

    # 사용자가 원하는게 뭔지 체크
    intent = pt.parse_intent_chain.run(context)
    # 간단한 인사면 넘기기
    if intent == "social_interaction":
        answer = pt.response_final.run(
            {'user_message': user_message, 'system_answer': '', 'history': context['chat_history']})

    # 간단한 인사가 아니면, 정보 가져와서 리턴
    else:
        #  '히스토리'와 함께 사용자 마지막 질문을 가지고 원하는 것이 뭔지 다시 파악해서 'keyword'로 알려달라고 하기
        json_fmt = pt.check_the_questions.run({'user_message': user_message, 'chat_history': context['chat_history']})
        result = json.loads(json_fmt)
        substance = result['keyword']
        context['substance'] = substance
        # keyword 로 vector db 검색
        context["related_documents"] = vc.query_db(substance)

        # 정보가 더 필요한 지 확인
        intent = pt.parse_intent_chain.run(context)
        print(intent)
        if intent == "insufficient_information":
            # 'keyword'로 구글 검색
            context["related_web_search_results"] = pt.search_info(substance)
            system_answer = pt.response_with_web.run(context)
        else:
            system_answer = pt.default_chain.run(context)

        # 결과를 다시 친절하게 답변 해달라고 하기
        answer = pt.response_final.run({'user_message': user_message,
                                        'system_answer': system_answer,
                                        'history': context['chat_history']
                                        })
    ht.log_user_message(history_file, user_message)
    ht.log_bot_message(history_file, answer)

    return answer


if __name__ == "__main__":
    import random
    import string

    _LENGTH = 10  # 12자리

    # 숫자 + 대소문자
    string_pool = string.ascii_letters + string.digits

    # 랜덤한 문자열 생성
    chat_id = ""
    for i in range(_LENGTH):
        chat_id += random.choice(string_pool)  # 랜덤한 문자열 하나 선택
    print(chat_id)

    # print(gernerate("카카오 창립자가 누구야?", True, chat_id))
    print(gernerate("그 중 김범수 나이는? ", False, "A8MkQYczlq"))
