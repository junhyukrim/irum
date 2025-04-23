import streamlit as st
import pymysql

def connect_to_db():
    """데이터베이스 연결을 생성하고 반환합니다."""
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

def execute_query(query, values=None, fetch=False, many=False):
    """
    SQL 쿼리를 실행하고 결과를 반환합니다.
    
    Args:
        query (str): SQL 쿼리문
        values (tuple|list): 쿼리 파라미터
        fetch (bool): 결과를 반환할지 여부
        many (bool): 여러 행을 가져올지 여부
    
    Returns:
        tuple: (성공 여부, 결과 또는 오류 메시지)
    """
    try:
        conn = connect_to_db()
        if conn is None:
            return False, "데이터베이스 연결 실패"
        
        cursor = conn.cursor()
        try:
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            
            if fetch:
                if many:
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchone()
            else:
                result = cursor.lastrowid
            
            conn.commit()
            return True, result
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return False, str(e) 