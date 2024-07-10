import base64
import streamlit as st
from langchain_openai import ChatOpenAI

###### dotenv を利用しない場合は消してください ######
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    import warnings
    warnings.warn("dotenv not found. Please make sure to set your environment variables manually.", ImportWarning)
################################################


def init_page():
    st.set_page_config(
        page_title="Image Recognizer",
        page_icon="🤗"
    )
    st.header("Image Recognizer 🤗")
    st.sidebar.title("Options")


def main():
    init_page()

    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4o",
        # なぜかmax_tokensないと挙動が安定しない (2024年2月現在)
        # 著しく短い回答になったり、途中で回答が途切れたりする。
        max_tokens=512
    )

    uploaded_file = st.file_uploader(
        label='Upload your Image here😇',
        # GPT-4Vが処理可能な画像ファイルのみ許可
        type=['png', 'jpg', 'webp', 'gif']
    )
    if uploaded_file:
        if user_input := st.chat_input("聞きたいことを入力してね！"):
            # 読み取ったファイルをBase64でエンコード
            image_base64 = base64.b64encode(uploaded_file.read()).decode()
            image = f"data:image/jpeg;base64,{image_base64}"

            query = [
                (
                    "user",
                    [
                        {
                            "type": "text",
                            "text": user_input
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
            st.markdown("### Question")
            st.write(user_input)     # ユーザーの質問
            st.image(uploaded_file)  # アップロードした画像を表示
            st.markdown("### Answer")
            st.write_stream(llm.stream(query))

    else:
        st.write('まずは画像をアップロードしてね😇')

if __name__ == '__main__':
    main()
