import streamlit as st
import pymysql
from datetime import datetime

def get_database_connection():
    try:
        conn = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"]
        )
        return conn
    except Exception as e:
        st.error(f"데이터베이스 연결 실패: {str(e)}")
        return None

def save_personal_info(name_kr, name_en, nationality, gender, birth_date, 
                      address, email, phone, photo_url, military_service,
                      military_branch, military_rank, veteran_status, 
                      service_start, service_end, discharge_type):
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        now = datetime.now()
        
        sql = """
        INSERT INTO tb_resume_personal_info 
        (name_kr, name_en, nationality, gender, birth_date, 
         address, email, phone, photo_url, military_service,
         military_branch, military_rank, veteran_status, 
         service_start_date, service_end_date, discharge_type,
         created_at, updated_at)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        data = (
            name_kr, name_en, nationality, gender, birth_date,
            address, email, phone, photo_url, military_service,
            military_branch, military_rank, veteran_status,
            service_start, service_end, discharge_type,
            now, now
        )
        
        cursor.execute(sql, data)
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"저장 중 오류 발생: {str(e)}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close() 