import streamlit as st
from openai import OpenAI

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="위로 생성기",
    page_icon="💙",
    layout="centered"
)

# -----------------------------
# OpenAI API 설정
# -----------------------------
try:
    api_key = st.secrets["OPENAL_API_KEY"]
    client = OpenAI(api_key=api_key)
except Exception:
    st.error("OPENAL_API_KEY가 설정되지 않았습니다.")
    st.stop()


# -----------------------------
# 제목
# -----------------------------
st.title("💙 위로 생성기")
st.write("오늘 힘들었던 일을 적어보세요.")
st.write("당신의 이야기에 맞는 따뜻한 위로를 만들어드릴게요.")


# -----------------------------
# 사용자 입력
# -----------------------------
user_input = st.text_area(
    "무슨 일이 있었나요?",
    placeholder="예: 오늘 시험을 망쳐서 너무 속상해...",
    height=180
)


# -----------------------------
# 위로 생성
# -----------------------------
if st.button("💙 위로받기", use_container_width=True):

    if not user_input.strip():
        st.warning("힘들었던 일을 먼저 적어주세요.")
        st.stop()

    with st.spinner("당신을 위한 위로를 만들고 있어요..."):

        try:
            response = client.responses.create(
                model="gpt-5.4-nano",
                instructions="""
                너는 따뜻하고 공감 능력이 뛰어난 위로 상담 도우미야.

                사용자가 힘든 일을 이야기하면 다음 원칙을 지켜서 답해줘.

                1. 사용자의 감정을 먼저 인정하고 공감한다.
                2. 사용자를 판단하거나 비난하지 않는다.
                3. 억지로 긍정적으로 생각하라고 하지 않는다.
                4. 너무 길게 설명하지 않고 자연스럽게 위로한다.
                5. 친한 사람이 따뜻하게 이야기해주는 느낌으로 작성한다.
                6. 구체적인 해결책을 강요하지 않는다.
                7. 마지막에는 사용자가 조금 편안해질 수 있는 따뜻한 한마디를 덧붙인다.
                8. 한국어로 답한다.
                """,
                input=user_input
            )

            answer = response.output_text

            st.success("💙 당신을 위한 위로")
            st.write(answer)

        except Exception as e:
            st.error("위로를 생성하는 중 오류가 발생했습니다.")
            st.caption(f"오류 내용: {e}")


# -----------------------------
# 하단 안내
# -----------------------------
st.divider()

st.caption(
    "💙 이 서비스는 AI가 작성한 위로 메시지를 제공하는 프로그램입니다."
)
