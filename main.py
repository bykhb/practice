# main.py
import streamlit as st
import importlib
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

PAGES = {
    "🏠 Home": "Home",
    "📸 Food Scan": "FoodScan",
    "📊 Scan History": "ScanHistory",
    "🍳 Food Recipe": "FoodRecipe",
    "💡 Food Consultant": "FoodConsultant",
    "💬 Share": "Share"
}

def show_home():
    st.title("🏠 Food Analyzer Home")
    st.write("Welcome to the Food Analyzer! Upload food images to get nutritional analysis.")
    st.write("### Features:")
    st.write("- 📸 Food Scan")
    st.write("- 💡 Food Consultant")
    st.write("- 📊 Scan History")
    st.write("- 💬 Share")

def main():
    st.set_page_config(
        page_title="Food Analyzer",
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
    
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    
    # Home 페이지는 main.py에서 직접 처리
    if selection == "🏠 Home":
        show_home()
    else:
        try:
            # 다른 페이지들은 pages 디렉토리에서 import
            page_module = importlib.import_module(f"pages.{PAGES[selection]}")
            page_module.show()
        except Exception as e:
            st.error(f"Error loading page: {str(e)}")
    
    st.sidebar.divider()
    st.sidebar.title("About")
    st.sidebar.info(
        """
        This app helps you analyze food images and track your nutrition.
        Upload photos of your meals to get instant nutritional information
        and personalized tips!
        """
    )

if __name__ == "__main__":
    main()