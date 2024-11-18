# pages/Analyzer.py
import streamlit as st
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from datetime import datetime
from typing import Dict, List, Any


class FoodAnalyzer:
    def __init__(self):
        self.processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
        self.model = AutoModelForImageClassification.from_pretrained("microsoft/resnet-50")
        
    def analyze_image(self, image):
        inputs = self.processor(image, return_tensors="pt")
        outputs = self.model(**inputs)
        probs = outputs.logits.softmax(1)
        
        top_preds = torch.topk(probs, 3)
        results = []
        for i in range(3):
            score = top_preds.values[0][i].item()
            label = self.model.config.id2label[top_preds.indices[0][i].item()]
            results.append({"food": label, "confidence": f"{score:.2%}"})
        return results
        
    def get_nutrition_info(self, foods):
        nutrition_data = {}
        for food in foods:
            nutrition_data[food["food"]] = {
                "calories": "300 kcal",
                "protein": "10g",
                "carbs": "45g",
                "fat": "12g"
            }
        return nutrition_data
        
    def get_nutrition_summary(self, nutrition_info):
        # Implement summary logic
        return {}

def display_results(detected_foods, nutrition_info):
    st.subheader("분석 결과")
    
    for food in detected_foods:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"🍽 음식: {food['food']}")
            st.write(f"신뢰도: {food['confidence']}")
        
        with col2:
            if food['food'] in nutrition_info:
                nutri = nutrition_info[food['food']]
                st.write("영양 정보:")
                st.write(f"• 칼로리: {nutri['calories']}")
                st.write(f"• 단백질: {nutri['protein']}")
                st.write(f"• 탄수화물: {nutri['carbs']}")
                st.write(f"• 지방: {nutri['fat']}")

def show():
    st.title("🔍 Food Scan")
    
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
        
        display_results(detected_foods, nutrition_info)
