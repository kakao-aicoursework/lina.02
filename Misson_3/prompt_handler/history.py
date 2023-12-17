from langchain.memory import ConversationBufferMemory, FileChatMessageHistory
from Misson_3.conf import HISTORY_DIR
from pathlib import Path
import os
import json

class History:
    def __init__(self):
        self.HISTORY_DIR = HISTORY_DIR

    def load_conversation_history(self, conversation_id: str):

        file_path = os.path.join(self.HISTORY_DIR, f"{conversation_id}.json")
        if os.path.isfile(file_path):
            return FileChatMessageHistory(file_path)
        else:
            Path(file_path).touch(exist_ok=True)
            # JSON 파일에 저장
            with open(file_path, 'w') as json_file:
                json.dump({}, json_file)
            return FileChatMessageHistory(file_path)
        # return FileChatMessageHistory(file_path)

    def log_user_message(self, history: FileChatMessageHistory, user_message: str):
        history.add_user_message(user_message)

    def log_bot_message(self, history: FileChatMessageHistory, bot_message: str):
        history.add_ai_message(bot_message)

    def get_chat_history(self, conversation_id: str):
        history = self.load_conversation_history(conversation_id)
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="user_message",
            chat_memory=history,
        )
        return memory.buffer


if __name__ == "__main__":
    file_path = os.path.join(HISTORY_DIR, f"fa1010.json")
    FileChatMessageHistory(file_path).add_user_message("user_message")



    # his = History()
    #
    # tmp, test = his.load_conversation_history("fa1010")
    # test.add_user_message(123)
    # his.log_user_message(test, "123")