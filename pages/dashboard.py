import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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
    
def show_gauge_chart(progress, title):
    fig = go.Figure(go.Pie(
        values=[progress, 100 - progress],
        labels=["입력됨", "입력 안 됨"],
        hole=0.7,
        direction="clockwise",
        sort=False,
        textinfo="label+percent",
        textposition="inside",
        marker=dict(colors=["#4285F4", "lightgray"]),
        showlegend=True
    ))
    fig.update_traces(marker=dict(line=dict(color="#000000", width=0.5)))
    fig.update_layout(
        annotations=[
            dict(text=f"{progress}/100", x=0.5, y=0.5, font_size=30, showarrow=False)
        ],
        height=300,
        margin=dict(t=0, b=20, l=0, r=0)
    )
    st.plotly_chart(fig, key=f"gauge_{title}")

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
        "tb_job_postings": {
            "company_name": "기업명", "position": "직무명", "openings": "채용인원", "deadline": "제출기한",
            "requirements": "자격요건", "main_duties": "주요업무", "motivation": "지원동기", "submission": "제출서류&지원방법",
            "contact": "문의처", "company_website": "홈페이지 주소", "company_intro": "기업소개", "talent": "인재상",
            "preferences": "우대조건", "company_culture": "근무환경", "faq": "FAQ", "additional_info": "기타 안내사항" 
        }
    }
    return field_mapping.get(table, {}).get(column, column)

def get_related_ids(cursor, table, id_column, email_col, login_email):
    try:
        query = f"SELECT id FROM {table} WHERE {email_col} = %s"
        cursor.execute(query, (login_email,))
        results = cursor.fetchall()
        return [row["id"] for row in results]
    except pymysql.MySQLError as e:
        st.warning(f"{table} 테이블 ID 가져오기 오류: {str(e)}")
        return []
    
def get_filled_field_count(cursor, table, where_clause, where_values):
    try:
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = [col["Field"] for col in cursor.fetchall()]

        query = f"SELECT {", ".join(columns)} FROM {table} {where_clause}"
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
                
                query = f"SELECT {", ".join(columns)} FROM {table} {where_clause}"
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

def get_job_posting_progress(login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return []

        cursor = conn.cursor()

        # 공고관리 테이블
        table_name = "tb_job_postings"
        where_clause = "WHERE login_email = %s"
        where_values = (login_email,)

        # 필수 필드명 가져오기
        essential_columns = [
            "company_name", "position", "openings", "deadline", "requirements", 
            "main_duties", "motivation", "submission", "contact", "company_website"
        ]

        # 데이터 가져오기
        query = f"SELECT {", ".join(essential_columns)} FROM {table_name} {where_clause}"
        cursor.execute(query, where_values)
        results = cursor.fetchall()

        filled_count = 0
        total_count = len(essential_columns)
        empty_fields = []

        for row in results:
            for col in essential_columns:
                if row[col] is not None and str(row[col]).strip() != "":
                    filled_count += 1
                else:
                    empty_fields.append(map_column_to_field("tb_job_postings", col))

        progress = round((filled_count / total_count) * 100, 2) if total_count else 0
        empty_fields_str = ", ".join(empty_fields) if empty_fields else "없음"
        return [{"공고관리 탭": "공고관리", "진행률 (%)": progress, "비어있는 필드": empty_fields_str}]
    except Exception as e:
        st.error(f"공고관리 진행률 계산 오류: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def get_additional_job_posting_progress(login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return []

        cursor = conn.cursor()

        # 추가 채용공고 필드
        additional_columns = [
            "company_intro", "talent", "preferences", 
            "company_culture", "faq", "additional_info"
        ]

        # 데이터 가져오기
        query = f"SELECT {", ".join(additional_columns)} FROM tb_job_postings WHERE login_email = %s"
        cursor.execute(query, (login_email,))
        results = cursor.fetchall()

        additional_progress = []

        for row in results:
            for col in additional_columns:
                status = "✅ 입력됨" if row[col] and str(row[col]).strip() != "" else "❌ 입력 안 됨"
                additional_progress.append({"필드명": map_column_to_field("tb_job_postings", col), "입력 상태": status})

        return additional_progress
    except Exception as e:
        st.error(f"추가 채용공고 진행률 계산 오류: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def show_tag_box(empty_fields, title):
    st.markdown(f"### {title}")
    if empty_fields:
        styled_fields = [f'<span style="background-color:#4285F4; color:white; padding:5px; margin:2px; border-radius:5px;">{field}</span>' for field in empty_fields]
        st.markdown(" ".join(styled_fields), unsafe_allow_html=True)
    else:
        st.markdown("모든 필드가 입력되었습니다.")

# 진행률 데이터 표시 함수
def display_progress_section(title, progress_data):
    if progress_data:
        st.markdown(f"##### {title}")
        df = pd.DataFrame(progress_data)
        st.dataframe(df)
    else:
        st.markdown(f"##### {title} 진행률 데이터를 가져올 수 없습니다.")

def show_dashboard_page():
    st.title("대시보드")
    if st.user.name:
        st.write(f"환영합니다, {st.user.name}님!")
        login_email = st.user.email
    else:
        st.write("환영합니다, 사용자님!")

    if not login_email:
        st.warning("로그인이 필요합니다.")
        return

    # 컬럼 구조 설정
    col1, _, col2 = st.columns([1, 0.1, 1])

    # 이력관리 진행률 표시
    with col1:
        st.markdown("### 이력관리 진행사항")
        tab_progress = get_resume_progress(login_email)
        if tab_progress:
            for item in tab_progress:
                tab_name = item['탭 이름']
                progress = item['진행률 (%)']
                empty_fields = item['비어있는 필드'].split(', ')
                st.markdown(f"#### {tab_name}")
                show_gauge_chart(progress, tab_name)
                show_tag_box(empty_fields, f"{tab_name} 비어있는 필드")
        else:
            st.markdown("### 이력관리 진행률 데이터를 가져올 수 없습니다.")

    # 공고관리 진행률 표시
    with col2:
        st.markdown("### 공고관리 진행사항")
        job_progress = get_job_posting_progress(login_email)
        add_job_progress = get_additional_job_posting_progress(login_email)

        if job_progress:
            st.markdown("#### 필수 채용공고 진행률")
            progress_value = job_progress[0]["진행률 (%)"]
            empty_fields = job_progress[0]["비어있는 필드"].split(", ")
            show_gauge_chart(progress_value, "필수 채용공고")
            show_tag_box(empty_fields, "비어있는 필드")
        else:
            st.markdown("필수 채용공고 진행률 데이터를 가져올 수 없습니다.")

        if add_job_progress:
            st.markdown("#### 추가 채용공고 진행률")
            filled_count = sum(1 for field in add_job_progress if "✅" in field["입력 상태"])
            total_count = len(add_job_progress)
            progress_value = (filled_count / total_count) * 100
            show_gauge_chart(progress_value, "추가 채용공고")
            empty_fields = [field["필드명"] for field in add_job_progress if "❌" in field["입력 상태"]]
            show_tag_box(empty_fields, "추가 채용공고 비어있는 필드")
        else:
            st.markdown("### 추가 채용공고 진행률 데이터를 가져올 수 없습니다.")

# 대시보드 페이지 표시
if __name__ == "__main__":
    show_dashboard_page()