import os
from dotenv import load_dotenv

HOME_DIR = PKGS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

DATA_DIR = os.path.join(HOME_DIR, "data")
CHROMA_PERSIST_DIR = os.path.join(DATA_DIR, "chroma-persist")
CHROMA_COLLECTION_NAME = "dosu-bot"

HISTORY_DIR = os.path.join(DATA_DIR, "history")
# 환경 변수 처리 필요!
load_dotenv()
API_KEY = os.environ.get('api_key')
