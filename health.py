
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="학생 건강 도우미",
    page_icon="🌿",
    layout="centered"
)

# ---------- 디자인 ----------
st.markdown("""
<style>
.stApp {
    background-color: #F6FAF7;
    color: #26382E;
}

.stApp p,
.stApp li,
.stMarkdown,
[data-testid="stChatMessage"] p {
    color: #26382E !important;
}

[data-testid="stChatMessage"] {
    background-color: #FFFFFF;
    border-radius: 15px;
    padding: 12px;
}

.main-title {
    text-align: center;
    color: #247653 !important;
    font-size: 32px;
    font-weight: 800;
}

.subtitle {
    text-align: center;
    color: #64756B !important;
    font-size: 15px;
    margin-bottom: 25px;
}

div.stButton > button {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🌿 학생 건강 도우미</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    '증상에 맞는 음식과 생활 관리 정보를 알아봐요.'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "이 서비스는 일반 건강 정보 제공용입니다. "
    "의사의 진단이나 처방을 대신하지 않습니다."
)

with st.expander("🚨 응급 증상 안내"):
    st.markdown("""
    심한 호흡곤란, 의식 저하, 심한 가슴 통증 등
    응급 증상이 있다면 AI 답변을 기다리지 마세요.

    주변 어른에게 즉시 알리고 119에 연락하세요.
    """)

# ---------- API 키 ----------
api_key = st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    st.error(
        "API 키가 설정되지 않았어요. "
        "Streamlit Cloud의 앱 설정에서 Secrets를 확인해 주세요."
    )
    st.stop()

client = OpenAI(api_key=api_key)

# ---------- AI 지침 ----------
SYSTEM_PROMPT = """
너는 대한민국 중고등학생을 위한 건강 정보 도우미다.
친절하고 쉬운 한국어로 답한다.

안전 수칙:
- 확정 진단을 내리지 않는다.
- 증상이 불분명하면 필요한 질문을 먼저 한다.
- 응급 증상이 의심되면 즉시 보호자에게 알리고
  119 또는 응급 의료 도움을 받도록 안내한다.
- 도움이 될 수 있는 음식과 피하면 좋은 음식을
  이유와 함께 설명하되 효과를 보장하지 않는다.
- 수분 섭취, 휴식 등 안전한 일반 관리법을 안내한다.
- 특정 약을 처방하거나 임의로 복용량을 결정하지 않는다.
- 약은 나이, 알레르기, 복용 중인 약에 따라 달라질 수 있으므로
  보호자와 약사 또는 의사에게 확인하도록 안내한다.
- 항생제나 다른 사람의 처방약을 임의로 복용하라고 하지 않는다.
- 증상이 악화되거나 지속되면 의료진의 진료를 권한다.
- 이름, 학교, 전화번호, 주소 등 개인정보를 요구하지 않는다.

일반적인 답변은 다음 형식으로 작성한다.

### 1. 증상 이해하기
### 2. 도움이 될 수 있는 음식
### 3. 주의하면 좋은 음식
### 4. 집에서 할 수 있는 대처법
### 5. 약을 사용할 때 주의할 점
### 6. 병원에 가야 하는 경우

정보가 부족하면 무리하게 답하지 말고 질문한다.
응급 상황에서는 다른 항목보다 응급 안내를 우선한다.
"""

# ---------- 응급 표현 확인 ----------
EMERGENCY_TERMS = [
    "숨을 못 쉬",
    "호흡이 안",
    "의식을 잃",
    "정신을 잃",
    "쓰러졌어",
    "가슴이 심하게 아",
    "갑자기 극심한 두통",
    "목이 부어 숨",
    "피를 많이"
]

def has_emergency_sign(text):
    normalized = text.replace(" ", "")
    return any(
        term.replace(" ", "") in normalized
        for term in EMERGENCY_TERMS
    )

# ---------- 대화 기록 ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- 사이드바 ----------
with st.sidebar:
    st.header("🌱 건강 도우미")
    st.write("아래 예시를 눌러 시작할 수 있어요.")

    examples = [
        "배가 아파요.",
        "머리가 아파요.",
        "목이 따갑고 기침이 나요.",
        "소화가 잘 안돼요.",
        "변비가 있는 것 같아요."
    ]

    for i, example in enumerate(examples):
        if st.button(example, key=f"example_{i}",
                     use_container_width=True):
            st.session_state.pending_question = example
            st.rerun()

    if st.button("🗑️ 새 상담 시작",
                 use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = ""
        st.rerun()

# ---------- 이전 대화 표시 ----------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- 입력 ----------
prompt = st.chat_input("불편한 증상을 입력해 주세요...")

if st.session_state.get("pending_question"):
    prompt = st.session_state.pending_question
    st.session_state.pending_question = ""

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    if has_emergency_sign(prompt):
        answer = (
            "🚨 **안전이 우선이에요.**\n\n"
            "입력한 증상은 긴급한 상황일 수 있어요. "
            "주변 어른이나 보호자에게 즉시 알리세요. "
            "호흡곤란이나 의식 저하 등 응급 상황이라면 "
            "119에 연락하세요. AI 답변을 기다리지 마세요."
        )

        with st.chat_message("assistant"):
            st.markdown(answer)

    else:
        with st.chat_message("assistant"):
            with st.spinner("건강 정보를 확인하고 있어요..."):
                try:
                    response = client.responses.create(
                        model="gpt-4.1-mini",
                        instructions=SYSTEM_PROMPT,
                        input=st.session_state.messages[-12:]
                    )

                    answer = response.output_text

                    if not answer:
                        answer = (
                            "답변을 받지 못했어요. "
                            "잠시 후 다시 시도해 주세요."
                        )

                    st.markdown(answer)

                except Exception as e:
                    st.error("AI 답변 생성에 실패했어요.")
                    st.write("오류 유형:", type(e).__name__)
                    st.code(str(e))

                    answer = (
                        "현재 AI 연결에 문제가 있어요. "
                        "오류 내용을 확인한 뒤 다시 시도해 주세요. "
                        "증상이 심하거나 악화되면 의료진의 도움을 받으세요."
                    )

                    st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

st.caption(
    "🌿 학생 건강 도우미 | 일반 건강 정보 제공 서비스"
)
