import streamlit as st
import streamlit.components.v1 as components

def login_screen():
    # Hide streamlit default menu
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        /* 전체 앱 배경색 변경 */
        .stApp {
            background-color: #4285F4;
        }
        
        /* 로고 스타일 */
        .logo-container {
            display: flex;
            justify-content: flex-start;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
            padding: 0 2rem;
            margin-top: 4rem;
            margin-bottom: 2rem;
        }
        
        .logo-container img {
            width: 200px;
            height: auto;
        }

        /* 텍스트 스타일 */
        .text-container {
            text-align: left;
            color: white;
            margin-bottom: 2rem;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
            padding: 0 2rem;
        }
        
        /* Google 로그인 버튼 스타일 */
        .stButton > button {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background-color: white !important;
            color: #444 !important;
            border: 1px solid #747775 !important;
            border-radius: 4px !important;
            padding: 8px 16px !important;
            font-family: 'Roboto', sans-serif !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            height: 40px !important;
            min-width: 200px !important;
            position: relative !important;
            margin: 0 !important;
        }

        .stButton > button:hover {
            background-color: #f8f8f8 !important;
            box-shadow: 0 1px 2px 0 rgba(60, 64, 67, .30), 0 1px 3px 1px rgba(60, 64, 67, .15) !important;
        }

        .stButton > button::before {
            content: '';
            background-image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGcgZmlsbD0ibm9uZSIgZmlsbC1ydWxlPSJldmVub2RkIj48cGF0aCBkPSJNMTcuNiA5LjJsLS4xLTEuOEg5djMuNGg0LjhDMTMuNiAxMiAxMyAxMyAxMiAxMy42djIuMmgzYTguOCA4LjggMCAwIDAgMi42LTYuNnoiIGZpbGw9IiM0Mjg1RjQiIGZpbGwtcnVsZT0ibm9uemVybyIvPjxwYXRoIGQ9Ik05IDE4YzIuNCAwIDQuNS0uOCA2LTIuMmwtMy0yLjJhNS40IDUuNCAwIDAgMS04LTIuOUgxVjEzYTkgOSAwIDAgMCA4IDV6IiBmaWxsPSIjMzRBODUzIiBmaWxsLXJ1bGU9Im5vbnplcm8iLz48cGF0aCBkPSJNNCAxMC43YTUuNCA1LjQgMCAwIDEgMC0zLjRWNUgxYTkgOSAwIDAgMCAwIDhsMy0yLjN6IiBmaWxsPSIjRkJCQzA1IiBmaWxsLXJ1bGU9Im5vbnplcm8iLz48cGF0aCBkPSJNOSAzLjZjMS4zIDAgMi41LjQgMy40IDEuM0wxNSAyLjNBOSA5IDAgMCAwIDEgNWwzIDIuNGE1LjQgNS40IDAgMCAxIDUtMy43eiIgZmlsbD0iI0VBNDMzNSIgZmlsbC1ydWxlPSJub256ZXJvIi8+PHBhdGggZD0iTTAgMGgxOHYxOEgweiIvPjwvZz48L3N2Zz4=");
            width: 18px;
            height: 18px;
            margin-right: 8px;
            background-repeat: no-repeat;
            background-position: center;
            background-size: contain;
        }

        /* 버튼 컨테이너 스타일 */
        .stMainBlockContainer.block-container.st-emotion-cache-mtjnbi.eht7o1d4 > div > div > div > div:nth-child(3) > div {
            padding-left: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # 로고 표시
    st.markdown(
        """
        <div class="logo-container">
            <img src="https://i.imgur.com/thQZtYk.png" alt="Logo">
        </div>
        <div class="text-container">
            <h1 style="font-size: 2rem; margin-bottom: 1.5rem; font-weight: 500; line-height: 1.35; color: white;">꿈으로의 문을 여는 곳, 이룸</h1>
            <h3 style="font-size: 1.1rem; margin-bottom: 3rem; line-height: 1.6; color: white;">
            이룸은 이력 관리와 지원 공고 분석을 통해<br> 
            취업과 이직을 위한 맞춤형 서류 제작은 물론 <br>
            경력 관리까지 지원하는 서비스입니다.<br>
            <br>
            여러분을 이해하고, 미래의 길을 함께 엽니다.</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Google 로그인 버튼
    st.button("Google로 로그인", on_click=st.login)

def main_screen():
    # 현재 페이지 상태 관리
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '대시보드'
    
    # 마지막으로 클릭된 버튼 상태 관리
    if 'last_clicked_button' not in st.session_state:
        st.session_state.last_clicked_button = 'dashboard'

    # 사이드바 설정
    with st.sidebar:
        st.markdown(
            """
            <style>
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
            
            /* 버튼 기본 스타일 */
            .stButton > button {
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

            /* 호버 스타일 */
            .stButton > button:hover {
                font-size: 2rem !important;
                font-weight: bold !important;
                background-color: rgba(255, 255, 255, 0.1) !important;
            }

            /* 선택된 버튼 스타일 */
            .stButton > button[aria-pressed="true"] {
                background-color: #0051FF !important;
                font-size: 2rem !important;
                font-weight: bold !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # 로고 추가
        st.image("https://i.imgur.com/thQZtYk.png")
        
        # 메뉴 버튼들
        if st.button('대시보드', key='dashboard', use_container_width=True):
            st.session_state.current_page = '대시보드'
            st.rerun()

        if st.button('이력관리', key='resume', use_container_width=True):
            st.session_state.current_page = '이력관리'
            st.rerun()

        if st.button('공고관리', key='jobs', use_container_width=True):
            st.session_state.current_page = '공고관리'
            st.rerun()

        if st.button('서류관리', key='documents', use_container_width=True):
            st.session_state.current_page = '서류관리'
            st.rerun()

        # 빈 공간 추가 (크기 조절)
        st.markdown("<div style='flex-grow: 1; min-height: calc(100vh - 800px);'></div>", unsafe_allow_html=True)
        
        # 로그아웃 버튼
        st.button("로그아웃", key='logout', on_click=st.logout)

    # 메인 컨텐츠 영역 스타일
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 2rem;
            font-weight: 500;
            margin-bottom: 2rem;
            color: #333;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 현재 페이지에 따른 컨텐츠 표시
    if st.session_state.current_page == '대시보드':
        st.markdown('<h3 class="main-header">대시보드</h3>', unsafe_allow_html=True)
        st.write("환영합니다, " + st.experimental_user.name + "님!")
        
    elif st.session_state.current_page == '이력관리':
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
                
                /* 섹션 제목 스타일링 */
                .section-title {
                    font-size: 2rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                    color: #333;
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
            st.markdown('<p class="section-title">인적사항</p>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                name_kr = st.text_input("한글 이름")
                nationality = st.text_input("국적", value="대한민국")
                birth_date = st.date_input("생년월일")
                email = st.text_input("이메일")
                photo_url = st.text_input("사진 링크")
            
            with col2:
                name_en = st.text_input("영문 이름")
                gender = st.selectbox("성별", ["선택", "남성", "여성"])
                address = st.text_input("주소")
                phone = st.text_input("연락처")
            
            # 구분선 추가
            st.markdown("---")
            
            # 병역 및 보훈 섹션
            st.markdown('<p class="section-title">병역 및 보훈</p>', unsafe_allow_html=True)
            col3, col4 = st.columns(2)
            
            with col3:
                military_service = st.selectbox("병역", ["선택", "군필", "미필", "면제", "해당없음"])
                military_branch = st.selectbox("군별", ["선택", "육군", "해군", "공군", "해병대", "의경", "공익", "기타"])
                military_rank = st.selectbox("계급", ["선택", "이병", "일병", "상병", "병장", "하사", "중사", "상사", "원사", "준위", "소위", "중위", "대위", "소령", "중령", "대령"])
                veteran_status = st.selectbox("보훈대상", ["선택", "대상", "비대상"])
            
            with col4:
                service_start = st.date_input("복무 시작일")
                service_end = st.date_input("복무 종료일")
                military_details = st.text_area("병역내용", height=100)
                special_note = st.text_area("특이사항", height=100)
            
            # 저장 버튼
            col5, col6, col7 = st.columns([1, 1, 5])
            with col5:
                if st.button("저장", use_container_width=True):
                    # TODO: 저장 로직 구현
                    st.success("저장되었습니다!")
            with col6:
                if st.button("취소", use_container_width=True):
                    # TODO: 취소 로직 구현
                    st.rerun()
        
        # 학력 탭
        with tab2:
            st.header("학력")
            st.write("여기에 학력 정보가 들어갑니다.")
        
        # 역량 탭
        with tab3:
            st.header("역량")
            st.write("여기에 역량 정보가 들어갑니다.")
        
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
        
    elif st.session_state.current_page == '공고관리':
        st.markdown('<h3 class="main-header">공고관리</h3>', unsafe_allow_html=True)
        
    elif st.session_state.current_page == '서류관리':
        st.markdown('<h3 class="main-header">서류관리</h3>', unsafe_allow_html=True)

if not st.experimental_user.is_logged_in:
    login_screen()
else:
    main_screen() 