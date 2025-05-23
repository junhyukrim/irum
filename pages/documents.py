import streamlit as st
import pymysql

def show_documents_page():
    # 페이지 초기화
    st.empty()
    
    # 페이지 제목
    st.title("서류관리")
     
    # DB 연결 테스트 - 단순하게
    try:
        conn = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        st.success("DB 연결 성공!")
        conn.close()
    except Exception as e:
        st.error(f"DB 연결 실패: {e}")
    
    # 여백 추가
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # 임시 메시지
    st.info("여기에 서류관리 내용이 들어갑니다.")