# pages/Home.py
import streamlit as st

def show():
    st.title("🏠 Food Analyzer Home")
    st.write("Welcome to the Food Analyzer! Upload food images to get nutritional analysis.")
    st.write("### Features:")
    st.write("- 📸 Image Recognition")
    st.write("- 🍎 Nutritional Analysis")
    st.write("- 📊 Historical Tracking")
    st.write("- 💡 Personalized Tips")

# pages/Analyzer.py
import streamlit as st
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from datetime import datetime
from typing import Dict, List, Any

def show():
    st.title("🔍 Food Analysis")
    
    if 'history' not in st.session_state:
        st.session_state.history = []

    analyzer = FoodAnalyzer()
    
    uploaded_file = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food", use_column_width=True)
        
        with st.spinner("Analyzing..."):
            detected_foods = analyzer.analyze_image(image)
            nutrition_info = analyzer.get_nutrition_info(detected_foods)
            nutrition_summary = analyzer.get_nutrition_summary(nutrition_info)
            
            st.session_state.history.append({
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "image": image,
                "detected_foods": detected_foods,
                "summary": nutrition_summary
            })
        
        display_results(detected_foods, nutrition_summary)

# pages/History.py
import streamlit as st
from datetime import datetime

def show():
    st.title("📊 Analysis History")
    
    if 'history' not in st.session_state:
        st.session_state.history = []
        
    if not st.session_state.history:
        st.info("No analysis history yet. Try analyzing some food images!")
        return
        
    for entry in st.session_state.history:
        with st.expander(entry["datetime"]):
            col1, col2 = st.columns(2)
            with col1:
                st.image(entry["image"], width=200)
            with col2:
                st.write("### Detected Foods:")
                for food, conf in entry["detected_foods"].items():
                    st.write(f"- {food}: {conf:.1%}")
                st.write("### Nutrition Summary:")
                for nutrient, value in entry["summary"]["totals"].items():
                    st.write(f"- {nutrient.title()}: {value}{'g' if nutrient != 'calories' else ''}")

# pages/Tips.py
import streamlit as st

def show():
    st.title("💡 Healthy Eating Tips")
    
    st.write("""
    ### General Tips:
    1. Balance your plate with proteins, carbs, and vegetables
    2. Stay hydrated throughout the day
    3. Watch portion sizes
    4. Include a variety of colors in your meals
    
    ### Food-Specific Tips:
    """)
    
    for food, info in NUTRITION_DB.items():
        with st.expander(f"Tips for {food.title()}"):
            for tip in info["tips"]:
                st.write(f"- {tip}")

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
    "🔍 Analyzer": "Analyzer",
    "📊 History": "History",
    "💡 Tips": "Tips"
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