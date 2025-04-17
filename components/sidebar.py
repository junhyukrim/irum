import streamlit as st

def setup_sidebar():
    """사이드바의 스타일과 구조를 설정하는 함수"""
    st.markdown(
        """
        <style>
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
        
        /* 버튼 기본 스타일 */
        .stButton > button {
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

        /* 호버 스타일 */
        .stButton > button:hover {
            font-size: 2rem !important;
            font-weight: bold !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
        }

        /* 선택된 버튼 스타일 */
        .stButton > button[aria-pressed="true"] {
            background-color: #0051FF !important;
            font-size: 2rem !important;
            font-weight: bold !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # 로고 추가
    st.image("https://i.imgur.com/thQZtYk.png")
    
    # 메뉴 버튼들
    if st.button('대시보드', key='dashboard', use_container_width=True):
        st.session_state.current_page = '대시보드'
        st.rerun()

    if st.button('이력관리', key='resume', use_container_width=True):
        st.session_state.current_page = '이력관리'
        st.rerun()

    if st.button('공고관리', key='jobs', use_container_width=True):
        st.session_state.current_page = '공고관리'
        st.rerun()

    if st.button('서류관리', key='documents', use_container_width=True):
        st.session_state.current_page = '서류관리'
        st.rerun()

    # 빈 공간 추가 (크기 조절)
    st.markdown("<div style='flex-grow: 1; min-height: calc(100vh - 800px);'></div>", unsafe_allow_html=True)
    
    # 로그아웃 버튼
    st.button("로그아웃", key='logout', on_click=st.logout) 