# GitHub: https://github.com/naotaka1128/llm_app_codes/chapter_010/src/feedback.py

import streamlit as st
from langsmith import Client
from streamlit_feedback import streamlit_feedback


def add_feedback():
    langsmith_client = Client()

    run_id = st.session_state["run_id"]

    # フィードバックを取得
    feedback = streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="[任意] 説明を入力してください",
        key=f"feedback_{run_id}",
    )

    scores = {"👍": 1, "👎": 0}

    if feedback:
        # 選択されたフィードバックオプションに応じたスコアを取得
        score = scores.get(feedback["score"])

        if score is not None:
            # フィードバックタイプの文字列を、選択されたオプションとスコア値を用いて作成
            feedback_type_str = f"thumbs {feedback['score']}"

            # 作成したフィードバックタイプの文字列と任意のコメントを用いて、
            # フィードバックをレコードに記録
            feedback_record = langsmith_client.create_feedback(
                run_id,
                feedback_type_str,
                score=score,
                comment=feedback.get("text"),
            )
            # フィードバックIDとスコアをセッション状態に保存
            st.session_state.feedback = {
                "feedback_id": str(feedback_record.id),
                "score": score,
            }
        else:
            # 無効なフィードバックスコアの場合は警告を表示
            st.warning("無効なフィードバックスコアです。")
