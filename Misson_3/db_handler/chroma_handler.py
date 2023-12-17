import os
import json
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from sqlalchemy.orm.collections import collection

from Misson_3.conf import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, API_KEY
import chromadb

os.environ["OPENAI_API_KEY"] = API_KEY


class Chro:
    def __init__(self):
        _db = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=OpenAIEmbeddings(),
            collection_name=CHROMA_COLLECTION_NAME,
        )
        _retriever = _db.as_retriever()
        client = chromadb.PersistentClient()
        self.collection = client.get_or_create_collection(
            name="k-drama",
            metadata={"hnsw:space": "cosine"}
        )
        # client = _db.PersistentClient()

    def query_db(self, query: str, use_retriever: bool = False) -> list[str]:
        # DB 쿼리
        str_docs = self.collection.query(
            query_texts=[query],
            n_results=2,
        )
        srchres = []
        for v in str_docs['documents'][0]:
            srchres.append(v)
        return srchres

    def update_db(self, info_data: list):

        # 인덱스
        ids = []
        # 벡터로 변환 저장할 텍스트 데이터로 ChromaDB에 Embedding 데이터가 없으면 자동으로 벡터로 변환해서 저장
        documents = []

        for idx in info_data:
            id = idx['title'].lower().replace(' ', '-')
            document = idx['content']
            ids.append(id)
            documents.append(document)
        # DB 저장
        self.collection.add(
            documents=documents,
            # metadatas=doc_meta,
            ids=ids
        )

    def upload_embedding_from_file(self, file_path):
        text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=30)
        docs = text_splitter.create_documents(init_data(file_path))
        print(docs, end='\n\n\n')

        Chroma.from_documents(
            docs,
            OpenAIEmbeddings(),
            collection_name=CHROMA_COLLECTION_NAME,
            persist_directory=CHROMA_PERSIST_DIR,
        )
        print('db success')

    # def insert_db(self):
    #     collection = self.client.get_or_create_collection(
    #         name="kakao-data",
    #         metadata={"hnsw:space": "cosine"}
    #     )
    #     # DB 저장
    #     collection.add(
    #         documents=documents,
    #         metadatas=doc_meta,
    #         ids=ids
    #     )


def init_data(file_path) -> list:
    tmp = []
    info_list = []

    f = open(file_path, 'r')
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
                info = {}
                info['title'] = title.replace(" ", "").replace("#", "")
                info['content'] = text.replace(" ", "")
                info_list.append(info)

    return info_list


if __name__ == "__main__":
    ch = Chro()
    file_path='/Users/lina/PycharmProjects/lina.02/Misson_3/data/project_data_카카오톡채널.txt'
    # print(init_data(file_path))
    ch.update_db(init_data(file_path))

    print(ch.query_db("카카오 채널 채널 추가 방법이 뭐야?"))
    # raw_data = init_data("/Users/lina/PycharmProjects/lina.02/Misson_3/data/project_data_카카오소셜.txt")
    # print(raw_data)