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
    
    # DB 연결 상태 메시지를 상단에 명확하게 표시
    st.markdown("### DB 연결 상태")
    
    try:
        conn = connect_to_db()
        if conn:
            st.markdown("""
                <div style='padding: 1rem; background-color: #DFF0D8; border: 1px solid #D6E9C6; border-radius: 4px; margin: 1rem 0;'>
                    <strong style='color: #3C763D;'>✓ 데이터베이스 연결 성공</strong>
                    <p style='margin: 0.5rem 0 0 0; color: #3C763D;'>데이터베이스에 성공적으로 연결되었습니다.</p>
                </div>
            """, unsafe_allow_html=True)
            conn.close()
        else:
            st.markdown("""
                <div style='padding: 1rem; background-color: #F2DEDE; border: 1px solid #EBCCD1; border-radius: 4px; margin: 1rem 0;'>
                    <strong style='color: #A94442;'>✗ 데이터베이스 연결 실패</strong>
                    <p style='margin: 0.5rem 0 0 0; color: #A94442;'>데이터베이스 연결에 실패했습니다.</p>
                </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"""
            <div style='padding: 1rem; background-color: #F2DEDE; border: 1px solid #EBCCD1; border-radius: 4px; margin: 1rem 0;'>
                <strong style='color: #A94442;'>✗ 데이터베이스 연결 오류</strong>
                <p style='margin: 0.5rem 0 0 0; color: #A94442;'>데이터베이스 연결 중 오류가 발생했습니다: {str(e)}</p>
            </div>
        """, unsafe_allow_html=True)
    
    # 여백 추가
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    st.write("여기에 서류관리 내용이 들어갑니다.") 