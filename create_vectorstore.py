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


# Chroma DB 경로 설정
PERSIST_DIRECTORY = Path(__file__).parent / "chroma"

def create_vectorstore():
    """벡터 스토어 생성 및 저장"""
    # URL 목록
    urls = [
        "https://namu.wiki/w/%EC%95%BC%EA%B5%AC/%EA%B2%BD%EA%B8%B0%20%EB%B0%A9%EC%8B%9D",
    ]

    headers = {
        "User-Agent": os.environ["USER_AGENT"]
    }

    # 문서 로드
    docs = [WebBaseLoader(url, header_template=headers).load() for url in urls]
    docs_list = [item for sublist in docs for item in sublist]

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