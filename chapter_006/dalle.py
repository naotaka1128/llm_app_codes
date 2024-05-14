import base64
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper

from dotenv import load_dotenv
load_dotenv()


GPT4V_PROMPT = """
まず、以下のユーザーのリクエストとアップロードされた画像を注意深く読んでください。

次に、アップロードされた画像に基づいて画像を生成するというユーザーのリクエストに沿ったDALL-Eプロンプトを作成してください。 
DALL-Eプロンプトは必ず英語で作成してください。

ユーザー入力: {user_input}

プロンプトでは、ユーザーがアップロードした写真に何が描かれているか、どのように構成されているかを詳細に説明してください。
写真に何が写っているのかはっきりと見える場合は、示されている場所や人物の名前を正確に書き留めてください。 
写真の構図とズームの程度を可能な限り詳しく説明してください。
写真の内容を可能な限り正確に再現することが重要です。

DALL-E 3向けのプロンプトを英語で回答してください:
"""


def init_page():
    st.set_page_config(
        page_title="Image Converter",
        page_icon="🤗"
    )
    st.header("Image Converter 🤗")


def main():
    init_page()

    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4o",
        # なぜかmax_tokensないとたまに挙動が不安定になる (2024年5月現在)
        max_tokens=512
    )

    dalle3_image_url = None
    uploaded_file = st.file_uploader(
        label='Upload your Image here😇',
        # GPT-4Vが処理可能な画像ファイルのみ許可
        type=['png', 'jpg', 'webp', 'gif']
    )
    if uploaded_file:
        if user_input := st.chat_input("画像をどのように加工したいか教えてね"):
            # 読み取ったファイルをBase64でエンコード
            image_base64 = base64.b64encode(uploaded_file.read()).decode()
            image = f"data:image/jpeg;base64,{image_base64}"

            query = [
                (
                    "user",
                    [
                        {
                            "type": "text",
                            "text": GPT4V_PROMPT.format(user_input=user_input)
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image,
                                "detail": "auto"
                            },
                        }
                    ]
                )
            ]

            # GPT-4Vに DALL-E 3 用の画像生成プロンプトを書いてもらう
            st.markdown("### Image Prompt")
            image_prompt = st.write_stream(llm.stream(query))

            # DALL-E 3 による画像生成
            with st.spinner("DALL-E 3 is drawing ..."):
                dalle3 = DallEAPIWrapper(
                    model="dall-e-3",
                    size="1792x1024",   # "1024x1024", "1024x1792" も選択可能
                    quality="standard", # 'hd' で高品質な画像も生成可能
                    n=1,  # 1度に1枚しか生成できない (並行してリクエストは可能)
                )
                dalle3_image_url = dalle3.run(image_prompt)
    else:
        st.write('まずは画像をアップロードしてね😇')

    # DALL-E 3 の画像表示
    if dalle3_image_url:
        st.markdown("### Question")
        st.write(user_input)
        st.image(
            uploaded_file,
            use_column_width="auto"
        )

        st.markdown("### DALL-E 3 Generated Image")
        st.image(
            dalle3_image_url,
            caption=image_prompt,
            use_column_width="auto"
        )


if __name__ == '__main__':
    main()
