
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
