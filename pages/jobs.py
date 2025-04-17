import streamlit as st
from components.sidebar import setup_sidebar

def show_jobs_page():
    # 사이드바 설정
    with st.sidebar:
        setup_sidebar()

    st.markdown('<h3 class="main-header">공고관리</h3>', unsafe_allow_html=True)
    st.write("여기에 공고관리 내용이 들어갑니다.") 