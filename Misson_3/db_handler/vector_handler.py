import os
import json

from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from sqlalchemy.orm.collections import collection
from langchain.document_loaders import (
    TextLoader,

)
from Misson_3.conf import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, API_KEY
import chromadb

os.environ["OPENAI_API_KEY"] = API_KEY


class Vector:
    def __init__(self):

        self.collection_name = CHROMA_COLLECTION_NAME
        self.persist_directory = CHROMA_PERSIST_DIR
        self.db = Chroma(
            embedding_function=OpenAIEmbeddings(),
            collection_name=CHROMA_COLLECTION_NAME,
            persist_directory=CHROMA_PERSIST_DIR,
        )

    def query_db(self, query: str, use_retriever: bool = False) -> list[str]:
        load_qa_with_sources_chain
        if use_retriever:
            docs = self.db.as_retriever().get_relevant_documents(query)
        else:
            docs = self.db.similarity_search(query)

        str_docs = [doc.page_content for doc in docs]
        return str_docs

    def upload_embedding(self, file_p: str):
        loader_dict = {
            "txt": TextLoader
        }
        loader = loader_dict.get(file_p.split(".")[-1])
        documents = loader(file_p).load()
        text_splitter = CharacterTextSplitter(chunk_size=50, chunk_overlap=10)
        docs = text_splitter.split_documents(documents)
        Chroma.from_documents(
            docs,
            OpenAIEmbeddings(),
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
        )
        print('db success')

    def upload_embeddings_from_dir(self, dir_path):
        failed_upload_files = []
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".txt"):
                    file_p = os.path.join(root, file)
                    try:
                        self.upload_embedding(file_p)
                        print("SUCCESS: ", file_p)
                    except Exception as e:
                        print("FAILED: ", file_p + f"\nby({e})")
                        failed_upload_files.append(file_p)


if __name__ == "__main__":
    file_path = '/Users/lina/PycharmProjects/lina.02/Misson_3/data/'
    vc = Vector()
    # vc.upload_embeddings_from_dir(file_path)
    print(vc.query_db("카카오 싱크 사용법이 뭐야?"))
