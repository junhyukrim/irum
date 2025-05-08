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
    
def map_column_to_field(table, column):
    field_mapping = {
        # 개인정보
        "tb_resume_personal_info": {
            "name": "이름", "birth_date": "생년월일", "phone": "전화번호", "email": "이메일"
        },
        # 학력
        "tb_resume_education": {
            "school_name": "학교명", "degree": "학위", "major": "전공", "gpa": "학점"
        },
        "tb_resume_education_major": {
            "department": "학과", "degree": "학위", "gpa": "학점"
        },
        # 역량
        "tb_resume_skills": {
            "skill_name": "기술명", "proficiency": "숙련도"
        },
        "tb_resume_certifications": {
            "cert_name": "자격증명", "issue_date": "발급일"
        },
        # 경력
        "tb_resume_experiences": {
            "company_name": "회사명", "position": "직무", "start_date": "시작일", "end_date": "종료일"
        },
        "tb_resume_positions": {
            "position": "직무명", "promotion_date": "승진일", "retirement_date": "퇴직일"
        },
        # 수상
        "tb_resume_awards": {
            "award_name": "수상명", "award_date": "수상일"
        },
        # 기타활동
        "tb_resume_activities": {
            "activity_name": "활동명", "activity_date": "활동일"
        },
        "tb_resume_training": {
            "training_name": "교육명", "training_date": "교육일"
        },
        # 자기소개
        "tb_resume_self_introductions": {
            "intro_text": "자기소개 내용"
        }
    }
    return field_mapping.get(table, {}).get(column, column)
    
def get_related_ids(cursor, table, id_column, email_col, login_email):
    try:
        query = f"SELECT id FROM {table} WHERE {email_col} = %s"
        cursor.execute(query, (login_email,))
        results = cursor.fetchall()
        return [row['id'] for row in results]
    except pymysql.MySQLError as e:
        st.warning(f"{table} 테이블 ID 가져오기 오류: {str(e)}")
        return []
    
def get_filled_field_count(cursor, table, where_clause, where_values):
    try:
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = [col["Field"] for col in cursor.fetchall()]

        query = f"SELECT {', '.join(columns)} FROM {table} {where_clause}"
        cursor.execute(query, where_values)
        results = cursor.fetchall()

        filled_count = 0
        total_count = 0
        empty_fields = []

        for row in results:
            for col in columns:
                total_count += 1
                if row[col] is not None and str(row[col]).strip() != "":
                    filled_count += 1
                else:
                    empty_fields.append(map_column_to_field(table, col))

        return filled_count, total_count, empty_fields
    except pymysql.MySQLError as e:
        st.warning(f"테이블 {table} 데이터 가져오기 오류: {str(e)}")
        return 0, 0, []

def calculate_completion_ratio(filled_count, total_count):
    if total_count == 0:
        return 0.0
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
            "학력": [
                ("tb_resume_education", "login_email"),
                ("tb_resume_education_major", "login_email")
            ],
            "역량": [
                ("tb_resume_skills", "login_email"),
                ("tb_resume_certifications", "login_email")
            ],
            "경력": [
                ("tb_resume_experiences", "login_email"),
                ("tb_resume_positions", "login_email")
            ],
            "수상": [("tb_resume_awards", "login_email")],
            "기타활동": [
                ("tb_resume_activities", "login_email"),
                ("tb_resume_training", "login_email")
            ],
            "자기소개": [("tb_resume_self_introductions", "login_email")]
        }

        tab_progress = []

        for tab_name, tables in tab_table_map.items():
            total_filled = 0
            total_fields = 0
            all_empty_fields = []

            for table, id_col in tables:
                where_clause = f"WHERE {id_col} = %s"
                where_values = (login_email,)

                filled_count, total_count, empty_fields = get_filled_field_count(cursor, table, where_clause, where_values)
                total_filled += filled_count
                total_fields += total_count
                all_empty_fields.extend(empty_fields)

            progress = calculate_completion_ratio(total_filled, total_fields)
            empty_fields_str = ", ".join(all_empty_fields) if all_empty_fields else "없음"
            tab_progress.append({"탭 이름": tab_name, "진행률 (%)": progress, "비어있는 필드": empty_fields_str})

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
        st.markdown("### 이력관리 탭별 진행률 및 비어있는 필드")
        st.dataframe(df)
    else:
        st.markdown("### 진행률 데이터를 가져올 수 없습니다.")

# 대시보드 페이지 표시
if __name__ == "__main__":
    show_dashboard_page()