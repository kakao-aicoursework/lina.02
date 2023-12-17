from langchain.chains import ConversationChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper

from Misson_3.conf import API_KEY
from Misson_3.db_handler.vector_handler import Vector

import os

os.environ["OPENAI_API_KEY"] = API_KEY


INTENT_LIST_TXT = "prompt_txt/intent_list.txt"
INTENT_PROMPT_TEMPLATE = "prompt_txt/parse_intent.txt"
DEFAULT_RESPONSE = "prompt_txt/response_default.txt"
RESPONSE_WITH_WEB = "prompt_txt/response_with_web.txt"
RESPONSE_FINAL = "prompt_txt/response_final.txt"

SEARCH_VALUE_CHECK_PROMPT_TEMPLATE = "prompt_txt/search_value_check.txt"
SEARCH_COMPRESSION_PROMPT_TEMPLATE = "prompt_txt/search_compression_chain.txt"

llm = ChatOpenAI(temperature=0.1, max_tokens=200, model="gpt-3.5-turbo")


def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()
    return prompt_template


def create_chain(llm, template_path, output_key):
    return LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_template(
            template=read_prompt_template(template_path)
        ),
        output_key=output_key,
        verbose=True,
    )


parse_intent_chain = create_chain(
    llm=llm,
    template_path=INTENT_PROMPT_TEMPLATE,
    output_key="intent",
)

# response
default_chain = create_chain(
    llm=llm,
    template_path=DEFAULT_RESPONSE,
    output_key="answer",
)
response_with_web = create_chain(
    llm=llm,
    template_path=RESPONSE_WITH_WEB,
    output_key="answer",
)
response_final = create_chain(
    llm=llm,
    template_path=RESPONSE_FINAL,
    output_key="answer",
)

# search prompt
search_value_check_chain = create_chain(
    llm=llm,
    template_path=SEARCH_VALUE_CHECK_PROMPT_TEMPLATE,
    output_key="related_web_search_results",
)
search_compression_chain = create_chain(
    llm=llm,
    template_path=SEARCH_COMPRESSION_PROMPT_TEMPLATE,
    output_key="output",
)


def search_info(user_message):
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
               "related_web_search_results": search_tool.run(user_message)}

    has_value = search_value_check_chain.run(context)

    print(has_value)
    if has_value == "Y":
        answer = search_compression_chain.run(context)
        return answer
    else:
        return ""


def gernerate_answer(user_message) -> dict[str, str]:
    vc = Vector()
    context = dict(user_message=user_message)
    context["input"] = context["user_message"]
    context["intent_list"] = read_prompt_template(INTENT_LIST_TXT)
    context["related_documents"] = ""
    intent = parse_intent_chain.run(context)

    if intent == "social_interaction":
        answer = response_final.run({'user_message': user_message, 'system_answer': ''})
        return answer
    else:
        context["related_documents"] = vc.query_db(context["user_message"])
        intent = parse_intent_chain.run(context)
        print(intent)
        if intent == "insufficient_information":
            context["related_web_search_results"] = search_info(user_message)
            system_answer = response_with_web.run(context)
        else:
            system_answer = default_chain.run(context)
        answer = response_final.run({'user_message': user_message, 'system_answer': system_answer})

        return answer


if __name__ == "__main__":
    # social_interaction
    # print(gernerate_answer("안녕?"))
    # insufficient_information
    # print(gernerate_answer("카카오 오피스는 어디에 있어?"))
    # sufficient_information
    print(gernerate_answer("카카오 채널 프로필 ID 확인하는 방법이 뭐야?"))