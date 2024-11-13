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
    "📸 Food Scan": "Food Scan",
    "📊 Scan History": "Scan History",
    "💡 Food Consultant": "Food Consultant",
    "💬 Share": "Share by Slack"
}

def main():
    st.set_page_config(
        page_title="Food Analyzer",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    
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