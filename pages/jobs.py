import streamlit as st
import pymysql
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

def show_success_message(message, message_type="success"):
    # 메시지 유형별 스타일 설정
    styles = {
        "success": {"color": "#155724", "background": "#d4edda"},
        "warning": {"color": "#856404", "background": "#fff3cd"},
        "error": {"color": "#721c24", "background": "#f8d7da"},
        "info": {"color": "#0c5460", "background": "#d1ecf1"},
    }
    
    # 메시지 유형이 유효하지 않으면 기본값으로 설정
    if message_type not in styles:
        message_type = "success"

    # 스타일 가져오기
    style = styles[message_type]

    # HTML로 메시지 표시
    st.markdown(f"""
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: {style['background']}; color: {style['color']};">
            <span style="font-size: 1.2rem;">{style['icon']}</span> {message}
        </div>
    """, unsafe_allow_html=True)

def load_jobs_info(login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return [], "데이터베이스에 접근할 수 없습니다. 관리자에게 문의해주세요."
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, company_name FROM tb_job_postings WHERE login_email = %s", (login_email,))
            result = cursor.fetchall()

            if result:
                return result, f"{login_email}님의 공고 목록을 불러왔습니다."
            else:
                return [], "저장된 공고가 없습니다. 새로운 공고를 추가해보세요."
        
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return [], f"데이터베이스 접근 중 오류가 발생했습니다: {str(e)}"
    
def load_single_job(job_id):
    try:
        conn = connect_to_db()
        if conn is None:
            return None,  "데이터베이스에 접근할 수 없습니다. 관리자에게 문의해주세요."
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tb_job_postings WHERE id = %s ", (job_id,))
            result = cursor.fetchone()
            
            if result:
                return result, f"공고 ID {job_id}의 정보를 불러왔습니다."
            else:
                return {}, "해당 공고를 찾을 수 없습니다. 공고 ID를 확인해주세요."
        
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return None, f"데이터베이스 접근 중 오류가 발생했습니다: {str(e)}"
    
def save_job(login_email, job_data, job_id=None):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            if job_id:
                cursor.execute("SELECT * FROM tb_job_postings WHERE id = %s", (job_id,))
                result = cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM tb_job_postings WHERE login_email = %s AND company_name = %s", 
                            (login_email, job_data['company_name']))
                result = cursor.fetchone()
            
            if result:
                update_query = """
                    UPDATE tb_job_postings SET
                        company_name = %s, position = %s, openings = %s, deadline = %s, requirements = %s,
                        main_duties = %s, submission = %s, contact = %s, company_website = %s, company_intro = %s,
                        talent = %s, preferences = %s, company_culture = %s, faq = %s, additional_info = %s,
                        motivation = %s
                    WHERE id = %s
                """
                cursor.execute(update_query, (
                    job_data['company_name'], job_data['position'], job_data['openings'], job_data['deadline'],
                    job_data['requirements'], job_data['main_duties'], job_data['submission'], job_data['contact'],
                    job_data['company_website'], job_data['company_intro'], job_data['talent'], job_data['preferences'],
                    job_data['company_culture'], job_data['faq'], job_data['additional_info'], job_data['motivation'],
                    job_id
                ))
            else:
                insert_query = """
                    INSERT INTO tb_job_postings (
                        login_email, company_name, position, openings, deadline, requirements, main_duties,
                        submission, contact, company_website, company_intro, talent, preferences, company_culture,
                        faq, additional_info, motivation, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(insert_query, (
                    login_email, job_data['company_name'], job_data['position'], job_data['openings'], 
                    job_data['deadline'], job_data['requirements'], job_data['main_duties'], job_data['submission'],
                    job_data['contact'], job_data['company_website'], job_data['company_intro'], job_data['talent'],
                    job_data['preferences'], job_data['company_culture'], job_data['faq'], 
                    job_data['additional_info'], job_data['motivation'], now
                ))
            conn.commit()
            return True
        except Exception as e:
                st.error(f"쿼리 실행 중 오류: {str(e)}")
                conn.rollback()
                return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류: {str(e)}")
        return False
    
def delete_job(job_id, login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id FROM tb_job_postings 
                WHERE id = %s AND login_email = %s
            """, (job_id, login_email))

            if not cursor.fetchone():
                st.warning("해당 공고를 찾을 수 없거나 삭제 권한이 없습니다.")
                return False
            
            cursor.execute("DELETE FROM tb_job_postings WHERE id = %s", (job_id,))
            conn.commit()
            st.success("공고가 성공적으로 삭제되었습니다.")
            return True
        except Exception as e:
                st.error(f"삭제 중 오류: {str(e)}")
                conn.rollback()
                return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류: {str(e)}")
        return False

def format_bullet_text(raw_text):
    lines = raw_text.strip().splitlines()
    return "\n".join(
        f"- {line.strip()}" if not line.strip().startswith("-") else line.strip()
        for line in lines if line.strip()
    )

def show_jobs_page():
    # 세션 상태 초기화
    if 'save_success' not in st.session_state:
        st.session_state['save_success'] = False
    
    st.markdown(
        """
        <style>
        /* 메인 컨테이너 width 조정 */
            div[data-testid="stMainBlockContainer"] {
                max-width: 1500px !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                margin: 0 auto !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('<h3 class="main-header">공고관리</h3>', unsafe_allow_html=True)
    
    if 'user_email' not in st.session_state:
        st.warning("로그인이 필요합니다.")
        return
    
    # 사용자 이메일로 저장된 공고 목록 불러오기
    login_email = st.session_state.user_email

    jobs, message = load_jobs_info(login_email)
    if not jobs:
        st.warning(message)
    job_titles = ["새 공고 추가"] + [job['company_name'] for job in jobs]
    job_ids = {job['company_name']: job['id'] for job in jobs}

    # 공고 선택 드롭다운
    selected_job = st.selectbox("저장된 공고 선택", job_titles)

    # 공고 id  초기화
    job_id = None

    # 공고를 선택할 때 동작
    if selected_job == "새 공고 추가":
        # 새 공고를 선택하면 필드 초기화
        st.session_state['job_data'] = {
        'company_name': "", 'position': "", 'openings': 1, 'deadline': str(datetime.now().date()), 
        'requirements': "", 'main_duties': "", 'submission': "", 'contact': "", 'company_website': "", 
        'company_intro': "", 'talent': "", 'preferences': "", 'company_culture': "", 'faq': "", 
        'additional_info': "", 'motivation': ""
    }
        st.info("새 공고 추가 모드입니다.")
    else:
        # 기존 공고를 선택하면 DB에서 데이터 불러오기
        job_id = job_ids.get(selected_job, None)
        if job_id:
            db_data, msg = load_single_job(job_id)
            if db_data:
                # 불러온 데이터를 세션 상태에 저장
                st.session_state['job_data'] = db_data
                st.success(f"{selected_job} 공고 데이터를 불러왔습니다.")
            else:
                st.warning(msg)

    # 필수 채용공고 양식
    st.markdown('<h5 class="section-header">필수 채용공고 양식</h5>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 3, 1])
    with col1:
        company_name = st.text_input("기업명")
    with col2:
        position = st.text_input("직무명")
    with col3:
        openings = st.number_input("채용인원", min_value=1, value=1)

    # 제출기한
    deadline = st.date_input("제출기한", value=datetime.now().date())

    # 자격요건 (여러 줄 입력 가능)
    requirements = st.text_area("자격요건", height=150,
                              help="• 각 항목을 줄바꿈하여 입력하세요. 자동으로 '-' 기호가 붙습니다.")
    
    if requirements:
        formatted_requirements = format_bullet_text(requirements)
        st.markdown(f"#### 가공된 자격요건\n{formatted_requirements}")

    # 주요업무 (여러 줄 입력 가능)
    main_duties = st.text_area("주요업무", height=150,
                             help="• 각 항목을 줄바꿈하여 입력하세요. 자동으로 '-' 기호가 붙습니다.")
    
    if main_duties:
        formatted_main_duties = format_bullet_text(main_duties)
        st.markdown(f"#### 가공된 주요업무\n{formatted_main_duties}")
    
    # 지원동기 (여러 줄 입력 가능)
    motivation = st.text_area("지원동기", height=150, value=job_data['motivation'],
                                          help="• 회사에 지원하는 동기를 기재해주세요.")

    # 제출서류 & 지원방법 (여러 줄 입력 가능)
    submission = st.text_area("제출서류 & 지원방법", height=150,
                            help="• 제출서류와 지원방법을 상세히 기재해주세요.")
    
    # 문의처와 홈페이지
    col4, col5 = st.columns(2)
    with col4:
        contact = st.text_input("문의처(이메일/연락처)", value=job_data["contact"])
    with col5:
        company_website = st.text_input("홈페이지 주소", value=job_data["company_website"])
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 추가 채용공고 양식
    st.markdown('<h5 class="section-header">추가 채용공고 양식</h5>', unsafe_allow_html=True)
    
    # 기업소개 (여러 줄 입력 가능)
    company_intro = st.text_area("기업소개", height=100,
                                help="• 기업의 비전, 미션, 주요 사업 영역 등을 소개해주세요.")
    
    # 인재상 (여러 줄 입력 가능)
    talent = st.text_area("인재상", height=100,
                         help="• 귀사가 추구하는 인재상을 기술해주세요.")
    
    # 우대조건 (여러 줄 입력 가능)
    preferences = st.text_area("우대조건", height=100,
                             help="• 우대하는 자격요건이나 경험을 기재해주세요.")
    
    # 근무환경 (여러 줄 입력 가능)
    company_culture = st.text_area("근무환경", height=100,
                                  help="• 근무지, 근무시간, 복리후생 등을 상세히 기재해주세요.")
    
    # FAQ (여러 줄 입력 가능)
    faq = st.text_area("FAQ", height=100,
                      help="• 자주 묻는 질문과 답변을 입력해주세요.\n• Q: 질문\n  A: 답변 형식으로 작성해주세요.")
    
    # 기타 안내사항 (여러 줄 입력 가능)
    additional_info = st.text_area("기타 안내사항", height=100,
                                 help="• 추가로 안내할 사항이 있다면 기재해주세요.")
    
    # 입력값을 job_data에 다시 저장
    job_data["company_name"] = company_name
    job_data["position"] = position
    job_data["openings"] = openings
    job_data["deadline"] = str(deadline)
    job_data["requirements"] = format_bullet_text(requirements)
    job_data["main_duties"] = format_bullet_text(main_duties)
    job_data["motivation"] = motivation
    job_data["submission"] = submission
    job_data["contact"] = contact
    job_data["company_website"] = company_website
    job_data["company_intro"] = company_intro
    job_data["talent"] = talent
    job_data["preferences"] = preferences
    job_data["company_culture"] = company_culture
    job_data["faq"] = faq
    job_data["additional_info"] = additional_info
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
        div[data-testid="stHorizontalBlock"] div.stButton > button:not([kind="primary"]) {
        background-color: white !important;
        color: #4285F4 !important;
        border: 1px solid #4285F4 !important;
        border-radius: 4px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        height: 42px !important;
        width: 150px !important;
        transition: background-color 0.2s ease !important;
    }
    div[data-testid="stHorizontalBlock"] div.stButton > button:not([kind="primary"]):hover {
        background-color: #e8f0fe !important;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(8)
    for i in range(7): 
        cols[i].empty()

    with cols[7]:
        if st.button("저장"):
            job_data.update({
                "company_name": company_name,
                "position": position,
                "openings": openings,
                "deadline": str(deadline),
                "requirements": requirements
            })

            if save_job(login_email, job_data, job_id):
                st.session_state['save_success'] = True
                st.success("성공적으로 저장되었습니다!")
            else:
                st.session_state['save_success'] = False
                st.error("저장에 실패했습니다.")

    if job_id is not None and st.button("삭제"):
        if delete_job(job_id, login_email):
            st.session_state.save_success = True
            st.success("성공적으로 삭제되었습니다!")
        else:
            st.error("삭제에 실패했습니다.")

    if 'save_success' in st.session_state and st.session_state['save_success']:
        st.success("작업이 완료되었습니다!")
        st.session_state.save_success = False

show_jobs_page()