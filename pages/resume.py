import streamlit as st

def show_resume_page():
    st.markdown('<h3 class="main-header">이력관리</h3>', unsafe_allow_html=True)
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["개인정보", "학력", "역량", "경력", "수상", "기타활동", "자기소개"])
    
    # 개인정보 탭
    with tab1:
        st.markdown(
            """
            <style>
            /* 폼 스타일링 */
            .stTextInput > label, .stSelectbox > label, .stDateInput > label {
                font-size: 1rem !important;
                font-weight: 500 !important;
            }
            
            /* 입력란 배경색 조정 */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > div,
            .stDateInput > div > div > input,
            div[data-baseweb="input"] > input,
            div[data-baseweb="input"],
            div[data-baseweb="base-input"],
            #tabs-bui222-tabpanel-0 > div > div > div > div:nth-child(4) > div:nth-child(2) > div > div > div > div > div:nth-child(2) > div > div > div > div > div > div > div > div {
                background-color: #F8F9FA !important;
            }

            /* 입력란 호버/포커스 시 배경색 */
            .stTextInput > div > div > input:hover,
            .stSelectbox > div > div > div:hover,
            .stDateInput > div > div > input:hover,
            div[data-baseweb="input"] > input:hover,
            div[data-baseweb="input"]:hover,
            div[data-baseweb="base-input"]:hover,
            #tabs-bui222-tabpanel-0 > div > div > div > div:nth-child(4) > div:nth-child(2) > div > div > div > div > div:nth-child(2) > div > div > div > div > div > div > div > div:hover,
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > div:focus,
            .stDateInput > div > div > input:focus,
            div[data-baseweb="input"] > input:focus,
            div[data-baseweb="input"]:focus-within,
            div[data-baseweb="base-input"]:focus-within,
            #tabs-bui222-tabpanel-0 > div > div > div > div:nth-child(4) > div:nth-child(2) > div > div > div > div > div:nth-child(2) > div > div > div > div > div > div > div > div:focus-within {
                background-color: #FFFFFF !important;
            }
            
            /* 개인정보 탭 내의 버튼 스타일링 */
            [data-testid="stHorizontalBlock"] .stButton > button {
                background-color: #0051FF !important;
                color: white !important;
                padding: 0.5rem 2rem !important;
                border-radius: 4px !important;
                width: auto !important;
                margin: 0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # 인적사항 섹션
        st.markdown('<h5>인적사항</h5>', unsafe_allow_html=True)
        
        # 한글/영문 이름
        name_col1, name_col2 = st.columns(2)
        with name_col1:
            name_kr = st.text_input("한글 이름", key="name_kr")
        with name_col2:
            name_en = st.text_input("영문 이름", key="name_en")
        
        # 국적/성별+생년월일
        nat_col1, nat_col2 = st.columns(2)
        with nat_col1:
            nationality = st.text_input("국적", value="대한민국", key="nationality")
        with nat_col2:
            gender_birth_col1, gender_birth_col2 = st.columns(2)
            with gender_birth_col1:
                gender = st.selectbox("성별", ["선택", "남성", "여성"], key="gender")
            with gender_birth_col2:
                birth_date = st.date_input("생년월일", key="birth_date")
        
        # 주소 (전체 너비)
        address = st.text_input("주소", key="address")
        
        # 이메일/연락처
        contact_col1, contact_col2 = st.columns(2)
        with contact_col1:
            email = st.text_input("이메일", key="email")
        with contact_col2:
            phone = st.text_input("연락처", key="phone")
        
        # 사진 링크
        photo_url = st.text_input("사진 링크", key="photo_url")
        
        # 구분선 추가
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        
        # 병역 및 보훈 섹션
        st.markdown('<h5>병역 및 보훈</h5>', unsafe_allow_html=True)
        
        # 병역/군별/계급/보훈대상 (4등분)
        mil_cols = st.columns(4)
        with mil_cols[0]:
            military_service = st.selectbox("병역", ["선택", "군필", "미필", "면제", "해당없음"], key="military_service")
        with mil_cols[1]:
            military_branch = st.selectbox("군별", ["선택", "육군", "해군", "공군", "해병대", "의경", "공익", "기타"], key="military_branch")
        with mil_cols[2]:
            military_rank = st.selectbox("계급", ["선택", "이병", "일병", "상병", "병장", "하사", "중사", "상사", "원사", "준위", "소위", "중위", "대위", "소령", "중령", "대령"], key="military_rank")
        with mil_cols[3]:
            veteran_status = st.selectbox("보훈대상", ["선택", "대상", "비대상"], key="veteran_status")
        
        # 복무 시작일/종료일/전역유형 (1:1:2 비율)
        service_cols = st.columns([1, 1, 2])
        with service_cols[0]:
            service_start = st.date_input("복무 시작일", key="service_start")
        with service_cols[1]:
            service_end = st.date_input("복무 종료일", key="service_end")
        with service_cols[2]:
            discharge_type = st.selectbox("전역 유형", ["선택", "만기전역", "의가사제대", "의병전역", "근무부적합", "기타"], key="discharge_type")
        
        # 구분선 추가
        st.markdown("<div style='margin: 5rem 0;'></div>", unsafe_allow_html=True)

        # 저장 버튼
        col1, col2 = st.columns([2, 5])
        with col1:
            if st.button("저장", use_container_width=True):
                # TODO: 저장 로직 구현
                st.success("저장되었습니다!")

    # 학력 탭
    with tab2:
        st.markdown('<h5 class="main-header">학력</h5>', unsafe_allow_html=True)
        
        # 학력 카운터 초기화
        if 'education_count' not in st.session_state:
            st.session_state.education_count = 1
        
        # 전공 카운터 초기화
        if 'major_counts' not in st.session_state:
            st.session_state.major_counts = {0: 1}

        # 학력 데이터 초기화
        if 'education_data' not in st.session_state:
            st.session_state.education_data = list(range(st.session_state.education_count))

        # 각 학력 정보 입력 폼
        for idx, i in enumerate(st.session_state.education_data):
            if idx > 0:
                st.markdown("<hr>", unsafe_allow_html=True)
            
            # 입학년월/졸업년월
            col1, col2 = st.columns(2)
            with col1:
                st.date_input("입학년월", key=f"admission_date_{i}")
            with col2:
                st.date_input("졸업년월", key=f"graduation_date_{i}")
            
            # 교육기관/학부 또는 분야
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("교육기관", key=f"institution_{i}")
            with col2:
                st.text_input("학부 또는 분야", key=f"department_{i}")
            
            # 전공 정보 (여러 개 추가 가능)
            if i not in st.session_state.major_counts:
                st.session_state.major_counts[i] = 1

            for j in range(st.session_state.major_counts[i]):
                if j > 0:
                    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
                
                # 학과, 전공, 세부내용
                st.text_input("학과, 전공, 세부내용", key=f"major_{i}_{j}")
                
                # 학위/성적
                col1, col2 = st.columns(2)
                with col1:
                    st.selectbox("학위", ["선택", "고등학교 졸업", "전문학사", "학사", "석사", "박사"], key=f"degree_{i}_{j}")
                with col2:
                    st.text_input("성적", placeholder="예: 4.0/4.3", key=f"gpa_{i}_{j}")

            # 전공 추가 버튼
            col1, col2 = st.columns([2, 5])
            with col1:
                if st.button("전공 추가", key=f"add_major_{i}", use_container_width=True):
                    st.session_state.major_counts[i] += 1
                    st.rerun()
            
            # 비고
            st.text_area("비고", key=f"notes_{i}", height=100)

            # 학력 삭제 버튼
            col1, col2 = st.columns([2, 5])
            with col1:
                if st.button("학력 삭제", key=f"delete_education_{i}", use_container_width=True):
                    st.session_state.education_data.remove(i)
                    if len(st.session_state.education_data) == 0:
                        st.session_state.education_count = 1
                        st.session_state.education_data = [0]
                        st.session_state.major_counts = {0: 1}
                    st.rerun()

        # 버튼들 (학력추가, 저장)
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 3])
        with col1:
            if st.button("학력 추가", use_container_width=True):
                new_idx = max(st.session_state.education_data) + 1 if st.session_state.education_data else 0
                st.session_state.education_data.append(new_idx)
                st.session_state.major_counts[new_idx] = 1
                st.session_state.education_count += 1
                st.rerun()
        with col2:
            if st.button("저장", key="save_education", use_container_width=True):
                st.success("저장되었습니다!")

    # 역량 탭
    with tab3:
        st.markdown('<h5 class="main-header">역량</h5>', unsafe_allow_html=True)
        
        # 역량 카운터 초기화
        if 'skill_count' not in st.session_state:
            st.session_state.skill_count = 1
        
        # 자격증, 교육 카운터 초기화
        if 'cert_counts' not in st.session_state:
            st.session_state.cert_counts = {0: 1}
        if 'edu_counts' not in st.session_state:
            st.session_state.edu_counts = {0: 1}

        # 역량 데이터 초기화
        if 'skill_data' not in st.session_state:
            st.session_state.skill_data = list(range(st.session_state.skill_count))

        # 각 역량 정보 입력 폼
        for idx, i in enumerate(st.session_state.skill_data):
            if idx > 0:
                st.markdown("<hr>", unsafe_allow_html=True)
            
            # 기술 및 역량
            st.text_area("기술 및 역량", height=100, key=f"skill_desc_{i}")
            
            # 자격증 섹션
            if i not in st.session_state.cert_counts:
                st.session_state.cert_counts[i] = 1

            for j in range(st.session_state.cert_counts[i]):
                if j > 0:
                    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("자격증", key=f"cert_name_{i}_{j}")
                with col2:
                    st.date_input("자격증 취득년월", key=f"cert_date_{i}_{j}")
                st.text_input("자격증 발급기관", key=f"cert_org_{i}_{j}")

            col1, col2 = st.columns([2, 5])
            with col1:
                if st.button("자격증 추가", key=f"add_cert_{i}", use_container_width=True):
                    st.session_state.cert_counts[i] += 1
                    st.rerun()

            st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

            # 교육 섹션
            if i not in st.session_state.edu_counts:
                st.session_state.edu_counts[i] = 1

            for j in range(st.session_state.edu_counts[i]):
                if j > 0:
                    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
                st.text_area("교육, 연수, 유학 등", height=100, key=f"education_{i}_{j}")

            col1, col2 = st.columns([2, 5])
            with col1:
                if st.button("교육, 연수, 유학 추가", key=f"add_edu_{i}", use_container_width=True):
                    st.session_state.edu_counts[i] += 1
                    st.rerun()

            st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
            
            # 비고
            st.text_area("비고", height=100, key=f"skill_notes_{i}")

            # 역량 삭제 버튼
            col1, col2 = st.columns([2, 5])
            with col1:
                if st.button("역량 삭제", key=f"delete_skill_{i}", use_container_width=True):
                    st.session_state.skill_data.remove(i)
                    if len(st.session_state.skill_data) == 0:
                        st.session_state.skill_count = 1
                        st.session_state.skill_data = [0]
                        st.session_state.cert_counts = {0: 1}
                        st.session_state.edu_counts = {0: 1}
                    st.rerun()

        # 버튼들 (역량추가, 저장)
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 3])
        with col1:
            if st.button("역량 추가", use_container_width=True):
                new_idx = max(st.session_state.skill_data) + 1 if st.session_state.skill_data else 0
                st.session_state.skill_data.append(new_idx)
                st.session_state.cert_counts[new_idx] = 1
                st.session_state.edu_counts[new_idx] = 1
                st.session_state.skill_count += 1
                st.rerun()
        with col2:
            if st.button("저장", key="save_skill", use_container_width=True):
                st.success("저장되었습니다!")

    # 경력 탭
    with tab4:
        st.header("경력")
        st.write("여기에 경력 정보가 들어갑니다.")
    
    # 수상 탭
    with tab5:
        st.header("수상")
        st.write("여기에 수상 정보가 들어갑니다.")
    
    # 기타활동 탭
    with tab6:
        st.header("기타활동")
        st.write("여기에 기타활동 정보가 들어갑니다.")
    
    # 자기소개 탭
    with tab7:
        st.header("자기소개")
        st.write("여기에 자기소개 내용이 들어갑니다.") 