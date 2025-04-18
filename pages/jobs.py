import streamlit as st

def show_jobs_page():
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
    
    st.markdown('<h3 class="main-header">공고관리</h3>', unsafe_allow_html=True)
    st.write("여기에 공고관리 내용이 들어갑니다.") 