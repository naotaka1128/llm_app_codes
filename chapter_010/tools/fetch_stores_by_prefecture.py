# GitHub: https://github.com/naotaka1128/llm_app_codes/chapter_010/tools/fetch_stores_by_prefecture.py

import pandas as pd
import streamlit as st
from langchain_core.tools import tool
from langchain_core.pydantic_v1 import (BaseModel, Field)


class FetchStoresInput(BaseModel):
    """ 型を指定するためのクラス """
    pref: str = Field()


@st.cache_data(ttl="1d")
def load_stores_from_csv():
    df = pd.read_csv('./data/bearmobile_stores.csv')
    return df.sort_values(by='pref_id')


@tool(args_schema=FetchStoresInput)
def fetch_stores_by_prefecture(pref):
    """
    都道府県別に店舗を検索するツールです。

    このツールは以下のデータを含む店舗のリストを返します
    - `store_name`（店舗名）
    - `postal_code`（郵便番号）
    - `address`（住所）
    - `tel`（電話番号）

    検索する際に都道府県名に「県」「府」「都」を付ける必要はありません。
    （例：「東京都」→「東京」、「大阪府」→「大阪」、「北海道」→「北海道」、「沖縄県」→「沖縄」）

    全国の店舗リストが欲しい場合は、「全国」と入力して検索してください。
    - ただし、この検索方法はおすすめしません。
    - ユーザーが「どこに店舗があるのが一般的ですか？」と尋ねてきた場合、
      まずユーザーの居住都道府県を確認してください。

    空のリストが返された場合、その都道府県に店舗が見つからなかったことを意味します。
    その場合、ユーザーに質問内容を明確にしてもらうのが良いでしょう。

    Returns
    -------
    List[Dict[str, Any]]:
    - store_name: str
    - post_code: str
    - address: str
    - tel: str
    """
    df = load_stores_from_csv()
    if pref != "全国":
        df = df[df['pref'] == pref]
    return [
        {
            "store_name": row['name'],
            "post_code": row['post_code'],
            "address": row['address'],
            "tel": row['tel']
        }
        for _, row in df.iterrows()
    ]
