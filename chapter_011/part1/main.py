# GitHub: https://github.com/naotaka1128/llm_app_codes/chapter_011/part1/main.py

import re
import streamlit as st
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_community.callbacks import StreamlitCallbackHandler

# models
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

# custom tools
from src.code_interpreter import CodeInterpreterClient
from tools.code_interpreter import code_interpreter_tool

from dotenv import load_dotenv
load_dotenv()


@st.cache_data
def load_system_prompt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def csv_upload():
    with st.form("my-form", clear_on_submit=True):
        file = st.file_uploader(
            label='Upload your CSV here😇',
            type='csv'
        )
        submitted = st.form_submit_button("Upload CSV")
        if submitted and file is not None:
            if not file.name in st.session_state.uploaded_files:
                assistant_api_file_id = st.session_state.code_interpreter_client.upload_file(file.read())
                st.session_state.custom_system_prompt += \
                    f"\アップロードファイル名: {file.name} (Code Interpreterでのpath: /mnt/data/{assistant_api_file_id})\n"
                st.session_state.uploaded_files.append(file.name)
        else:
            st.write("データ分析したいファイルをアップロードしてね")

    if st.session_state.uploaded_files:
        st.sidebar.markdown("## Uploaded files:")
        for file_name in st.session_state.uploaded_files:
            st.sidebar.markdown(f"- {file_name}")


def init_page():
    st.set_page_config(
        page_title="Data Analysis Agent",
        page_icon="🤗"
    )
    st.header("Data Analysis Agent 🤗", divider='rainbow')
    st.sidebar.title("Options")

    # message 初期化 / python runtime の初期化
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = []
	    # 会話がリセットされる時に Code Interpreter のセッションも作り直す
        st.session_state.code_interpreter_client = CodeInterpreterClient()
        st.session_state['memory'] = ConversationBufferWindowMemory(
            return_messages=True,
            memory_key="chat_history",
            k=10
        )
        st.session_state.custom_system_prompt = load_system_prompt(
            "./prompt/system_prompt.txt")
        st.session_state.uploaded_files = []


def select_model():
    models = ("GPT-4", "Claude 3 Sonnet", "Gemini 1.5 Pro", "GPT-3.5 (not recommended)")
    model = st.sidebar.radio("Choose a model:", models)
    if model == "GPT-3.5 (not recommended)":
        return ChatOpenAI(
            temperature=0, model_name="gpt-3.5-turbo")
    elif model == "GPT-4":
        return ChatOpenAI(
            temperature=0, model_name="gpt-4-turbo")
    elif model == "Claude 3 Sonnet":
        return ChatAnthropic(
            temperature=0, model_name="claude-3-sonnet-20240229")
    elif model == "Gemini 1.5 Pro":
        return ChatGoogleGenerativeAI(
            temperature=0, model="gemini-1.5-pro-latest")


def create_agent():
    # tools 以外の部分はは前章までと全く同じ
    tools = [code_interpreter_tool]
    prompt = ChatPromptTemplate.from_messages([
        ("system", st.session_state.custom_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    llm = select_model()
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=st.session_state['memory']
    )


def parse_response(response):
    """
    response から text と image_paths を取得する

    responseの例
    ===    
    ビットコインの終値のチャートを作成しました。以下の画像で確認できます。
    <img src="./files/file-s4W0rog1pjneOAtWeq21lbDy.png" alt="Bitcoin Closing Price Chart">

    image_pathを取得した後はimgタグを削除しておく
    """
    # imgタグを取得するための正規表現パターン
    img_pattern = re.compile(r'<img\s+[^>]*?src="([^"]+)"[^>]*?>')

    # imgタグを検索してimage_pathsを取得
    image_paths = img_pattern.findall(response)

    # imgタグを削除してテキストを取得
    text = img_pattern.sub('', response).strip()

    return text, image_paths


def display_content(content):
    text, image_paths = parse_response(content)
    st.write(text)
    for image_path in image_paths:
        st.image(image_path, caption="")


def main():
    init_page()
    csv_upload()
    data_analysis_agent = create_agent()

    for msg in st.session_state['memory'].chat_memory.messages:
        with st.chat_message(msg.type):
            display_content(msg.content)

    if prompt := st.chat_input(placeholder="分析したいことを書いてね"):
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(
                st.container(), expand_new_thoughts=True)
            response = data_analysis_agent.invoke(
                {'input': prompt},
                config=RunnableConfig({'callbacks': [st_cb]})
            )
            display_content(response["output"])


if __name__ == '__main__':
    main()
