import streamlit as st
import streamlit.components.v1 as components
from pages.resume import show_resume_page
from pages.jobs import show_jobs_page
from pages.documents import show_documents_page
from components.sidebar import setup_sidebar

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
    
    # 디버깅을 위한 상태 출력
    st.write("디버그 - 현재 페이지:", st.session_state.current_page)
    
    # 사이드바 설정
    with st.sidebar:
        setup_sidebar()

    # 현재 페이지에 따른 컨텐츠 표시
    if st.session_state.current_page == '서류관리':
        st.write("서류관리 페이지로 전환 시도...")
        show_documents_page()
    elif st.session_state.current_page == '이력관리':
        show_resume_page()
    elif st.session_state.current_page == '공고관리':
        show_jobs_page()
    else:
        st.title('대시보드')
        if st.experimental_user and st.experimental_user.email:
            st.write(f"환영합니다, {st.experimental_user.email}님!")

# 메인 실행 부분
if not st.experimental_user.is_logged_in:
    login_screen()
else:
    main_screen() 