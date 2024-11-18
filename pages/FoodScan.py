# pages/Analyzer.py
import streamlit as st
from PIL import Image
from openai import OpenAI
from datetime import datetime
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw
import pandas as pd

class FoodAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def analyze_image(self, image):
        img_byte_arr = self.prepare_image(image)
        
        try:
            # 이미지 크기 가져오기
            width, height = image.size
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # 정확한 모델명으로 수정
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""이미지에서 발견된 각각의 음식에 대해 다음 정보를 제공해주세요:
이미지 크기는 너비 {width}px, 높이 {height}px입니다.

다음 형식으로 각 음식마다 답변해주세요:
1. 음식 이름: [음식명]
2. 위치: 왼쪽 상단 x,y 좌표와 오른쪽 하단 x,y 좌표 (예: 100,100,300,300)
3. 칼로리: [숫자]kcal
4. 영양성분: 단백질 [숫자]g, 탄수화물 [숫자]g, 지방 [숫자]g

각 음식은 번호를 매겨서 구분해주세요."""
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
            
            analysis_result = response.choices[0].message.content
            detected_items = self.parse_detection_result(analysis_result)
            return detected_items
            
        except Exception as e:
            st.error(f"이미지 분석 중 오류 발생: {str(e)}")
            return []

    def draw_boxes(self, image, detected_items):
        img_draw = image.copy()
        draw = ImageDraw.Draw(img_draw)
        
        # 폰트 설정 (기본 폰트 사용)
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("NanumGothic.ttf", 20)  # 한글 폰트
        except:
            font = None
        
        for item in detected_items:
            if 'bbox' in item:
                x1, y1, x2, y2 = item['bbox']
                
                # 박스 그리기
                draw.rectangle([x1, y1, x2, y2], outline='red', width=3)
                
                # 텍스트 배경 그리기
                text = f"{item['food']} ({item.get('calories', '')})"
                text_bbox = draw.textbbox((x1, y1-25), text, font=font)
                draw.rectangle(text_bbox, fill='red')
                
                # 텍스트 그리기
                draw.text((x1, y1-25), text, fill='white', font=font)
        
        return img_draw

    def prepare_image(self, image):
        import base64
        import io
        
        # PIL Image를 바이트로 변환
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

    def get_nutrition_info(self, foods):
        nutrition_data = {}
        for food in foods:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": f"'{food['food']}'의 예상되는 영양성분을 다음 형식으로만 답변해주세요:\n칼로리: [숫자]kcal\n단백질: [숫자]g\n탄수화물: [숫자]g\n지방: [숫자]g"
                        }
                    ]
                )
                nutrition_info = response.choices[0].message.content
                
                # GPT 응답을 파싱하여 영양 정보 구조화
                info_lines = nutrition_info.strip().split('\n')
                parsed_info = {}
                
                for line in info_lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        parsed_info[key.strip().lower()] = value.strip()
                
                nutrition_data[food["food"]] = {
                    "calories": parsed_info.get('칼로리', 'N/A'),
                    "protein": parsed_info.get('단백질', 'N/A'),
                    "carbs": parsed_info.get('탄수화물', 'N/A'),
                    "fat": parsed_info.get('지방', 'N/A')
                }
                
            except Exception as e:
                st.error(f"영양 정보 분석 중 오류 발생: {str(e)}")
                nutrition_data[food["food"]] = {
                    "calories": "분석 실패",
                    "protein": "분석 실패",
                    "carbs": "분석 실패",
                    "fat": "분석 실패"
                }
        return nutrition_data
        
    def get_nutrition_summary(self, nutrition_info):
        # Implement summary logic
        return {}

    def parse_detection_result(self, analysis_result):
        try:
            detected_items = []
            current_item = {}
            
            # 각 음식 항목을 분리
            items = analysis_result.split('\n\n')
            
            for item in items:
                lines = item.strip().split('\n')
                current_item = {}
                
                for line in lines:
                    if '음식 이름:' in line:
                        current_item['food'] = line.split('음식 이름:')[1].strip()
                    elif '위치:' in line:
                        coords = line.split('위치:')[1].strip()
                        try:
                            x1, y1, x2, y2 = map(int, coords.split(','))
                            current_item['bbox'] = [x1, y1, x2, y2]
                        except:
                            continue
                    elif '칼로리:' in line:
                        current_item['calories'] = line.split('칼로리:')[1].strip()
                    elif '영양성분:' in line:
                        current_item['nutrition'] = line.split('영양성분:')[1].strip()
                
                if current_item and 'food' in current_item and 'bbox' in current_item:
                    detected_items.append(current_item)
            
            return detected_items
        except Exception as e:
            st.error(f"분석 결과 파싱 중 오류 발생: {str(e)}")
            return []

def display_results(image, detected_foods, nutrition_info):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 바운딩 박스가 그려진 이미지 표시
        st.image(image, caption="분석된 음식", use_column_width=True)
    
    with col2:
        # 데이터프레임으로 결과 표시
        results_data = []
        for food in detected_foods:
            if food['food'] in nutrition_info:
                nutri = nutrition_info[food['food']]
                results_data.append({
                    '음식': food['food'],
                    '칼로리': nutri['calories'],
                    '단백질': nutri['protein'],
                    '탄수화물': nutri['carbs'],
                    '지방': nutri['fat']
                })
        
        if results_data:
            df = pd.DataFrame(results_data)
            st.table(df)
        else:
            st.warning("분석된 영양 정보가 없습니다.")

def show():
    st.title("🔍 음식 스캔")
    
    if 'history' not in st.session_state:
        st.session_state.history = []

    analyzer = FoodAnalyzer()
    
    uploaded_file = st.file_uploader("음식 이미지 업로드", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        with st.spinner("음식을 분석하고 있습니다..."):
            detected_foods = analyzer.analyze_image(image)
            nutrition_info = analyzer.get_nutrition_info(detected_foods)
            
            # 바운딩 박스 그리기
            annotated_image = analyzer.draw_boxes(image, detected_foods)
            
            # 세션 상태 업데이트
            st.session_state.history.append({
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "image": annotated_image,
                "detected_foods": detected_foods,
                "summary": nutrition_info
            })
        
        display_results(annotated_image, detected_foods, nutrition_info)
