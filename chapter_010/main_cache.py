# GitHub: https://github.com/naotaka1128/llm_app_codes/chapter_010/main_cache.py

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
from tools.fetch_qa_content import fetch_qa_content
from tools.fetch_stores_by_prefecture import fetch_stores_by_prefecture
from src.cache import Cache

from dotenv import load_dotenv
load_dotenv()


@st.cache_data  # キャッシュを利用するように変更
def load_system_prompt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def init_page():
    st.set_page_config(
        page_title="カスタマーサポート",
        page_icon="🐻"
    )
    st.header("カスタマーサポート🐻")
    st.sidebar.title("Options")


def init_messages():
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        welcome_message = "ベアーモバイル カスタマーサポートへようこそ。ご質問をどうぞ🐻"
        st.session_state.messages = [
            {"role": "assistant", "content": welcome_message}
        ]
        st.session_state['memory'] = ConversationBufferWindowMemory(
            return_messages=True,
            memory_key="chat_history",
            k=10
        )

    if len(st.session_state.messages) == 1:  # welcome messageのみの場合
        st.session_state['first_question'] = True  # 追加部分
    else:
        st.session_state['first_question'] = False  # 追加部分


def select_model():
    models = ("GPT-4", "Claude 3 Sonnet", "Gemini 1.5 Pro", "GPT-3.5 (not recommended)")
    model = st.sidebar.radio("Choose a model:", models)
    if model == "GPT-3.5 (not recommended)":
        return ChatOpenAI(
            temperature=0, model_name="gpt-3.5-turbo")
    elif model == "GPT-4":
        return ChatOpenAI(
            temperature=0, model_name="gpt-4o")
    elif model == "Claude 3 Sonnet":
        return ChatAnthropic(
            temperature=0, model_name="claude-3-sonnet-20240229")
    elif model == "Gemini 1.5 Pro":
        return ChatGoogleGenerativeAI(
            temperature=0, model="gemini-1.5-pro-latest")


def create_agent():
    ## https://learn.deeplearning.ai/functions-tools-agents-langchain/lesson/7/conversational-agent
    tools = [fetch_qa_content, fetch_stores_by_prefecture]
    # キャッシュを利用するように変更
    custom_system_prompt = load_system_prompt("./prompt/system_prompt.txt")
    prompt = ChatPromptTemplate.from_messages([
        ("system", custom_system_prompt),
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


def main():
    init_page()
    init_messages()
    customer_support_agent = create_agent()

    # キャッシュの初期化
    cache = Cache()

    for msg in st.session_state['memory'].chat_memory.messages:
        st.chat_message(msg.type).write(msg.content)

    if prompt := st.chat_input(placeholder="法人で契約することはできるの？"):
        st.chat_message("user").write(prompt)

        # 最初の質問の場合はキャッシュをチェックする
        if st.session_state['first_question']:
            if cache_content := cache.search(query=prompt):
                st.chat_message("assistant").write(f"(cache) {cache_content}")
                st.session_state.messages.append(
                    {"role": "assistant", "content": cache_content})
                st.stop()  # キャッシュの内容を書いた場合は実行を終了する

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(
                st.container(), expand_new_thoughts=True)
            response = customer_support_agent.invoke(
                {'input': prompt},
                config=RunnableConfig({'callbacks': [st_cb]})
            )
            st.write(response["output"])

        # 最初の質問の場合はキャッシュに保存する
        if st.session_state['first_question']:
            cache.save(prompt, response["output"])


if __name__ == '__main__':
    main()
