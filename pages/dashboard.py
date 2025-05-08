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

def get_empty_fields():
    try:
        conn = connect_to_db()
        if conn is None:
            return []

        cursor = conn.cursor()

        # 이력관리 테이블 목록
        resume_tables = [
            "tb_resume_activities", "tb_resume_awards", "tb_resume_certifications", 
            "tb_resume_education", "tb_resume_education_major", "tb_resume_experiences",
            "tb_resume_personal_info", "tb_resume_positions", "tb_resume_self_introductions",
            "tb_resume_skills", "tb_resume_training"
        ]
        empty_fields = []

        for table in resume_tables:
            try:
                # 테이블의 모든 컬럼명 가져오기
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = [col["Field"] for col in cursor.fetchall()]
                
                # 각 필드의 빈 값 확인
                query = f"SELECT {', '.join(columns)} FROM {table} WHERE login_email = %s"
                cursor.execute(query, (st.user.email,))
                results = cursor.fetchall()

                for row in results:
                    for col in columns:
                        if row[col] is None or row[col] == "":
                            empty_fields.append({"Table": table, "Field": col, "Status": "Empty"})
            except pymysql.MySQLError as e:
                st.warning(f"테이블 {table} 데이터 가져오기 오류: {str(e)}")
    except Exception as e:
        st.error(f"빈 필드 데이터 가져오기 오류: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()
    return empty_fields

def get_progress_data():
    try:
        conn = connect_to_db()
        if conn is None:
            return 0, 0
        
        cursor = conn.cursor()
        
        # 이력관리 진행률 계산
        resume_tables = [
        "tb_resume_activities", "tb_resume_awards", "tb_resume_certifications", 
        "tb_resume_education", "tb_resume_education_major", "tb_resume_experiences",
        "tb_resume_personal_info", "tb_resume_positions", "tb_resume_self_introductions",
        "tb_resume_skills", "tb_resume_training"
    ]
        resume_count = 0
        max_resume_count = len(resume_tables) * 1
        try:
            for table in resume_tables:
                cursor.execute(f"SELECT COUNT(*) AS count FROM {table} WHERE login_email = %s", (st.user.email,))
                count = cursor.fetchone()['count']
                resume_count += 1 if count > 0 else 0

            resume_percent = (resume_count / max_resume_count) * 100
            
        except pymysql.MySQLError as e:
            st.warning(f"이력관리 데이터 가져오기 오류: {str(e)}")
            resume_count = 0

        # 공고관리 진행률 계산
        try:
            cursor.execute("SELECT COUNT(*) AS count FROM tb_job_postings WHERE login_email = %s", (st.user.email,))
            jobs_count = cursor.fetchone()['count']
            jobs_percent = 100 if jobs_count > 0 else 0
        except pymysql.MySQLError as e:
            st.warning(f"공고관리 데이터 가져오기 오류: {str(e)}")
            jobs_count = 0

        return resume_count, jobs_count
    except Exception as e:
        st.error(f"진행률 데이터 가져오기 오류: {str(e)}")
        return 0, 0
    finally:
        if conn:
            conn.close()
    
def show_dashboard_page():
    st.title("대시보드")

    resume_percent, jobs_percent = get_progress_data()

    st.markdown(f"### 이력관리 완료 상태: **{resume_percent:.2f}%**")
    st.markdown(f"### 공고관리 완료 상태: **{jobs_percent:.2f}%**")
    
    empty_fields = get_empty_fields()

    if empty_fields:
        df = pd.DataFrame(empty_fields)
        st.markdown("### 이력관리 탭별 빈 필드 상태")
        st.dataframe(df)
    else:
        st.markdown("### 모든 필드가 채워져 있습니다!")


if __name__ == "__main__":
    show_dashboard_page()