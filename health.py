
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
}
.main-title {
    text-align: center;
    color: #247653;
    font-size: 34px;
    font-weight: 800;
}
.subtitle {
    text-align: center;
    color: #64756B;
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

# ---------- 안전 관련 안내 ----------
st.warning(
    "이 서비스는 건강 정보 제공용이며 의사의 진단이나 처방을 "
    "대신하지 않습니다. 심한 증상은 보호자에게 알리고 의료진의 "
    "도움을 받으세요."
)

with st.expander("🚨 먼저 확인하세요: 응급 증상"):
    st.markdown("""
    다음 증상이 있다면 AI 상담보다 즉각적인 도움이 우선입니다.

    - 심한 호흡곤란 또는 의식 저하
    - 갑작스럽고 매우 심한 두통
    - 심한 가슴 통증
    - 심한 복통과 함께 의식이 흐려지거나 쓰러질 것 같은 경우
    - 심한 알레르기 반응으로 호흡이 어려운 경우

    이런 상황에서는 주변 어른에게 즉시 알리고 119에 연락하세요.
    """)

# ---------- API 연결 ----------
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    api_key = ""

if not api_key:
    st.error(
        "OpenAI API 키가 설정되지 않았어요. "
        "배포 안내에 따라 Secrets에 API 키를 등록해 주세요."
    )
    st.stop()

client = OpenAI(api_key=api_key)

# ---------- AI 안전 지침 ----------
SYSTEM_PROMPT = """
너는 대한민국 중고등학생을 위한 건강 정보 도우미다.
한국어로 친절하고 이해하기 쉽게 답한다.

중요한 원칙:
1. 의사처럼 확정 진단하지 않는다. 가능한 원인은 단정하지 않는다.
2. 나이, 증상의 정도, 지속 시간, 기저질환, 알레르기 등
   정보가 부족하면 필요한 질문을 먼저 한다.
3. 심각한 응급 징후가 있으면 음식이나 생활 팁보다
   응급 도움을 우선 안내한다. 한국에서는 119에 연락하도록 한다.
4. 음식은 증상에 따라 일반적으로 섭취하기 편한 선택지를 설명한다.
   모든 사람에게 효과가 있다고 말하지 않는다.
5. 피해야 할 음식은 증상을 악화할 가능성이 있는 음식 위주로 설명한다.
   불필요한 식품 제한을 권하지 않는다.
6. 집에서 할 수 있는 안전한 일반 관리법을 안내한다.
7. 특정 처방약을 선택하거나 처방하지 않는다.
   약의 용량, 복용 횟수, 여러 약의 병용을 임의로 지시하지 않는다.
   일반의약품도 연령, 알레르기, 다른 약 복용 여부 등에 따라
   적합성이 달라지므로 보호자와 약사 또는 의사에게 확인하도록 한다.
8. 항생제, 남의 처방약, 임의로 구한 약을 복용하도록 권하지 않는다.
9. 증상이 지속되거나 악화되면 보호자에게 알리고 진료를 권한다.
10. 학생에게 민감한 개인정보를 불필요하게 요구하지 않는다.
    이름, 학교명, 전화번호, 주소는 묻지 않는다.

답변 형식:
### 1. 증상 이해하기
입력된 증상을 요약하고, 필요하면 추가 질문을 한다.

### 2. 도움이 될 수 있는 음식
일반적으로 먹기 편한 음식과 그 이유를 설명한다.

### 3. 주의하면 좋은 음식
증상을 악화할 수 있는 음식과 그 이유를 설명한다.
해당 사항이 없다면 억지로 만들지 않는다.

### 4. 집에서 할 수 있는 대처법
수분 섭취, 휴식 등 안전한 방법을 안내한다.

### 5. 약을 사용할 때 주의할 점
약사나 의사에게 확인할 사항을 안내한다.
임의로 약을 처방하거나 복용량을 정하지 않는다.

### 6. 병원에 가야 하는 경우
악화 징후와 진료가 필요한 상황을 설명한다.

정보가 부족하다면 모든 항목을 억지로 채우지 말고
안전을 위한 질문부터 한다.
응급 증상이 의심되면 위의 형식보다 응급 안내를 우선한다.
"""

# 간단한 응급 징후 사전 확인
EMERGENCY_TERMS = [
    "숨을 못 쉬", "호흡이 안", "의식을 잃",
    "정신을 잃", "쓰러졌어", "가슴이 심하게 아",
    "갑자기 극심한 두통", "입술이 파래",
    "목이 부어 숨", "피를 많이"
]

def has_emergency_sign(text):
    text = text.replace(" ", "")
    return any(
        term.replace(" ", "") in text
        for term in EMERGENCY_TERMS
    )

# ---------- 대화 상태 ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- 사이드바 ----------
with st.sidebar:
    st.header("🌱 건강 도우미 안내")
    st.write("예시 증상")
    examples = [
        "시험 기간에 두통이 있어요.",
        "배가 아프고 소화가 잘 안돼요.",
        "목이 따갑고 기침이 나요.",
        "변비가 있는 것 같아요.",
        "운동 후 근육이 아파요."
    ]

    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.pending_question = example

    st.divider()
    if st.button("🗑️ 새 상담 시작", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = ""
        st.rerun()

# ---------- 이전 대화 표시 ----------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- 사용자 입력 ----------
prompt = st.chat_input(
    "불편한 증상을 입력해 주세요..."
)

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

    # 명확한 위험 표현이 있으면 AI 응답 전에 안전 안내
    if has_emergency_sign(prompt):
        answer = (
            "🚨 **지금은 AI 상담보다 안전이 우선이에요.**\n\n"
            "입력한 내용에 긴급한 증상일 수 있는 표현이 있어요. "
            "주변 어른이나 보호자에게 즉시 알리고, "
            "호흡곤란·의식 저하 등 응급 상황이라면 119에 연락하세요. "
            "증상이 심하면 답변을 기다리지 말고 즉시 도움을 받으세요."
        )
        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })
    else:
        with st.chat_message("assistant"):
            with st.spinner("건강 정보를 확인하고 있어요..."):
                try:
                    response = client.responses.create(
                        model="gpt-5.4-nano",
                        instructions=SYSTEM_PROMPT,
                        input=st.session_state.messages[-12:]
                    )
                    answer = response.output_text
                    st.markdown(answer)

                except Exception:
                    answer = (
                        "죄송해요. 지금은 답변을 생성하지 못했어요. "
                        "잠시 후 다시 시도해 주세요. "
                        "증상이 심하거나 악화되면 보호자에게 알리고 "
                        "의료진의 도움을 받으세요."
                    )
                    st.error(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

st.caption(
    "🌿 학생 건강 도우미 | 교육 목적의 일반 건강 정보 서비스"
)
