import streamlit as st
import pymysql

def connect_to_db():
    try:
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
        return None

def show_documents_page():
    st.markdown('<h3 class="main-header">서류관리</h3>', unsafe_allow_html=True)
    
    # DB 연결 테스트
    try:
        conn = connect_to_db()
        if conn:
            st.success('데이터베이스에 성공적으로 연결되었습니다.')
            conn.close()
        else:
            st.error('데이터베이스 연결에 실패했습니다.')
    except Exception as e:
        st.error(f'데이터베이스 연결 중 오류가 발생했습니다: {str(e)}')
    
    # 여백 추가
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    st.write("여기에 서류관리 내용이 들어갑니다.") 