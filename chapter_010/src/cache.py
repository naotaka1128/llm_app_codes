# GitHub: https://github.com/naotaka1128/llm_app_codes/chapter_010/src/cache.py

import os
import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


class Cache:
    def __init__(
        self,
        vectorstore_path="./vectorstore/cache",
    ):
        self.vectorstore_path = vectorstore_path
        self.embeddings = OpenAIEmbeddings()

    def load_vectorstore(self):
        if os.path.exists(self.vectorstore_path):
            return FAISS.load_local(
                self.vectorstore_path,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            return None

    def save(self, query, answer):
        """ (初回質問に対する) 回答をキャッシュとして保存する """
        self.vectorstore = self.load_vectorstore()
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_texts(
                texts=[query],
                metadatas=[{"answer": answer}],
                embedding=self.embeddings
            )
        else:
            self.vectorstore.add_texts(
                texts=[query],
                metadatas=[{"answer": answer}]
            )
        self.vectorstore.save_local(self.vectorstore_path)

    def search(self, query):
        """ 質問に類似する過去の質問を検索し、その回答を返す。 """
        self.vectorstore = self.load_vectorstore()
        if self.vectorstore is None:
            return None

        docs = self.vectorstore.similarity_search_with_score(
            query=query,
            k=1,
            # 類似度の閾値は調整が必要 / L2距離なので小さい方が類似度が高い
            score_threshold=0.05
        )
        if docs:
            return docs[0][0].metadata["answer"]
        else:
            return None
