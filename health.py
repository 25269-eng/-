
import streamlit as st
from openai import OpenAI

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="학생 건강 도우미",
    page_icon="🌿",
    layout="centered"
)

# ==========================================
# 2. 디자인
# ==========================================
st.markdown("""
<style>
.stApp {
    background-color: #F4FAF6;
    color: #26382E;
}

.main-title {
    text-align: center;
    color: #237650 !important;
    font-size: 32px;
    font-weight: 800;
    margin-bottom: 8px;
}

.subtitle {
    text-align: center;
    color: #617569 !important;
    font-size: 15px;
    margin-bottom: 25px;
}

[data-testid="stChatMessage"] {
    background-color: #FFFFFF;
    border: 1px solid #E1EDE5;
    border-radius: 16px;
    padding: 12px;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    color: #26382E !important;
}

.stMarkdown p,
.stMarkdown li {
    color: #26382E;
}

div.stButton > button {
    border-radius: 12px;
    min-height: 42px;
}

[data-testid="stChatInput"] {
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🌿 학생 건강 도우미</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    '증상을 입력하고 건강 관리 정보를 알아보세요.'
    '</div>',
    unsafe_allow_html=True
)

# ==========================================
# 3. 건강 안전 안내
# ==========================================
st.info(
    "이 서비스는 일반 건강 정보 제공용이며 "
    "의사의 진단이나 처방을 대신하지 않습니다."
)

with st.expander("🚨 응급 증상이 있다면 꼭 확인하세요"):
    st.markdown("""
    다음과 같은 증상이 있다면 AI 상담을 기다리지 마세요.

    - 심한 호흡곤란 또는 의식 저하
    - 갑작스럽고 매우 심한 두통
    - 심한 가슴 통증
    - 심한 알레르기 반응으로 호흡이 어려운 경우

    주변 어른이나 보호자에게 즉시 알리고,
    응급 상황이라면 119에 연락하세요.
    """)

# ==========================================
# 4. OpenAI API 설정
# ==========================================
# Streamlit Cloud의 Settings → Secrets에서 설정
api_key = st.secrets.get("OPENAI_API_KEY", "").strip()

if not api_key:
    st.error(
        "OPENAI_API_KEY를 찾을 수 없어요.\n\n"
        "Streamlit Cloud의 앱 설정에서 Secrets를 확인해 주세요."
    )
    st.stop()

client = OpenAI(api_key=api_key)

# 사용할 모델
MODEL_NAME = "gpt-5.4-nano"

# ==========================================
# 5. AI 건강 상담 지침
# ==========================================
SYSTEM_PROMPT = """
너는 대한민국 중고등학생을 위한 건강 정보 도우미다.
학생이 이해하기 쉽도록 친절하고 정확한 한국어로 답변한다.

[안전 원칙]

1. 증상만으로 질병을 확정하거나 진단하지 않는다.
2. 증상이 불분명하면 지속 시간, 심각도 등 필요한 내용을 질문한다.
3. 응급 증상이 의심되면 음식이나 생활 관리법보다
   즉각적인 의료 도움을 안내한다.
4. 일반적으로 먹기 편한 음식과 증상을 악화할 수 있는 음식을
   이유와 함께 설명한다. 음식의 효과를 보장하지 않는다.
5. 모든 사람에게 특정 음식을 강제로 권하거나
   불필요하게 다양한 음식을 제한하지 않는다.
6. 수분 섭취, 휴식 등 안전한 일반 관리법을 안내한다.
7. 특정 약을 처방하거나 임의로 약의 용량과 복용 횟수를
   결정하지 않는다.
8. 약의 적합성은 나이, 알레르기, 복용 중인 약 등에 따라
   달라질 수 있으므로 보호자와 약사 또는 의사에게 확인하도록 한다.
9. 다른 사람의 처방약이나 남은 항생제를 임의로 복용하지 않도록 한다.
10. 증상이 심해지거나 지속되면 보호자에게 알리고 진료를 권한다.
11. 이름, 학교, 주소, 전화번호 등 개인정보를 요구하지 않는다.
12. 근거가 불확실한 정보는 사실처럼 단정하지 않는다.

[답변 형식]

### 1. 증상 이해하기
학생이 말한 증상을 간단히 정리한다.
정보가 부족하면 필요한 질문을 먼저 한다.

### 2. 도움이 될 수 있는 음식
먹기 편한 음식과 그 이유를 설명한다.

### 3. 주의하면 좋은 음식
증상을 악화할 수 있는 음식과 그 이유를 설명한다.
해당 사항이 없다면 억지로 만들지 않는다.

### 4. 집에서 할 수 있는 대처법
안전한 휴식 및 생활 관리 방법을 설명한다.

### 5. 약을 사용할 때 주의할 점
약사나 의사에게 확인할 사항을 설명한다.
임의로 약을 처방하거나 용량을 정하지 않는다.

### 6. 병원에 가야 하는 경우
진료가 필요한 상황과 악화 징후를 설명한다.

응급 상황이 의심되면 위의 형식보다 응급 안내를 우선한다.
"""

# ==========================================
# 6. 응급 표현 사전 확인
# ==========================================
EMERGENCY_TERMS = [
    "숨을 못 쉬",
    "숨쉬기 힘들",
    "호흡이 안",
    "의식을 잃",
    "정신을 잃",
    "쓰러졌어",
    "심한 가슴 통증",
    "가슴이 심하게 아",
    "갑자기 극심한 두통",
    "목이 부어 숨",
    "피를 많이 흘",
    "입술이 파래"
]

def has_emergency_sign(text):
    normalized = text.replace(" ", "")
    return any(
        term.replace(" ", "") in normalized
        for term in EMERGENCY_TERMS
    )

# ==========================================
# 7. 대화 기록 초기화
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 8. 사이드바
# ==========================================
with st.sidebar:
    st.header("🌱 건강 도우미")
    st.write("어떤 증상이 있는지 선택해 보세요.")

    examples = [
        "배가 아파요.",
        "머리가 아파요.",
        "목이 따갑고 기침이 나요.",
        "소화가 잘 안돼요.",
        "변비가 있는 것 같아요.",
        "운동 후 근육이 아파요."
    ]

    for i, example in enumerate(examples):
        if st.button(
            example,
            key=f"example_{i}",
            use_container_width=True
        ):
            st.session_state.pending_question = example
            st.rerun()

    st.divider()

    if st.button(
        "🗑️ 새 상담 시작",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.session_state.pending_question = ""
        st.rerun()

    st.caption(
        "개인정보나 민감한 의료정보는 입력하지 마세요."
    )

# ==========================================
# 9. 이전 대화 표시
# ==========================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 10. 사용자 입력 받기
# ==========================================
prompt = st.chat_input(
    "불편한 증상을 입력해 주세요..."
)

# 사이드바 예시 버튼을 누른 경우
if st.session_state.get("pending_question"):
    prompt = st.session_state.pending_question
    st.session_state.pending_question = ""

# ==========================================
# 11. AI 답변 생성
# ==========================================
if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # 응급 표현이 있는 경우 우선 안내
    if has_emergency_sign(prompt):
        answer = (
            "🚨 **지금은 안전이 우선이에요.**\n\n"
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
                        model=MODEL_NAME,
                        instructions=SYSTEM_PROMPT,
                        input=st.session_state.messages[-12:]
                    )

                    answer = response.output_text

                    if not answer:
                        answer = (
                            "답변을 생성하지 못했어요. "
                            "질문을 조금 바꾸어 다시 시도해 주세요."
                        )

                    st.markdown(answer)

                except Exception as e:
                    st.error("AI 답변 생성 중 오류가 발생했어요.")
                    st.caption(
                        f"오류 유형: {type(e).__name__}"
                    )

                    # API 키 전체를 화면에 표시하지 않음
                    error_message = str(e)
                    if api_key:
                        error_message = error_message.replace(
                            api_key, "[API KEY]"
                        )

                    st.code(error_message)

                    answer = (
                        "현재 AI 연결에 문제가 있어 답변을 "
                        "생성하지 못했어요. 오류 유형을 확인해 주세요. "
                        "증상이 심하거나 악화되면 보호자에게 알리고 "
                        "의료진의 도움을 받으세요."
                    )

                    st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

# ==========================================
# 12. 하단 안내
# ==========================================
st.divider()

st.caption(
    "🌿 학생 건강 도우미 | 일반 건강 정보 제공 서비스\n\n"
    "이 서비스는 응급 상황을 완벽하게 감지하지 못할 수 있습니다. "
    "위험한 증상이 있다면 AI의 안내와 관계없이 즉시 도움을 받으세요."
)
