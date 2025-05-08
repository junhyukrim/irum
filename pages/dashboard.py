import streamlit as st
import plotly.graph_objects as go

from pages.resume import load_personal_info, load_skills_info, load_education_info, load_career_info
from pages.jobs import load_jobs_info


def calculate_completion_ratio(total, filled):
    if total == 0:
        return 0
    return round((filled / total) * 100, 2)


def render_gauge_chart(title, value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#4285F4"},
            'steps': [
                {'range': [0, 50], 'color': "#f2f2f2"},
                {'range': [50, 100], 'color': "#d4edda"}
            ]
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

def connect_to_db():
    try:
        connection = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            cursorclass=pymysql.cursors.DictCursor,
            charset="utf8mb4"
        )

        return connection
    except Exception as e:
        st.error(f"DB 연결 오류: {str(e)}")
        return None

st.markdown('<h3 class="main-header">대시보드</h3>', unsafe_allow_html=True)

if 'user_email' not in st.session_state:
    st.warning("로그인이 필요합니다.")
    st.stop()

login_email = st.session_state.user_email

# 이력관리 완성도 계산
personal_info, _ = load_personal_info(login_email)
skills_info, _ = load_skills_info(login_email)
education_info, _ = load_education_info(login_email)
career_info, _ = load_career_info(login_email)

resume_total = 4
resume_filled = 0

try:
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tb_resume_personal_info WHERE login_email = %s", (login_email,))
        personal_count = cursor.fetchone()["COUNT(*)"]
        if personal_count > 0:
            resume_filled += 1

        cursor.execute("SELECT COUNT(*) FROM tb_resume_skills WHERE login_email = %s", (login_email,))
        skills_count = cursor.fetchone()["COUNT(*)"]
        if skills_count > 0:
            resume_filled += 1

        cursor.execute("SELECT COUNT(*) FROM tb_resume_education WHERE login_email = %s", (login_email,))
        education_count = cursor.fetchone()["COUNT(*)"]
        if education_count > 0:
            resume_filled += 1

        cursor.execute("SELECT COUNT(*) FROM tb_resume_career WHERE login_email = %s", (login_email,))
        career_count = cursor.fetchone()["COUNT(*)"]
        if career_count > 0:
            resume_filled += 1
        cursor.close()
        conn.close()
except Exception as e:
    st.error(f"DB 오류: {str(e)}")
resume_completion = calculate_completion_ratio(resume_total, resume_filled)

# 공고관리 완성도 계산
jobs, _ = load_jobs_info(login_email)
jobs_total = 1
jobs_filled = 0

try:
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tb_job_postings WHERE login_email = %s", (login_email,))
        jobs_count = cursor.fetchone()["COUNT(*)"]
        jobs_filled = jobs_count
        cursor.close()
        conn.close()
except Exception as e:
    st.error(f"DB 오류: {str(e)}")
jobs_completion = calculate_completion_ratio(jobs_total, jobs_filled)

# 시각화
st.markdown("### 이력관리 진행률")
render_gauge_chart("이력관리 완성도", resume_completion)

st.markdown("### 공고관리 진행률")
render_gauge_chart("공고관리 완성도", jobs_completion)
