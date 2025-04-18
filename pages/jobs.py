import streamlit as st

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

        /* 섹션 스타일 */
        .section-header {
            margin-top: 2rem;
            margin-bottom: 1rem;
            font-weight: bold;
            color: #333;
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
    
    # 필수 채용공고 양식
    st.markdown('<h4 class="section-header">필수 채용공고 양식</h4>', unsafe_allow_html=True)
    
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
    st.markdown('<h4 class="section-header">추가적 채용공고 양식</h4>', unsafe_allow_html=True)
    
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
    
    # 저장 버튼
    col6, col7, col8 = st.columns([6, 1, 1, 1])
    with col7:
        if st.button("초기화"):
            st.rerun()
    with col8:
        if st.button("임시저장"):
            st.success("임시저장 되었습니다!")
    with col8:
        if st.button("저장"):
            st.success("저장되었습니다!") 