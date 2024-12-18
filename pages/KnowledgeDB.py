import streamlit as st
from pages.lg_rag import ask_question
import sys
from pathlib import Path
import sqlite3

# SQLite3 버전 문제 해결을 위한 코드
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def show():
    st.title("📚 지식 DB")
    st.write("야구 관련 지식을 물어보세요!")

    # 도움말을 페이지 본문에 추가
    st.subheader("💡 도움말")
    st.markdown("""
    - 야구 규칙에 대해 질문해보세요
    - 구체적인 질문일수록 더 정확한 답변을 받을 수 있습니다
    - 현재 야구 경기 방식에 대한 정보를 제공합니다
    """)

    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if prompt := st.chat_input("질문을 입력하세요"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 어시스턴트 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("답변을 생성하고 있습니다..."):
                try:
                    response = ask_question(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"답변 생성 중 오류가 발생했습니다: {str(e)}")

    # 대화 내용 초기화 버튼을 페이지 본문에 추가
    if st.button("대화 내용 초기화"):
        st.session_state.messages = []
        st.rerun() 