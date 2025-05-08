import streamlit as st
import plotly.express as px
import pymysql
from datetime import datetime
# from pages.resume import load_personal_info, load_skills_info, load_education_info, load_career_info
# from pages.jobs import load_jobs_info


# def calculate_completion_ratio(total, filled):
#     if total == 0:
#         return 0
#     return round((filled / total) * 100, 2)


# def render_gauge_chart(title, value):
#     fig = go.Figure(go.Indicator(
#         mode="gauge+number",
#         value=value,
#         title={'text': title},
#         gauge={
#             'axis': {'range': [0, 100]},
#             'bar': {'color': "#4285F4"},
#             'steps': [
#                 {'range': [0, 50], 'color': "#f2f2f2"},
#                 {'range': [50, 100], 'color': "#d4edda"}
#             ]
#         }
#     ))
#     st.plotly_chart(fig, use_container_width=True)

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
    
def get_progress_data():
    try:
        conn = connect_to_db()
        if conn is None:
            return 0, 0
        
        cursor = conn.cursor()
        
        # 이력관리 진행률 계산
        cursor.execute("SELECT COUNT(*) AS count FROM tb_resume WHERE user_email = %s", (st.session_state.user_email,))
        resume_count = cursor.fetchone()['count']

        # 공고관리 진행률 계산
        cursor.execute("SELECT COUNT(*) AS count FROM tb_job_postings WHERE login_email = %s", (st.session_state.user_email,))
        jobs_count = cursor.fetchone()['count']

        return resume_count, jobs_count
    except Exception as e:
        st.error(f"진행률 데이터 가져오기 오류: {str(e)}")
        return 0, 0
    finally:
        if conn:
            conn.close()
    
def show_dashboard_page():
    st.title("대시보드")
    st.write("환영합니다, " + st.experimental_user.name + "님!")

    resume_count, jobs_count = get_progress_data()

    # 시각화 데이터 준비
    progress_data = {
        "페이지": ["이력관리", "공고관리"],
        "완성도": [resume_count, jobs_count]
    }

    # 막대 그래프 그리기
    fig = px.bar(progress_data, x="페이지", y="완성도", title="페이지별 완료 상태",
                 color="페이지", text="완성도", height=400)

    st.plotly_chart(fig)