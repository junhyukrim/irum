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

def save_jobs_info(login_email, data):
    try:
        conn = connect_to_db()
        if conn is None:
            return False

        cursor = conn.cursor()
        try:
            # 현재 사용자의 기존 공고 ID 목록 조회
            cursor.execute(
                "SELECT id FROM tb_jobs WHERE login_email = %s",
                (login_email,)
            )
            existing_ids = {row['id'] for row in cursor.fetchall()}
            saved_ids = set()

            # 데이터 저장/수정
            for idx, job in data.items():
                if idx in existing_ids:
                    # 기존 공고 업데이트
                    update_query = """
                        UPDATE tb_jobs
                        SET
                            company_name = %s,
                            position_name = %s,
                            position_count = %s,
                            requirements = %s,
                            main_tasks = %s,
                            submission = %s,
                            contact = %s,
                            website = %s,
                            company_intro = %s,
                            talent = %s,
                            preferences = %s,
                            work_environment = %s,  
                            faq = %s,
                            additional_info = %s
                        WHERE id = %s
                    """
                    cursor.execute(update_query, (
                        job['company_name'], job['position_name'], job['position_count'], job['requirements'],  
                        job['main_tasks'], job['submission'], job['contact'], job['website'], job['company_intro'],
                        job['talent'], job['preferences'], job['work_environment'], job['faq'], job['additional_info'],
                        idx
                    ))
                    saved_ids.add(idx)
                else:
                    # 새로운 공고 저장
                    insert_query = """
                        INSERT INTO tb_jobs (
                            login_email, company_name, position_name, position_count, requirements, main_tasks, submission,
                            contact, website, company_intro, talent, preferences, work_environment, faq, additional_info
                        )
                    """
                    cursor.execute(insert_query, (
                        login_email, job['company_name'], job['position_name'], job['position_count'], job['requirements'],
                        job['main_tasks'], job['submission'], job['contact'], job['website'], job['company_intro'],
                        job['talent'], job['preferences'], job['work_environment'], job['faq'], job['additional_info']
                    ))
                    saved_ids.add(idx)
                    
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

def load_jobs_info():
    # 데이터베이스에서 불러오기
    return []

def delete_jobs_info(job_id):
    # 데이터베이스에서 삭제
    return True

def update_jobs_info(job_id, jobs_data):
    # 데이터베이스에서 업데이트
    return True

def show_jobs_list():
    # 저장된 공고 목록 표시
    st.markdown("""
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #d8e6fd;">
            저장된 공고 목록
        </div>
    """, unsafe_allow_html=True)

def show_jobs_page():
    st.markdown(
        """
        <style>
        div[data-testid="stMainBlockContainer"] {
            max-width: 1500px !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            margin: 0 auto !important;
        }
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
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 class="main-header">공고관리</h3>', unsafe_allow_html=True)
    
    # 드롭다운 추가
    st.selectbox(
        "저장된 공고",
        ["공고 1", "공고 2"],
        placeholder="저장된 공고를 선택하세요"
    )
    
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
    company_intro = st.text_area("기업소개", height=150,
                                help="• 기업의 비전, 미션, 주요 사업 영역 등을 소개해주세요.")
    
    # 인재상 (여러 줄 입력 가능)
    talent = st.text_area("인재상", height=100,
                         help="• 귀사가 추구하는 인재상을 기술해주세요.")
    
    # 우대조건 (여러 줄 입력 가능)
    preferences = st.text_area("우대조건", height=100,
                             help="• 우대하는 자격요건이나 경험을 기재해주세요.")
    
    # 근무환경 (여러 줄 입력 가능)
    work_environment = st.text_area("근무환경", height=150,
                                  help="• 근무지, 근무시간, 복리후생 등을 상세히 기재해주세요.")
    
    # FAQ (여러 줄 입력 가능)
    faq = st.text_area("FAQ", height=150,
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
            if 'user_email' not in st.session_state:
                    st.error("로그인이 필요합니다.")
                    return
            
            # 현재 입력된 모든 공고 데이터 수집
            jobs_data = {
                'company_name': company_name,
                'position_name': position_name,
                'position_count': position_count,
                'requirements': requirements,
                'main_tasks': main_tasks,
                'submission': submission,
                'contact': contact,
                'website': website,
                'company_intro': company_intro,
                'talent': talent,
                'preferences': preferences,
                'work_environment': work_environment,
                'faq': faq,
                'additional_info': additional_info
            }
            
            if save_jobs_info(st.session_state.user_email, jobs_data):
                show_success_message()
                st.rerun()
            else:
                st.error("저장 중 오류가 발생했습니다.")
