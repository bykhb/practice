import streamlit as st
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
import os
from pathlib import Path

# Chroma DB 경로 설정
PERSIST_DIRECTORY = Path(__file__).parent.parent / "chroma"

# 저장된 벡터 스토어 로드
try:
    vectorstore = Chroma(
        collection_name="food-recipe",  # 음식 레시피용 컬렉션
        embedding_function=OpenAIEmbeddings(),
        persist_directory=str(PERSIST_DIRECTORY),
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
except Exception as e:
    print(f"Error loading vector store: {e}")
    raise

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    context: str
    response: str

def should_retrieve(state: AgentState) -> dict:
    query = state["query"]
    docs = retriever.invoke(query)
    context = "\n".join([doc.page_content for doc in docs])
    return {"next": "grade_documents", "context": context}

def grade_documents(state: AgentState) -> dict:
    context = state["context"]
    if not context:
        return {"next": "rewrite_query"}
    return {"next": "generate_answer"}

def rewrite_query(state: AgentState) -> dict:
    return None

def generate_answer(state: AgentState) -> dict:
    llm = ChatOpenAI(temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
당신은 요리 전문가입니다. 주어진 컨텍스트를 바탕으로 사용자의 레시피 관련 질문에 정확하게 답변해주세요.
답변할 때는 다음 규칙을 따르세요:
1. 컨텍스트에 있는 정보만 사용하세요
2. 컨텍스트에 없는 내용은 "제가 가진 정보로는 답변하기 어렵습니다"라고 말씀해주세요
3. 답변은 친절하고 자연스러운 한국어로 작성해주세요
4. 레시피 정보가 있다면 단계별로 명확하게 설명해주세요

컨텍스트:
{context}
"""),
        ("human", "{query}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "context": state["context"],
        "query": state["query"]
    })
    
    return {"response": response.content}

# StateGraph 설정
from langgraph.graph import StateGraph

graph = StateGraph(AgentState)
graph.add_node("should_retrieve", should_retrieve)
graph.add_node("grade_documents", grade_documents)
graph.add_node("rewrite_query", rewrite_query)
graph.add_node("generate_answer", generate_answer)

graph.set_entry_point("should_retrieve")
graph.add_edge("should_retrieve", "grade_documents")
graph.add_edge("grade_documents", "generate_answer")
graph.add_edge("grade_documents", "rewrite_query")

chain = graph.compile()

def ask_recipe(question: str):
    initial_state = AgentState(
        messages=[],
        query=question,
        context="",
        response=""
    )
    result = chain.invoke(initial_state)
    return result["response"]

def show():
    st.title("🍳 음식 레시피")
    st.write("레시피나 요리 방법에 대해 질문해보세요!")

    # 도움말 추가
    st.subheader("💡 도움말")
    st.markdown("""
    - 특정 요리의 레시피를 물어보세요
    - 조리 방법이나 팁에 대해 질문해보세요
    - 구체적인 질문일수록 더 정확한 답변을 받을 수 있습니다
    """)

    # 세션 상태 초기화
    if "recipe_messages" not in st.session_state:
        st.session_state.recipe_messages = []

    # 채팅 히스토리 표시
    for message in st.session_state.recipe_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if prompt := st.chat_input("레시피나 요리 방법에 대해 질문해주세요"):
        # 사용자 메시지 추가
        st.session_state.recipe_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 어시스턴트 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("답변을 생성하고 있습니다..."):
                try:
                    response = ask_recipe(prompt)
                    st.markdown(response)
                    st.session_state.recipe_messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"답변 생성 중 오류가 발생했습니다: {str(e)}")

    # 대화 내용 초기화 버튼
    if st.button("대화 내용 초기화"):
        st.session_state.recipe_messages = []
        st.rerun() 