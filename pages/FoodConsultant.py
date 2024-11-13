import streamlit as st

# 영양 데이터베이스 정의
NUTRITION_DB = {
    "vegetables": {
        "tips": [
            "Eat a rainbow of colors for different nutrients",
            "Steam or roast to preserve nutrients",
            "Include leafy greens daily"
        ]
    },
    "fruits": {
        "tips": [
            "Eat whole fruits instead of juices",
            "Choose seasonal fruits for best nutrition",
            "Pair with protein for balanced blood sugar"
        ]
    },
    "proteins": {
        "tips": [
            "Include both plant and animal sources",
            "Choose lean cuts of meat",
            "Include fish at least twice a week"
        ]
    },
    "grains": {
        "tips": [
            "Choose whole grains over refined grains",
            "Look for high fiber content",
            "Control portion sizes"
        ]
    }
}

def show():
    st.title("💡 Food Consultant")
    
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