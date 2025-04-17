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

    # 사이드바 설정
    with st.sidebar:
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"] {
                background-color: #4285F4;
                width: 250px !important;
            }
            
            /* 사이드바 버튼 스타일 */
            .stButton > button {
                width: 100%;
                background-color: transparent !important;
                border: none !important;
                color: white !important;
                font-size: 1.1rem !important;
                padding: 0.5rem 0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: flex-start !important;
                transition: all 0.2s ease !important;
            }

            .stButton > button:hover {
                font-size: 1.2rem !important;
                font-weight: bold !important;
            }

            /* 현재 선택된 버튼 스타일 */
            .selected-button button {
                font-size: 1.2rem !important;
                font-weight: bold !important;
            }
            
            img {
                width: 150px;
                margin-bottom: 3rem;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # 로고 추가
        st.image("https://i.imgur.com/thQZtYk.png")
        
        # 메뉴 버튼들
        col1, col2, col3 = st.columns([0.1, 3, 0.1])
        with col2:
            # 각 버튼에 대해 현재 페이지인 경우 selected-button 클래스 추가
            st.markdown(f"""<div class="{'selected-button' if st.session_state.current_page == '대시보드' else ''}">""", unsafe_allow_html=True)
            if st.button('대시보드', key='dashboard', use_container_width=True):
                st.session_state.current_page = '대시보드'
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f"""<div class="{'selected-button' if st.session_state.current_page == '이력관리' else ''}">""", unsafe_allow_html=True)
            if st.button('이력관리', key='resume', use_container_width=True):
                st.session_state.current_page = '이력관리'
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f"""<div class="{'selected-button' if st.session_state.current_page == '공고관리' else ''}">""", unsafe_allow_html=True)
            if st.button('공고관리', key='jobs', use_container_width=True):
                st.session_state.current_page = '공고관리'
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f"""<div class="{'selected-button' if st.session_state.current_page == '서류관리' else ''}">""", unsafe_allow_html=True)
            if st.button('서류관리', key='documents', use_container_width=True):
                st.session_state.current_page = '서류관리'
            st.markdown('</div>', unsafe_allow_html=True)

            # 빈 공간 추가 (크기 조절)
            st.markdown("<div style='flex-grow: 1; min-height: calc(100vh - 450px);'></div>", unsafe_allow_html=True)
            
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
        st.markdown('<h1 class="main-header">대시보드</h1>', unsafe_allow_html=True)
        st.write("환영합니다, " + st.experimental_user.name + "님!")
        
    elif st.session_state.current_page == '이력관리':
        st.markdown('<h1 class="main-header">이력관리</h1>', unsafe_allow_html=True)
        
    elif st.session_state.current_page == '공고관리':
        st.markdown('<h1 class="main-header">공고관리</h1>', unsafe_allow_html=True)
        
    elif st.session_state.current_page == '서류관리':
        st.markdown('<h1 class="main-header">서류관리</h1>', unsafe_allow_html=True)

if not st.experimental_user.is_logged_in:
    login_screen()
else:
    main_screen() 