import openai
import json
import os
from dotenv import load_dotenv
import tkinter as tk
import pandas as pd
from tkinter import scrolledtext
import tkinter.filedialog as filedialog
import random
import string
from Misson_3.prompt_handler.prompt import Prompt
from Misson_3.prompt_handler.history import History
from Misson_3.db_handler.vector_handler import Vector


def main():

    def show_popup_message(window, message):
        popup = tk.Toplevel(window)
        popup.title("")

        # 팝업 창의 내용
        label = tk.Label(popup, text=message, font=("맑은 고딕", 12))
        label.pack(expand=True, fill=tk.BOTH)

        # 팝업 창의 크기 조절하기
        window.update_idletasks()
        popup_width = label.winfo_reqwidth() + 20
        popup_height = label.winfo_reqheight() + 20
        popup.geometry(f"{popup_width}x{popup_height}")

        # 팝업 창의 중앙에 위치하기
        window_x = window.winfo_x()
        window_y = window.winfo_y()
        window_width = window.winfo_width()
        window_height = window.winfo_height()

        popup_x = window_x + window_width // 2 - popup_width // 2
        popup_y = window_y + window_height // 2 - popup_height // 2
        popup.geometry(f"+{popup_x}+{popup_y}")

        popup.transient(window)
        popup.attributes('-topmost', True)

        popup.update()
        return popup

    def on_send():
        user_input = user_entry.get()
        user_entry.delete(0, tk.END)

        if user_input.lower() == "quit":
            window.destroy()
            return

        conversation.config(state=tk.NORMAL)  # 이동
        conversation.insert(tk.END, f"You: {user_input}\n", "user")  # 이동
        thinking_popup = show_popup_message(window, "처리중...")
        window.update_idletasks()
        # '생각 중...' 팝업 창이 반드시 화면에 나타나도록 강제로 설정하기
        # 해당 부분에 입력
        response = gernerate(user_input, False, chat_id)

        thinking_popup.destroy()

        # 태그를 추가한 부분(1)
        conversation.insert(tk.END, f"gpt assistant: {response}\n", "assistant")
        conversation.config(state=tk.DISABLED)
        # conversation을 수정하지 못하게 설정하기
        conversation.see(tk.END)

    window = tk.Tk()
    window.title("GPT AI")

    font = ("맑은 고딕", 10)

    # 숫자 + 대소문자
    string_pool = string.ascii_letters + string.digits
    # 랜덤한 문자열 생성
    chat_id = ""
    for i in range(10):
        chat_id += random.choice(string_pool)  # 랜덤한 문자열 하나 선택
    print(chat_id)

    conversation = scrolledtext.ScrolledText(window, wrap=tk.WORD, bg='#f0f0f0', font=font)
    # width, height를 없애고 배경색 지정하기(2)
    conversation.tag_configure("user", background="#c9daf8")
    # 태그별로 다르게 배경색 지정하기(3)
    conversation.tag_configure("assistant", background="#e4e4e4")
    # 태그별로 다르게 배경색 지정하기(3)
    conversation.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    # 창의 폭에 맞추어 크기 조정하기(4)

    input_frame = tk.Frame(window)  # user_entry와 send_button을 담는 frame(5)
    input_frame.pack(fill=tk.X, padx=10, pady=10)  # 창의 크기에 맞추어 조절하기(5)

    user_entry = tk.Entry(input_frame)
    user_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)

    send_button = tk.Button(input_frame, text="Send", command=on_send)
    send_button.pack(side=tk.RIGHT)

    window.bind('<Return>', lambda event: on_send())
    window.mainloop()


def gernerate(user_message, is_new, conversation_id: str) -> dict[str, str]:
    INTENT_LIST_TXT = "/Users/lina/PycharmProjects/lina.02/Misson_3/prompt_handler/prompt_txt/intent_list.txt"
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


if __name__ == '__main__':
    # Main
    main()

