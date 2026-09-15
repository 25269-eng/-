import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="위로 생성기",
    page_icon="💙",
    layout="centered"
)

# OpenAI API 연결
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# 제목
st.title("💙 AI 위로 생성기")
st.write("힘든 일을 적어주면 따뜻한 위로의 말을 만들어드려요.")

# 사용자 입력
user_input = st.text_area(
    "💬 지금 어떤 일이 있었나요?",
    placeholder="오늘 있었던 힘든 일이나 속상한 일을 자유롭게 적어주세요.",
    height=180
)

# 위로 생성
if st.button("💙 위로받기", use_container_width=True):

    if not user_input.strip():
        st.warning("먼저 힘들었던 일을 적어주세요.")
    else:
        with st.spinner("따뜻한 위로를 생각하고 있어요..."):

            try:
                response = client.responses.create(
                    model="gpt-5.4-nano",
                    instructions="""
                    너는 따뜻하고 공감 능력이 높은 위로 도우미이다.

                    사용자가 힘든 일이나 속상한 일을 이야기하면
                    판단하거나 훈계하지 말고 먼저 감정을 공감해준다.

                    답변은 한국어로 작성한다.
                    너무 길지 않게 3~5개의 문단으로 작성한다.
                    사용자의 감정을 가볍게 여기지 않는다.
                    억지로 긍정적인 말만 하지 않는다.
                    '힘내' 같은 짧은 말만 반복하지 않는다.

                    사용자가 스스로를 탓하고 있다면
                    지나치게 자책하지 않아도 된다는 점을 부드럽게 알려준다.

                    마지막에는 사용자가 조금이라도 편안해질 수 있는
                    따뜻한 한마디를 덧붙인다.
                    """,
                    input=user_input
                )

                st.success("💙 당신에게 필요한 위로를 준비했어요.")
                st.markdown("### 🌷 당신에게 전하는 말")
                st.write(response.output_text)

            except Exception as e:
                st.error("위로를 생성하는 중 문제가 발생했어요.")
                st.caption(f"오류: {e}")
