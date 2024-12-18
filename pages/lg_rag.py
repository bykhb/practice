# lg_rag.py
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
import os
from pathlib import Path

load_dotenv()

# Chroma DB 경로 설정
PERSIST_DIRECTORY = Path(__file__).parent.parent / "chroma"

# 디버깅을 위한 코드 추가
print(f"Looking for Chroma DB at: {PERSIST_DIRECTORY}")
print(f"Directory exists: {PERSIST_DIRECTORY.exists()}")
if PERSIST_DIRECTORY.exists():
    print(f"Contents: {list(PERSIST_DIRECTORY.glob('*'))}")

# 저장된 벡터 스토어 로드
try:
    vectorstore = Chroma(
        collection_name="baseball-chroma",
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
당신은 야구 전문가입니다. 주어진 컨텍스트를 바탕으로 사용자의 질문에 정확하게 답변해주세요.
답변할 때는 다음 규칙을 따르세요:
1. 컨텍스트에 있는 정보만 사용하세요
2. 컨텍스트에 없는 내용은 "제가 가진 정보로는 답변하기 어렵습니다"라고 말씀해주세요
3. 답변은 친절하고 자연스러운 한국어로 작성해주세요

텍스트:
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

def ask_question(question: str):
    initial_state = AgentState(
        messages=[],
        query=question,
        context="",
        response=""
    )
    result = chain.invoke(initial_state)
    return result["response"]