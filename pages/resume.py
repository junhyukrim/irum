import streamlit as st
import pymysql
from datetime import datetime
from collections import defaultdict

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

def save_personal_info(login_email, data):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 기존 데이터가 있는지 확인
            cursor.execute("SELECT * FROM tb_resume_personal_info WHERE login_email = %s", (login_email,))
            result = cursor.fetchone()
            
            if result:
                # 기존 데이터 업데이트
                update_query = """
                    UPDATE tb_resume_personal_info SET
                    ko_lastname = %s, ko_firstname = %s, en_firstname = %s, en_lastname = %s,
                    nationality = %s, gender = %s, birth_date = %s, address = %s,
                    email = %s, contact_number = %s, photo_url = %s,
                    military_status = %s, military_type = %s, military_rank = %s,
                    veterans_status = %s, service_start = %s, service_end = %s,
                    discharge_type = %s
                    WHERE login_email = %s
                """
                cursor.execute(update_query, (
                    data['kr_last'], data['kr_first'], data['en_first'], data['en_last'],
                    data['nationality'], data['gender'], data['birth_date'], data['address'],
                    data['email'], data['phone'], data['photo_url'],
                    data['military_status'],
                    data['military_branch'] if data['military_status'] == "군필" else None,
                    data['military_rank'] if data['military_status'] == "군필" else None,
                    data['veteran_status'] if data['military_status'] == "군필" else None,
                    data['service_start'] if data['military_status'] == "군필" else None,
                    data['service_end'] if data['military_status'] == "군필" else None,
                    data['discharge_type'] if data['military_status'] == "군필" else None,
                    login_email
                ))
            else:
                # 새로운 데이터 삽입
                insert_query = """
                    INSERT INTO tb_resume_personal_info (
                        login_email, ko_lastname, ko_firstname, en_firstname, en_lastname,
                        nationality, gender, birth_date, address,
                        email, contact_number, photo_url,
                        military_status, military_type, military_rank,
                        veterans_status, service_start, service_end,
                        discharge_type
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    login_email,
                    data['kr_last'], data['kr_first'], data['en_first'], data['en_last'],
                    data['nationality'], data['gender'], data['birth_date'], data['address'],
                    data['email'], data['phone'], data['photo_url'],
                    data['military_status'],
                    data['military_branch'] if data['military_status'] == "군필" else None,
                    data['military_rank'] if data['military_status'] == "군필" else None,
                    data['veteran_status'] if data['military_status'] == "군필" else None,
                    data['service_start'] if data['military_status'] == "군필" else None,
                    data['service_end'] if data['military_status'] == "군필" else None,
                    data['discharge_type'] if data['military_status'] == "군필" else None
                ))
            
            conn.commit()
            return True
        except Exception as e:
            st.error(f"쿼리 실행 중 오류: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류: {str(e)}")
        return False

def load_personal_info(login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return None, "데이터베이스에 접근할 수 없습니다. 관리자에게 문의해주세요."
            
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tb_resume_personal_info WHERE login_email = %s", (login_email,))
            result = cursor.fetchone()
            
            if result:
                return result, f"{login_email} 님의 정보를 불러왔습니다."
            else:
                return {}, "더 자세한 정보를 입력하시면 좋은 이력서가 완성됩니다."
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return None, f"데이터베이스 접근 중 오류가 발생했습니다: {str(e)}"

def load_skills_info(login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return None, "데이터베이스 연결 실패"
        
        cursor = conn.cursor()
        try:
            # 기본 기술 정보 조회
            cursor.execute("""
                SELECT id, skill_name, skill_level, note 
                FROM tb_resume_skills 
                WHERE login_email = %s
                ORDER BY id
            """, (login_email,))
            skills = cursor.fetchall()
            
            # 각 기술에 대한 자격증과 교육 정보 조회
            result = []
            for skill in skills:
                # 자격증 정보 조회
                cursor.execute("""
                    SELECT id, certification_name, issue_date, issuing_agency 
                    FROM tb_resume_certifications 
                    WHERE login_email = %s
                """, (login_email,))
                certifications = cursor.fetchall()
                
                # 교육 정보 조회
                cursor.execute("""
                    SELECT id, description 
                    FROM tb_resume_training 
                    WHERE login_email = %s
                """, (login_email,))
                training = cursor.fetchall()
                
                skill_data = {
                    'id': skill['id'],
                    'skill_name': skill['skill_name'],
                    'skill_level': skill['skill_level'],
                    'note': skill['note'],
                    'certifications': certifications,
                    'training': training
                }
                result.append(skill_data)
            
            return result, None
        except Exception as e:
            return None, f"데이터 조회 중 오류: {str(e)}"
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return None, f"데이터베이스 연결 중 오류: {str(e)}"

def save_education_info(login_email, data):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 현재 사용자의 모든 학력 정보 조회
            cursor.execute("""
                SELECT id FROM tb_resume_education 
                WHERE login_email = %s
            """, (login_email,))
            existing_education_ids = {row['id'] for row in cursor.fetchall()}
            
            # 현재 폼에 있는 학력 ID 수집
            current_education_ids = set()
            
            for edu_idx in data:
                education_data = data[edu_idx]
                
                # 날짜 데이터 처리
                admission_date = education_data['admission_date']
                graduation_date = education_data['graduation_date']
                
                # 기존 학력 정보가 있는지 확인
                if education_data.get('id'):  # 기존 데이터 업데이트
                    current_education_ids.add(education_data['id'])
                    update_query = """
                        UPDATE tb_resume_education SET
                        start_date = %s, end_date = %s, institution = %s, note = %s
                        WHERE id = %s AND login_email = %s
                    """
                    cursor.execute(update_query, (
                        admission_date,
                        graduation_date,
                        education_data['institution'],
                        education_data['notes'],
                        education_data['id'],
                        login_email
                    ))
                    education_id = education_data['id']
                    
                    # 기존 전공 정보 조회
                    cursor.execute("""
                        SELECT id, department, major, degree, gpa 
                        FROM tb_resume_education_major 
                        WHERE education_id = %s
                    """, (education_id,))
                    existing_majors = cursor.fetchall()
                    
                    # 전공 정보 매핑 생성
                    existing_major_map = {
                        (major['department'], major['major']): major['id']
                        for major in existing_majors
                    }
                    
                else:  # 새 학력 정보 삽입
                    insert_query = """
                        INSERT INTO tb_resume_education 
                        (login_email, start_date, end_date, institution, note)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        login_email,
                        admission_date,
                        graduation_date,
                        education_data['institution'],
                        education_data['notes']
                    ))
                    education_id = cursor.lastrowid
                    current_education_ids.add(education_id)
                    existing_major_map = {}

                # 새로운 전공 정보 처리
                new_majors = []
                update_majors = []
                for major_idx in range(education_data['major_count']):
                    department = education_data[f'department_{major_idx}']
                    major = education_data[f'major_{major_idx}']
                    degree = education_data[f'degree_{major_idx}']
                    gpa = education_data[f'gpa_{major_idx}']
                    
                    # degree가 '선택'인 경우 스킵
                    if degree == '선택':
                        continue
                    
                    # 빈 department와 major인 경우 스킵
                    if not department.strip() and not major.strip():
                        continue
                    
                    major_key = (department, major)
                    if major_key in existing_major_map:
                        # 기존 전공 정보 업데이트
                        update_majors.append({
                            'id': existing_major_map[major_key],
                            'degree': degree,
                            'gpa': gpa
                        })
                    else:
                        # 새로운 전공 정보 추가
                        new_majors.append({
                            'department': department,
                            'major': major,
                            'degree': degree,
                            'gpa': gpa
                        })

                # 기존 전공 정보 업데이트
                if update_majors:
                    for major in update_majors:
                        cursor.execute("""
                            UPDATE tb_resume_education_major 
                            SET degree = %s, gpa = %s
                            WHERE id = %s
                        """, (major['degree'], major['gpa'], major['id']))

                # 새로운 전공 정보 삽입
                if new_majors:
                    insert_major_query = """
                        INSERT INTO tb_resume_education_major 
                        (education_id, department, major, degree, gpa)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    for major in new_majors:
                        cursor.execute(insert_major_query, (
                            education_id,
                            major['department'],
                            major['major'],
                            major['degree'],
                            major['gpa']
                        ))

                # 삭제된 전공 정보 처리
                if education_data.get('id'):
                    current_majors = {
                        (education_data[f'department_{idx}'], education_data[f'major_{idx}'])
                        for idx in range(education_data['major_count'])
                        if education_data[f'degree_{idx}'] != '선택' and 
                           (education_data[f'department_{idx}'].strip() or education_data[f'major_{idx}'].strip())
                    }
                    for old_major_key, old_major_id in existing_major_map.items():
                        if old_major_key not in current_majors:
                            cursor.execute("""
                                DELETE FROM tb_resume_education_major 
                                WHERE id = %s
                            """, (old_major_id,))
            
            # 삭제된 학력 정보 처리
            deleted_education_ids = existing_education_ids - current_education_ids
            if deleted_education_ids:
                delete_query = """
                    DELETE FROM tb_resume_education 
                    WHERE id IN ({})
                """.format(','.join(['%s'] * len(deleted_education_ids)))
                cursor.execute(delete_query, tuple(deleted_education_ids))

            conn.commit()
            return True
        except Exception as e:
            st.error(f"쿼리 실행 중 오류: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류: {str(e)}")
        return False

def load_education_info(login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return None, "데이터베이스 연결 실패"
        
        cursor = conn.cursor()
        try:
            # 기본 학력 정보 조회
            cursor.execute("""
                SELECT id, start_date, end_date, institution, note 
                FROM tb_resume_education 
                WHERE login_email = %s
                ORDER BY start_date DESC
            """, (login_email,))
            educations = cursor.fetchall()
            
            # 각 학력의 전공 정보 조회
            result = []
            for edu in educations:
                cursor.execute("""
                    SELECT department, major, degree, gpa 
                    FROM tb_resume_education_major 
                    WHERE education_id = %s
                """, (edu['id'],))
                majors = cursor.fetchall()
                
                edu_data = {
                    'id': edu['id'],
                    'start_date': edu['start_date'],
                    'end_date': edu['end_date'],
                    'institution': edu['institution'],
                    'note': edu['note'],
                    'majors': majors
                }
                result.append(edu_data)
            
            return result, None
        except Exception as e:
            return None, f"데이터 조회 중 오류: {str(e)}"
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return None, f"데이터베이스 연결 중 오류: {str(e)}"

def delete_education(education_id, login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 해당 학력이 현재 로그인한 사용자의 것인지 확인
            cursor.execute("""
                SELECT id FROM tb_resume_education 
                WHERE id = %s AND login_email = %s
            """, (education_id, login_email))
            
            if not cursor.fetchone():
                return False
            
            # CASCADE 설정으로 인해 tb_resume_education_major의 데이터도 자동 삭제됨
            cursor.execute("DELETE FROM tb_resume_education WHERE id = %s", (education_id,))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"삭제 중 오류: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류: {str(e)}")
        return False

def save_skills_info(login_email, data):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 현재 사용자의 모든 기술 정보 조회
            cursor.execute("""
                SELECT id FROM tb_resume_skills 
                WHERE login_email = %s
            """, (login_email,))
            existing_skill_ids = {row['id'] for row in cursor.fetchall()}
            
            # 현재 폼에 있는 기술 ID 수집
            current_skill_ids = set()
            
            for skill_idx in data:
                skill_data = data[skill_idx]
                
                # 기존 기술 정보가 있는지 확인
                if skill_data.get('id'):  # 기존 데이터 업데이트
                    current_skill_ids.add(skill_data['id'])
                    update_query = """
                        UPDATE tb_resume_skills SET
                        skill_name = %s, skill_level = %s, note = %s
                        WHERE id = %s AND login_email = %s
                    """
                    cursor.execute(update_query, (
                        skill_data['skill_name'],
                        skill_data['skill_level'],
                        skill_data['note'],
                        skill_data['id'],
                        login_email
                    ))
                else:  # 새 기술 정보 삽입
                    insert_query = """
                        INSERT INTO tb_resume_skills 
                        (login_email, skill_name, skill_level, note)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        login_email,
                        skill_data['skill_name'],
                        skill_data['skill_level'],
                        skill_data['note']
                    ))
                    skill_id = cursor.lastrowid
                    current_skill_ids.add(skill_id)
            
            # 삭제된 기술 정보 처리
            deleted_skill_ids = existing_skill_ids - current_skill_ids
            if deleted_skill_ids:
                delete_query = """
                    DELETE FROM tb_resume_skills 
                    WHERE id IN ({})
                """.format(','.join(['%s'] * len(deleted_skill_ids)))
                cursor.execute(delete_query, tuple(deleted_skill_ids))

            conn.commit()
            return True
        except Exception as e:
            st.error(f"쿼리 실행 중 오류: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류: {str(e)}")
        return False

def save_certifications_info(login_email, data):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 현재 사용자의 모든 자격증 정보 조회
            cursor.execute("""
                SELECT id FROM tb_resume_certifications 
                WHERE login_email = %s
            """, (login_email,))
            existing_cert_ids = {row['id'] for row in cursor.fetchall()}
            
            # 현재 폼에 있는 자격증 ID 수집
            current_cert_ids = set()
            
            # 데이터 구조 변경에 맞게 처리
            for idx in data:
                cert_data = data[idx]
                
                # 기존 자격증 정보가 있는지 확인
                if cert_data.get('id'):  # 기존 데이터 업데이트
                    current_cert_ids.add(cert_data['id'])
                    update_query = """
                        UPDATE tb_resume_certifications SET
                        certification_name = %s,
                        issue_date = %s,
                        issuing_agency = %s
                        WHERE id = %s AND login_email = %s
                    """
                    cursor.execute(update_query, (
                        cert_data['certification_name'],
                        cert_data['issue_date'],
                        cert_data['issuing_agency'],
                        cert_data['id'],
                        login_email
                    ))
                else:  # 새 자격증 정보 삽입
                    insert_query = """
                        INSERT INTO tb_resume_certifications 
                        (login_email, certification_name, issue_date, issuing_agency)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        login_email,
                        cert_data['certification_name'],
                        cert_data['issue_date'],
                        cert_data['issuing_agency']
                    ))
                    cert_id = cursor.lastrowid
                    current_cert_ids.add(cert_id)
            
            # 삭제된 자격증 정보 처리
            deleted_cert_ids = existing_cert_ids - current_cert_ids
            if deleted_cert_ids:
                delete_query = """
                    DELETE FROM tb_resume_certifications 
                    WHERE id IN ({})
                """.format(','.join(['%s'] * len(deleted_cert_ids)))
                cursor.execute(delete_query, tuple(deleted_cert_ids))

            conn.commit()
            return True
        except Exception as e:
            st.error(f"쿼리 실행 중 오류: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류: {str(e)}")
        return False

def save_training_info(login_email, data):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 현재 사용자의 모든 교육 정보 조회
            cursor.execute("""
                SELECT id FROM tb_resume_training 
                WHERE login_email = %s
            """, (login_email,))
            existing_training_ids = {row['id'] for row in cursor.fetchall()}
            
            # 현재 폼에 있는 교육 ID 수집
            current_training_ids = set()
            
            # 데이터 구조 변경에 맞게 처리
            for idx in data:
                train_data = data[idx]
                
                # 기존 교육 정보가 있는지 확인
                if train_data.get('id'):  # 기존 데이터 업데이트
                    current_training_ids.add(train_data['id'])
                    update_query = """
                        UPDATE tb_resume_training SET
                        description = %s
                        WHERE id = %s AND login_email = %s
                    """
                    cursor.execute(update_query, (
                        train_data['description'],
                        train_data['id'],
                        login_email
                    ))
                else:  # 새 교육 정보 삽입
                    insert_query = """
                        INSERT INTO tb_resume_training 
                        (login_email, description)
                        VALUES (%s, %s)
                    """
                    cursor.execute(insert_query, (
                        login_email,
                        train_data['description']
                    ))
                    training_id = cursor.lastrowid
                    current_training_ids.add(training_id)
            
            # 삭제된 교육 정보 처리
            deleted_training_ids = existing_training_ids - current_training_ids
            if deleted_training_ids:
                delete_query = """
                    DELETE FROM tb_resume_training 
                    WHERE id IN ({})
                """.format(','.join(['%s'] * len(deleted_training_ids)))
                cursor.execute(delete_query, tuple(deleted_training_ids))

            conn.commit()
            return True
        except Exception as e:
            st.error(f"쿼리 실행 중 오류: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류: {str(e)}")
        return False

def load_certifications_info(login_email):
    """
    사용자의 자격증 정보를 조회하는 함수
    Args:
        login_email (str): 사용자 이메일
    Returns:
        dict: 자격증 정보를 담은 딕셔너리
    """
    if not login_email:
        return {}

    try:
        conn = connect_to_db()
        if conn is None:
            return {}
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, certification_name, issuing_agency, issue_date
                FROM tb_resume_certifications 
                WHERE login_email = %s
                ORDER BY issue_date DESC, id DESC
            """, (login_email,))
            
            certifications = {}
            for row in enumerate(cursor.fetchall()):
                certifications[idx] = {
                    'certification_name': row['certification_name'],
                    'issuing_agency': row['issuing_agency'],
                    'issue_date': row['issue_date']
                }

            return certifications
            
        except Exception as e:
            print(f"Error in load_certifications_info: {str(e)}")
            return {}
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Database connection error in load_certifications_info: {str(e)}")
        return {}
        
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

def load_training_info(login_email):
    if not login_email:
        return {}
    
    try:
        conn = connect_to_db()
        if conn is None:
            return None
        
        cursor = conn.cursor()
        try:
            # 교육 정보 조회
            cursor.execute("""
                SELECT id, description 
                FROM tb_resume_training 
                WHERE login_email = %s
            """, (login_email,))

            trainings = {}
            for idx, row in enumerate(cursor.fetchall()):
                trainings[idx] = {
                    'description': row['description']
                }
            
            return trainings
        
        except Exception as e:
            print(f"Error in load_training_info: {str(e)}")
            return {}
            
        finally:
            cursor.close()

    except Exception as e:
            print(f"Error in load_training_info: {str(e)}")
            return {}
            
    finally:
        cursor.close()

def save_career_info(login_email, data):
    try:
        conn = connect_to_db()
        if conn is None:
            return None, "데이터베이스 연결 실패"
        
        cursor = conn.cursor()
        try:
            # 현재 사용자의 모든 경력 정보 조회
            cursor.execute("""
                SELECT id FROM tb_resume_experiences 
                WHERE login_email = %s
            """, (login_email,))
            existing_career_ids = {row['id'] for row in cursor.fetchall()}
            
            # 현재 폼에 있는 경력 ID 수집
            current_career_ids = set()
            saved_career_ids = {}  # 각 인덱스에 대한 career_id를 저장
            
            # 데이터 구조 변경에 맞게 처리
            for idx in data:
                career_data = data[idx]
                
                # 기존 경력 정보가 있는지 확인
                if career_data.get('id'):  # 기존 데이터 업데이트
                    current_career_ids.add(career_data['id'])
                    update_query = """
                        UPDATE tb_resume_experiences SET
                        company_name = %s,
                        join_date = %s,
                        leave_date = %s,
                        leave_reason = %s
                        WHERE id = %s AND login_email = %s
                    """
                    cursor.execute(update_query, (
                        career_data['company'],
                        career_data['join_date'],
                        career_data['leave_date'],
                        career_data.get('leave_reason', ''),
                        career_data['id'],
                        login_email
                    ))
                    saved_career_ids[idx] = career_data['id']
                else:  # 새 경력 정보 삽입
                    insert_query = """
                        INSERT INTO tb_resume_experiences 
                        (login_email, company_name, join_date, leave_date, leave_reason)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        login_email,
                        career_data['company'],
                        career_data['join_date'],
                        career_data['leave_date'],
                        career_data.get('leave_reason', '')
                    ))
                    career_id = cursor.lastrowid
                    current_career_ids.add(career_id)
                    saved_career_ids[idx] = career_id
            
            # 삭제된 경력 정보 처리
            deleted_career_ids = existing_career_ids - current_career_ids
            if deleted_career_ids:
                # 먼저 관련된 position 정보 삭제
                position_delete_query = """
                    DELETE FROM tb_resume_positions 
                    WHERE experience_id IN ({})
                """.format(','.join(['%s'] * len(deleted_career_ids)))
                cursor.execute(position_delete_query, tuple(deleted_career_ids))
                
                # 그 다음 career 정보 삭제
                career_delete_query = """
                    DELETE FROM tb_resume_experiences 
                    WHERE id IN ({})
                """.format(','.join(['%s'] * len(deleted_career_ids)))
                cursor.execute(career_delete_query, tuple(deleted_career_ids))

            conn.commit()
            return saved_career_ids, None
        except Exception as e:
            conn.rollback()
            return None, str(e)
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return None, str(e)

def load_career_info(login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return None, "데이터베이스 연결 실패"
        
        cursor = conn.cursor()
        try:
            # 경력 정보 조회
            cursor.execute("""
                SELECT id, company_name, join_date, leave_date, leave_reason
                FROM tb_resume_experiences 
                WHERE login_email = %s
                ORDER BY join_date DESC
            """, (login_email,))
            careers = cursor.fetchall()
            
            if careers is None:
                careers = []
            
            return careers, None
        except Exception as e:
            return None, f"데이터 조회 중 오류: {str(e)}"
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return None, f"데이터베이스 연결 중 오류: {str(e)}"

def delete_career(career_id, login_email):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 해당 경력이 현재 로그인한 사용자의 것인지 확인
            cursor.execute("""
                SELECT id FROM tb_resume_experiences 
                WHERE id = %s AND login_email = %s
            """, (career_id, login_email))
            
            if not cursor.fetchone():
                return False
            
            # 먼저 관련된 position 정보 삭제
            cursor.execute("DELETE FROM tb_resume_positions WHERE experience_id = %s", (career_id,))
            
            # 그 다음 career 정보 삭제
            cursor.execute("DELETE FROM tb_resume_experiences WHERE id = %s", (career_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return False

def save_position_info(experience_id, data):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 현재 경력의 모든 직위 정보 조회
            cursor.execute("""
                SELECT id FROM tb_resume_positions 
                WHERE experience_id = %s
            """, (experience_id,))
            existing_position_ids = {row['id'] for row in cursor.fetchall()}
            
            # 현재 폼에 있는 직위 ID 수집
            current_position_ids = set()
            
            # 데이터 구조 변경에 맞게 처리
            for idx in data:
                position_data = data[idx]
                # 기존 직위 정보가 있는지 확인
                if position_data.get('id'):  # 기존 데이터 업데이트
                    current_position_ids.add(position_data['id'])
                    update_query = """
                        UPDATE tb_resume_positions SET
                        position = %s,
                        promotion_date = %s,
                        retirement_date = %s,
                        description = %s
                        WHERE id = %s AND experience_id = %s
                    """
                    cursor.execute(update_query, (
                        position_data['position'],
                        position_data['promotion_date'],
                        position_data['retirement_date'],
                        position_data.get('description', ''),
                        position_data['id'],
                        experience_id
                    ))
                else:  # 새 직위 정보 삽입
                    insert_query = """
                        INSERT INTO tb_resume_positions 
                        (experience_id, position, promotion_date, retirement_date, description)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        experience_id,
                        position_data['position'],
                        position_data['promotion_date'],
                        position_data['retirement_date'],
                        position_data.get('description', '')
                    ))
                    position_id = cursor.lastrowid
                    current_position_ids.add(position_id)
            
            # 삭제된 직위 정보 처리
            deleted_position_ids = existing_position_ids - current_position_ids
            if deleted_position_ids:
                delete_query = """
                    DELETE FROM tb_resume_positions 
                    WHERE id IN ({})
                """.format(','.join(['%s'] * len(deleted_position_ids)))
                cursor.execute(delete_query, tuple(deleted_position_ids))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return False

def load_position_info(experience_id):
    try:
        conn = connect_to_db()
        if conn is None:
            return None, "데이터베이스 연결 실패"
        
        cursor = conn.cursor()
        try:
            # 직위 정보 조회
            cursor.execute("""
                SELECT id, position, promotion_date, retirement_date, description
                FROM tb_resume_positions 
                WHERE experience_id = %s
                ORDER BY promotion_date ASC
            """, (experience_id,))
            positions = cursor.fetchall()
            
            if positions is None:
                positions = []
            
            return positions, None
        except Exception as e:
            return None, f"데이터 조회 중 오류: {str(e)}"
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return None, f"데이터베이스 연결 중 오류: {str(e)}"

def delete_position(position_id, experience_id):
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 해당 직위가 현재 경력의 것인지 확인
            cursor.execute("""
                SELECT id FROM tb_resume_positions 
                WHERE id = %s AND experience_id = %s
            """, (position_id, experience_id))
            
            if not cursor.fetchone():
                return False
            
            cursor.execute("DELETE FROM tb_resume_positions WHERE id = %s", (position_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return False

def save_award_info(login_email, data):
    """
    수상 정보를 저장/수정/삭제하는 함수
    Args:
        login_email (str): 사용자 이메일
        data (dict): 수상 정보 데이터
    Returns:
        bool: 성공 여부
    """
    if not login_email or not isinstance(data, dict):
        print("Invalid input parameters in save_award_info")
        return False

    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 현재 사용자의 모든 수상 정보 조회
            cursor.execute("""
                SELECT id FROM tb_resume_awards 
                WHERE login_email = %s
            """, (login_email,))
            existing_award_ids = {row['id'] for row in cursor.fetchall()}
            
            # 현재 폼에 있는 수상 ID 수집
            current_award_ids = set()
            
            # 수상 정보 저장/수정
            for idx, award_info in data.items():
                # 필수 필드 검증
                required_fields = ['award_name', 'award_date', 'awarding_body']
                if not all(field in award_info for field in required_fields):
                    print(f"Missing required fields in award data: {idx}")
                    continue

                award_id = award_info.get('id')
                award_note = award_info.get('award_note', '')  # Changed from 'note' to 'award_note'
                
                if award_id:  # 기존 데이터 수정
                    if award_id not in existing_award_ids:
                        print(f"Invalid award_id: {award_id}")
                        continue
                        
                    cursor.execute("""
                        UPDATE tb_resume_awards 
                        SET award_name = %s,
                            award_date = %s,
                            awarding_body = %s,
                            note = %s
                        WHERE id = %s AND login_email = %s
                    """, (
                        award_info['award_name'],
                        award_info['award_date'],
                        award_info['awarding_body'],
                        award_note,
                        award_id,
                        login_email
                    ))
                    if cursor.rowcount > 0:
                        current_award_ids.add(award_id)
                else:  # 새 데이터 추가
                    cursor.execute("""
                        INSERT INTO tb_resume_awards 
                        (login_email, award_name, award_date, awarding_body, note)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        login_email,
                        award_info['award_name'],
                        award_info['award_date'],
                        award_info['awarding_body'],
                        award_note
                    ))
                    if cursor.rowcount > 0:
                        new_award_id = cursor.lastrowid
                        current_award_ids.add(new_award_id)
            
            # 삭제된 수상 정보 처리
            awards_to_delete = existing_award_ids - current_award_ids
            if awards_to_delete:
                placeholders = ', '.join(['%s'] * len(awards_to_delete))
                cursor.execute(f"""
                    DELETE FROM tb_resume_awards 
                    WHERE id IN ({placeholders}) AND login_email = %s
                """, (*awards_to_delete, login_email))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error in save_award_info: {str(e)}")
            return False
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Database connection error in save_award_info: {str(e)}")
        return False
        
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

def load_award_info(login_email):
    """
    사용자의 수상 정보를 조회하는 함수
    Args:
        login_email (str): 사용자 이메일
    Returns:
        tuple: (awards_list, error_message)
    """
    if not login_email:
        return None, "유효하지 않은 사용자 정보입니다."

    try:
        conn = connect_to_db()
        if conn is None:
            return None, "데이터베이스 연결 실패"
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, award_name, award_date, awarding_body, note
                FROM tb_resume_awards 
                WHERE login_email = %s
                ORDER BY award_date DESC, id DESC
            """, (login_email,))
            
            awards = []
            for row in cursor.fetchall():
                awards.append({
                    'id': row['id'],
                    'award_name': row['award_name'],
                    'award_date': row['award_date'],
                    'awarding_body': row['awarding_body'],
                    'award_note': row['note'] if row['note'] is not None else ''
                })
            
            return awards, None
            
        except Exception as e:
            print(f"Error in load_award_info: {str(e)}")
            return None, f"수상 정보 조회 중 오류가 발생했습니다: {str(e)}"
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Database connection error in load_award_info: {str(e)}")
        return None, f"데이터베이스 연결 중 오류가 발생했습니다: {str(e)}"
        
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

def delete_award(award_id, login_email):
    """
    특정 수상 정보를 삭제하는 함수
    Args:
        award_id (int): 삭제할 수상 정보 ID
        login_email (str): 사용자 이메일
    Returns:
        bool: 성공 여부
    """
    if not award_id or not login_email:
        print("Invalid input parameters in delete_award")
        return False

    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 해당 수상 정보가 존재하는지 확인
            cursor.execute("""
                SELECT id FROM tb_resume_awards 
                WHERE id = %s AND login_email = %s
            """, (award_id, login_email))
            
            if not cursor.fetchone():
                print(f"Award not found: {award_id}")
                return False
            
            # 수상 정보 삭제
            cursor.execute("""
                DELETE FROM tb_resume_awards 
                WHERE id = %s AND login_email = %s
            """, (award_id, login_email))
            
            if cursor.rowcount > 0:
                conn.commit()
                return True
            return False
            
        except Exception as e:
            conn.rollback()
            print(f"Error in delete_award: {str(e)}")
            return False
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Database connection error in delete_award: {str(e)}")
        return False
        
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

def save_activities_info(login_email, data):
    """
    기타활동 정보를 저장/수정/삭제하는 함수
    Args:
        login_email (str): 사용자 이메일
        data (dict): 기타활동 정보 데이터
    Returns:
        bool: 성공 여부
    """
    if not login_email or not isinstance(data, dict):
        print("Invalid input parameters in save_activities_info")
        return False

    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 현재 사용자의 모든 기타활동 정보 조회
            cursor.execute("""
                SELECT id FROM tb_resume_activities 
                WHERE login_email = %s
            """, (login_email,))
            existing_activity_ids = {row['id'] for row in cursor.fetchall()}
            
            # 현재 폼에 있는 활동 ID 수집
            current_activity_ids = set()
            
            # 기타활동 정보 저장/수정
            for idx, activity_info in data.items():
                # 필수 필드 검증
                required_fields = ['activity_name', 'organization', 'start_date']
                if not all(field in activity_info and activity_info[field] for field in required_fields):
                    print(f"Missing required fields in activity data: {idx}")
                    continue

                activity_id = activity_info.get('id')
                
                if activity_id:  # 기존 데이터 수정
                    if activity_id not in existing_activity_ids:
                        print(f"Invalid activity_id: {activity_id}")
                        continue
                        
                    cursor.execute("""
                        UPDATE tb_resume_activities 
                        SET activity_name = %s,
                            organization = %s,
                            start_date = %s,
                            end_date = %s,
                            role = %s,
                            link = %s,
                            details = %s
                        WHERE id = %s AND login_email = %s
                    """, (
                        activity_info['activity_name'],
                        activity_info['organization'],
                        activity_info['start_date'],
                        activity_info.get('end_date'),
                        activity_info.get('role', ''),
                        activity_info.get('link', ''),
                        activity_info.get('details', ''),
                        activity_id,
                        login_email
                    ))
                    if cursor.rowcount > 0:
                        current_activity_ids.add(activity_id)
                else:  # 새 데이터 추가
                    cursor.execute("""
                        INSERT INTO tb_resume_activities 
                        (login_email, activity_name, organization, start_date, end_date, role, link, details)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        login_email,
                        activity_info['activity_name'],
                        activity_info['organization'],
                        activity_info['start_date'],
                        activity_info.get('end_date'),
                        activity_info.get('role', ''),
                        activity_info.get('link', ''),
                        activity_info.get('details', '')
                    ))
                    if cursor.rowcount > 0:
                        new_activity_id = cursor.lastrowid
                        current_activity_ids.add(new_activity_id)
            
            # 삭제된 기타활동 정보 처리
            activities_to_delete = existing_activity_ids - current_activity_ids
            if activities_to_delete:
                placeholders = ', '.join(['%s'] * len(activities_to_delete))
                cursor.execute(f"""
                    DELETE FROM tb_resume_activities 
                    WHERE id IN ({placeholders}) AND login_email = %s
                """, (*activities_to_delete, login_email))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error in save_activities_info: {str(e)}")
            return False
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Database connection error in save_activities_info: {str(e)}")
        return False
        
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

def load_activities_info(login_email):
    """
    사용자의 기타활동 정보를 조회하는 함수
    Args:
        login_email (str): 사용자 이메일
    Returns:
        tuple: (activities_list, error_message)
    """
    if not login_email:
        return None, "유효하지 않은 사용자 정보입니다."

    try:
        conn = connect_to_db()
        if conn is None:
            return None, "데이터베이스 연결 실패"
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, activity_name, organization, start_date, end_date, role, link, details
                FROM tb_resume_activities 
                WHERE login_email = %s
                ORDER BY start_date DESC, id DESC
            """, (login_email,))
            
            activities = []
            for row in cursor.fetchall():
                activities.append({
                    'id': row['id'],
                    'activity_name': row['activity_name'],
                    'organization': row['organization'],
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'role': row['role'] if row['role'] is not None else '',
                    'link': row['link'] if row['link'] is not None else '',
                    'details': row['details'] if row['details'] is not None else ''
                })
            
            return activities, None
            
        except Exception as e:
            print(f"Error in load_activities_info: {str(e)}")
            return None, f"기타활동 정보 조회 중 오류가 발생했습니다: {str(e)}"
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Database connection error in load_activities_info: {str(e)}")
        return None, f"데이터베이스 연결 중 오류가 발생했습니다: {str(e)}"
        
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

def delete_activity(activity_id, login_email):
    """
    특정 기타활동 정보를 삭제하는 함수
    Args:
        activity_id (int): 삭제할 기타활동 정보 ID
        login_email (str): 사용자 이메일
    Returns:
        bool: 성공 여부
    """
    if not activity_id or not login_email:
        print("Invalid input parameters in delete_activity")
        return False

    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 해당 기타활동 정보가 존재하는지 확인
            cursor.execute("""
                SELECT id FROM tb_resume_activities 
                WHERE id = %s AND login_email = %s
            """, (activity_id, login_email))
            
            if not cursor.fetchone():
                print(f"Activity not found: {activity_id}")
                return False
            
            # 기타활동 정보 삭제
            cursor.execute("""
                DELETE FROM tb_resume_activities 
                WHERE id = %s AND login_email = %s
            """, (activity_id, login_email))
            
            if cursor.rowcount > 0:
                conn.commit()
                return True
            return False
            
        except Exception as e:
            conn.rollback()
            print(f"Error in delete_activity: {str(e)}")
            return False
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Database connection error in delete_activity: {str(e)}")
        return False
        
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

def save_intro_info(login_email, data):
    """자기소개 정보를 저장하는 함수"""
    try:
        conn = connect_to_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            # 현재 사용자의 기존 자기소개 ID 목록 조회
            cursor.execute(
                "SELECT id FROM tb_resume_self_introductions WHERE login_email = %s",
                (login_email,)
            )
            existing_ids = {row['id'] for row in cursor.fetchall()}
            saved_ids = set()
            
            # 데이터 저장/수정
            for idx, intro in data.items():
                intro_id = intro.get('id')
                
                if intro_id:  # 기존 데이터 수정
                    cursor.execute("""
                        UPDATE tb_resume_self_introductions 
                        SET topic_category = %s, topic_title = %s, content = %s
                        WHERE id = %s AND login_email = %s
                    """, (
                        intro['category'],
                        intro['topic'],
                        intro['content'],
                        intro_id,
                        login_email
                    ))
                    saved_ids.add(intro_id)
                else:  # 새 데이터 추가
                    cursor.execute("""
                        INSERT INTO tb_resume_self_introductions 
                        (login_email, topic_category, topic_title, content)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        login_email,
                        intro['category'],
                        intro['topic'],
                        intro['content']
                    ))
                    if cursor.lastrowid:
                        saved_ids.add(cursor.lastrowid)
            
            # 삭제된 항목 처리
            ids_to_delete = existing_ids - saved_ids
            if ids_to_delete:
                placeholders = ','.join(['%s'] * len(ids_to_delete))
                cursor.execute(
                    f"DELETE FROM tb_resume_self_introductions WHERE id IN ({placeholders}) AND login_email = %s",
                    (*ids_to_delete, login_email)
                )
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error in save_intro_info: {str(e)}")
            return False
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Database connection error in save_intro_info: {str(e)}")
        return False
        
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

def load_intro_info(login_email):
    """자기소개 정보를 불러오는 함수"""
    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT id, topic_category, topic_title, content
                FROM tb_resume_self_introductions
                WHERE login_email = %s
                ORDER BY id
            """, (login_email,))
            
            results = cursor.fetchall()
            return results, None
            
        except Exception as e:
            error_msg = f"Error in load_intro_info: {str(e)}"
            print(error_msg)
            return None, error_msg
            
        finally:
            cursor.close()
            
    except Exception as e:
        error_msg = f"Database connection error in load_intro_info: {str(e)}"
        print(error_msg)
        return None, error_msg
        
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

def delete_intro(intro_id, login_email):
    """특정 자기소개를 삭제하는 함수"""
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM tb_resume_self_introductions 
                WHERE id = %s AND login_email = %s
            """, (intro_id, login_email))
            
            if cursor.rowcount > 0:
                conn.commit()
                return True
            return False
            
        except Exception as e:
            conn.rollback()
            print(f"Error in delete_intro: {str(e)}")
            return False
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Database connection error in delete_intro: {str(e)}")
        return False
        
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

def show_success_message():
    st.markdown("""
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #d8e6fd;">
            성공적으로 저장되었습니다!
        </div>
    """, unsafe_allow_html=True)

def show_resume_page():
    # 세션 상태 초기화
    if 'skills_loaded' not in st.session_state:
        st.session_state.skills_loaded = False
    
    if 'skill_data' not in st.session_state:
        st.session_state.skill_data = [0]
    
    if 'cert_counts' not in st.session_state or not st.session_state.cert_counts:
        st.session_state.cert_counts = defaultdict(int)
        st.session_state.cert_counts[0] = 1
    
    if 'train_counts' not in st.session_state or not st.session_state.train_counts:
        st.session_state.train_counts = defaultdict(int)
        st.session_state.train_counts[0] = 1
    
    # 사용자가 로그인한 경우에만 데이터 로드
    if 'user_email' in st.session_state and not st.session_state.skills_loaded:
        # 기술 및 역량 데이터 로드
        skills_info, error = load_skills_info(st.session_state.user_email)
        if error:
            st.error(error)
        elif skills_info:
            st.session_state.skill_data = list(range(len(skills_info)))
            for i, skill in enumerate(skills_info):
                st.session_state[f'skill_id_{i}'] = skill.get('id')
                st.session_state[f'skill_desc_{i}'] = skill.get('skill_name', '')
                st.session_state[f'skill_level_{i}'] = str(skill.get('skill_level', '1'))
                st.session_state[f'skill_note_{i}'] = skill.get('note', '')
        
        # 자격증 데이터 로드
        cert_info = load_certifications_info(st.session_state.user_email)
        if cert_info:
            for skill_idx, cert_data in cert_info.items():
                skill_idx = int(skill_idx)
                st.session_state.cert_counts[skill_idx] = cert_data.get('cert_count', 0)
                for j, cert in enumerate(cert_data.get('certifications', [])):
                    st.session_state[f'cert_id_{skill_idx}_{j}'] = cert.get('id')
                    st.session_state[f'certification_name_{skill_idx}_{j}'] = cert.get('certification_name', '')
                    st.session_state[f'cert_date_{skill_idx}_{j}'] = cert.get('issue_date', '')
                    st.session_state[f'cert_org_{skill_idx}_{j}'] = cert.get('issuing_agency', '')
        
        # 교육 데이터 로드
        training_info = load_training_info(st.session_state.user_email)
        if training_info:
            for skill_idx, train_data in training_info.items():
                skill_idx = int(skill_idx)
                st.session_state.train_counts[skill_idx] = train_data.get('train_count', 0)
                for j, train in enumerate(train_data.get('training', [])):
                    st.session_state[f'train_id_{skill_idx}_{j}'] = train.get('id')
                    st.session_state[f'train_{skill_idx}_{j}'] = train.get('description', '')
        
        st.session_state.skills_loaded = True
    
    st.markdown('<h3 class="main-header">이력관리</h3>', unsafe_allow_html=True)
    
    # 로그인 확인 및 이메일 가져오기
    if 'user_email' not in st.session_state:
        st.error("로그인이 필요합니다.")
        return
    
    login_email = st.session_state.user_email
    
    # DB에서 데이터 로드
    try:
        conn = connect_to_db()
        if conn is None:
            st.markdown("""
                <div style="padding: 1rem; background-color: #ffe9e9; border-radius: 0.5rem; margin: 1rem 0;">
                    데이터베이스에 접근할 수 없습니다. 관리자에게 문의해주세요.
                </div>
            """, unsafe_allow_html=True)
            data = {}
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tb_resume_personal_info WHERE login_email = %s", (login_email,))
            data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if data:
                st.markdown(f"""
                    <div style="padding: 1rem; background-color: #d8e6fd; border-radius: 0.5rem; margin: 1rem 0;">
                        {login_email} 님의 정보를 불러왔습니다.
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="padding: 1rem; background-color: #d8e6fd; border-radius: 0.5rem; margin: 1rem 0;">
                        더 자세한 정보를 입력하시면 좋은 이력서가 완성됩니다.
                    </div>
                """, unsafe_allow_html=True)
                data = {}
    except Exception as e:
        st.markdown(f"""
            <div style="padding: 1rem; background-color: #ffe9e9; border-radius: 0.5rem; margin: 1rem 0;">
                데이터베이스 접근 중 오류가 발생했습니다: {str(e)}
            </div>
        """, unsafe_allow_html=True)
        data = {}
    
    st.session_state.personal_info = data

    # 탭 생성
    tabs = st.tabs([
        "개인정보", "학력", "역량", "경력", "수상", "기타활동", "자기소개"
    ])
    
    # 개인정보 탭
    with tabs[0]:
        st.markdown(
            """
            <style>
            /* 메인 컨테이너 width 조정 */
            div[data-testid="stMainBlockContainer"] {
                max-width: 1500px !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                margin: 0 auto !important;
            }

            /* 폼 스타일링 */
            .stTextInput > label, 
            .stSelectbox > label, 
            .stDateInput > label,
            .stTextArea > label {
                font-size: 14px !important;
                font-weight: 500 !important;
            }
            
            /* 입력란 폰트 크기 */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > div,
            .stDateInput > div > div > input,
            .stTextArea > div > div > textarea,
            div[data-baseweb="input"] > input,
            div[data-baseweb="textarea"] > textarea,
            div[data-baseweb="select"] > div {
                font-size: 14px !important;
            }
            
            /* 입력란 배경색 조정 */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > div,
            .stDateInput > div > div > input,
            div[data-baseweb="input"] > input,
            div[data-baseweb="input"],
            div[data-baseweb="base-input"] {
                background-color: #F8F9FA !important;
            }

            /* 입력란 호버/포커스 시 배경색 */
            .stTextInput > div > div > input:hover,
            .stSelectbox > div > div > div:hover,
            .stDateInput > div > div > input:hover,
            div[data-baseweb="input"] > input:hover,
            div[data-baseweb="input"]:hover,
            div[data-baseweb="base-input"]:hover,
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > div:focus,
            .stDateInput > div > div > input:focus,
            div[data-baseweb="input"] > input:focus,
            div[data-baseweb="input"]:focus-within,
            div[data-baseweb="base-input"]:focus-within {
                background-color: #FFFFFF !important;
            }
            
            /* 버튼 스타일링 */
            div.stButton > button {
                width: 100% !important;
                height: 42px !important;
                margin: 0 !important;
                padding: 0.5rem !important;
                background-color: #4285F4 !important;
                color: white !important;
                font-size: 14px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                border-radius: 4px !important;
                transition: all 0.2s ease !important;
                border: 1px solid #4285F4 !important;
            }

            div.stButton > button:hover {
                background-color: #1967D2 !important;
                border-color: #1967D2 !important;
            }

            div.stButton > button:active {
                background-color: #1557B0 !important;
                border-color: #1557B0 !important;
            }

            /* 사이드바 스타일 */
            section[data-testid="stSidebar"] {
                background-color: #4285F4;
                width: 250px !important;
            }
            
            /* 이미지 컨테이너 스타일 */
            div.element-container:has(img) {
                padding: 0 !important;
                display: flex !important;
                justify-content: center !important;
            }
            
            img {
                width: 150px;
                margin-bottom: 3rem;
            }
            
            /* 사이드바 버튼 스타일 */
            section[data-testid="stSidebar"] .stButton > button {
                width: calc(100% + 4rem) !important;
                margin-left: -2rem !important;
                background-color: transparent !important;
                border: none !important;
                color: white !important;
                font-size: 1.1rem !important;
                padding: 0.5rem 2rem !important;
                display: flex !important;
                align-items: center !important;
                justify-content: flex-start !important;
                transition: all 0.2s ease !important;
                border-radius: 0 !important;
            }

            section[data-testid="stSidebar"] .stButton > button:hover {
                font-size: 2rem !important;
                font-weight: bold !important;
                background-color: rgba(255, 255, 255, 0.1) !important;
            }

            section[data-testid="stSidebar"] .stButton > button[aria-pressed="true"] {
                background-color: #0051FF !important;
                font-size: 2rem !important;
                font-weight: bold !important;
            }

            /* 모바일 화면 대응 */
            @media (max-width: 768px) {
                div[data-testid="stMainBlockContainer"] {
                    max-width: 100% !important;
                }
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # 인적사항 섹션
        st.markdown('<h5>인적사항</h5>', unsafe_allow_html=True)
        
        # 기존 데이터가 있다면 사용, 없다면 빈 값
        personal_info = st.session_state.personal_info
        
        # 한글 성/이름, 영문 성/이름, 국적, 성별, 생년월일 (1:1:1:1:2:1:1 = 8)
        cols = st.columns([1,1,1,1,2,1,1])
        with cols[0]:
            kr_last = st.text_input("한글 이름", value=personal_info.get('ko_lastname', ''), placeholder="성", key="kr_last")
        with cols[1]:
            kr_first = st.text_input(" ", value=personal_info.get('ko_firstname', ''), placeholder="이름", key="kr_first")
        with cols[2]:
            en_first = st.text_input("영문 이름", value=personal_info.get('en_firstname', ''), placeholder="firstname", key="en_first")
        with cols[3]:
            en_last = st.text_input(" ", value=personal_info.get('en_lastname', ''), placeholder="lastname", key="en_last")
        with cols[4]:
            nationality = st.text_input("국적", value=personal_info.get('nationality', '대한민국'), key="nationality")
        with cols[5]:
            gender = st.selectbox("성별", [None, "남성", "여성"], index=[None, "남성", "여성"].index(personal_info.get('gender', None)), key="gender")
        with cols[6]:
            birth_date = st.date_input("생년월일", value=personal_info.get('birth_date', None), key="birth_date")
        
        # 주소/이메일/연락처 (4:2:2 = 8)
        cols = st.columns([4, 2, 2])
        with cols[0]:
            address = st.text_input("주소", value=personal_info.get('address', ''), key="address")
        with cols[1]:
            email = st.text_input("이메일", value=personal_info.get('email', ''), key="email")
        with cols[2]:
            phone = st.text_input("연락처", value=personal_info.get('contact_number', ''), key="phone")
        
        # 사진 링크 (8 = 8)
        cols = st.columns([8])
        with cols[0]:
            photo_url = st.text_input("사진 링크", value=personal_info.get('photo_url', ''), key="photo_url")
        
        # 구분선 추가
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        
        # 병역 및 보훈 섹션
        st.markdown('<h5>병역 및 보훈</h5>', unsafe_allow_html=True)
        
        # 병역/군별/계급/보훈대상/복무시작일/복무종료일/전역유형 (1:1:1:1:1:1:2)
        cols = st.columns([1, 1, 1, 1, 1, 1, 2])
        with cols[0]:
            military_status = st.selectbox("병역", ["군필", "미필", "면제", "해당없음"], index=["군필", "미필", "면제", "해당없음"].index(personal_info.get('military_status', '군필')), key="military_service")
        
        # 군필일 경우에만 나머지 항목 표시
        if military_status == "군필":
            with cols[1]:
                military_branch = st.selectbox("군별", ["육군", "해군", "공군", "해병대", "의경", "공익", "기타"], index=["육군", "해군", "공군", "해병대", "의경", "공익", "기타"].index(personal_info.get('military_branch', '육군')), key="military_branch")
            with cols[2]:
                military_rank = st.selectbox("계급", ["이병", "일병", "상병", "병장", "하사", "중사", "상사", "원사", "준위", "소위", "중위", "대위", "소령", "중령", "대령"], index=["이병", "일병", "상병", "병장", "하사", "중사", "상사", "원사", "준위", "소위", "중위", "대위", "소령", "중령", "대령"].index(personal_info.get('military_rank', '이병')), key="military_rank")
            with cols[3]:
                veteran_status = st.selectbox("보훈대상", ["대상", "비대상"], index=["대상", "비대상"].index(personal_info.get('veteran_status', '대상')), key="veteran_status")
            with cols[4]:
                service_start = st.date_input("복무 시작일", value=personal_info.get('service_start', None), key="service_start")
            with cols[5]:
                service_end = st.date_input("복무 종료일", value=personal_info.get('service_end', None), key="service_end")
            with cols[6]:
                discharge_type = st.selectbox("전역 유형", ["만기전역", "의가사제대", "의병전역", "근무부적합", "기타"], index=["만기전역", "의가사제대", "의병전역", "근무부적합", "기타"].index(personal_info.get('discharge_type', '만기전역')), key="discharge_type")
        else:
            # 빈 칸으로 남기기 위한 처리
            for i in range(1, 7):
                with cols[i]:
                    st.empty()
        
        # 구분선 추가
        st.markdown("<div style='margin: 5rem 0;'></div>", unsafe_allow_html=True)

        # 저장 버튼 (우측 정렬, 1/8 크기)
        cols = st.columns(8)  # 8등분
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:
            if st.button("저장", key="save_personal", use_container_width=True):
                if 'user_email' not in st.session_state:
                    st.error("로그인이 필요합니다.")
                    return
                
                login_email = st.session_state.user_email
                
                # 입력된 데이터 수집
                data = {
                    'kr_last': kr_last,
                    'kr_first': kr_first,
                    'en_first': en_first,
                    'en_last': en_last,
                    'nationality': nationality,
                    'gender': gender,
                    'birth_date': birth_date,
                    'address': address,
                    'email': email,
                    'phone': phone,
                    'photo_url': photo_url,
                    'military_status': military_status,
                    'military_branch': military_branch if military_status == "군필" else None,
                    'military_rank': military_rank if military_status == "군필" else None,
                    'veteran_status': veteran_status if military_status == "군필" else None,
                    'service_start': service_start if military_status == "군필" else None,
                    'service_end': service_end if military_status == "군필" else None,
                    'discharge_type': discharge_type if military_status == "군필" else None
                }
                
                if save_personal_info(login_email, data):
                    show_success_message()
                else:
                    st.error("저장 중 오류가 발생했습니다.")

    # 학력 탭
    with tabs[1]:
        st.markdown(
            """
            <style>
            /* 학력 섹션 스타일링 - 여백만 유지 */
            div[data-testid="stVerticalBlock"] > div:has(> div.element-container:has(h5)):not(:first-child) {
                padding-top: 20px;
                margin-top: 20px;
            }

            div[data-testid="stVerticalBlock"] > div:has(> div.element-container:has(h5)) {
                padding-bottom: 20px;
                margin-bottom: 20px;
            }

            /* 도움말 아이콘과 툴팁 컨테이너 */
            .help-tooltip-container {
                position: relative;
                display: inline-block;
            }

            /* 도움말 아이콘 스타일링 */
            .help-icon {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background-color: #E0E0E0;
                color: #505050;
                font-size: 14px;
                margin-left: 8px;
                cursor: help;
                transition: background-color 0.3s;
            }

            .help-icon:hover {
                background-color: #4285F4;
                color: white;
            }

            /* 툴팁 스타일링 */
            .tooltip-text {
                visibility: hidden;
                position: absolute;
                z-index: 1000;
                width: 350px;
                background-color: #ffffff;
                color: #333333;
                text-align: left;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
                line-height: 1.6;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border: 1px solid #e0e0e0;
                
                /* 위치 조정 */
                bottom: 155%;
                left: 25px;
                
                /* 페이드 효과 */
                opacity: 0;
                transition: opacity 0.3s, visibility 0.3s;
            }

            /* 화살표 */
            .tooltip-text::after {
                content: "";
                position: absolute;
                top: 100%;
                left: 10px;
                margin-left: -5px;
                border-width: 8px;
                border-style: solid;
                border-color: #ffffff transparent transparent transparent;
                filter: drop-shadow(0 2px 2px rgba(0,0,0,0.1));
            }

            /* 호버 시 툴팁 표시 */
            .help-tooltip-container:hover .tooltip-text {
                visibility: visible;
                opacity: 1;
            }

            /* 도움말 컨테이너 스타일링 */
            .help-container {
                display: flex;
                align-items: center;
                margin-bottom: 1rem;
                position: relative;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # 학력 섹션 헤더와 도움말
        st.markdown(
            """
            <div class="help-container">
                <h5 style="margin: 0;">학력</h5>
                <div class="help-tooltip-container">
                    <div class="help-icon">?</div>
                    <div class="tooltip-text">
                        <strong style="font-size: 16px; color: #4285F4;">학위 변경 시나리오 안내</strong>
                        <div style="margin-top: 12px;">
                            <div style="margin-bottom: 15px;">
                                <strong style="color: #4285F4;">1. 학위 변경만 원할 경우:</strong><br>
                                • 기존 전공의 학위 정보만 변경<br>
                                • 예: 경영학부 회계재무학과 학사 → 석사
                            </div>
                            <div style="margin-bottom: 15px;">
                                <strong style="color: #4285F4;">2. 같은 학력에 전공 추가:</strong><br>
                                • '전공 추가' 버튼 사용<br>
                                • 예: 경영학부 회계재무학과(학사) + 재무회계(석사)
                            </div>
                            <div>
                                <strong style="color: #4285F4;">3. 새로운 학력 추가:</strong><br>
                                • '학력 추가' 버튼 사용<br>
                                • 예: 학사(2019-2023) + 석사(2023-2025)
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
        
        # 로그인 확인
        if 'user_email' not in st.session_state:
            st.error("로그인이 필요합니다.")
            return
            
        # 기존 데이터 로드
        if 'education_loaded' not in st.session_state:
            educations, error = load_education_info(st.session_state.user_email)
            if error:
                st.error(error)
            elif educations:
                # 기존 데이터로 session_state 초기화
                st.session_state.education_data = []
                st.session_state.major_counts = {}
                
                for idx, edu in enumerate(educations):
                    st.session_state.education_data.append(idx)
                    st.session_state[f'education_id_{idx}'] = edu['id']
                    st.session_state[f'admission_date_{idx}'] = edu['start_date']
                    st.session_state[f'graduation_date_{idx}'] = edu['end_date']
                    st.session_state[f'institution_{idx}'] = edu['institution']
                    st.session_state[f'notes_{idx}'] = edu['note']
                    
                    # 전공 정보 설정
                    st.session_state.major_counts[idx] = len(edu['majors'])
                    for major_idx, major in enumerate(edu['majors']):
                        st.session_state[f'department_{idx}_{major_idx}'] = major['department']
                        st.session_state[f'major_{idx}_{major_idx}'] = major['major']
                        st.session_state[f'degree_{idx}_{major_idx}'] = major['degree']
                        st.session_state[f'gpa_{idx}_{major_idx}'] = major['gpa']
                
                st.session_state.education_count = len(educations)
            else:
                # 초기 상태 설정
                st.session_state.education_count = 1
                st.session_state.education_data = [0]
                st.session_state.major_counts = {0: 1}
            
            st.session_state.education_loaded = True
        
        # 학력 카운터 초기화
        if 'education_count' not in st.session_state:
            st.session_state.education_count = 1
        
        # 전공 카운터 초기화
        if 'major_counts' not in st.session_state:
            st.session_state.major_counts = {0: 1}

        # 학력 데이터 초기화
        if 'education_data' not in st.session_state:
            st.session_state.education_data = list(range(st.session_state.education_count))

        # 각 학력 정보 입력 폼
        for idx, i in enumerate(st.session_state.education_data):
            if idx > 0:
                st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
            
            # 입학년월/졸업년월/교육기관/학력삭제 버튼 (2:2:3:1 = 8)
            cols = st.columns([2, 2, 3, 1])
            with cols[0]:
                st.date_input("입학년월", value=personal_info.get(f'admission_date_{i}', None), key=f"admission_date_{i}")
            with cols[1]:
                st.date_input("졸업년월", value=personal_info.get(f'graduation_date_{i}', None), key=f"graduation_date_{i}")
            with cols[2]:
                st.text_input("교육기관", value=personal_info.get(f'institution_{i}', ''), key=f"institution_{i}")
            with cols[3]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if len(st.session_state.education_data) > 1:
                    if st.button("학력 삭제", key=f"delete_education_{i}", use_container_width=True):
                        if st.session_state.get(f'education_id_{i}'):  # 기존 데이터인 경우
                            if delete_education(st.session_state[f'education_id_{i}'], st.session_state.user_email):
                                st.session_state.education_data.remove(i)
                                if i in st.session_state.major_counts:
                                    del st.session_state.major_counts[i]
                                st.session_state.education_loaded = False  # 다시 로드하도록 설정
                                st.rerun()
                        else:  # 새로 추가했다가 삭제하는 경우
                            st.session_state.education_data.remove(i)
                            if i in st.session_state.major_counts:
                                del st.session_state.major_counts[i]
                            if len(st.session_state.education_data) == 0:
                                st.session_state.education_count = 1
                                st.session_state.education_data = [0]
                                st.session_state.major_counts = {0: 1}
                            st.rerun()

            # 전공 정보 (여러 개 추가 가능)
            if i not in st.session_state.major_counts:
                st.session_state.major_counts[i] = 1

            for j in range(st.session_state.major_counts[i]):
                if j > 0:
                    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
                
                # 학부/전공/학위/성적/삭제/추가 버튼 (2:2:1:1:1:1 = 8)
                cols = st.columns([2, 2, 1, 1, 1, 1])
                with cols[0]:
                    st.text_input("학부 또는 분야", value=personal_info.get(f'department_{i}_{j}', ''), key=f"department_{i}_{j}")
                with cols[1]:
                    st.text_input("학과, 전공, 세부내용", value=personal_info.get(f'major_{i}_{j}', ''), key=f"major_{i}_{j}")
                with cols[2]:
                    st.selectbox("학위", ["선택", "고등학교 졸업", "전문학사", "학사", "석사", "박사"], index=["선택", "고등학교 졸업", "전문학사", "학사", "석사", "박사"].index(personal_info.get(f'degree_{i}_{j}', '선택')), key=f"degree_{i}_{j}")
                with cols[3]:
                    st.text_input("성적", value=personal_info.get(f'gpa_{i}_{j}', ''), placeholder="예: 4.0/4.3", key=f"gpa_{i}_{j}")
                with cols[4]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.session_state.major_counts[i] > 1:
                        if st.button("전공 삭제", key=f"delete_major_{i}_{j}", use_container_width=True):
                            st.session_state.major_counts[i] -= 1
                            st.rerun()
                with cols[5]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.button("전공 추가", key=f"add_major_{i}_{j}", use_container_width=True):
                        st.session_state.major_counts[i] += 1
                        st.rerun()
            
            # 비고
            st.text_area("비고", value=personal_info.get(f'notes_{i}', ''), key=f"notes_{i}", height=100)

        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

        # 학력 추가 버튼 (1:7 = 8, left align)
        cols = st.columns(8)
        with cols[0]:
            if st.button("학력 추가", use_container_width=True):
                new_idx = max(st.session_state.education_data) + 1 if st.session_state.education_data else 0
                st.session_state.education_data.append(new_idx)
                st.session_state.major_counts[new_idx] = 1
                st.session_state.education_count += 1
                st.rerun()

        # 저장 버튼 (7:1)
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_education_tab", use_container_width=True):
                if 'user_email' not in st.session_state:
                    st.error("로그인이 필요합니다.")
                    return
                
                # 현재 입력된 모든 학력 데이터 수집
                education_data = {}
                for i in st.session_state.education_data:
                    education_data[i] = {
                        'id': st.session_state.get(f'education_id_{i}'),
                        'admission_date': st.session_state[f'admission_date_{i}'],
                        'graduation_date': st.session_state[f'graduation_date_{i}'],
                        'institution': st.session_state[f'institution_{i}'],
                        'notes': st.session_state[f'notes_{i}'],
                        'major_count': st.session_state.major_counts[i]
                    }
                    
                    # 각 전공 정보 추가
                    for j in range(st.session_state.major_counts[i]):
                        education_data[i][f'department_{j}'] = st.session_state[f'department_{i}_{j}']
                        education_data[i][f'major_{j}'] = st.session_state[f'major_{i}_{j}']
                        education_data[i][f'degree_{j}'] = st.session_state[f'degree_{i}_{j}']
                        education_data[i][f'gpa_{j}'] = st.session_state[f'gpa_{i}_{j}']
                
                # 디버깅을 위한 데이터 출력
                st.write("저장할 데이터:", education_data)
                
                if save_education_info(st.session_state.user_email, education_data):
                    show_success_message()
                    # 저장 성공 시 데이터 다시 로드하도록 설정
                    st.session_state.education_loaded = False
                    st.rerun()
                else:
                    st.error("저장 중 오류가 발생했습니다.")

    # 역량 탭
    with tabs[2]:
        st.markdown(
            """
            <style>
            /* 역량 섹션 스타일링 - 여백만 유지 */
            div[data-testid="stVerticalBlock"] > div:has(> div.element-container:has(h5)):not(:first-child) {
                padding-top: 20px;
                margin-top: 20px;
            }

            div[data-testid="stVerticalBlock"] > div:has(> div.element-container:has(h5)) {
                padding-bottom: 20px;
                margin-bottom: 20px;
            }

            /* 역량 탭의 버튼 스타일 (저장 버튼 제외) */
            div[data-testid="stHorizontalBlock"] div.stButton > button:not([kind="primary"]) {
                background-color: transparent !important;
                color: #4285F4 !important;
                border: 1px solid #4285F4 !important;
            }

            div[data-testid="stHorizontalBlock"] div.stButton > button:not([kind="primary"]):hover {
                background-color: #F8F9FA !important;
                color: #1967D2 !important;
                border-color: #1967D2 !important;
            }

            div[data-testid="stHorizontalBlock"] div.stButton > button:not([kind="primary"]):active {
                background-color: #F1F3F4 !important;
                color: #1557B0 !important;
                border-color: #1557B0 !important;
            }

            /* 성공 메시지 스타일 수정 */
            div.element-container div[data-testid="stMarkdownContainer"] div.stSuccess {
                background-color: #d8e6fd !important;
                color: #1967D2 !important;
                border: none !important;
                border-radius: 0.5rem !important;
                padding: 1rem !important;
                margin: 1rem 0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # 로그인 확인
        if 'user_email' not in st.session_state:
            st.error("로그인이 필요합니다.")
            return

        # 기술 필드 초기화
        if 'skill_fields' not in st.session_state:
            st.session_state.skill_fields = [0]

        st.markdown('<h5>기술 및 역량</h5>', unsafe_allow_html=True)

        # 기술 및 역량 입력 폼
        for idx in st.session_state.skill_fields:
            cols = st.columns([2, 1, 4, 2])
            with cols[0]:
                st.text_input("기술 및 역량", key=f"skill_desc_{idx}")
            with cols[1]:
                st.selectbox(
                    "성취 수준",
                    ["1", "2", "3", "4", "5"],
                    key=f"skill_level_{idx}",
                    help="1: 기초 수준, 2: 초급 수준, 3: 중급 수준, 4: 고급 수준, 5: 전문가 수준"
                )
            with cols[2]:
                st.text_input("비고", key=f"skill_note_{idx}")
            with cols[3]:
                bcols = st.columns(2)
                with bcols[0]:
                    if len(st.session_state.skill_fields) > 1:
                        if st.button("기술 삭제", key=f"delete_skill_{idx}", use_container_width=True):
                            st.session_state.skill_fields.remove(idx)
                            st.rerun()
                    else:
                        st.empty()
                with bcols[1]:
                    if st.button("기술 추가", key=f"add_skill_{idx}", use_container_width=True):
                        new_idx = max(st.session_state.skill_fields) + 1 if st.session_state.skill_fields else 0
                        st.session_state.skill_fields.append(new_idx)
                        st.rerun()

        st.markdown("<hr style='margin: 2rem 0; border-top: 2px solid #eee;'>", unsafe_allow_html=True)

        # 자격증 섹션
        st.markdown('<div class="section-header">자격증</div>', unsafe_allow_html=True)
        
        # 자격증 필드 초기화
        if 'cert_fields' not in st.session_state:
            certifications = load_certifications_info(st.session_state.user_email)  # DB에서 불러오기
            print(certifications)
            if certifications:
                st.session_state.cert_fields = list(certifications.keys())
                for cert_idx, cert in certifications.items():
                    st.session_state[f'certification_name_{cert_idx}'] = cert['certification_name']
                    st.session_state[f'cert_date_{cert_idx}'] = cert['issue_date']
                    st.session_state[f'cert_org_{cert_idx}'] = cert['issuing_agency']
            else:
                st.session_state.cert_fields = [0]
        
        # 자격증 입력 필드들
        for cert_idx in st.session_state.cert_fields:
            if cert_idx > 0:
                st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            
            # 자격증 (3:2:2:1:1)
            cols = st.columns([3, 2, 2, 1, 1])
            with cols[0]:
                st.text_input("자격증명", key=f"certification_name_{cert_idx}",
                            placeholder="예: 정보처리기사")
            with cols[1]:
                st.date_input("취득일", key=f"cert_date_{cert_idx}")
            with cols[2]:
                st.text_input("발급기관", key=f"cert_org_{cert_idx}",
                            placeholder="예: 한국산업인력공단")
            with cols[3]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if len(st.session_state.cert_fields) > 1:
                    if st.button("자격증 삭제", key=f"delete_cert_{cert_idx}", use_container_width=True):
                        st.session_state.cert_fields.remove(cert_idx)
                        st.rerun()
                else:
                    st.empty()
            with cols[4]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if st.button("자격증 추가", key=f"add_cert_{cert_idx}", use_container_width=True):
                    new_idx = max(st.session_state.cert_fields) + 1 if st.session_state.cert_fields else 0
                    st.session_state.cert_fields.append(new_idx)
                    st.rerun()

        st.markdown("<hr style='margin: 2rem 0; border-top: 2px solid #eee;'>", unsafe_allow_html=True)

        # 교육 섹션
        st.markdown('<div class="section-header">교육: 훈련, 연수, 유학 등</div>', unsafe_allow_html=True)
        
        # 교육 필드 초기화
        if 'train_fields' not in st.session_state:
            trainings = load_training_info(st.session_state.user_email)  # DB에서 불러오기
            if trainings:
                st.session_state.train_fields = list(trainings.keys())
                for train_idx, train in trainings.items():
                    st.session_state[f'traincation_{train_idx}'] = train['description']
            else:
                st.session_state.train_fields = [0]
        
        # 교육 입력 필드들
        for train_idx in st.session_state.train_fields:
            if train_idx > 0:
                st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            
            # 교육 (6:1:1)
            cols = st.columns([6, 1, 1])
            with cols[0]:
                st.text_area("교육 내용", key=f"traincation_{train_idx}", 
                           height=100,
                           placeholder="교육명:\n교육기관:\n교육기간:\n교육내용:")
            with cols[1]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if len(st.session_state.train_fields) > 1:
                    if st.button("교육 삭제", key=f"delete_train_{train_idx}", use_container_width=True):
                        st.session_state.train_fields.remove(train_idx)
                        st.rerun()
                else:
                    st.empty()
            with cols[2]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if st.button("교육 추가", key=f"add_train_{train_idx}", use_container_width=True):
                    new_idx = max(st.session_state.train_fields) + 1 if st.session_state.train_fields else 0
                    st.session_state.train_fields.append(new_idx)
                    st.rerun()

        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

        # 저장 버튼 (7:1)
        cols = st.columns(8)
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_skill_tab", use_container_width=True):
                if 'user_email' not in st.session_state:
                    st.error("로그인이 필요합니다.")
                    return
                
                # 현재 입력된 모든 데이터 수집
                success = True
                
                # 기술 및 역량 데이터 수집
                skills_data = {}
                for idx in st.session_state.skill_fields:
                    skill_name = st.session_state.get(f'skill_desc_{idx}', '').strip()
                    skill_level = st.session_state.get(f'skill_level_{idx}')
                    
                    if not skill_name:
                        st.warning(f"{idx+1}번째 기술의 '기술 및 역량' 항목이 비어 있습니다.")
                        success = False
                        continue
                    
                    if not skill_level or skill_level not in ["1", "2", "3", "4", "5"]:
                        st.warning(f"{idx+1}번째 기술의 성취 수준이 유효하지 않습니다.")
                        success = False
                        continue
                    
                    skills_data[idx] = {
                        'skill_name': skill_name,
                        'skill_level': int(skill_level),
                        'note': st.session_state.get(f'skill_note_{idx}', '')
                    }
                
                # 자격증 데이터 수집
                certifications_data = {}
                for idx in st.session_state.cert_fields:
                    cert_name = st.session_state.get(f'certification_name_{idx}', '').strip()
                    cert_date = st.session_state.get(f'cert_date_{idx}')
                    cert_org = st.session_state.get(f'cert_org_{idx}', '').strip()
                    
                    if cert_name or cert_date or cert_org:  # 하나라도 입력된 경우
                        if not cert_name:
                            st.warning(f"{idx+1}번째 자격증의 자격증명이 비어 있습니다.")
                            success = False
                            continue
                        
                        if not cert_date:
                            st.warning(f"{idx+1}번째 자격증의 취득일이 비어 있습니다.")
                            success = False
                            continue
                        
                        if not cert_org:
                            st.warning(f"{idx+1}번째 자격증의 발급기관이 비어 있습니다.")
                            success = False
                            continue
                        
                        certifications_data[idx] = {
                            'certification_name': cert_name,
                            'issue_date': cert_date,
                            'issuing_agency': cert_org
                        }
                
                # 교육 데이터 수집
                training_data = {}
                for idx in st.session_state.train_fields:
                    train_desc = st.session_state.get(f'traincation_{idx}', '').strip()
                    
                    if train_desc:  # 입력된 경우만 저장
                        training_data[idx] = {
                            'description': train_desc
                        }
                
                if success:
                    if not save_skills_info(st.session_state.user_email, skills_data):
                        st.error("기술 및 역량 정보 저장 중 오류가 발생했습니다.")
                        success = False
                    
                    if not save_certifications_info(st.session_state.user_email, certifications_data):
                        st.error("자격증 정보 저장 중 오류가 발생했습니다.")
                        success = False
                    
                    if not save_training_info(st.session_state.user_email, training_data):
                        st.error("교육 정보 저장 중 오류가 발생했습니다.")
                        success = False
                    
                    if success:
                        show_success_message()
                        st.rerun()

    # 경력 탭
    with tabs[3]:
        st.markdown(
            """
            <style>
            /* 경력 섹션 스타일링 - 여백만 유지 */
            div[data-testid="stVerticalBlock"] > div:has(> div.element-container:has(h5)):not(:first-child) {
                padding-top: 20px;
                margin-top: 20px;
            }

            div[data-testid="stVerticalBlock"] > div:has(> div.element-container:has(h5)) {
                padding-bottom: 20px;
                margin-bottom: 20px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<h5>경력</h5>', unsafe_allow_html=True)
        
        # 로그인 확인
        if 'user_email' not in st.session_state:
            st.error("로그인이 필요합니다.")
            return
        
        # 경력 데이터 로드
        if 'career_loaded' not in st.session_state:
            careers, error = load_career_info(st.session_state.user_email)
            if error:
                st.error(error)
            elif careers:
                # 기존 데이터로 session_state 초기화
                st.session_state.career_data = []
                st.session_state.position_counts = {}
                
                for idx, career in enumerate(careers):
                    st.session_state.career_data.append(idx)
                    st.session_state[f'career_id_{idx}'] = career['id']
                    st.session_state[f'company_{idx}'] = career['company_name']
                    st.session_state[f'join_date_{idx}'] = career['join_date']
                    st.session_state[f'leave_date_{idx}'] = career['leave_date']
                    st.session_state[f'leave_reason_{idx}'] = career['leave_reason']
                    
                    # 직위 정보 로드
                    positions, pos_error = load_position_info(career['id'])
                    if not pos_error and positions:
                        st.session_state.position_counts[idx] = len(positions)
                        for pos_idx, position in enumerate(positions):
                            st.session_state[f'position_id_{idx}_{pos_idx}'] = position['id']
                            st.session_state[f'position_{idx}_{pos_idx}'] = position['position']
                            st.session_state[f'promotion_date_{idx}_{pos_idx}'] = position['promotion_date']
                            st.session_state[f'retirement_date_{idx}_{pos_idx}'] = position['retirement_date']
                            st.session_state[f'description_{idx}_{pos_idx}'] = position['description']
                    else:
                        st.session_state.position_counts[idx] = 1
                        # 빈 직위 정보 초기화
                        st.session_state[f'position_{idx}_0'] = ''
                        st.session_state[f'promotion_date_{idx}_0'] = None
                        st.session_state[f'retirement_date_{idx}_0'] = None
                        st.session_state[f'description_{idx}_0'] = ''
                
                st.session_state.career_count = len(careers)
            else:
                # 초기 상태 설정
                st.session_state.career_count = 1
                st.session_state.career_data = [0]
                st.session_state.position_counts = {0: 1}
                # 빈 데이터 초기화
                st.session_state['company_0'] = ''
                st.session_state['join_date_0'] = None
                st.session_state['leave_date_0'] = None
                st.session_state['leave_reason_0'] = ''
                st.session_state['position_0_0'] = ''
                st.session_state['promotion_date_0_0'] = None
                st.session_state['retirement_date_0_0'] = None
                st.session_state['description_0_0'] = ''
            
            st.session_state.career_loaded = True
        
        # 경력 카운터 초기화
        if 'career_count' not in st.session_state:
            st.session_state.career_count = 1
        
        # 직위 카운터 초기화
        if 'position_counts' not in st.session_state:
            st.session_state.position_counts = {0: 1}
        
        # 경력 데이터 초기화
        if 'career_data' not in st.session_state:
            st.session_state.career_data = list(range(st.session_state.career_count))

        # 각 경력 정보 입력 폼
        for idx, i in enumerate(st.session_state.career_data):
            if idx > 0:
                st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
            
            # 회사명/입사년월/퇴사년월/퇴사사유/경력삭제 (2:1:1:3:1)
            cols = st.columns([2, 1, 1, 3, 1])
            with cols[0]:
                st.text_input("회사명", key=f"company_{i}")
            with cols[1]:
                st.date_input("입사년월", key=f"join_date_{i}")
            with cols[2]:
                st.date_input("퇴사년월", key=f"leave_date_{i}")
            with cols[3]:
                st.text_input("퇴사사유", key=f"leave_reason_{i}")
            with cols[4]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if len(st.session_state.career_data) > 1:
                    if st.button("경력 삭제", key=f"delete_career_{i}", use_container_width=True):
                        if st.session_state.get(f'career_id_{i}'):  # 기존 데이터인 경우
                            if delete_career(st.session_state[f'career_id_{i}'], st.session_state.user_email):
                                st.session_state.career_data.remove(i)
                                if i in st.session_state.position_counts:
                                    del st.session_state.position_counts[i]
                                st.session_state.career_loaded = False
                                st.rerun()
                        else:  # 새로 추가했다가 삭제하는 경우
                            st.session_state.career_data.remove(i)
                            if len(st.session_state.career_data) == 0:
                                st.session_state.career_count = 1
                                st.session_state.career_data = [0]
                                st.session_state.position_counts = {0: 1}
                            st.rerun()
            
            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            
            # 직위 정보 섹션
            if i not in st.session_state.position_counts:
                st.session_state.position_counts[i] = 1

            for pos_idx in range(st.session_state.position_counts[i]):
                if pos_idx > 0:
                    st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
                
                # 직위/취임일/퇴임일/삭제/추가 (2:1:1:1:1)
                cols = st.columns([2, 1, 1, 1, 1])
                with cols[0]:
                    st.text_input("직위/직책", key=f"position_{i}_{pos_idx}")
                with cols[1]:
                    st.date_input("취임일", key=f"promotion_date_{i}_{pos_idx}")
                with cols[2]:
                    st.date_input("퇴임일", key=f"retirement_date_{i}_{pos_idx}")
                with cols[3]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.session_state.position_counts[i] > 1:
                        if st.button("직위 삭제", key=f"delete_position_{i}_{pos_idx}", use_container_width=True):
                            position_id = st.session_state.get(f'position_id_{i}_{pos_idx}')
                            career_id = st.session_state.get(f'career_id_{i}')
                            
                            if position_id and career_id:  # 기존 데이터인 경우
                                if delete_position(position_id, career_id):
                                    # 세션에서 해당 직위 정보 제거
                                    for key in [f'position_id_{i}_{pos_idx}', 
                                              f'position_{i}_{pos_idx}',
                                              f'promotion_date_{i}_{pos_idx}',
                                              f'retirement_date_{i}_{pos_idx}',
                                              f'description_{i}_{pos_idx}']:
                                        if key in st.session_state:
                                            del st.session_state[key]
                                    
                                    # 남은 직위 정보 재정렬
                                    for j in range(pos_idx + 1, st.session_state.position_counts[i]):
                                        for key_suffix in ['position_id', 'position', 'promotion_date', 'retirement_date', 'description']:
                                            old_key = f'{key_suffix}_{i}_{j}'
                                            new_key = f'{key_suffix}_{i}_{j-1}'
                                            if old_key in st.session_state:
                                                st.session_state[new_key] = st.session_state[old_key]
                                                del st.session_state[old_key]
                                    
                                    st.session_state.position_counts[i] -= 1
                                    st.rerun()
                            else:  # 새로 추가했다가 삭제하는 경우
                                # 세션에서 해당 직위 정보 제거
                                for key in [f'position_{i}_{pos_idx}',
                                          f'promotion_date_{i}_{pos_idx}',
                                          f'retirement_date_{i}_{pos_idx}',
                                          f'description_{i}_{pos_idx}']:
                                    if key in st.session_state:
                                        del st.session_state[key]
                                
                                # 남은 직위 정보 재정렬
                                for j in range(pos_idx + 1, st.session_state.position_counts[i]):
                                    for key_suffix in ['position', 'promotion_date', 'retirement_date', 'description']:
                                        old_key = f'{key_suffix}_{i}_{j}'
                                        new_key = f'{key_suffix}_{i}_{j-1}'
                                        if old_key in st.session_state:
                                            st.session_state[new_key] = st.session_state[old_key]
                                            del st.session_state[old_key]
                                
                                st.session_state.position_counts[i] -= 1
                                st.rerun()
                with cols[4]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.button("직위 추가", key=f"add_position_{i}_{pos_idx}", use_container_width=True):
                        st.session_state.position_counts[i] += 1
                        # 새 직위 필드 초기화
                        new_idx = st.session_state.position_counts[i] - 1
                        st.session_state[f'position_{i}_{new_idx}'] = ''
                        st.session_state[f'promotion_date_{i}_{new_idx}'] = None
                        st.session_state[f'retirement_date_{i}_{new_idx}'] = None
                        st.session_state[f'description_{i}_{new_idx}'] = ''
                        st.rerun()
                
                # 업무내용 (8)
                cols = st.columns([8])
                with cols[0]:
                    st.text_area("업무내용", key=f"description_{i}_{pos_idx}", height=100)

        # 경력 추가 버튼 (1:7)
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        with cols[0]:
            if st.button("경력 추가", use_container_width=True):
                new_idx = max(st.session_state.career_data) + 1 if st.session_state.career_data else 0
                st.session_state.career_data.append(new_idx)
                st.session_state.position_counts[new_idx] = 1
                st.session_state.career_count += 1
                st.rerun()

        # 저장 버튼 (7:1)
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_career_tab", use_container_width=True):
                if 'user_email' not in st.session_state:
                    st.error("로그인이 필요합니다.")
                    return
                
                # 현재 입력된 모든 경력 데이터 수집
                career_data = {}
                for i in st.session_state.career_data:
                    career_data[i] = {
                        'id': st.session_state.get(f'career_id_{i}'),
                        'company': st.session_state[f'company_{i}'],
                        'join_date': st.session_state[f'join_date_{i}'],
                        'leave_date': st.session_state[f'leave_date_{i}'],
                        'leave_reason': st.session_state[f'leave_reason_{i}']
                    }
                
                success = True
                # 먼저 경력 정보 저장
                saved_career_ids, error = save_career_info(st.session_state.user_email, career_data)
                if saved_career_ids:
                    # 각 경력에 대한 직위 정보 저장
                    for i in st.session_state.career_data:
                        career_id = saved_career_ids.get(i)
                        if career_id:
                            position_data = {}
                            for j in range(st.session_state.position_counts[i]):
                                position_data[j] = {
                                    'id': st.session_state.get(f'position_id_{i}_{j}'),
                                    'position': st.session_state[f'position_{i}_{j}'],
                                    'promotion_date': st.session_state[f'promotion_date_{i}_{j}'],
                                    'retirement_date': st.session_state[f'retirement_date_{i}_{j}'],
                                    'description': st.session_state[f'description_{i}_{j}']
                                }
                            
                            if not save_position_info(career_id, position_data):
                                st.error(f"{st.session_state[f'company_{i}']} 회사의 직위 정보 저장 중 오류가 발생했습니다.")
                                success = False
                    
                    if success:
                        show_success_message()
                        # 저장 성공 시 데이터 다시 로드하도록 설정
                        st.session_state.career_loaded = False
                        st.rerun()
                else:
                    st.error(f"경력 정보 저장 중 오류가 발생했습니다: {error}")

    # 수상 탭
    with tabs[4]:
        st.markdown('<h5 class="main-header">수상</h5>', unsafe_allow_html=True)
        
        # 로그인 확인
        if 'user_email' not in st.session_state:
            st.error("로그인이 필요합니다.")
            return
        
        # 수상 데이터 로드
        if 'award_loaded' not in st.session_state:
            awards, error = load_award_info(st.session_state.user_email)
            if error:
                st.error(error)
            elif awards:
                # 기존 데이터로 session_state 초기화
                st.session_state.award_data = []
                
                for idx, award in enumerate(awards):
                    st.session_state.award_data.append(idx)
                    st.session_state[f'award_id_{idx}'] = award['id']
                    st.session_state[f'award_name_{idx}'] = award['award_name']
                    st.session_state[f'award_date_{idx}'] = award['award_date']
                    st.session_state[f'awarding_body_{idx}'] = award['awarding_body']
                    st.session_state[f'award_note_{idx}'] = award['award_note']
                
                st.session_state.award_count = len(awards)
            else:
                # 초기 상태 설정
                st.session_state.award_count = 1
                st.session_state.award_data = [0]
                # 빈 데이터 초기화
                st.session_state['award_name_0'] = ''
                st.session_state['award_date_0'] = None
                st.session_state['awarding_body_0'] = ''
                st.session_state['award_note_0'] = ''
            
            st.session_state.award_loaded = True
        
        # 수상 카운터 초기화
        if 'award_count' not in st.session_state:
            st.session_state.award_count = 1
        
        # 수상 데이터 초기화
        if 'award_data' not in st.session_state:
            st.session_state.award_data = list(range(st.session_state.award_count))
        
        # 각 수상 정보 입력 폼
        for idx, i in enumerate(st.session_state.award_data):
            if idx > 0:
                st.markdown("<hr>", unsafe_allow_html=True)
            
            # 수상명/수상일/수여기관/삭제 버튼 (3:2:2:1 = 8)
            cols = st.columns([3, 2, 2, 1])
            with cols[0]:
                st.text_input("수상명", key=f"award_name_{i}")
            with cols[1]:
                st.date_input("수상일", key=f"award_date_{i}")
            with cols[2]:
                st.text_input("수여기관", key=f"awarding_body_{i}")
            with cols[3]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if len(st.session_state.award_data) > 1:
                    if st.button("삭제", key=f"delete_award_{i}", use_container_width=True):
                        # 기존 수상 정보인 경우 DB에서도 삭제
                        award_id = st.session_state.get(f'award_id_{i}')
                        if award_id:
                            if delete_award(award_id, st.session_state.user_email):
                                st.session_state.award_data.remove(i)
                                st.session_state.award_count -= 1
                                st.session_state.award_loaded = False
                                st.rerun()
                            else:
                                st.error("수상 정보 삭제 중 오류가 발생했습니다.")
                        else:
                            # 새로 추가된 수상 정보인 경우 세션에서만 삭제
                            st.session_state.award_data.remove(i)
                            st.session_state.award_count -= 1
                            st.rerun()
            
            # 비고 (8)
            st.text_area("비고", key=f"award_note_{i}", height=100)
        
        # 수상 추가/저장 버튼 (1:7)
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        with cols[0]:
            if st.button("수상 추가", use_container_width=True):
                new_idx = max(st.session_state.award_data) + 1 if st.session_state.award_data else 0
                st.session_state.award_data.append(new_idx)
                st.session_state.award_count += 1
                # 새 수상 정보 필드 초기화
                st.session_state[f'award_name_{new_idx}'] = ''
                st.session_state[f'award_date_{new_idx}'] = None
                st.session_state[f'awarding_body_{new_idx}'] = ''
                st.session_state[f'award_note_{new_idx}'] = ''
                st.rerun()
        
        # 저장 버튼 (7:1)
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_award_tab", use_container_width=True):
                if 'user_email' not in st.session_state:
                    st.error("로그인이 필요합니다.")
                    return
                
                # 현재 입력된 모든 수상 데이터 수집
                award_data = {}
                for i in st.session_state.award_data:
                    award_name = st.session_state.get(f'award_name_{i}', '').strip()
                    award_date = st.session_state.get(f'award_date_{i}')
                    awarding_body = st.session_state.get(f'awarding_body_{i}', '').strip()
                    
                    if award_name or award_date or awarding_body:
                        award_data[i] = {
                            'id': st.session_state.get(f'award_id_{i}'),
                            'award_name': award_name,
                            'award_date': award_date,
                            'awarding_body': awarding_body,
                            'note': st.session_state.get(f'award_note_{i}', '').strip()
                        }
                
                if save_award_info(st.session_state.user_email, award_data):
                    show_success_message()
                    st.session_state.award_loaded = False
                    st.rerun()
                else:
                    st.error("저장 중 오류가 발생했습니다.")

    # 기타활동 탭
    with tabs[5]:
        st.markdown('<h5 class="main-header">기타활동</h5>', unsafe_allow_html=True)
        
        # 로그인 확인
        if 'user_email' not in st.session_state:
            st.error("로그인이 필요합니다.")
            return
        
        # 기타활동 데이터 로드
        if 'activities_loaded' not in st.session_state:
            activities, error = load_activities_info(st.session_state.user_email)
            if error:
                st.error(error)
            elif activities:
                # 기존 데이터로 session_state 초기화
                st.session_state.activities_data = []
                
                for idx, activity in enumerate(activities):
                    st.session_state.activities_data.append(idx)
                    st.session_state[f'activity_id_{idx}'] = activity['id']
                    st.session_state[f'activity_name_{idx}'] = activity['activity_name']
                    st.session_state[f'organization_{idx}'] = activity['organization']
                    st.session_state[f'start_date_{idx}'] = activity['start_date']
                    st.session_state[f'end_date_{idx}'] = activity['end_date']
                    st.session_state[f'role_{idx}'] = activity['role']
                    st.session_state[f'link_{idx}'] = activity['link']
                    st.session_state[f'details_{idx}'] = activity['details']
                
                st.session_state.activities_count = len(activities)
            else:
                # 초기 상태 설정
                st.session_state.activities_count = 1
                st.session_state.activities_data = [0]
                # 빈 데이터 초기화
                st.session_state['activity_name_0'] = ''
                st.session_state['organization_0'] = ''
                st.session_state['start_date_0'] = None
                st.session_state['end_date_0'] = None
                st.session_state['role_0'] = ''
                st.session_state['link_0'] = ''
                st.session_state['details_0'] = ''
            
            st.session_state.activities_loaded = True
        
        # 활동 카운터 초기화
        if 'activities_count' not in st.session_state:
            st.session_state.activities_count = 1
        
        # 활동 데이터 초기화
        if 'activities_data' not in st.session_state:
            st.session_state.activities_data = list(range(st.session_state.activities_count))

        # 각 활동 정보 입력 폼
        for idx, i in enumerate(st.session_state.activities_data):
            if idx > 0:
                st.markdown("<hr>", unsafe_allow_html=True)
            
            # 활동명/소속/시작일/종료일/직책/링크/상세내용/삭제 버튼
            cols1 = st.columns([2, 2])
            with cols1[0]:
                st.text_input("활동명", key=f"activity_name_{i}")
            with cols1[1]:
                st.text_input("소속", key=f"organization_{i}")
            
            cols2 = st.columns([1, 1, 1, 1])
            with cols2[0]:
                st.date_input("시작년월", key=f"start_date_{i}")
            with cols2[1]:
                st.date_input("종료년월", key=f"end_date_{i}")
            with cols2[2]:
                st.text_input("직책/역할", key=f"role_{i}")
            with cols2[3]:
                if len(st.session_state.activities_data) > 1:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.button("활동 삭제", key=f"delete_activity_{i}", use_container_width=True):
                        if st.session_state.get(f'activity_id_{i}'):  # 기존 데이터인 경우
                            if delete_activity(st.session_state[f'activity_id_{i}'], st.session_state.user_email):
                                st.session_state.activities_data.remove(i)
                                if len(st.session_state.activities_data) == 0:
                                    st.session_state.activities_count = 1
                                    st.session_state.activities_data = [0]
                                st.session_state.activities_loaded = False
                                st.rerun()
                        else:  # 새로 추가했다가 삭제하는 경우
                            st.session_state.activities_data.remove(i)
                            if len(st.session_state.activities_data) == 0:
                                st.session_state.activities_count = 1
                                st.session_state.activities_data = [0]
                            st.rerun()
            
            st.text_input("링크", key=f"link_{i}")
            st.text_area("활동 세부내역", key=f"details_{i}", height=100)

        # 활동 추가 버튼
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns([1, 7])
        with cols[0]:
            if st.button("활동 추가", use_container_width=True):
                new_idx = max(st.session_state.activities_data) + 1 if st.session_state.activities_data else 0
                st.session_state.activities_data.append(new_idx)
                st.session_state.activities_count += 1
                # 새 활동 필드 초기화
                st.session_state[f'activity_name_{new_idx}'] = ''
                st.session_state[f'organization_{new_idx}'] = ''
                st.session_state[f'start_date_{new_idx}'] = None
                st.session_state[f'end_date_{new_idx}'] = None
                st.session_state[f'role_{new_idx}'] = ''
                st.session_state[f'link_{new_idx}'] = ''
                st.session_state[f'details_{new_idx}'] = ''
                st.rerun()

        # 저장 버튼
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns([7, 1])
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[0].empty()
        with cols[1]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_activities_tab", use_container_width=True):
                if 'user_email' not in st.session_state:
                    st.error("로그인이 필요합니다.")
                    return
                
                # 현재 입력된 모든 활동 데이터 수집
                activities_data = {}
                for i in st.session_state.activities_data:
                    activity_name = st.session_state.get(f'activity_name_{i}', '').strip()
                    organization = st.session_state.get(f'organization_{i}', '').strip()
                    start_date = st.session_state.get(f'start_date_{i}')
                    
                    if activity_name or organization or start_date:  # 하나라도 입력된 경우
                        if not activity_name:
                            st.warning(f"{i+1}번째 활동의 활동명이 비어 있습니다.")
                            continue
                        
                        if not organization:
                            st.warning(f"{i+1}번째 활동의 소속이 비어 있습니다.")
                            continue
                        
                        if not start_date:
                            st.warning(f"{i+1}번째 활동의 시작년월이 비어 있습니다.")
                            continue
                        
                        activities_data[i] = {
                            'id': st.session_state.get(f'activity_id_{i}'),
                            'activity_name': activity_name,
                            'organization': organization,
                            'start_date': start_date,
                            'end_date': st.session_state.get(f'end_date_{i}'),
                            'role': st.session_state.get(f'role_{i}', ''),
                            'link': st.session_state.get(f'link_{i}', ''),
                            'details': st.session_state.get(f'details_{i}', '')
                        }
                
                if save_activities_info(st.session_state.user_email, activities_data):
                    show_success_message()
                    st.session_state.activities_loaded = False
                    st.rerun()
                else:
                    st.error("저장 중 오류가 발생했습니다.")

    # 자기소개 탭
    with tabs[6]:
        st.markdown('<h5 class="main-header">자기소개</h5>', unsafe_allow_html=True)
        
        # 자기소개 주제 맵 정의
        intro_topic_map = {
            "성장 배경 및 가치관": [
                "성장 과정에서 가장 기억에 남는 경험은 무엇인가요?",
                "어린 시절 본인에게 영향을 준 인물은 누구인가요?",
                "가족이나 친구와의 관계에서 배운 점은 무엇인가요?",
                "본인이 중요하게 생각하는 가치관은 무엇인가요?",
                "본인의 인생 좌우명은 무엇인가요?",
                "경력 동안 본인의 가치관이 변화한 계기는 무엇인가요?",
                "조직에서 본인의 가치관을 실현한 경험이 있나요?",
                "경력 중 가장 영향을 준 멘토나 동료는 누구인가요?",
                "조직 문화와 본인의 가치관이 충돌했던 경험은 있나요?",
                "본인의 신념이 업무에 긍정적으로 작용한 사례는 무엇인가요?"
            ],
            "성격 및 강점/약점": [
                "본인의 성격을 한 단어로 표현해 보세요.",
                "친구들이 본인을 어떻게 평가하나요?",
                "본인이 생각하는 강점은 무엇인가요?",
                "약점을 극복하기 위해 노력한 경험이 있나요?",
                "성격이 긍정적으로 작용한 경험은 무엇인가요?",
                "본인의 강점이 업무에 어떻게 기여했나요?",
                "약점이 업무에 미친 영향을 극복한 사례는?",
                "동료들이 평가하는 본인의 성격은?",
                "성격 변화가 경력에 미친 영향은?",
                "본인의 성격이 리더십에 어떻게 작용했나요?"
            ],
            "목표 및 비전": [
                "단기적으로 이루고 싶은 목표는 무엇인가요?",
                "장기적으로 이루고 싶은 꿈은 무엇인가요?",
                "5년 후 본인의 모습은?",
                "이루고 싶은 커리어 목표는?",
                "목표 달성을 위해 어떤 노력을 하고 있나요?",
                "경력 중 달성한 가장 큰 목표는?",
                "앞으로의 커리어 비전은 무엇인가요?",
                "경력 내 목표 달성을 위해 포기한 것은?",
                "새로운 목표를 세운 계기는?",
                "비전을 실현하기 위해 현재 준비 중인 것은?"
            ],
            "문제 해결 및 갈등 관리": [
                "예상치 못한 문제를 해결한 경험은?",
                "팀 내 갈등을 조정한 경험이 있나요?",
                "문제 상황에서 창의적으로 접근한 경험은?",
                "실수나 실패를 극복한 경험은?",
                "어려운 결정을 내린 적이 있나요?",
                "조직 내 복잡한 문제를 해결한 경험은?",
                "이해관계자 간 갈등을 중재한 사례는?",
                "위기 상황에서 리더십을 발휘한 경험은?",
                "반복되는 문제를 근본적으로 해결한 경험은?",
                "갈등 관리로 팀 성과를 높인 사례는?"
            ],
            "리더십 및 협업 경험": [
                "팀장이나 리더 역할을 맡아본 경험이 있나요?",
                "협업 과정에서 맡았던 역할은?",
                "팀워크를 높이기 위해 노력한 점은?",
                "협업 중 갈등을 해결한 경험은?",
                "협업을 통해 얻은 교훈은?",
                "프로젝트 리더로서 팀을 이끈 경험은?",
                "부서 간 협업을 성공적으로 이끈 사례는?",
                "리더십 발휘로 조직에 기여한 경험은?",
                "팀원 동기부여를 위해 시도한 방법은?",
                "다양한 배경의 구성원과 협업한 경험은?"
            ],
            "도전 및 실패 경험": [
                "새로운 일에 도전한 경험은?",
                "도전 과정에서 힘들었던 점은?",
                "실패를 경험한 순간과 원인은?",
                "실패 후 다시 도전한 계기는?",
                "도전을 통해 얻은 성취는?",
                "경력 중 가장 큰 도전과 그 결과는?",
                "실패를 조직적으로 극복한 사례는?",
                "도전적 과제를 성공적으로 완수한 경험은?",
                "실패 경험이 경력에 미친 영향은?",
                "도전 후 조직에 남긴 변화는?"
            ],
            "자기계발 및 학습": [
                "최근 1년 내 새롭게 배운 것은?",
                "자기계발을 위해 실천하는 습관은?",
                "자주 활용하는 학습 방법은?",
                "자기계발을 위해 투자한 시간은?",
                "학습 과정에서 극복한 어려움은?",
                "경력 중 자기계발로 성장한 경험은?",
                "직무 관련 자격증이나 교육 이수 경험은?",
                "새로운 기술을 습득해 적용한 사례는?",
                "학습을 통해 팀에 기여한 경험은?",
                "자기계발이 커리어에 미친 영향은?"
            ],
            "관심 분야 및 동기": [
                "지원 분야에 관심을 갖게 된 계기는?",
                "해당 분야에서 가진 강점은?",
                "관심 분야에 대해 경험한 것은?",
                "지원 분야에서 이루고 싶은 목표는?",
                "열정을 보여준 경험은?",
                "경력 중 해당 분야를 선택한 이유는?",
                "업계 동향을 파악하기 위해 하는 노력은?",
                "관심 분야에서 본인만의 전문성은?",
                "해당 분야에서 성취한 대표 경험은?",
                "앞으로 이루고 싶은 분야 내 목표는?"
            ],
            "기타(개성, 좌우명 등)": [
                "본인을 한 문장으로 표현해 주세요.",
                "자신을 나타내는 키워드 3가지는?",
                "본인의 좌우명은?",
                "특별한 취미가 있나요?",
                "남들과 다른 본인만의 강점은?",
                "경력에서 본인의 개성이 드러난 사례는?",
                "본인을 대표하는 키워드와 그 이유는?",
                "좌우명이 업무에 미친 영향은?",
                "조직에서 차별화된 자신만의 강점은?",
                "경력 중 가장 자랑스러웠던 순간은?"
            ]
        }
        
        # 자기소개 카운터 초기화
        if 'intro_count' not in st.session_state:
            st.session_state.intro_count = 1
        
        # 자기소개 데이터 초기화
        if 'intro_data' not in st.session_state:
            st.session_state.intro_data = list(range(st.session_state.intro_count))

        # 각 자기소개 정보 입력 폼
        for idx, i in enumerate(st.session_state.intro_data):
            if idx > 0:
                st.markdown("<hr>", unsafe_allow_html=True)
            
            # 자기소개분야/주제/삭제 버튼 (2:5:1)
            cols = st.columns([2, 5, 1])
            with cols[0]:
                # 선택된 분야가 session_state에 없으면 첫 번째 분야를 기본값으로 설정
                if f'selected_category_{i}' not in st.session_state:
                    st.session_state[f'selected_category_{i}'] = list(intro_topic_map.keys())[0]
                
                selected_category = st.selectbox(
                    "자기소개분야",
                    list(intro_topic_map.keys()),
                    key=f"intro_category_{i}"
                )
                # 분야가 변경되면 session_state 업데이트
                if selected_category != st.session_state[f'selected_category_{i}']:
                    st.session_state[f'selected_category_{i}'] = selected_category
                    if f'intro_topic_{i}' in st.session_state:
                        del st.session_state[f'intro_topic_{i}']
                    st.rerun()
            
            with cols[1]:
                # 선택된 분야에 따른 주제 목록 표시
                topics = intro_topic_map[selected_category]
                st.selectbox(
                    "주제",
                    topics,
                    key=f"intro_topic_{i}"
                )
            
            with cols[2]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if len(st.session_state.intro_data) > 1:
                    if st.button("자기소개 삭제", key=f"delete_intro_{i}", use_container_width=True):
                        st.session_state.intro_data.remove(i)
                        if len(st.session_state.intro_data) == 0:
                            st.session_state.intro_count = 1
                            st.session_state.intro_data = [0]
                        st.rerun()
            
            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            
            # 자기소개문 (8)
            cols = st.columns([8])
            with cols[0]:
                st.text_area("자기소개문", value=personal_info.get(f'intro_answer_{i}', ''), height=200, key=f"intro_answer_{i}")

        # 자기소개 추가 버튼 (1:7)
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        with cols[0]:
            if st.button("자기소개 추가", use_container_width=True):
                new_idx = max(st.session_state.intro_data) + 1 if st.session_state.intro_data else 0
                st.session_state.intro_data.append(new_idx)
                st.session_state.intro_count += 1
                st.rerun()

        # 저장 버튼 (7:1)
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_intro_tab", use_container_width=True):
                if 'user_email' not in st.session_state:
                    st.error("로그인이 필요합니다.")
                    return
                
                # 현재 입력된 모든 자기소개 데이터 수집
                intro_data = {}
                for i in st.session_state.intro_data:
                    category = st.session_state[f'intro_category_{i}']
                    topic = st.session_state[f'intro_topic_{i}']
                    answer = st.session_state[f'intro_answer_{i}']
                    
                    if category and topic and answer.strip():
                        intro_data[i] = {
                            'category': category,
                            'topic': topic,
                            'content': answer.strip()
                        }
                
                if save_intro_info(st.session_state.user_email, intro_data):
                    show_success_message()
                    st.rerun()
                else:
                    st.error("저장 중 오류가 발생했습니다.")
