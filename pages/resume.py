import streamlit as st
import pymysql
from datetime import datetime

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
            
            for skill_idx in data:
                for cert_idx in range(data[skill_idx]['cert_count']):
                    cert_data = data[skill_idx]['certifications'][cert_idx]
                    
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
            
            for skill_idx in data:
                for edu_idx in range(data[skill_idx]['edu_count']):
                    edu_data = data[skill_idx]['training'][edu_idx]
                    
                    # 기존 교육 정보가 있는지 확인
                    if edu_data.get('id'):  # 기존 데이터 업데이트
                        current_training_ids.add(edu_data['id'])
                        update_query = """
                            UPDATE tb_resume_training SET
                            description = %s
                            WHERE id = %s AND login_email = %s
                        """
                        cursor.execute(update_query, (
                            edu_data['description'],
                            edu_data['id'],
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
                            edu_data['description']
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

def show_resume_page():
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
                    <div style="padding: 1rem; background-color: #e9ffe9; border-radius: 0.5rem; margin: 1rem 0;">
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
                    st.success("저장되었습니다!")
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
                    st.success("저장되었습니다!")
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
        
        st.markdown('<h5>역량</h5>', unsafe_allow_html=True)
        
        # 로그인 확인
        if 'user_email' not in st.session_state:
            st.error("로그인이 필요합니다.")
            return
        
        # 기존 데이터 로드
        if 'skills_loaded' not in st.session_state:
            skills, error = load_skills_info(st.session_state.user_email)
            if error:
                st.error(error)
            elif skills:
                # 기존 데이터로 session_state 초기화
                st.session_state.skill_data = []
                st.session_state.cert_counts = {}
                st.session_state.edu_counts = {}
                
                for idx, skill in enumerate(skills):
                    st.session_state.skill_data.append(idx)
                    st.session_state[f'skill_id_{idx}'] = skill['id']
                    st.session_state[f'skill_desc_{idx}'] = skill['skill_name']
                    st.session_state[f'skill_level_{idx}'] = skill['skill_level']
                    st.session_state[f'skill_note_{idx}'] = skill['note']
                    
                    # 자격증 정보 설정
                    st.session_state.cert_counts[idx] = len(skill['certifications'])
                    for cert_idx, cert in enumerate(skill['certifications']):
                        st.session_state[f'cert_id_{idx}_{cert_idx}'] = cert['id']
                        st.session_state[f'certification_name_{idx}_{cert_idx}'] = cert['certification_name']
                        st.session_state[f'cert_date_{idx}_{cert_idx}'] = cert['issue_date']
                        st.session_state[f'cert_org_{idx}_{cert_idx}'] = cert['issuing_agency']
                    
                    # 교육 정보 설정
                    st.session_state.edu_counts[idx] = len(skill['training'])
                    for edu_idx, edu in enumerate(skill['training']):
                        st.session_state[f'edu_id_{idx}_{edu_idx}'] = edu['id']
                        st.session_state[f'education_{idx}_{edu_idx}'] = edu['description']
                
                st.session_state.skill_count = len(skills)
            else:
                # 초기 상태 설정
                st.session_state.skill_count = 1
                st.session_state.skill_data = [0]
                st.session_state.cert_counts = {0: 1}
                st.session_state.edu_counts = {0: 1}
            
            st.session_state.skills_loaded = True
        
        # 역량 카운터 초기화
        if 'skill_count' not in st.session_state:
            st.session_state.skill_count = 1
        
        # 자격증, 교육 카운터 초기화
        if 'cert_counts' not in st.session_state:
            st.session_state.cert_counts = {0: 1}
        if 'edu_counts' not in st.session_state:
            st.session_state.edu_counts = {0: 1}

        # 역량 데이터 초기화
        if 'skill_data' not in st.session_state:
            st.session_state.skill_data = list(range(st.session_state.skill_count))

        # 각 역량 정보 입력 폼
        for idx, i in enumerate(st.session_state.skill_data):
            if idx > 0:
                st.markdown("<hr>", unsafe_allow_html=True)
            
            # 기술 및 역량 (2:1:4:1:1)
            cols = st.columns([2, 1, 4, 1, 1])
            with cols[0]:
                st.text_input("기술 및 역량", value=personal_info.get(f'skill_desc_{i}', ''), key=f"skill_desc_{i}")
            with cols[1]:
                level_options = ["1", "2", "3", "4", "5"]
                skill_level_key = f"skill_level_{i}"
                # session_state 값이 유효한지 확인하고, 유효하지 않다면 제거
                if skill_level_key in st.session_state and st.session_state[skill_level_key] not in level_options:
                    del st.session_state[skill_level_key]  # 에러 방지를 위해 잘못된 값 삭제
                selected_level = st.selectbox(
                "성취 수준",
                level_options,
                key=skill_level_key,
                help="1: 기초 수준, 2: 초급 수준, 3: 중급 수준, 4: 고급 수준, 5: 전문가 수준"
            )
                
                skills_data = {}
                # 저장 버튼 클릭 시 모든 항목은 반드시 기술명과 성취 수준을 모두 유효하게 입력해야 함
                for i in st.session_state.skill_data:
                    skill_name = st.session_state[f'skill_desc_{i}'].strip()
                    selected_level = st.session_state[f'skill_level_{i}']

                    if not skill_name:
                        st.warning(f"{i+1}번째 기술의 '기술 및 역량' 항목이 비어 있어 저장되지 않습니다.")
                        success = False
                        continue

                    if selected_level not in ["1", "2", "3", "4", "5"]:
                        st.warning(f"{i+1}번째 기술의 성취 수준이 유효하지 않아 저장되지 않습니다.")
                        success = False
                        continue

                    skills_data[i] = {
                        'id': st.session_state.get(f'skill_id_{i}'),
                        'skill_name': skill_name,
                        'skill_level': int(selected_level),
                        'note': st.session_state[f'skill_note_{i}']
                    }

            with cols[2]:
                st.text_input("비고", value=personal_info.get(f'skill_note_{i}', ''), key=f"skill_note_{i}")
            with cols[3]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if len(st.session_state.skill_data) > 1:
                    if st.button("기술 및 역량 삭제", key=f"delete_skill_{i}", use_container_width=True):
                        st.session_state.skill_data.remove(i)
                        if len(st.session_state.skill_data) == 0:
                            st.session_state.skill_count = 1
                            st.session_state.skill_data = [0]
                            st.session_state.cert_counts = {0: 1}
                            st.session_state.edu_counts = {0: 1}
                        st.rerun()
            with cols[4]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if st.button("기술 및 역량 추가", key=f"add_skill_{i}", use_container_width=True):
                    new_idx = max(st.session_state.skill_data) + 1 if st.session_state.skill_data else 0
                    st.session_state.skill_data.append(new_idx)
                    st.session_state.cert_counts[new_idx] = 0
                    st.session_state.edu_counts[new_idx] = 0
                    st.session_state.skill_count += 1
                    st.rerun()
            
            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            
            # 자격증 섹션
            st.markdown('<div class="section-header">자격증</div>', unsafe_allow_html=True)
            
            certifications_data = {}
            for i in st.session_state.skill_data:
                if i in st.session_state.cert_counts:
                    for j in range(st.session_state.cert_counts[i]):
                        if j > 0:
                            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
                        
                        # 자격증 (3:1:2:1:1)
                        cols = st.columns([3, 1, 2, 1, 1])
                        with cols[0]:
                            st.text_input("자격증명", value=personal_info.get(f'certification_name_{i}_{j}', ''), key=f"certification_name_{i}_{j}")
                        with cols[1]:
                            st.date_input("취득년월", value=personal_info.get(f'cert_date_{i}_{j}', None), key=f"cert_date_{i}_{j}")
                        with cols[2]:
                            st.text_input("발급기관", value=personal_info.get(f'cert_org_{i}_{j}', ''), key=f"cert_org_{i}_{j}")
                        with cols[3]:
                            st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                            if st.button("삭제", key=f"delete_cert_{i}_{j}", use_container_width=True):
                                st.session_state.cert_counts[i] -= 1
                                st.rerun()
                        with cols[4]:
                            st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                            if st.button("추가", key=f"add_cert_{i}_{j}", use_container_width=True):
                                st.session_state.cert_counts[i] += 1
                                st.rerun()

            st.markdown("<hr>", unsafe_allow_html=True)

            # 교육 섹션
            st.markdown('<div class="section-header">교육: 훈련, 연수, 유학 등</div>', unsafe_allow_html=True)
            
            training_data = {}
            for i in st.session_state.skill_data:
                if i in st.session_state.edu_counts:
                    for j in range(st.session_state.edu_counts[i]):
                        if j > 0:
                            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
                        
                        # 교육 (6:1:1)
                        cols = st.columns([6, 1, 1])
                        with cols[0]:
                            st.text_area("교육 내용", value=personal_info.get(f'education_{i}_{j}', ''), key=f"education_{i}_{j}", height=100)
                        with cols[1]:
                            st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                            if st.button("삭제", key=f"delete_edu_{i}_{j}", use_container_width=True):
                                st.session_state.edu_counts[i] -= 1
                                st.rerun()
                        with cols[2]:
                            st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                            if st.button("추가", key=f"add_edu_{i}_{j}", use_container_width=True):
                                st.session_state.edu_counts[i] += 1
                                st.rerun()

            st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

        # 저장 버튼 (7:1)
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_skill_tab", use_container_width=True):
                if 'user_email' not in st.session_state:
                    st.error("로그인이 필요합니다.")
                    return
                
                # 현재 입력된 모든 역량 데이터 수집
                skills_data = {}
                certifications_data = {}
                training_data = {}
                
                for i in st.session_state.skill_data:
                    # 기술 및 역량 데이터
                    skills_data[i] = {
                        'id': st.session_state.get(f'skill_id_{i}'),
                        'skill_name': st.session_state[f'skill_desc_{i}'],
                        'skill_level': st.session_state[f'skill_level_{i}'],
                        'note': st.session_state[f'skill_note_{i}']
                    }
                    
                    # 자격증 데이터
                    certifications_data[i] = {
                        'cert_count': st.session_state.cert_counts[i],
                        'certifications': []
                    }
                    for j in range(st.session_state.cert_counts[i]):
                        certifications_data[i]['certifications'].append({
                            'id': st.session_state.get(f'cert_id_{i}_{j}'),
                            'certification_name': st.session_state[f'certification_name_{i}_{j}'],
                            'issue_date': st.session_state[f'cert_date_{i}_{j}'],
                            'issuing_agency': st.session_state[f'cert_org_{i}_{j}']
                        })
                    
                    # 교육 데이터
                    training_data[i] = {
                        'edu_count': st.session_state.edu_counts[i],
                        'training': []
                    }
                    for j in range(st.session_state.edu_counts[i]):
                        training_data[i]['training'].append({
                            'id': st.session_state.get(f'edu_id_{i}_{j}'),
                            'description': st.session_state[f'education_{i}_{j}']
                        })
                
                # 각 데이터 저장
                success = True
                if not save_skills_info(st.session_state.user_email, skills_data):
                    success = False
                    st.error("기술 및 역량 정보 저장 중 오류가 발생했습니다.")
                
                if not save_certifications_info(st.session_state.user_email, certifications_data):
                    success = False
                    st.error("자격증 정보 저장 중 오류가 발생했습니다.")
                
                if not save_training_info(st.session_state.user_email, training_data):
                    success = False
                    st.error("교육 정보 저장 중 오류가 발생했습니다.")
                
                if success:
                    st.success("저장되었습니다!")
                    # 저장 성공 시 데이터 다시 로드하도록 설정
                    st.session_state.skills_loaded = False
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
        
        # 경력 카운터 초기화
        if 'career_count' not in st.session_state:
            st.session_state.career_count = 1
        
        # 직위 카운터 초기화
        if 'position_counts' not in st.session_state:
            st.session_state.position_counts = {0: 1}
        
        # 업무 카운터 초기화
        if 'task_counts' not in st.session_state:
            st.session_state.task_counts = {0: {0: 1}}

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
                st.text_input("회사명", value=personal_info.get(f'company_{i}', ''), key=f"company_{i}")
            with cols[1]:
                st.date_input("입사년월", value=personal_info.get(f'join_date_{i}', None), key=f"join_date_{i}")
            with cols[2]:
                st.date_input("퇴사년월", value=personal_info.get(f'leave_date_{i}', None), key=f"leave_date_{i}")
            with cols[3]:
                st.text_input("퇴사사유", value=personal_info.get(f'leave_reason_{i}', ''), key=f"leave_reason_{i}")
            with cols[4]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if len(st.session_state.career_data) > 1:
                    if st.button("경력 삭제", key=f"delete_career_{i}", use_container_width=True):
                        st.session_state.career_data.remove(i)
                        if len(st.session_state.career_data) == 0:
                            st.session_state.career_count = 1
                            st.session_state.career_data = [0]
                            st.session_state.position_counts = {0: 1}
                            st.session_state.task_counts = {0: {0: 1}}
                        st.rerun()
            
            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            
            # 직위/직책 정보
            if i not in st.session_state.position_counts:
                st.session_state.position_counts[i] = 1
            if i not in st.session_state.task_counts:
                st.session_state.task_counts[i] = {0: 1}

            for j in range(st.session_state.position_counts[i]):
                if j > 0:
                    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
                
                # 직위/직책/취임년월/퇴임년월/업무내용 (2:1:1:4)
                cols = st.columns([2, 1, 1, 4])
                with cols[0]:
                    st.text_input("직위/직책", value=personal_info.get(f'position_{i}_{j}', ''), key=f"position_{i}_{j}")
                with cols[1]:
                    st.date_input("취임년월", value=personal_info.get(f'position_start_{i}_{j}', None), key=f"position_start_{i}_{j}")
                with cols[2]:
                    st.date_input("퇴임년월", value=personal_info.get(f'position_end_{i}_{j}', None), key=f"position_end_{i}_{j}")
                
                # 업무 내용 입력란
                if j not in st.session_state.task_counts[i]:
                    st.session_state.task_counts[i][j] = 1

                for k in range(st.session_state.task_counts[i][j]):
                    if k > 0:
                        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
                    with cols[3]:
                        st.text_input("업무내용", value=personal_info.get(f'task_{i}_{j}_{k}', ''), key=f"task_{i}_{j}_{k}")
                
                # 버튼들 (4:1:1:1:1)
                cols = st.columns([4, 1, 1, 1, 1])
                with cols[1]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.session_state.position_counts[i] > 1:
                        if st.button("직위/직책 삭제", key=f"delete_position_{i}_{j}", use_container_width=True):
                            st.session_state.position_counts[i] -= 1
                            if j in st.session_state.task_counts[i]:
                                del st.session_state.task_counts[i][j]
                            st.rerun()
                with cols[2]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.button("직위/직책 추가", key=f"add_position_{i}_{j}", use_container_width=True):
                        st.session_state.position_counts[i] += 1
                        st.session_state.task_counts[i][st.session_state.position_counts[i]-1] = 1
                        st.rerun()
                with cols[3]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.session_state.task_counts[i][j] > 1:
                        if st.button("업무 삭제", key=f"delete_task_{i}_{j}", use_container_width=True):
                            st.session_state.task_counts[i][j] -= 1
                            st.rerun()
                with cols[4]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.button("업무 추가", key=f"add_task_{i}_{j}", use_container_width=True):
                        st.session_state.task_counts[i][j] += 1
                        st.rerun()

        # 경력 추가 버튼 (1:7)
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        with cols[0]:
            if st.button("경력 추가", use_container_width=True):
                new_idx = max(st.session_state.career_data) + 1 if st.session_state.career_data else 0
                st.session_state.career_data.append(new_idx)
                st.session_state.position_counts[new_idx] = 1
                st.session_state.task_counts[new_idx] = {0: 1}
                st.session_state.career_count += 1
                st.rerun()

        # 저장 버튼 (7:1)
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_career_tab", use_container_width=True):
                st.success("저장되었습니다!")

    # 수상 탭
    with tabs[4]:
        st.markdown('<h5 class="main-header">수상</h5>', unsafe_allow_html=True)
        
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
            
            # 상명/수상일/수여기관/비고/삭제 버튼 (1:1:1:4:1)
            cols = st.columns([2, 1, 1, 3, 1])
            with cols[0]:
                st.text_input("상명", value=personal_info.get(f'award_name_{i}', ''), key=f"award_name_{i}")
            with cols[1]:
                st.date_input("수상년월", value=personal_info.get(f'award_date_{i}', None), key=f"award_date_{i}")
            with cols[2]:
                st.text_input("수여기관", value=personal_info.get(f'award_org_{i}', ''), key=f"award_org_{i}")
            with cols[3]:
                st.text_input("비고", value=personal_info.get(f'award_note_{i}', ''), key=f"award_note_{i}")
            with cols[4]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if len(st.session_state.award_data) > 1:
                    if st.button("수상내역 삭제", key=f"delete_award_{i}", use_container_width=True):
                        st.session_state.award_data.remove(i)
                        if len(st.session_state.award_data) == 0:
                            st.session_state.award_count = 1
                            st.session_state.award_data = [0]
                        st.rerun()

        # 수상내역 추가 버튼 (1:7)
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        with cols[0]:
            if st.button("수상내역 추가", use_container_width=True):
                new_idx = max(st.session_state.award_data) + 1 if st.session_state.award_data else 0
                st.session_state.award_data.append(new_idx)
                st.session_state.award_count += 1
                st.rerun()

        # 저장 버튼 (7:1)
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_award_tab", use_container_width=True):
                st.success("저장되었습니다!")

    # 기타활동 탭
    with tabs[5]:
        st.markdown('<h5 class="main-header">기타활동</h5>', unsafe_allow_html=True)
        
        # 활동 카운터 초기화
        if 'activity_count' not in st.session_state:
            st.session_state.activity_count = 1
        
        # 활동 데이터 초기화
        if 'activity_data' not in st.session_state:
            st.session_state.activity_data = list(range(st.session_state.activity_count))

        # 각 활동 정보 입력 폼
        for idx, i in enumerate(st.session_state.activity_data):
            if idx > 0:
                st.markdown("<hr>", unsafe_allow_html=True)
            
            # 활동명/소속/시작년월/종료년월/직책/역할/삭제 버튼 (2:2:1:1:1:1)
            cols = st.columns([2, 2, 1, 1, 1, 1])
            with cols[0]:
                st.text_input("활동명", value=personal_info.get(f'activity_name_{i}', ''), key=f"activity_name_{i}")
            with cols[1]:
                st.text_input("소속", value=personal_info.get(f'activity_org_{i}', ''), key=f"activity_org_{i}")
            with cols[2]:
                st.date_input("시작년월", value=personal_info.get(f'activity_start_{i}', None), key=f"activity_start_{i}")
            with cols[3]:
                st.date_input("종료년월", value=personal_info.get(f'activity_end_{i}', None), key=f"activity_end_{i}")
            with cols[4]:
                st.text_input("직책/역할", value=personal_info.get(f'activity_role_{i}', ''), key=f"activity_role_{i}")
            with cols[5]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if len(st.session_state.activity_data) > 1:
                    if st.button("활동 삭제", key=f"delete_activity_{i}", use_container_width=True):
                        st.session_state.activity_data.remove(i)
                        if len(st.session_state.activity_data) == 0:
                            st.session_state.activity_count = 1
                            st.session_state.activity_data = [0]
                        st.rerun()
            
            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            
            # 링크와 활동 세부내역 (4:4)
            cols = st.columns([4, 4])
            with cols[0]:
                st.text_input("링크", value=personal_info.get(f'activity_link_{i}', ''), key=f"activity_link_{i}", placeholder="관련 웹사이트나 문서 링크를 입력하세요")
            with cols[1]:
                st.text_input("활동세부내역", value=personal_info.get(f'activity_detail_{i}', ''), key=f"activity_detail_{i}")

        # 활동 추가 버튼 (1:7)
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        with cols[0]:
            if st.button("활동 추가", use_container_width=True):
                new_idx = max(st.session_state.activity_data) + 1 if st.session_state.activity_data else 0
                st.session_state.activity_data.append(new_idx)
                st.session_state.activity_count += 1
                st.rerun()

        # 저장 버튼 (7:1)
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_activity_tab", use_container_width=True):
                st.success("저장되었습니다!")

    # 자기소개 탭
    with tabs[6]:
        st.markdown('<h5 class="main-header">자기소개</h5>', unsafe_allow_html=True)
        
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
                st.selectbox(
                    "자기소개분야",
                    ["자기소개분야1", "자기소개분야2", "자기소개분야3"],
                    index=["자기소개분야1", "자기소개분야2", "자기소개분야3"].index(personal_info.get(f'intro_category_{i}', '자기소개분야1')),
                    key=f"intro_category_{i}"
                )
            with cols[1]:
                st.selectbox(
                    "주제",
                    ["주제1", "주제2", "주제3"],
                    index=["주제1", "주제2", "주제3"].index(personal_info.get(f'intro_topic_{i}', '주제1')),
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
            if st.button("저장", key="save_introduction_tab", use_container_width=True):
                st.success("저장되었습니다!") 