import streamlit as st
from lg_rag import ask_question

def show():
    st.title("📚 지식 DB")
    st.write("야구 관련 지식을 물어보세요!")

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

    # 사이드바에 추가 정보 표시
    with st.sidebar:
        st.subheader("💡 도움말")
        st.markdown("""
        - 야구 규칙에 대해 질문해보세요
        - 구체적인 질문일수록 더 정확한 답변을 받을 수 있습니다
        - 현재 야구 경기 방식에 대한 정보를 제공합니다
        """)

        if st.button("대화 내용 초기화"):
            st.session_state.messages = []
            st.rerun() 