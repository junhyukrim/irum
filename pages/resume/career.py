import streamlit as st
from utils.db import execute_query

def load_career_info(login_email):
    """사용자의 경력 정보를 불러옵니다."""
    query = """
        SELECT c.*, GROUP_CONCAT(p.project_name) as projects
        FROM tb_resume_career c
        LEFT JOIN tb_resume_career_project p ON c.career_id = p.career_id
        WHERE c.login_email = %s
        GROUP BY c.career_id
        ORDER BY c.start_date DESC
    """
    success, result = execute_query(query, (login_email,), fetch=True, many=True)
    if success:
        return result or []
    return []

def save_career_info(login_email, career_data):
    """경력 정보를 저장합니다."""
    try:
        for career in career_data:
            # 기본 경력 정보 저장
            if career.get('career_id'):
                # 기존 데이터 업데이트
                update_query = """
                    UPDATE tb_resume_career 
                    SET company_name = %s, department = %s, position = %s,
                        start_date = %s, end_date = %s, status = %s
                    WHERE career_id = %s AND login_email = %s
                """
                values = (
                    career['company_name'], career['department'], career['position'],
                    career['start_date'], career['end_date'], career['status'],
                    career['career_id'], login_email
                )
                success, _ = execute_query(update_query, values)
                if not success:
                    return False, "경력 정보 업데이트 실패"
            else:
                # 새 데이터 삽입
                insert_query = """
                    INSERT INTO tb_resume_career 
                    (login_email, company_name, department, position, start_date, end_date, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    login_email, career['company_name'], career['department'],
                    career['position'], career['start_date'], career['end_date'],
                    career['status']
                )
                success, career_id = execute_query(insert_query, values)
                if not success:
                    return False, "경력 정보 저장 실패"
                career['career_id'] = career_id

            # 프로젝트 정보 저장
            if career.get('career_id'):
                # 기존 프로젝트 정보 삭제
                delete_project_query = "DELETE FROM tb_resume_career_project WHERE career_id = %s"
                success, _ = execute_query(delete_project_query, (career['career_id'],))
                if not success:
                    return False, "프로젝트 정보 삭제 실패"

                # 새 프로젝트 정보 삽입
                if career.get('projects'):
                    for project in career['projects']:
                        insert_project_query = """
                            INSERT INTO tb_resume_career_project (career_id, project_name)
                            VALUES (%s, %s)
                        """
                        success, _ = execute_query(insert_project_query, (career['career_id'], project))
                        if not success:
                            return False, "프로젝트 정보 저장 실패"

        return True, "경력 정보가 성공적으로 저장되었습니다."
    except Exception as e:
        return False, f"경력 정보 저장 중 오류 발생: {str(e)}"

def delete_career(career_id, login_email):
    """경력 정보를 삭제합니다."""
    # 사용자 확인
    check_query = "SELECT career_id FROM tb_resume_career WHERE career_id = %s AND login_email = %s"
    success, result = execute_query(check_query, (career_id, login_email), fetch=True)
    
    if not success or not result:
        return False, "삭제 권한이 없거나 데이터가 존재하지 않습니다."
    
    # 경력 정보 삭제 (CASCADE 설정으로 인해 관련 프로젝트 정보도 자동 삭제됨)
    delete_query = "DELETE FROM tb_resume_career WHERE career_id = %s"
    success, _ = execute_query(delete_query, (career_id,))
    
    if success:
        return True, "경력 정보가 성공적으로 삭제되었습니다."
    return False, "경력 정보 삭제 중 오류가 발생했습니다." 