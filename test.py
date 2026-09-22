import streamlit as st
import requests
from datetime import date, datetime

# =========================
# 페이지 설정
# =========================

st.set_page_config(
    page_title="보라고등학교 시험 정보",
    page_icon="📚",
    layout="centered"
)

# =========================
# 보라고등학교 정보
# =========================

OFFICE_CODE = "J10"       # 경기도교육청
SCHOOL_CODE = "7530882"   # 보라고등학교

API_URL = "https://open.neis.go.kr/hub/SchoolSchedule"

# =========================
# 제목
# =========================

st.title("📚 보라고등학교 시험 정보")
st.caption("NEIS 학사일정 기반 시험 일정 조회")

st.divider()

# =========================
# 학년도 선택
# =========================

current_year = date.today().year

year = st.selectbox(
    "📅 학년도",
    [current_year - 1, current_year, current_year + 1],
    index=1
)

# =========================
# NEIS API 호출
# =========================

@st.cache_data(ttl=600)
def get_schedule(year):

    params = {
        "Type": "json",
        "pIndex": 1,
        "pSize": 1000,

        "ATPT_OFCDC_SC_CODE": OFFICE_CODE,
        "SD_SCHUL_CODE": SCHOOL_CODE,

        "AA_FROM_YMD": f"{year}0101",
        "AA_TO_YMD": f"{year}1231"
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    # NEIS 오류 처리
    if "RESULT" in data:
        result = data["RESULT"]

        code = result.get("CODE", "")
        message = result.get("MESSAGE", "")

        raise Exception(
            f"{code}: {message}"
        )

    if "SchoolSchedule" not in data:
        return []

    try:
        return data["SchoolSchedule"][1]["row"]
    except (IndexError, KeyError):
        return []


# =========================
# 시험 일정 판별
# =========================

def is_exam(schedule):

    event_name = str(
        schedule.get("EVENT_NM", "")
    )

    event_content = str(
        schedule.get("EVENT_CNTNT", "")
    )

    text = (
        event_name +
        " " +
        event_content
    )

    keywords = [
        "중간고사",
        "기말고사",
        "시험",
        "고사",
        "지필",
        "평가",
        "모의고사"
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# =========================
# 날짜 변환
# =========================

def format_date(ymd):

    if len(ymd) == 8:
        return (
            f"{ymd[:4]}년 "
            f"{ymd[4:6]}월 "
            f"{ymd[6:]}일"
        )

    return ymd


# =========================
# 조회 버튼
# =========================

if st.button(
    "🔍 시험 일정 조회",
    use_container_width=True
):

    with st.spinner(
        "NEIS에서 시험 일정을 불러오는 중..."
    ):

        try:
            schedules = get_schedule(year)

        except requests.exceptions.RequestException:
            st.error(
                "NEIS 서버에 연결하지 못했습니다."
            )
            st.stop()

        except Exception as e:
            st.error(
                f"NEIS API 오류가 발생했습니다.\n\n{e}"
            )
            st.stop()

    exams = [
        schedule
        for schedule in schedules
        if is_exam(schedule)
    ]

    exams.sort(
        key=lambda x: x.get("AA_YMD", "")
    )

    st.divider()

    if not exams:

        st.info(
            f"{year}학년도 NEIS 학사일정에서 "
            "시험 관련 일정을 찾지 못했습니다."
        )

    else:

        st.subheader(
            f"📝 {year}학년도 시험 일정"
        )

        for exam in exams:

            ymd = exam.get("AA_YMD", "")
            name = exam.get("EVENT_NM", "")
            content = exam.get(
                "EVENT_CNTNT",
                ""
            )

            with st.container(border=True):

                st.markdown(
                    f"### 📅 {format_date(ymd)}"
                )

                st.markdown(
                    f"**{name}**"
                )

                if content:
                    st.write(content)


# =========================
# 전체 학사일정
# =========================

st.divider()

with st.expander("📖 전체 학사일정 보기"):

    if st.button(
        "전체 일정 불러오기",
        use_container_width=True
    ):

        try:
            schedules = get_schedule(year)

            if not schedules:

                st.info(
                    "등록된 학사일정이 없습니다."
                )

            else:

                schedules.sort(
                    key=lambda x:
                    x.get("AA_YMD", "")
                )

                for schedule in schedules:

                    ymd = schedule.get(
                        "AA_YMD",
                        ""
                    )

                    name = schedule.get(
                        "EVENT_NM",
                        ""
                    )

                    content = schedule.get(
                        "EVENT_CNTNT",
                        ""
                    )

                    st.markdown(
                        f"**{format_date(ymd)}**  "
                        f"— {name}"
                    )

                    if content:
                        st.caption(content)

        except Exception as e:

            st.error(
                f"일정을 불러오지 못했습니다: {e}"
            )


# =========================
# 하단 안내
# =========================

st.divider()

st.caption(
    "학교: 보라고등학교 · "
    "경기도교육청 · "
    "학교코드 7530882"
)

st.caption(
    "※ 학교가 NEIS에 등록한 학사일정을 기준으로 합니다."
)
