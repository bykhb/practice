
# pages/History.py
import streamlit as st
from datetime import datetime

def show():
    st.title("📊 Scan History")
    
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
