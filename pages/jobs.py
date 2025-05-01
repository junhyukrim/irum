import streamlit as st
import pymysql

def connect_to_db():
    try:
        connection = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            cursorclass=pymysql.cursors.DictCursor
        )
        
        return connection
    except Exception as e:
        
        return None

def show_success_message():
    st.markdown("""
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #d8e6fd;">
            성공적으로 저장되었습니다!
        </div>
    """, unsafe_allow_html=True)

def load_jobs_info(login_email):
    # 데이터베이스에서 불러오기
    try:
        conn = connect_to_db()
        if conn is None:
            return []
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, company_name FROM tb_job_postings WHERE login_email = %s", (login_email,))
            return cursor.fetchall()
    except Exception as e:
        st.error(f"불러오기 오류: {str(e)}")
        return []
    
def load_single_job(job_id):
    try:
        conn = connect_to_db()
        if conn is None:
            return None
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tb_job_postings WHERE id = %s", (job_id,))
            return cursor.fetchone()
    except Exception as e:
        st.error(f"불러오기 오류: {str(e)}")
        return None
    
def save_job(login_email, job_data, job_id=None):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        with conn.cursor() as cursor:
            if job_id:
                update_query = """
                    UPDATE tb_job_postings SET
                        company_name = %s, position_name = %s, position_count = %s, requirements = %s,
                        main_tasks = %s, submission = %s, contact = %s, website = %s, company_intro = %s,
                        talent = %s, preferences = %s, work_environment = %s, faq = %s, additional_info = %s,
                        motivation = %s
                    WHERE id = %s
                """
                cursor.execute(update_query, (*job_data.values(), job_id))
            else:
                insert_query = """
                    INSERT INTO tb_job_postings (
                        login_email, company_name, position_name, position_count, requirements, main_tasks,
                        submission, contact, website, company_intro, talent, preferences, work_environment,
                        faq, additional_info, motivation
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (login_email, *job_data.values()))
            conn.commit()
            return True
    except Exception as e:
        st.error(f"저장 오류: {str(e)}")
        return False
    
def delete_job(job_id):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tb_job_postings WHERE id = %s", (job_id,))
            conn.commit()
            return True
    except Exception as e:
        st.error(f"삭제 오류: {str(e)}")
        return False

def show_jobs_page():
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

            /* 폼 스타일링 */
            .stTextInput > label, 
            .stSelectbox > label, 
            .stDateInput > label,
            .stTextArea > label {
                font-size: 14px !important;
                font-weight: 500 !important;
            }
            
            /* 입력란 폰트 크기 */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > div,
            .stDateInput > div > div > input,
            .stTextArea > div > div > textarea,
            div[data-baseweb="input"] > input,
            div[data-baseweb="textarea"] > textarea,
            div[data-baseweb="select"] > div {
                font-size: 14px !important;
            }
            
            /* 입력란 배경색 조정 */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > div,
            .stDateInput > div > div > input,
            div[data-baseweb="input"] > input,
            div[data-baseweb="input"],
            div[data-baseweb="base-input"] {
                background-color: #F8F9FA !important;
            }

            /* 입력란 호버/포커스 시 배경색 */
            .stTextInput > div > div > input:hover,
            .stSelectbox > div > div > div:hover,
            .stDateInput > div > div > input:hover,
            div[data-baseweb="input"] > input:hover,
            div[data-baseweb="input"]:hover,
            div[data-baseweb="base-input"]:hover,
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > div:focus,
            .stDateInput > div > div > input:focus,
            div[data-baseweb="input"] > input:focus,
            div[data-baseweb="input"]:focus-within,
            div[data-baseweb="base-input"]:focus-within {
                background-color: #FFFFFF !important;
            }
            
            /* 버튼 스타일링 */
            div.stButton > button {
                width: 100% !important;
                height: 42px !important;
                margin: 0 !important;
                padding: 0.5rem !important;
                background-color: #4285F4 !important;
                color: white !important;
                font-size: 14px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                border-radius: 4px !important;
                transition: all 0.2s ease !important;
                border: 1px solid #4285F4 !important;
            }

            div.stButton > button:hover {
                background-color: #1967D2 !important;
                border-color: #1967D2 !important;
            }

            div.stButton > button:active {
                background-color: #1557B0 !important;
                border-color: #1557B0 !important;
            }

            /* 사이드바 스타일 */
            section[data-testid="stSidebar"] {
                background-color: #4285F4;
                width: 250px !important;
            }
            
            /* 이미지 컨테이너 스타일 */
            div.element-container:has(img) {
                padding: 0 !important;
                display: flex !important;
                justify-content: center !important;
            }
            
            img {
                width: 150px;
                margin-bottom: 3rem;
            }
            
            /* 사이드바 버튼 스타일 */
            section[data-testid="stSidebar"] .stButton > button {
                width: calc(100% + 4rem) !important;
                margin-left: -2rem !important;
                background-color: transparent !important;
                border: none !important;
                color: white !important;
                font-size: 1.1rem !important;
                padding: 0.5rem 2rem !important;
                display: flex !important;
                align-items: center !important;
                justify-content: flex-start !important;
                transition: all 0.2s ease !important;
                border-radius: 0 !important;
            }

            section[data-testid="stSidebar"] .stButton > button:hover {
                font-size: 2rem !important;
                font-weight: bold !important;
                background-color: rgba(255, 255, 255, 0.1) !important;
            }

            section[data-testid="stSidebar"] .stButton > button[aria-pressed="true"] {
                background-color: #0051FF !important;
                font-size: 2rem !important;
                font-weight: bold !important;
            }
            
            /* 공고관리 저장 버튼만 스타일링 (key 기반 선택) */
            button[aria-label="save_jobs_button"] {
                width: 100% !important;
                height: 42px !important;
                margin: 0 !important;
                padding: 0.5rem !important;
                background-color: white !important;
                color: #4285F4 !important;
                font-size: 14px !important;
                font-weight: bold !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                border-radius: 4px !important;
                border: 2px solid #4285F4 !important;
                transition: all 0.2s ease !important;
            }

            button[aria-label="save_jobs_button"]:hover {
                background-color: #e8f0fe !important;
            }

            /* 모바일 화면 대응 */
            @media (max-width: 768px) {
                div[data-testid="stMainBlockContainer"] {
                    max-width: 100% !important;
                }
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('<h3 class="main-header">공고관리</h3>', unsafe_allow_html=True)
    
    if 'user_email' not in st.session_state:
        st.warning("로그인이 필요합니다.")
        return
    
    login_email = st.session_state.user_email
    jobs = load_jobs_info(login_email)
    job_titles = [job['company_name'] for job in jobs]
    job_ids = {job['company_name']: job['id'] for job in jobs}

    selected_job = st.selectbox("저장된 공고 선택", ["새 공고 추가"] + job_titles)
    job_data = {key: "" for key in [
        'company_name', 'position_name', 'position_count', 'requirements', 'main_tasks', 'submission',
        'contact', 'website', 'company_intro', 'talent', 'preferences', 'work_environment', 'faq',
        'additional_info', 'motivation']}
    job_id = None

    if selected_job != "새 공고 추가":
        job_id = job_ids[selected_job]
        db_data = load_single_job(job_id)
        if db_data:
            job_data.update(db_data)

    # 필수 채용공고 양식
    st.markdown('<h5 class="section-header">필수 채용공고 양식</h5>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 3, 1])
    with col1:
        company_name = st.text_input("기업명")
    with col2:
        position_name = st.text_input("직무명")
    with col3:
        position_count = st.number_input("채용인원", min_value=1, value=1)
    
    # 자격요건 (여러 줄 입력 가능)
    requirements = st.text_area("자격요건", height=150,
                              help="• 항목별로 새로운 줄에 입력해주세요.")
    
    # 주요업무 (여러 줄 입력 가능)
    main_tasks = st.text_area("주요업무", height=150,
                             help="• 항목별로 새로운 줄에 입력해주세요.")
    
    # 지원동기 (여러 줄 입력 가능)
    job_data['motivation'] = st.text_area("지원동기", height=150, value=job_data['motivation'])

    # 제출서류 & 지원방법 (여러 줄 입력 가능)
    submission = st.text_area("제출서류 & 지원방법", height=150,
                            help="• 제출서류와 지원방법을 상세히 기재해주세요.")
    
    # 문의처와 홈페이지
    col4, col5 = st.columns(2)
    with col4:
        contact = st.text_input("문의처(이메일/연락처)")
    with col5:
        website = st.text_input("홈페이지 주소")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 추가적 채용공고 양식
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
    work_environment = st.text_area("근무환경", height=100,
                                  help="• 근무지, 근무시간, 복리후생 등을 상세히 기재해주세요.")
    
    # FAQ (여러 줄 입력 가능)
    faq = st.text_area("FAQ", height=100,
                      help="• 자주 묻는 질문과 답변을 입력해주세요.\n• Q: 질문\n  A: 답변 형식으로 작성해주세요.")
    
    # 기타 안내사항 (여러 줄 입력 가능)
    additional_info = st.text_area("기타 안내사항", height=100,
                                 help="• 추가로 안내할 사항이 있다면 기재해주세요.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 저장 버튼
    st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
    cols = st.columns(8)
    for i in range(7):  # 처음 7개 컬럼은 빈 공간
        cols[i].empty()
    with cols[7]:  # 마지막 컬럼에 버튼 배치
        if st.button("저장", key="save_jobs_button", use_container_width=True):
            if save_job(login_email, job_data, job_id):
                show_success_message()
                st.rerun()
            
    if job_id:
        if st.button("공고 삭제", key="delete_jobs_button"):
            if delete_job(job_id):
                st.success("공고가 삭제되었습니다.")
                st.rerun()
