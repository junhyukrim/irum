import streamlit as st
import pymysql

def connect_to_db():
    try:
        st.write("DB 연결 시도 중...")  # 디버깅용
        st.write("DB 설정값:", st.secrets["mysql"])  # 디버깅용
        
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
        st.write(f"연결 오류 발생: {str(e)}")  # 디버깅용
        return None

def show_documents_page():
    st.markdown('<h3 class="main-header">서류관리</h3>', unsafe_allow_html=True)
    
    # DB 연결 테스트
    conn = connect_to_db()
    if conn is None:
        st.markdown("""
            <div style="padding: 1rem; background-color: #ffe9e9; border-radius: 0.5rem; margin: 1rem 0;">
                데이터베이스 연결 실패! 관리자에게 문의하세요.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="padding: 1rem; background-color: #e9ffe9; border-radius: 0.5rem; margin: 1rem 0;">
                데이터베이스 연결 성공!
            </div>
        """, unsafe_allow_html=True)
        conn.close() 