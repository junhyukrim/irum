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
        "tb_resume_personal_info": {
            "ko_lastname": "한글 성", "ko_firstname": "한글 이름", 
            "en_firstname": "영문 이름", "en_lastname": "영문 성",
            "nationality": "국적", "gender": "성별", "birth_date": "생년월일", 
            "address": "주소", "email": "이메일", "contact_number": "연락처", 
            "photo_url": "사진 링크", "military_status": "병역",
            "military_type": "병역 유형", "military_rank": "계급", 
            "veterans_status": "보훈 여부", "service_start": "복무 시작일", 
            "service_end": "복무 종료일", "discharge_type": "전역 유형"
        },
        "tb_resume_education": {
            "institution": "교육기관", "start_date": "입학년월", "end_date": "졸업년월", "note": "비고"
        },
        "tb_resume_education_major": {
            "department": "학부 또는 분야", "major": "학과, 전공, 세부내용", "degree": "학위", "gpa": "성적"
        },
        "tb_resume_skills": {
            "skill_name": "기술 및 역량", "skill_level": "성취수준", "note": "비고"
        },
        "tb_resume_certifications": {
            "certification_name": "자격증명", "issue_date": "취득일", "issuing_agency": "발급기관"
        },
        "tb_resume_experiences": {
            "company_name": "회사명", "join_date": "입사년월", "leave_date": "퇴사년월", "leave_reason": "퇴사사유"
        },
        "tb_resume_positions": {
            "position": "직위/직책", "promotion_date": "취임일", "retirement_date": "퇴임일", "description": "업무내용"
        },
        "tb_resume_awards": {
            "award_name": "수상명", "award_date": "수상일", "awarding_body": "수여기관", "note": "비고"
        },
        "tb_resume_activities": {
            "activity_name": "활동명", "organization": "소속", "start_date": "시작년월", "end_date": "종료년월", "role" : "직책/역할", "link": "링크", "details": "활동 세부내역"
        },
        "tb_resume_training": {
            "description": "교육 내용"
        },
        "tb_resume_self_introductions": {
            "topic_category": "자기소개분야", "topic_title": "주제", "content": "자기소개문"
        },
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

def get_resume_progress(login_email):
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
                ("tb_resume_education_major", "education_id")
            ],
            "역량": [
                ("tb_resume_skills", "login_email"),
                ("tb_resume_certifications", "login_email")
            ],
            "경력": [
                ("tb_resume_experiences", "login_email"),
                ("tb_resume_positions", "experience_id")
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

                cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = [col["Field"] for col in cursor.fetchall()]
                
                query = f"SELECT {', '.join(columns)} FROM {table} {where_clause}"
                cursor.execute(query, where_values)
                results = cursor.fetchall()

                for row in results:
                    for col in columns:
                        total_fields += 1
                        if row[col] is not None and str(row[col]).strip() != "":
                            total_filled += 1
                        else:
                            all_empty_fields.append(map_column_to_field(table, col))

            progress = round((total_filled / total_fields) * 100, 2) if total_fields else 0
            empty_fields_str = ", ".join(all_empty_fields) if all_empty_fields else "없음"
            tab_progress.append({"탭 이름": tab_name, "진행률 (%)": progress, "비어있는 필드": empty_fields_str})

        return tab_progress
    except Exception as e:
        st.error(f"탭별 진행률 계산 오류: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def get_career_progress(login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return []

        cursor = conn.cursor()

        # 경력관리 테이블 매핑
        career_table_map = {
            "경력": [
                ("tb_resume_experiences", "login_email"),
                ("tb_resume_positions", "experience_id")
            ]
        }

        career_progress = []

        for tab_name, tables in career_table_map.items():
            total_filled = 0
            total_fields = 0
            all_empty_fields = []

            for table, id_col in tables:
                if id_col == "login_email":
                    where_clause = f"WHERE {id_col} = %s"
                    where_values = (login_email,)
                elif id_col == "experience_id":
                    where_clause = f"WHERE {id_col} IN (SELECT id FROM tb_resume_experiences WHERE login_email = %s)"
                    where_values = (login_email,)
                else:
                    continue

                filled_count, total_count, empty_fields = get_filled_field_count(cursor, table, where_clause, where_values)
                total_filled += filled_count
                total_fields += total_count
                all_empty_fields.extend(empty_fields)

            progress = calculate_completion_ratio(total_filled, total_fields)
            empty_fields_str = ", ".join(all_empty_fields) if all_empty_fields else "없음"
            career_progress.append({"경력관리 탭": tab_name, "진행률 (%)": progress, "비어있는 필드": empty_fields_str})

        return career_progress
    except Exception as e:
        st.error(f"경력관리 진행률 계산 오류: {str(e)}")
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
    tab_progress = get_resume_progress(login_email)

    if tab_progress:
        df = pd.DataFrame(tab_progress)
        st.markdown("### 이력관리 탭별 진행률 및 비어있는 필드")
        st.dataframe(df)
    else:
        st.markdown("### 진행률 데이터를 가져올 수 없습니다.")


    # 경력관리 진행률 가져오기
    career_progress = get_career_progress(login_email)

    if career_progress:
        df_career = pd.DataFrame(career_progress)
        st.markdown("### 경력관리 진행률 및 비어있는 필드")
        st.dataframe(df_career)
    else:
        st.markdown("### 경력관리 진행률 데이터를 가져올 수 없습니다.")

# 대시보드 페이지 표시
if __name__ == "__main__":
    show_dashboard_page()