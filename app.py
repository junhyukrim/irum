import streamlit as st
import streamlit.components.v1 as components

def login_container():
    st.markdown(
        """
        <style>
        .login-container {
            background-color: #4285F4;
            padding: 2rem;
            border-radius: 10px;
            color: white;
            margin: 2rem auto;
            max-width: 800px;
        }
        
        .logo-container {
            display: flex;
            justify-content: center;
            margin-bottom: 2rem;
        }
        
        .logo-container img {
            width: 200px;
            height: auto;
        }

        .login-header {
            color: white !important;
            text-align: center;
        }

        .login-subheader {
            color: white !important;
            text-align: center;
            margin-bottom: 2rem;
        }

        /* Streamlit 버튼 스타일 수정 */
        .stButton button {
            background-color: white !important;
            color: #444 !important;
            border: 1px solid #747775 !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            font-family: 'Roboto', sans-serif !important;
            font-weight: 500 !important;
            margin: 0 auto !important;
            display: block !important;
        }

        .stButton button:hover {
            background-color: #f8f8f8 !important;
            box-shadow: 0 1px 2px 0 rgba(60, 64, 67, .30), 0 1px 3px 1px rgba(60, 64, 67, .15) !important;
        }
        </style>
        <div class="login-container">
            <div class="logo-container">
                <img src="https://i.imgur.com/thQZtYk.png" alt="Logo">
            </div>
            <h1 class="login-header">이 앱은 비공개입니다.</h1>
            <h3 class="login-subheader">로그인이 필요합니다.</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

def login_screen():
    login_container()
    st.button("Google로 로그인", on_click=st.login)

if not st.experimental_user.is_logged_in:
    login_screen()
else:
    st.header(f"환영합니다, {st.experimental_user.name}님!")
    st.button("로그아웃", on_click=st.logout) 