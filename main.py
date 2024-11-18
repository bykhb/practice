# main.py
import streamlit as st
import importlib
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

PAGES = {
    "🏠 홈": "Home",
    "📸 음식 스캔": "FoodScan",
    "🍳 음식 레시피": "FoodRecipe",
    "💡 음식 컨설턴트": "FoodConsultant",
    "💬 공유하기": "Share"
}

def show_home():
    st.title("🏠 음식 분석기 홈")
    st.write("음식 분석기에 오신 것을 환영합니다! 음식 이미지를 업로드하여 영양 분석을 받아보세요.")
    st.write("### 주요 기능:")
    st.write("- 📸 음식 스캔")
    st.write("- 🍳 음식 레시피")
    st.write("- 💡 음식 컨설턴트")
    st.write("- 💬 공유하기")

def main():
    st.set_page_config(
        page_title="음식 분석기",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )
    
    # Hide default Streamlit pages navigation
    hide_pages = """
        <style>
            div[data-testid="stSidebarNav"] {display: none !important;}
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_pages, unsafe_allow_html=True)
    
    st.sidebar.title("메뉴")
    selection = st.sidebar.radio("이동하기", list(PAGES.keys()))
    
    # Home 페이지는 main.py에서 직접 처리
    if selection == "🏠 홈":
        show_home()
    else:
        try:
            # 다른 페이지들은 pages 디렉토리에서 import
            page_module = importlib.import_module(f"pages.{PAGES[selection]}")
            page_module.show()
        except Exception as e:
            st.error(f"Error loading page: {str(e)}")
    
    st.sidebar.divider()
    st.sidebar.title("소개")
    st.sidebar.info(
        """
        이 앱은 음식 이미지를 분석하고 영양 정보를 추적하는 데 도움을 줍니다.
        식사 사진을 업로드하여 즉시 영양 정보와 맞춤형 조언을 받아보세요!
        """
    )

if __name__ == "__main__":
    main()