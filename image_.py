import streamlit as st
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from datetime import datetime
from typing import Dict, List, Any

NUTRITION_DB = {
    "pizza": {
        "calories": 285,
        "protein": 12,
        "carbs": 36,
        "fat": 10,
        "vitamins": ["B12", "D"],
        "tips": ["Consider thin crust", "Add vegetables", "Limit to 2 slices"]
    },
    "salad": {
        "calories": 100,
        "protein": 3,
        "carbs": 12,
        "fat": 7,
        "vitamins": ["A", "C", "K"],
        "tips": ["Add lean protein", "Use olive oil dressing", "Include colorful vegetables"]
    },
    "burger": {
        "calories": 354,
        "protein": 20,
        "carbs": 29,
        "fat": 17,
        "vitamins": ["B12", "Iron"],
        "tips": ["Choose whole grain bun", "Add vegetables", "Consider plant-based options"]
    }
}

class FoodAnalyzer:
    def __init__(self):
        self.processor, self.model = self._load_model()
        self.nutrition_db = NUTRITION_DB

    @st.cache_resource
    def _load_model(self):
        processor = AutoImageProcessor.from_pretrained("nateraw/food")
        model = AutoModelForImageClassification.from_pretrained("nateraw/food")
        return processor, model

    def analyze_image(self, image: Image.Image) -> Dict[str, float]:
        inputs = self.processor(image, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
        top_probs, top_ids = torch.topk(probs, 3)
        
        return {
            self.model.config.id2label[id.item()]: prob.item()
            for id, prob in zip(top_ids, top_probs)
        }

    def get_nutrition_info(self, food_items: Dict[str, float]) -> Dict[str, Dict]:
        return {
            food: {**self.nutrition_db[food], "confidence": conf}
            for food, conf in food_items.items()
            if food in self.nutrition_db
        }

    def get_nutrition_summary(self, nutrition_info: Dict[str, Dict]) -> Dict[str, Any]:
        totals = {
            "calories": sum(food["calories"] for food in nutrition_info.values()),
            "protein": sum(food["protein"] for food in nutrition_info.values()),
            "carbs": sum(food["carbs"] for food in nutrition_info.values()),
            "fat": sum(food["fat"] for food in nutrition_info.values())
        }
        
        tips = [tip for food in nutrition_info.values() for tip in food["tips"]]
        vitamins = {v for food in nutrition_info.values() for v in food["vitamins"]}
        
        return {
            "totals": totals,
            "tips": list(set(tips)),
            "vitamins": sorted(vitamins)
        }

def display_results(detected_foods: Dict[str, float], nutrition_summary: Dict[str, Any]):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Detection Results")
        for food, conf in detected_foods.items():
            st.metric(label=food.title(), value=f"{conf:.1%}")
        
        st.subheader("📊 Nutrition Totals")
        for nutrient, value in nutrition_summary["totals"].items():
            st.metric(label=nutrient.title(), value=f"{value}{'g' if nutrient != 'calories' else ''}")
    
    with col2:
        st.subheader("🌟 Vitamins")
        st.write(", ".join(nutrition_summary["vitamins"]) if nutrition_summary["vitamins"] else "No data")
        
        st.subheader("✨ Tips")
        for i, tip in enumerate(nutrition_summary["tips"], 1):
            st.write(f"{i}. {tip}")

def main():
    st.set_page_config(page_title="Food Analyzer", page_icon="🥗", layout="wide")
    st.title("🥗 Food Analyzer")
    
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
    
    with st.sidebar:
        st.header("📊 History")
        for entry in st.session_state.history[-5:]:
            with st.expander(entry["datetime"]):
                st.image(entry["image"], width=100)
                for food, conf in entry["detected_foods"].items():
                    st.write(f"- {food}: {conf:.1%}")

if __name__ == "__main__":
    main()