import streamlit as st
from utils.db import execute_query

def load_education_info(login_email):
    """사용자의 교육 정보를 불러옵니다."""
    query = """
        SELECT e.*, GROUP_CONCAT(m.major) as majors
        FROM tb_resume_education e
        LEFT JOIN tb_resume_education_major m ON e.education_id = m.education_id
        WHERE e.login_email = %s
        GROUP BY e.education_id
        ORDER BY e.start_date DESC
    """
    success, result = execute_query(query, (login_email,), fetch=True, many=True)
    if success:
        return result or []
    return []

def save_education_info(login_email, education_data):
    """교육 정보를 저장합니다."""
    try:
        for edu in education_data:
            # 기본 교육 정보 저장
            if edu.get('education_id'):
                # 기존 데이터 업데이트
                update_query = """
                    UPDATE tb_resume_education 
                    SET school_name = %s, start_date = %s, end_date = %s, status = %s
                    WHERE education_id = %s AND login_email = %s
                """
                values = (
                    edu['school_name'], edu['start_date'], edu['end_date'],
                    edu['status'], edu['education_id'], login_email
                )
                success, _ = execute_query(update_query, values)
                if not success:
                    return False, "교육 정보 업데이트 실패"
            else:
                # 새 데이터 삽입
                insert_query = """
                    INSERT INTO tb_resume_education 
                    (login_email, school_name, start_date, end_date, status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (
                    login_email, edu['school_name'], edu['start_date'],
                    edu['end_date'], edu['status']
                )
                success, education_id = execute_query(insert_query, values)
                if not success:
                    return False, "교육 정보 저장 실패"
                edu['education_id'] = education_id

            # 전공 정보 저장
            if edu.get('education_id'):
                # 기존 전공 정보 삭제
                delete_major_query = "DELETE FROM tb_resume_education_major WHERE education_id = %s"
                success, _ = execute_query(delete_major_query, (edu['education_id'],))
                if not success:
                    return False, "전공 정보 삭제 실패"

                # 새 전공 정보 삽입
                if edu.get('majors'):
                    for major in edu['majors']:
                        insert_major_query = """
                            INSERT INTO tb_resume_education_major (education_id, major)
                            VALUES (%s, %s)
                        """
                        success, _ = execute_query(insert_major_query, (edu['education_id'], major))
                        if not success:
                            return False, "전공 정보 저장 실패"

        return True, "교육 정보가 성공적으로 저장되었습니다."
    except Exception as e:
        return False, f"교육 정보 저장 중 오류 발생: {str(e)}"

def delete_education(education_id, login_email):
    """교육 정보를 삭제합니다."""
    # 사용자 확인
    check_query = "SELECT education_id FROM tb_resume_education WHERE education_id = %s AND login_email = %s"
    success, result = execute_query(check_query, (education_id, login_email), fetch=True)
    
    if not success or not result:
        return False, "삭제 권한이 없거나 데이터가 존재하지 않습니다."
    
    # 교육 정보 삭제 (CASCADE 설정으로 인해 관련 전공 정보도 자동 삭제됨)
    delete_query = "DELETE FROM tb_resume_education WHERE education_id = %s"
    success, _ = execute_query(delete_query, (education_id,))
    
    if success:
        return True, "교육 정보가 성공적으로 삭제되었습니다."
    return False, "교육 정보 삭제 중 오류가 발생했습니다." 