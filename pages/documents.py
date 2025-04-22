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
    
    # 로그인한 이메일 표시
    if 'user_email' in st.session_state:
        st.markdown(f'로그인한 이메일: <span style="color: #4285F4;">{st.session_state.user_email}</span>', unsafe_allow_html=True)
    
    # DB 연결 테스트
    try:
        conn = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            cursorclass=pymysql.cursors.DictCursor
        )
        st.markdown("""
            <div style="padding: 1rem; background-color: #e9ffe9; border-radius: 0.5rem; margin: 1rem 0;">
                데이터베이스에 성공적으로 연결되었습니다.
            </div>
        """, unsafe_allow_html=True)
        conn.close()
    except Exception as e:
        st.markdown(f"""
            <div style="padding: 1rem; background-color: #ffe9e9; border-radius: 0.5rem; margin: 1rem 0;">
                데이터베이스 연결에 실패했습니다: {str(e)}
            </div>
        """, unsafe_allow_html=True)
    
    st.write("여기에 서류관리 내용이 들어갑니다.") 