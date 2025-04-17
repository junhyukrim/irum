import streamlit as st

def login_screen():
    st.header("이 앱은 비공개입니다.")
    st.subheader("로그인이 필요합니다.")
    st.button("Google로 로그인", on_click=st.login)

if not st.experimental_user.is_logged_in:
    login_screen()
else:
    st.header(f"환영합니다, {st.experimental_user.name}님!")
    st.button("로그아웃", on_click=st.logout) 