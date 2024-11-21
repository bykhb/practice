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
        try:
            # API 키 확인
            if not os.getenv('OPENAI_API_KEY'):
                st.error("OpenAI API 키가 설정되지 않았습니다.")
                return []
                
            # 이미지 준비 과정 로깅
            st.write("🔄 이미지 준비 시작...")
            img_byte_arr = self.prepare_image(image)
            st.write("✅ 이미지 준비 완료")
            
            width, height = image.size
            
            try:
                st.write("🚀 OpenAI API 호출 시작...")
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini-2024-07-18",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"""이미지에 있는 모든 음식을 찾아서 분석해주세요.
이미지에 음식이 하나만 있더라도 반드시 분석해주세요.

각 음식에 대해 다음 정보를 제공해주세요:
1. 음식 이름: [구체적인 음식명]
2. 위치: 음식이 있는 영역의 좌표값 (x1,y1,x2,y2 형식)
   - x1,y1: 왼쪽 상단 좌표
   - x2,y2: 오른쪽 하단 좌표
   - 이미지 크기는 {width}x{height}px입니다.
3. 칼로리: 예상 칼로리를 kcal 단위로
4. 영양성분: 단백질, 탄수화물, 지방을 g 단위로

주의사항:
- 이미지에 음식이 하나만 있는 경우에도 반드시 분석해주세요.
- 음식이 없는 경우에만 "음식을 찾을 수 없습니다"라고 답변해주세요.
- 좌표는 이미지 크기 내에서 적절한 값으로 지정해주세요."""
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
                    max_tokens=2000,
                    timeout=120  # 타임아웃 설정 추가
                )
                st.write("✅ OpenAI API 호출 완료")
                
                # API 응답 확인
                if not response or not response.choices:
                    st.error("API 응답이 비어있습니다.")
                    return []
                    
                analysis_result = response.choices[0].message.content
                st.info(f"분석 결과 (일부): {analysis_result[:100]}...")
                
            except Exception as api_error:
                st.error(f"OpenAI API 호출 중 오류 발생: {str(api_error)}")
                st.error(f"에러 타입: {type(api_error).__name__}")
                return []
            
            # 파싱 결과 확인
            detected_items = self.parse_detection_result(analysis_result)
            st.write(f"📊 감지된 아이템 수: {len(detected_items)}")
            
            return detected_items
            
        except Exception as e:
            st.error(f"전체 프로세스 오류: {str(e)}")
            st.error(f"에러 발생 위치: {e.__traceback__.tb_frame.f_code.co_name}")
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
                    model="gpt-4o-mini-2024-07-18",
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
