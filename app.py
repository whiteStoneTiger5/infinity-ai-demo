import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from gym_knowledge import GYM_KNOWLEDGE
from prompts import (
    AI_TRAINER_SYSTEM_PROMPT,
    GYM_CONCIERGE_SYSTEM_PROMPT,
)


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


st.set_page_config(
    page_title="PERSONAL AI Demo",
    page_icon="🏋️",
)

st.markdown(
    """
    <style>
    div.stButton > button {
        width: 100%;
        border: 1px solid #d0d0d0;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12);
        transition: all 0.15s ease-in-out;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 12px rgba(0, 0, 0, 0.16);
    }

    div.stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.10);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("PERSONAL AI Demo")
st.caption("Personal Training Gym × AI")


# -------------------------
# Session State 初期化
# -------------------------

if "mode" not in st.session_state:
    st.session_state.mode = None

if "profile_completed" not in st.session_state:
    st.session_state.profile_completed = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_goal" not in st.session_state:
    st.session_state.user_goal = ""

if "messages" not in st.session_state:
    st.session_state.messages = []


# -------------------------
# 共通関数
# -------------------------

def reset_demo() -> None:
    st.session_state.mode = None
    st.session_state.profile_completed = False
    st.session_state.user_name = ""
    st.session_state.user_goal = ""
    st.session_state.messages = []


def generate_response(
    system_prompt: str,
) -> str:
    system_message = (
        system_prompt
        + "\n\n"
        + "# 以下がINFINITYのKnowledgeです\n\n"
        + GYM_KNOWLEDGE
    )

    api_messages = [
        {
            "role": "system",
            "content": system_message,
        }
    ]

    for message in st.session_state.messages:
        api_messages.append(
            {
                "role": message["role"],
                "content": message["content"],
            }
        )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=api_messages,
    )

    return response.choices[0].message.content


# -------------------------
# モード選択画面
# -------------------------

if st.session_state.mode is None:
    st.subheader("体験するAIチャットを選んでください")

    st.write(
        "当ジムに関する質問/相談の専用チャット"
    )

    if st.button(
        "💬 当ジムについて相談",
        use_container_width=True,
    ):
        st.session_state.mode = "concierge"
        st.session_state.messages = []
        st.rerun()

    st.write(
            "AIトレーナーによる食事サポートを無料体験できます。"
        )

    if st.button(
        "🥗 3日間AI食事サポート",
        use_container_width=True,
    ):
        st.session_state.mode = "trainer"
        st.session_state.messages = []
        st.rerun()


# -------------------------
# 当ジムへの質問/相談モード
# -------------------------

elif st.session_state.mode == "concierge":
    st.subheader("💬 当ジムに関する質問/相談について専属AIが回答")

    st.caption(
        "当ジムについて知りたいことや、利用にあたって不安なことをお気軽にお聞きください。"
    )

    if st.button("← TOP画面に戻る"):
        reset_demo()
        st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input(
        "例：運動初心者でも大丈夫ですか？"
    )

    if user_input:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner(
            "回答を生成中です..."
        ):
            assistant_response = generate_response(
                GYM_CONCIERGE_SYSTEM_PROMPT
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response,
            }
        )

        with st.chat_message("assistant"):
            st.write(assistant_response)


# -------------------------
# AIトレーナーモード
# -------------------------

elif st.session_state.mode == "trainer":

    if not st.session_state.profile_completed:
        st.subheader("🥗 3日間AI食事サポート")

        st.write(
            "お客様にぴったりのサポートをさせていただくために、"
            "お名前と食事サポートを体験する目的を教えてください。"
        )

        user_name = st.text_input(
            "お名前(名字だけでOK)"
        )

        user_goal = st.selectbox(
            "今回の目的",
            [
                "痩せたい/体を引き締めたい",
                "筋肉をつけたい/ボディメイク大会に出たい",
                "生活習慣を改善したい/運動習慣をつけたい",
                "姿勢・身体に関する悩みを改善したい",
            ],
        )

        if st.button(
            "食事サポート体験を始めましょう",
            use_container_width=True,
        ):
            if user_name.strip():
                st.session_state.user_name = (
                    user_name.strip()
                )
                st.session_state.user_goal = user_goal
                st.session_state.profile_completed = True
                st.session_state.messages = []

                st.rerun()

            else:
                st.warning(
                    "お名前を入力してください。"
                )

        if st.button("← TOP画面に戻る"):
            reset_demo()
            st.rerun()

    else:
        st.subheader("🥗 専属AIトレーナーによる食事サポート中(3日間)")

        st.success(
            f"{st.session_state.user_name}さん専用のチャット画面"
        )

        st.caption(
            f"目的：{st.session_state.user_goal}"
        )

        st.caption("体験期間：1日目")

        with st.expander(
            "👤 トレーナー本人(人間)へ相談する"
        ):
            st.write(
                "デモ版のため、実際の送信は行われません。"
            )

            st.write(
                "本番アプリ版では、必要に応じて"
                "トレーナー本人(人間)へ"
                "チャットを引き継ぐことを想定しています。"
            )

        if st.button("← TOP画面に戻る"):
            reset_demo()
            st.rerun()

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_input = st.chat_input(
            "食事やトレーニングについて相談してください"
        )

        if user_input:
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

            with st.chat_message("user"):
                st.write(user_input)

            profile_context = f"""
# 利用者プロフィール

名前：
{st.session_state.user_name}

目的：
{st.session_state.user_goal}

このプロフィールを踏まえて、
必要に応じて利用者の名前を呼びながら、
目的に合った回答をしてください。
"""

            trainer_system_prompt = (
                AI_TRAINER_SYSTEM_PROMPT
                + "\n\n"
                + profile_context
            )

            with st.spinner(
                "AIトレーナーが考えています..."
            ):
                assistant_response = generate_response(
                    trainer_system_prompt
                )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_response,
                }
            )

            with st.chat_message("assistant"):
                st.write(assistant_response)