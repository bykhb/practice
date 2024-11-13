# main.py
import streamlit as st
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from datetime import datetime
from typing import Dict, List, Any
import importlib
import sys
from pathlib import Path

# Your existing NUTRITION_DB and classes (FoodAnalyzer, etc.) go here...
PAGES = {
    "🏠 Home": "Home",
    "📸 Food Scan": "FoodScan",
    "📊 Scan History": "ScanHistory",
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
    
    # 중복된 radio button 제거 - 하나만 유지
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    
    # Handle home page separately
    if selection == "🏠 Home":
        show_home()
    else:
        page = importlib.import_module(f"pages.{PAGES[selection]}")
        page.show()
    
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