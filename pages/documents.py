import streamlit as st
import pymysql

def connect_to_db():
    st.write("DB 연결을 시도합니다...")  # 디버깅 메시지 1
    
    try:
        # DB 설정값 확인
        st.write("DB 설정:", {
            "host": st.secrets["mysql"]["host"],
            "port": st.secrets["mysql"]["port"],
            "user": st.secrets["mysql"]["user"],
            "database": st.secrets["mysql"]["database"]
        })  # 디버깅 메시지 2
        
        connection = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            cursorclass=pymysql.cursors.DictCursor
        )
        st.write("DB 연결 성공!")  # 디버깅 메시지 3
        return connection
    except Exception as e:
        st.write(f"DB 연결 실패: {str(e)}")  # 디버깅 메시지 4
        return None

def show_documents_page():
    st.markdown('<h3 class="main-header">서류관리</h3>', unsafe_allow_html=True)
    
    # DB 연결 상태 메시지를 상단에 명확하게 표시
    st.markdown("### DB 연결 상태")
    st.write("연결 상태를 확인합니다...")  # 디버깅 메시지 5
    
    try:
        conn = connect_to_db()
        if conn:
            st.success("✓ 데이터베이스 연결 성공")
            conn.close()
        else:
            st.error("✗ 데이터베이스 연결 실패")
    except Exception as e:
        st.error(f"✗ 데이터베이스 연결 오류: {str(e)}")
    
    # 여백 추가
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    st.write("여기에 서류관리 내용이 들어갑니다.") 