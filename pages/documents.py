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
        st.error(f"DB 연결 실패: {str(e)}")
        return None

def show_documents_page():
    print("서류관리 페이지 함수 실행됨")  # 디버깅용
    st.write("디버그: show_documents_page 함수가 호출되었습니다.")
    
    st.title("서류관리")
    st.write("현재 페이지:", st.session_state.get('current_page', 'None'))
    
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

# Streamlit 페이지가 직접 실행될 때를 위한 코드
if __name__ == "__main__":
    show_documents_page() 