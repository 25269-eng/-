import streamlit as st
import requests
from datetime import date, timedelta
import re

# =========================
# 기본 설정
# =========================

st.set_page_config(
    page_title="보라고등학교 급식",
    page_icon="🍚",
    layout="centered"
)

SCHOOL_CODE = "7530882"
EDU_CODE = "J10"

API_URL = "https://kschoolinfo.com/api/v1/meals"

# =========================
# 화면
# =========================

st.title("🍚 보라고등학교 급식")
st.caption("오늘의 급식과 칼로리를 확인하세요")

st.divider()

# =========================
# 날짜 선택
# =========================

selected_date = st.date_input(
    "📅 급식 날짜",
    value=date.today()
)

date_string = selected_date.strftime("%Y%m%d")

# =========================
# 급식 조회
# =========================

@st.cache_data(ttl=600)
def get_meal(date_string):

    params = {
        "eduCode": EDU_CODE,
        "schoolCode": SCHOOL_CODE,
        "date": date_string
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# =========================
# 칼로리 숫자 추출
# =========================

def get_calorie(value):

    if value is None:
        return None

    text = str(value)

    match = re.search(
        r"[\d,.]+",
        text
    )

    if match:
        return match.group()

    return None


# =========================
# 조회
# =========================

if st.button(
    "🔍 급식 조회",
    use_container_width=True
):

    with st.spinner("급식 정보를 불러오는 중..."):

        try:
            data = get_meal(date_string)

        except requests.exceptions.RequestException:
            st.error(
                "급식 정보를 불러오지 못했습니다."
            )
            st.stop()

        except Exception as e:
            st.error(
                f"오류가 발생했습니다: {e}"
            )
            st.stop()

    # API 응답 형태에 따라 meals 추출
    if isinstance(data, dict):

        meals = (
            data.get("meals")
            or data.get("data")
            or data.get("meal")
            or []
        )

    elif isinstance(data, list):

        meals = data

    else:

        meals = []

    # 혹시 단일 객체로 오는 경우
    if isinstance(meals, dict):
        meals = [meals]

    st.divider()

    if not meals:

        st.info(
            f"{selected_date.strftime('%Y년 %m월 %d일')}에는 "
            "등록된 급식 정보가 없습니다."
        )

    else:

        st.subheader(
            f"🍽️ {selected_date.strftime('%Y년 %m월 %d일')}"
        )

        for meal in meals:

            if not isinstance(meal, dict):
                continue

            # 식사 종류
            meal_name = (
                meal.get("MMEAL_SC_NM")
                or meal.get("mealType")
                or meal.get("meal")
                or "급식"
            )

            # 메뉴
            menu = (
                meal.get("DDISH_NM")
                or meal.get("menu")
                or meal.get("dishes")
                or ""
            )

            # 칼로리
            calorie = (
                meal.get("CAL_INFO")
                or meal.get("calorie")
                or meal.get("calories")
                or ""
            )

            with st.container(border=True):

                st.markdown(
                    f"### 🍽️ {meal_name}"
                )

                if calorie:

                    number = get_calorie(calorie)

                    if number:
                        st.metric(
                            "🔥 칼로리",
                            f"{number} kcal"
                        )
                    else:
                        st.write(
                            f"🔥 {calorie}"
                        )

                if menu:

                    st.markdown("#### 🍴 메뉴")

                    # <br> 또는 줄바꿈 처리
                    menu_text = str(menu)
                    menu_text = re.sub(
                        r"<br\s*/?>",
                        "\n",
                        menu_text,
                        flags=re.IGNORECASE
                    )

                    # 알레르기 번호 제거
                    menu_text = re.sub(
                        r"\d+(?:\.\d+)*",
                        "",
                        menu_text
                    )

                    menu_items = [
                        item.strip()
                        for item in menu_text.split("\n")
                        if item.strip()
                    ]

                    for item in menu_items:
                        st.write(f"• {item}")

                st.divider()


# =========================
# 빠른 날짜 이동
# =========================

st.subheader("📆 빠른 날짜 이동")

col1, col2, col3 = st.columns(3)

with col1:

    if st.button("어제", use_container_width=True):

        st.session_state[
            "selected_date"
        ] = date.today() - timedelta(days=1)

        st.rerun()

with col2:

    if st.button("오늘", use_container_width=True):

        st.session_state[
            "selected_date"
        ] = date.today()

        st.rerun()

with col3:

    if st.button("내일", use_container_width=True):

        st.session_state[
            "selected_date"
        ] = date.today() + timedelta(days=1)

        st.rerun()


# =========================
# 안내
# =========================

st.divider()

st.caption(
    "학교: 보라고등학교"
)

st.caption(
    "교육청 코드: J10 · 학교 코드: 7530882"
)

st.caption(
    "※ 급식 정보는 NEIS 기반 공개 데이터를 이용합니다."
)
