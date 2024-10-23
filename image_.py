import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch
import json
import plotly.express as px
from datetime import datetime
from typing import Dict, List, Any

# Constants
NUTRITION_DB = {
    "pizza": {
        "calories": 285,
        "protein": 12,
        "carbs": 36,
        "fat": 10,
        "vitamins": ["B12", "D"],
        "health_tips": [
            "Consider thin crust for fewer calories",
            "Add vegetables as toppings for more nutrients",
            "Watch portion size - limit to 2 slices"
        ]
    },
    "salad": {
        "calories": 100,
        "protein": 3,
        "carbs": 12,
        "fat": 7,
        "vitamins": ["A", "C", "K"],
        "health_tips": [
            "Add lean protein to make it more filling",
            "Use olive oil-based dressings for healthy fats",
            "Include a variety of colorful vegetables"
        ]
    },
    "burger": {
        "calories": 354,
        "protein": 20,
        "carbs": 29,
        "fat": 17,
        "vitamins": ["B12", "Iron"],
        "health_tips": [
            "Choose whole grain buns for more fiber",
            "Add lettuce and tomato for nutrients",
            "Consider plant-based alternatives"
        ]
    }
}

class FoodAnalyzer:
    def __init__(self):
        self.processor, self.model = self._load_model()
        self.nutrition_db = NUTRITION_DB

    @st.cache_resource
    def _load_model(self):
        """Load and cache the pre-trained model."""
        processor = AutoImageProcessor.from_pretrained("nateraw/food")
        model = AutoModelForImageClassification.from_pretrained("nateraw/food")
        return processor, model

    def analyze_image(self, image: Image.Image) -> Dict[str, float]:
        """Analyze the image and return top food predictions with confidence scores."""
        inputs = self.processor(image, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
        top_probs, top_ids = torch.topk(probabilities, 3)
        
        return {
            self.model.config.id2label[id.item()]: prob.item()
            for id, prob in zip(top_ids, top_probs)
        }

    def get_nutrition_info(self, food_items: Dict[str, float]) -> Dict[str, Dict]:
        """Get nutrition information for detected food items."""
        return {
            food: {**self.nutrition_db[food], "confidence": confidence}
            for food, confidence in food_items.items()
            if food in self.nutrition_db
        }

    def generate_health_advice(self, nutrition_info: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate comprehensive health advice based on nutrition information."""
        nutrition_analysis = {
            "calories": sum(food["calories"] for food in nutrition_info.values()),
            "protein": sum(food["protein"] for food in nutrition_info.values()),
            "carbs": sum(food["carbs"] for food in nutrition_info.values()),
            "fat": sum(food["fat"] for food in nutrition_info.values())
        }
        
        # Calculate percentage of daily values (based on 2000 calorie diet)
        daily_values = {
            "calories": f"{(nutrition_analysis['calories'] / 2000 * 100):.1f}%",
            "protein": f"{(nutrition_analysis['protein'] / 50 * 100):.1f}%",
            "carbs": f"{(nutrition_analysis['carbs'] / 300 * 100):.1f}%",
            "fat": f"{(nutrition_analysis['fat'] / 65 * 100):.1f}%"
        }
        
        health_tips = []
        vitamins = set()
        
        for food_info in nutrition_info.values():
            if "health_tips" in food_info:
                health_tips.extend(food_info["health_tips"])
            if "vitamins" in food_info:
                vitamins.update(food_info["vitamins"])
        
        return {
            "summary": (
                f"This meal contains approximately {nutrition_analysis['calories']} calories "
                f"({daily_values['calories']} of daily value), "
                f"{nutrition_analysis['protein']}g protein, "
                f"{nutrition_analysis['carbs']}g carbs, and "
                f"{nutrition_analysis['fat']}g fat."
            ),
            "health_tips": list(set(health_tips)),  # Remove duplicates
            "nutrition_analysis": nutrition_analysis,
            "daily_values": daily_values,
            "vitamins": list(vitamins)
        }

def create_nutrition_chart(nutrition_data: Dict[str, float]) -> px.Figure:
    """Create an interactive nutrition breakdown chart."""
    fig = px.pie(
        values=list(nutrition_data.values()),
        names=list(nutrition_data.keys()),
        title="Nutrition Breakdown",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def display_history(history: List[Dict]):
    """Display analysis history with improved formatting."""
    st.header("📊 Analysis History")
    for entry in history[-5:]:  # Show last 5 entries
        with st.expander(f"📅 {entry['datetime']}"):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(entry['image'], width=100)
            with col2:
                st.write("**Detected Foods:**")
                for food, conf in entry['detected_foods'].items():
                    st.write(f"- {food}: {conf:.1%}")

def main():
    st.set_page_config(
        page_title="Food Analyzer & Health Advisor",
        page_icon="🥗",
        layout="wide"
    )

    if 'history' not in st.session_state:
        st.session_state.history = []

    st.title("🥗 Food Analyzer & Health Advisor")
    st.write("Upload a food image to get nutritional analysis and health advice!")
    
    analyzer = FoodAnalyzer()
    
    # Sidebar
    with st.sidebar:
        display_history(st.session_state.history)
    
    # Main content
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of your food for best results"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Image", use_column_width=True)
        
        with st.spinner("🔍 Analyzing your food..."):
            detected_foods = analyzer.analyze_image(image)
            nutrition_info = analyzer.get_nutrition_info(detected_foods)
            health_advice = analyzer.generate_health_advice(nutrition_info)
            
            # Save to history
            st.session_state.history.append({
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "image": image,
                "detected_foods": detected_foods,
                "nutrition_info": nutrition_info,
                "health_advice": health_advice
            })
        
        # Results display
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Detection Results")
            for food, confidence in detected_foods.items():
                st.metric(
                    label=food.title(),
                    value=f"{confidence:.1%} confidence"
                )
            
            st.subheader("📊 Nutrition Information")
            fig = create_nutrition_chart(health_advice["nutrition_analysis"])
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("🎯 Daily Values")
            for nutrient, percentage in health_advice["daily_values"].items():
                st.write(f"**{nutrient.title()}:** {percentage}")
        
        with col2:
            st.subheader("💡 Health Insights")
            st.info(health_advice["summary"])
            
            st.subheader("🌟 Vitamins Present")
            if health_advice["vitamins"]:
                st.write(", ".join(sorted(health_advice["vitamins"])))
            else:
                st.write("No vitamin information available")
            
            st.subheader("✨ Healthy Eating Tips")
            for i, tip in enumerate(health_advice["health_tips"], 1):
                st.write(f"{i}. {tip}")

if __name__ == "__main__":
    main()