import streamlit as st

def show_documents_page():
    st.markdown(
        """
        <style>
        /* 사이드바 버튼 스타일링 */
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

        /* 사이드바 호버 스타일 */
        section[data-testid="stSidebar"] .stButton > button:hover {
            font-size: 2rem !important;
            font-weight: bold !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
        }

        /* 사이드바 선택된 버튼 스타일 */
        section[data-testid="stSidebar"] .stButton > button[aria-pressed="true"] {
            background-color: #0051FF !important;
            font-size: 2rem !important;
            font-weight: bold !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<h3 class="main-header">서류관리</h3>', unsafe_allow_html=True)
    st.write("여기에 서류관리 내용이 들어갑니다.") 