# pages/Analyzer.py
import streamlit as st
from PIL import Image
from openai import OpenAI
from datetime import datetime
import os

class FoodAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def analyze_image(self, image):
        # 이미지를 바이트로 변환
        img_byte_arr = self.prepare_image(image)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "이 이미지에 있는 음식을 분석해주세요. 다음 형식으로 답변해주세요:\n1. 음식 이름\n2. 예상 칼로리\n3. 영양성분(단백질, 탄수화물, 지방)"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_byte_arr}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # OpenAI 응답을 파싱하여 결과 반환
            analysis_result = response.choices[0].message.content
            return [{"food": analysis_result, "confidence": "높음"}]
            
        except Exception as e:
            st.error(f"이미지 분석 중 오류 발생: {str(e)}")
            return []

    def prepare_image(self, image):
        import base64
        import io
        
        # PIL Image를 바이트로 변환
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

    def get_nutrition_info(self, foods):
        # 영양 정보 데이터베이스 연동 (예시)
        nutrition_data = {}
        for food in foods:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "user",
                            "content": f"'{food['food']}'의 예상되는 영양성분을 칼로리, 단백질, 탄수화물, 지방 수치로 알려주세요."
                        }
                    ]
                )
                nutrition_info = response.choices[0].message.content
                nutrition_data[food["food"]] = {
                    "calories": "분석 중...",
                    "protein": "분석 중...",
                    "carbs": "분석 중...",
                    "fat": "분석 중..."
                }
            except Exception as e:
                st.error(f"영양 정보 분석 중 오류 발생: {str(e)}")
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
