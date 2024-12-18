from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from pathlib import Path

load_dotenv()

# 환경 변수 설정
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# OpenAI API 키 설정
# Chroma DB 경로 설정
PERSIST_DIRECTORY = Path(__file__).parent / "chroma"

def create_vectorstore():
    """벡터 스토어 생성 및 저장"""
    # URL 목록
    urls = [
        "https://namu.wiki/w/%EC%95%BC%EA%B5%AC/%EA%B2%BD%EA%B8%B0%20%EB%B0%A9%EC%8B%9D",
        "https://food-wiki-mate.streamlit.app/"  # 추가된 URL
    ]

    headers = {
        "User-Agent": os.environ["USER_AGENT"]
    }

    # 문서 로드
    docs = []
    for url in urls:
        try:
            loader = WebBaseLoader(url, header_template=headers)
            url_docs = loader.load()
            docs.extend(url_docs)
            print(f"Successfully loaded: {url}")
        except Exception as e:
            print(f"Error loading {url}: {e}")
    
    docs_list = [item for item in docs]

    # 문서 분할
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=0, model_name="gpt-4o-mini"
    )
    doc_splits = text_splitter.split_documents(docs_list)

    # 벡터 스토어 생성 및 저장
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="baseball-chroma",
        embedding=OpenAIEmbeddings(),
        persist_directory=str(PERSIST_DIRECTORY),
    )
    print("Vector store created and saved successfully!")
    return vectorstore

if __name__ == "__main__":
    create_vectorstore()