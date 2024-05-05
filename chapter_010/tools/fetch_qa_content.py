# GitHub: https://github.com/naotaka1128/llm_app_codes/chapter_010/tools/fetch_qa_content.py

import streamlit as st
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.pydantic_v1 import (BaseModel, Field)


class FetchQAContentInput(BaseModel):
    """ 型を指定するためのクラス """
    query: str = Field()


@st.cache_resource
def load_qa_vectorstore(
    vectorstore_path="./vectorstore/qa_vectorstore"
):
    """「よくある質問」のベクトルDBをロードする"""
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(
        vectorstore_path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )


@tool(args_schema=FetchQAContentInput)
def fetch_qa_content(query):
    """
    「よくある質問」リストから、あなたの質問に関連するコンテンツを見つけるツールです。
    "ベアーモバイル"に関する具体的な知識を得るのに役立ちます。

    このツールは `similarity`（類似度）と `content`（コンテンツ）を返します。
    - 'similarity'は、回答が質問にどの程度関連しているかを示します。
        値が高いほど、質問との関連性が高いことを意味します。
        'similarity'値が0.5未満のドキュメントは返されません。
    - 'content'は、質問に対する回答のテキストを提供します。
        通常、よくある質問とその対応する回答で構成されています。

    空のリストが返された場合、ユーザーの質問に対する回答が見つからなかったことを意味します。
    その場合、ユーザーに質問内容を明確にしてもらうのが良いでしょう。

    Returns
    -------
    List[Dict[str, Any]]:
    - page_content
      - similarity: float
      - content: str
    """
    db = load_qa_vectorstore()
    docs = db.similarity_search_with_score(
        query=query,
        k=5,
        score_threshold=0.5
    )
    return [
        {
            "similarity": 1 - similarity,
            "content": i.page_content
        }
        for i, similarity in docs
    ]
