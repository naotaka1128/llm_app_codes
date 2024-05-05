# GitHub: https://github.com/naotaka1128/llm_app_codes/chapter_010/main.py

import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.agents import create_tool_calling_agent, AgentExecutor

from langchain.agents import AgentExecutor
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain.memory import ConversationBufferWindowMemory

# models
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

# custom tools
from tools.fetch_qa_content import fetch_qa_content
from tools.fetch_stores_by_prefecture import fetch_stores_by_prefecture


from dotenv import load_dotenv
load_dotenv()

CUSTOM_SYSTEM_PROMPT = """
あなたは日本の格安携帯電話会社「ベアーモバイル」のカスタマーサポート(CS)担当者です。
お客様からのお問い合わせに対して、誠実かつ正確な回答を心がけてください。

携帯電話会社のCSとして、当社のサービスや携帯電話に関する一般的な知識についてのみ答えます。
それ以外のトピックに関する質問には、丁重にお断りしてください。

回答の正確性を保証するため「ベアーモバイル」に関する質問を受けた際は、
必ずツールを使用して回答を見つけてください。

お客様が質問に使用した言語で回答してください。
例えば、お客様が英語で質問された場合は、必ず英語で回答してください。
スペイン語ならスペイン語で回答してください。

回答する際、不明な点がある場合は、お客様に確認しましょう。
それにより、お客様の意図を把握して、適切な回答を行えます。

例えば、ユーザーが「店舗はどこにありますか？」と質問した場合、
まずユーザーの居住都道府県を尋ねてください。

日本全国の店舗の場所を知りたいユーザーはほとんどいません。
自分の都道府県内の店舗の場所を知りたいのです。
したがって、日本全国の店舗を検索して回答するのではなく、
ユーザーの意図を本当に理解するまで回答しないでください！

あくまでこれは一例です。
その他のケースでもお客様の意図を理解し、適切な回答を行ってください。
"""


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
    ## https://learn.deeplearning.ai/functions-tools-agents-langchain/lesson/7/conversational-agent
    tools = [fetch_qa_content, fetch_stores_by_prefecture]
    prompt = ChatPromptTemplate.from_messages([
        ("system", CUSTOM_SYSTEM_PROMPT),
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

    for msg in st.session_state['memory'].chat_memory.messages:
        st.chat_message(msg.type).write(msg.content)

    if prompt := st.chat_input(placeholder="法人で契約することはできるの？"):
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(
                st.container(), expand_new_thoughts=True)
            response = customer_support_agent.invoke(
                {'input': prompt},
                config=RunnableConfig({'callbacks': [st_cb]})
            )
            st.write(response["output"])


if __name__ == '__main__':
    main()
