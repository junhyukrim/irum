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
        st.success("데이터베이스 연결 성공!")
        return connection
    except Exception as e:
        st.error(f"데이터베이스 연결 실패: {str(e)}")
        return None

def save_personal_info(login_email, data):
    # 디버깅을 위한 데이터 출력
    st.write("로그인 이메일:", login_email)
    st.write("저장할 데이터:", data)
    
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
                st.write("기존 데이터 업데이트")
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
                st.write("새 데이터 삽입")
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

def show_resume_page():
    st.markdown('<h3 class="main-header">이력관리</h3>', unsafe_allow_html=True)
    
    # 로그인 확인 및 이메일 가져오기
    if 'user_email' not in st.session_state:
        st.error("로그인이 필요합니다.")
        return
    
    login_email = st.session_state.user_email
    
    # 로그인한 이메일 표시
    st.markdown(f'로그인한 이메일: <span style="color: #4285F4;">{login_email}</span>', unsafe_allow_html=True)
    
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
                    <div style="padding: 1rem; background-color: #e9ffe9; border-radius: 0.5rem; margin: 1rem 0;">
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
            gender = st.selectbox("성별", ["선택", "남성", "여성"], index=["선택", "남성", "여성"].index(personal_info.get('gender', '선택')), key="gender")
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
            </style>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<h5>학력</h5>', unsafe_allow_html=True)
        
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

        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)

        # 저장 버튼 (7:1 = 8, right align)
        cols = st.columns(8)
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_education", use_container_width=True):
                st.success("저장되었습니다!")

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
            </style>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<h5>역량</h5>', unsafe_allow_html=True)
        
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
            
            # 기술 및 역량 (2:1:4:1)
            cols = st.columns([2, 1, 4, 1])
            with cols[0]:
                st.text_input("기술 및 역량", value=personal_info.get(f'skill_desc_{i}', ''), key=f"skill_desc_{i}")
            with cols[1]:
                st.text_input("성취 수준", value=personal_info.get(f'skill_level_{i}', ''), key=f"skill_level_{i}")
            with cols[2]:
                st.text_input("비고", value=personal_info.get(f'skill_note_{i}', ''), key=f"skill_note_{i}")
            with cols[3]:
                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                if len(st.session_state.skill_data) > 1:
                    if st.button("역량 삭제", key=f"delete_skill_{i}", use_container_width=True):
                        st.session_state.skill_data.remove(i)
                        if len(st.session_state.skill_data) == 0:
                            st.session_state.skill_count = 1
                            st.session_state.skill_data = [0]
                            st.session_state.cert_counts = {0: 1}
                            st.session_state.edu_counts = {0: 1}
                        st.rerun()
            
            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            
            # 자격증 섹션
            if i not in st.session_state.cert_counts:
                st.session_state.cert_counts[i] = 1

            for j in range(st.session_state.cert_counts[i]):
                # 자격증 (3:1:2:1:1)
                cols = st.columns([3, 1, 2, 1, 1])
                with cols[0]:
                    st.text_input("자격증", value=personal_info.get(f'cert_name_{i}_{j}', ''), key=f"cert_name_{i}_{j}")
                with cols[1]:
                    st.date_input("취득년월", value=personal_info.get(f'cert_date_{i}_{j}', None), key=f"cert_date_{i}_{j}")
                with cols[2]:
                    st.text_input("발급기관", value=personal_info.get(f'cert_org_{i}_{j}', ''), key=f"cert_org_{i}_{j}")
                with cols[3]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.session_state.cert_counts[i] > 1:
                        if st.button("자격증 삭제", key=f"delete_cert_{i}_{j}", use_container_width=True):
                            st.session_state.cert_counts[i] -= 1
                            st.rerun()
                with cols[4]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.button("자격증 추가", key=f"add_cert_{i}_{j}", use_container_width=True):
                        st.session_state.cert_counts[i] += 1
                        st.rerun()

                if j < st.session_state.cert_counts[i] - 1:
                    st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)

            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)

            # 교육 섹션 (6:1:1)
            if i not in st.session_state.edu_counts:
                st.session_state.edu_counts[i] = 1

            for j in range(st.session_state.edu_counts[i]):
                if j > 0:
                    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
                
                cols = st.columns([6, 1, 1])
                with cols[0]:
                    st.text_input("교육: 훈련, 연수, 유학 등", value=personal_info.get(f'education_{i}_{j}', ''), key=f"education_{i}_{j}")
                with cols[1]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.session_state.edu_counts[i] > 1:
                        if st.button("교육 삭제", key=f"delete_edu_{i}_{j}", use_container_width=True):
                            st.session_state.edu_counts[i] -= 1
                            st.rerun()
                with cols[2]:
                    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
                    if st.button("교육 추가", key=f"add_edu_{i}_{j}", use_container_width=True):
                        st.session_state.edu_counts[i] += 1
                        st.rerun()

        # 역량 추가 버튼 (1:7)
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        with cols[0]:
            if st.button("역량 추가", use_container_width=True):
                new_idx = max(st.session_state.skill_data) + 1 if st.session_state.skill_data else 0
                st.session_state.skill_data.append(new_idx)
                st.session_state.cert_counts[new_idx] = 1
                st.session_state.edu_counts[new_idx] = 1
                st.session_state.skill_count += 1
                st.rerun()

        # 저장 버튼 (7:1)
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        for i in range(7):  # 처음 7개 컬럼은 빈 공간
            cols[i].empty()
        with cols[7]:  # 마지막 컬럼에 버튼 배치
            if st.button("저장", key="save_skill", use_container_width=True):
                st.success("저장되었습니다!")

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
            if st.button("저장", key="save_career", use_container_width=True):
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
            if st.button("저장", key="save_award", use_container_width=True):
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
            if st.button("저장", key="save_activity", use_container_width=True):
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
            if st.button("저장", key="save_intro", use_container_width=True):
                st.success("저장되었습니다!") 