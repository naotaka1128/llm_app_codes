# GitHub: https://github.com/naotaka1128/llm_app_codes/chapter_011/part1/tools/code_interpreter.py

import streamlit as st
from langchain_core.tools import tool
from langchain_core.pydantic_v1 import (BaseModel, Field)


class ExecPythonInput(BaseModel):
    """ 型を指定するためのクラス """
    code: str = Field()


@tool(args_schema=ExecPythonInput)
def code_interpreter_tool(code):
    """
    Code Interpreter を使用して、Pythonコードを実行します。
    - 以下のような内容を行うのに適しています。
      - pandasやmatplotlibなどのライブラリを使って、データの加工や可視化が行えます。
      - 数式の計算や、統計的な分析なども行うことができます。
      - 自然言語処理のためのライブラリを使って、テキストデータの分析も可能です。
    - Code Interpreterはインターネット接続はできません
      - 外部のWEBサイトの情報を読み取ったり、新しいライブラリをインストールすることはできません
    - Code Interpreterが書いたコードも出力するように要求すると良いでしょう
      - ユーザーが結果の検証を行いやすくなります
    - 多少コードが間違っていても自動で修正してくれることがあります

    Returns:
    - text: Code Interpreter が出力したテキスト (コード実行結果が主)
    - files: Code Interpreter が保存したファイルのパス
        - ファイル先は、`./files/` 以下に保存されます。
    """
    return st.session_state.code_interpreter_client.run(code)
