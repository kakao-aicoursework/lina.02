import openai

from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from pprint import pprint
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import SystemMessage
import os
import json


SYSTEM_MSG = "당신은 카카오 서비스 제공자입니다."

CUR_DIR = os.path.dirname(os.path.abspath('./data/'))
# RAW_DATA = os.path.join(CUR_DIR, "project_data_카카오싱크.txt")
RAW_DATA = "/Users/lina/PycharmProjects/kakaochattest_guide/data/project_data_카카오싱크.txt"
STEP1_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "/Users/lina/PycharmProjects/kakaochattest_guide/data/prompt/kakaosink_step_1.txt")

STEP4_PROMPT_TEMPLATE = "/Users/lina/PycharmProjects/kakaochattest_guide/data/prompt/prompt.txt"

STEP2_PROMPT_TEMPLATE =  os.path.join(CUR_DIR, "/Users/lina/PycharmProjects/kakaochattest_guide/data/prompt/kakaosink_step_2.txt")
# STEP2_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_template1/2_write_outline.txt")
# STEP3_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_template1/3_write_plot.txt")
# WRITE_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_template1/4_write_chapter.txt")


def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()
    return prompt_template


def request_gpt_api(
    prompt: str,
    model: str = "gpt-3.5-turbo-16k",
    max_token: int = 500,
    temperature: float = 0.8,
) -> str:
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_token,
        temperature=temperature,
    )

    return response.choices[0].message.content


def create_chain(llm, template_path, output_key):
    return LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_template(
            template=read_prompt_template(template_path),
        ),
        output_key=output_key,
        verbose=True,
    )


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
    print(info)
    return info


def build_summarizer(llm):
    system_message = "As a Kakao sink counselor, you have to respond kindly to people's questions. The contents of Kakao sink are as follows\n {text} \n You always answer in Korean"
    system_message_prompt = SystemMessage(content=system_message)

    human_template = "\n\n{ask}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                    human_message_prompt])

    chain = LLMChain(llm=llm, prompt=chat_prompt)
    return chain


if __name__ == "__main__":

    raw_data = init_data()
    # print(raw_data)

    writer_llm = ChatOpenAI(temperature=0.1, max_tokens=300, model="gpt-3.5-turbo-16k")
    summarizer = build_summarizer(writer_llm)

    anwser = summarizer.run(text=raw_data, ask="카카오 싱크 설정 어떻게 해?")

    print(anwser)
    # STEP_1 = create_chain(writer_llm, STEP1_PROMPT_TEMPLATE, "STEP_1")
    # STEP_2 = create_chain(writer_llm, STEP1_PROMPT_TEMPLATE, "STEP_2")
    # STEP_3 = create_chain(writer_llm, STEP1_PROMPT_TEMPLATE, "STEP_3")
    # LAST_STEP = create_chain(writer_llm, STEP4_PROMPT_TEMPLATE, "output")
    # preprocess_chain = SequentialChain(
    #     chains=[
    #         STEP_1,
    #         STEP_2,
    #         STEP_3
    #         # novel_plot_chain,
    #     ],
    #     input_variables=["title_1", "content_1", "title_2", "content_2"],
    #     output_variables=["STEP_1", "STEP_2", "STEP_3"],
    #     verbose=True,
    # )

    # context = {}
    # tmp = 1
    # for i, v in raw_data.items():
    #     print(i, v)
    #     context['title_' + str(tmp)] = i
    #     context['content_' + str(tmp)] = v
    #     tmp = tmp + 1
    #
    # context = preprocess_chain(context)
    # print(context)
    # context["novel_chapter"] = []
    # for chapter_number in range(1, 2):
    #     context["chapter_number"] = chapter_number
    #     context = LAST_STEP(context)
    #     context["novel_chapter"].append(context["output"])
    #
    # contents = "\n\n".join(context["novel_chapter"])

    # return {"results": contents}

    # prompt_template = read_prompt_template('data/prompt/prompt.txt')
    # print(prompt_template)
    # print(request_gpt_api(prompt_template))