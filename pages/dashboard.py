import streamlit as st
import plotly.express as px
import pymysql
import pandas as pd
from datetime import datetime

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
    
def get_empty_field_count(cursor, table, email_col, login_email):
    try:
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = [col["Field"] for col in cursor.fetchall()]

        query = f"SELECT {', '.join(columns)} FROM {table} WHERE {email_col} = %s"
        cursor.execute(query, (login_email,))
        results = cursor.fetchall()

        empty_count = 0
        total_count = 0
        for row in results:
            for col in columns:
                total_count += 1
                if row[col] is None or str(row[col]).strip() == "":
                    empty_count += 1
        return empty_count, total_count
    except pymysql.MySQLError as e:
        st.warning(f"테이블 {table} 데이터 가져오기 오류: {str(e)}")
        return 0, 0

def calculate_completion_ratio(empty_count, total_count):
    if total_count == 0:
        return 100.0  # 데이터가 없는 경우 완료로 간주
    filled_count = total_count - empty_count
    return round((filled_count / total_count) * 100, 2)

def get_tab_progress(login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return []

        cursor = conn.cursor()

        # 탭 이름과 테이블 매핑
        tab_table_map = {
            "개인정보": [("tb_resume_personal_info", "login_email")],
            "학력": [("tb_resume_education", "login_email"), ("tb_resume_education_major", "login_email")],
            "역량": [("tb_resume_skills", "login_email"), ("tb_resume_certifications", "login_email")],
            "경력": [("tb_resume_experiences", "login_email"), ("tb_resume_positions", "login_email")],
            "수상": [("tb_resume_awards", "login_email")],
            "기타활동": [("tb_resume_activities", "login_email"), ("tb_resume_training", "login_email")],
            "자기소개": [("tb_resume_self_introductions", "login_email")]
        }

        tab_progress = []

        for tab_name, tables in tab_table_map.items():
            total_empty = 0
            total_fields = 0
            for table, email_col in tables:
                empty_count, total_count = get_empty_field_count(cursor, table, email_col, login_email)
                total_empty += empty_count
                total_fields += total_count
            progress = calculate_completion_ratio(total_empty, total_fields)
            tab_progress.append({"탭 이름": tab_name, "진행률 (%)": progress})

        return tab_progress
    except Exception as e:
        st.error(f"탭별 진행률 계산 오류: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()
    
def show_dashboard_page():
    st.title("대시보드")
    if st.user.name:
        st.write(f"환영합니다, {st.user.name}님!")
    else:
        st.write("환영합니다, 사용자님!")

    # 로그인 이메일 가져오기
    login_email = st.user.email

    # 탭별 진행률 가져오기
    tab_progress = get_tab_progress(login_email)

    if tab_progress:
        df = pd.DataFrame(tab_progress)
        st.markdown("### 이력관리 탭별 진행률")
        st.dataframe(df)
    else:
        st.markdown("### 진행률 데이터를 가져올 수 없습니다.")

# 대시보드 페이지 표시
if __name__ == "__main__":
    show_dashboard_page()