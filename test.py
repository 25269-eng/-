import streamlit as st
import requests
from datetime import date

# =========================
# 기본 설정
# =========================

st.set_page_config(
    page_title="보라고등학교 시험 정보",
    page_icon="📚",
    layout="centered"
)

# 경기도교육청 / 보라고등학교
ATPT_OFCDC_SC_CODE = "J10"
SD_SCHUL_CODE = "7530882"

API_URL = "https://open.neis.go.kr/hub/SchoolSchedule"

# =========================
# API 키
# =========================

try:
    API_KEY = st.secrets["NEIS_API_KEY"]
except Exception:
    API_KEY = ""

# =========================
# 제목
# =========================

st.title("📚 보라고등학교 시험 정보")
st.caption("NEIS 교육정보 개방 API를 이용한 학사일정 조회")

st.divider()

if not API_KEY:
    st.error(
        "NEIS API 인증키가 설정되지 않았습니다.\n\n"
        "Streamlit Cloud의 Settings → Secrets에 "
        "`NEIS_API_KEY`를 추가해주세요."
    )
    st.stop()

# =========================
# 학년도 선택
# =========================

current_year = date.today().year

school_year = st.selectbox(
    "학년도",
    list(range(current_year - 1, current_year + 2)),
    index=1
)

# =========================
# NEIS 데이터 가져오기
# =========================

@st.cache_data(ttl=600)
def get_school_schedule(year):
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 1000,
        "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,
        "AA_FROM_YMD": f"{year}0101",
        "AA_TO_YMD": f"{year}1231",
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    # API 오류 확인
    if "RESULT" in data:
        result = data["RESULT"]
        code = result.get("CODE", "")
        message = result.get("MESSAGE", "알 수 없는 오류")

        raise Exception(f"{code}: {message}")

    if "SchoolSchedule" not in data:
        return []

    rows = data["SchoolSchedule"][1].get("row", [])

    return rows


# =========================
# 시험 일정 필터
# =========================

def is_exam_event(event):
    """
    학사일정의 행사명/내용에서 시험 관련 일정을 찾는다.
    """

    event_name = str(event.get("EVENT_NM", ""))
    event_content = str(event.get("EVENT_CNTNT", ""))

    text = f"{event_name} {event_content}"

    keywords = [
        "시험",
        "고사",
        "중간고사",
        "기말고사",
        "평가",
        "지필",
        "모의고사"
    ]

    return any(keyword in text for keyword in keywords)


# =========================
# 조회
# =========================

if st.button("🔍 시험 일정 조회", use_container_width=True):

    with st.spinner("NEIS에서 학사일정을 불러오는 중..."):

        try:
            schedules = get_school_schedule(school_year)

        except requests.exceptions.RequestException:
            st.error("NEIS 서버에 연결하지 못했습니다.")
            st.stop()

        except Exception as e:
            st.error(f"NEIS API 오류: {e}")
            st.stop()

    exams = [
        item for item in schedules
        if is_exam_event(item)
    ]

    # 날짜순 정렬
    exams.sort(
        key=lambda x: x.get("AA_YMD", "")
    )

    st.divider()

    if not exams:
        st.info(
            f"{school_year}학년도 NEIS 학사일정에서 "
            "시험 관련 일정이 확인되지 않았습니다."
        )
    else:

        st.subheader(f"📝 {school_year}학년도 시험 일정")

        for exam in exams:

            exam_date = exam.get("AA_YMD", "")
            event_name = exam.get("EVENT_NM", "")
            event_content = exam.get("EVENT_CNTNT", "")

            # YYYYMMDD → YYYY년 MM월 DD일
            if len(exam_date) == 8:
                formatted_date = (
                    f"{exam_date[:4]}년 "
                    f"{exam_date[4:6]}월 "
                    f"{exam_date[6:]}일"
                )
            else:
                formatted_date = exam_date

            with st.container(border=True):

                st.markdown(
                    f"### 📅 {formatted_date}"
                )

                st.markdown(
                    f"**{event_name}**"
                )

                if event_content:
                    st.write(event_content)

        st.divider()

        st.caption(
            "※ 시험 일정은 NEIS에 학교가 등록한 학사일정을 기준으로 표시됩니다."
        )


# =========================
# 전체 학사일정 확인
# =========================

with st.expander("📖 전체 학사일정 보기"):

    if st.button(
        "전체 일정 불러오기",
        key="all_schedule"
    ):

        with st.spinner("학사일정을 불러오는 중..."):

            try:
                schedules = get_school_schedule(school_year)

                if not schedules:
                    st.info("등록된 학사일정이 없습니다.")
                else:

                    for item in sorted(
                        schedules,
                        key=lambda x: x.get("AA_YMD", "")
                    ):

                        ymd = item.get("AA_YMD", "")
                        name = item.get("EVENT_NM", "")
                        content = item.get("EVENT_CNTNT", "")

                        if len(ymd) == 8:
                            ymd = (
                                f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"
                            )

                        st.markdown(
                            f"**{ymd}** — {name}"
                        )

                        if content:
                            st.caption(content)

            except Exception as e:
                st.error(f"조회 중 오류가 발생했습니다: {e}")


# =========================
# 안내
# =========================

st.divider()

st.caption(
    "데이터 출처: 교육부 나이스(NEIS) 교육정보 개방 포털"
)
