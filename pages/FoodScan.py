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
            img_byte_arr, resized_image = self.prepare_image(image)
            st.write("✅ 이미지 준비 완료")
            
            width, height = resized_image.size
            
            try:
                st.write("🚀 OpenAI API 호출 시작...")
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini-2024-07-18",
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 음식 이미지 분석 전문가입니다. 이미지의 모든 음식을 정확하게 식별하고 위치와 영양정보를 제공해야 합니다."
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"""다음 형식으로 정확히 응답해주세요:

[음식 1]
음식 이름: [구체적인 음식명]
위치: [x1,y1,x2,y2]
칼로리: [숫자]kcal
영양성분:
- 단백질: [숫자]g
- 탄수화물: [숫자]g
- 지방: [숫자]g

[음식 2]
...

주의사항:
- 이미지 크기는 {width}x{height}px입니다
- 모든 음식을 빠짐없이 분석해주세요
- 정확한 좌표값을 제공해주세요
- 영양정보는 1인분 기준으로 제공해주세요"""
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
                    max_tokens=4096,
                    timeout=180  # 3분으로 증가
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
        try:
            st.write("📦 바운딩 박스 그리기 시작...")
            img_draw = image.copy()
            draw = ImageDraw.Draw(img_draw)
            
            # 폰트 설정
            try:
                from PIL import ImageFont
                font = ImageFont.truetype("NanumGothic.ttf", 20)
            except Exception as font_error:
                st.warning(f"기본 폰트를 사용합니다: {str(font_error)}")
                font = None
            
            for item in detected_items:
                try:
                    if 'bbox' not in item:
                        st.warning(f"{item['food']}의 바운딩 박스 정보가 없습니다.")
                        continue
                        
                    x1, y1, x2, y2 = item['bbox']
                    
                    # 이미지 경계 확인
                    width, height = image.size
                    x1 = max(0, min(x1, width))
                    y1 = max(0, min(y1, height))
                    x2 = max(0, min(x2, width))
                    y2 = max(0, min(y2, height))
                    
                    # 박스 그리기
                    draw.rectangle([x1, y1, x2, y2], outline='red', width=3)
                    
                    # 텍스트 준비
                    text = f"{item['food']}"
                    if 'calories' in item:
                        text += f" ({item['calories']})"
                    
                    # 텍스트 배경 그리기
                    if font:
                        text_bbox = draw.textbbox((x1, y1-25), text, font=font)
                        draw.rectangle(text_bbox, fill='red')
                        draw.text((x1, y1-25), text, fill='white', font=font)
                    else:
                        draw.rectangle([x1, y1-25, x1+200, y1], fill='red')
                        draw.text((x1, y1-25), text, fill='white')
                    
                    st.write(f"✅ {item['food']}의 바운딩 박스 그리기 완료")
                    
                except Exception as box_error:
                    st.error(f"개별 박스 그리기 실패: {str(box_error)}")
                    continue
            
            st.write("📦 바운딩 박스 그리기 완료")
            return img_draw
            
        except Exception as e:
            st.error(f"바운딩 박스 그리기 중 오류 발생: {str(e)}")
            return image  # 오류 발생 시 원본 이미지 반환

    def prepare_image(self, image):
        import base64
        import io
        
        # 이미지 크기 조정 (최대 800px)
        max_size = 800
        ratio = min(max_size/image.size[0], max_size/image.size[1])
        if ratio < 1:
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # PIL Image를 바이트로 변환
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str, image  # 리사이즈된 이미지도 반환

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
            items = analysis_result.split('[음식 ')[1:]
            
            for item in items:
                current_item = {}
                lines = [line.strip() for line in item.split('\n') if line.strip()]
                
                for line in lines:
                    try:
                        if '음식 이름:' in line:
                            current_item['food'] = line.split('음식 이름:')[1].strip()
                        elif '위치:' in line:
                            # 좌표 파싱 개선
                            coords_str = line.split('위치:')[1].strip()
                            coords_str = coords_str.replace('[', '').replace(']', '')
                            coords = [int(float(x.strip())) for x in coords_str.split(',') if x.strip()]
                            if len(coords) == 4:  # 좌표가 4개인 경우만 저장
                                current_item['bbox'] = coords
                        elif '칼로리:' in line:
                            calories = line.split('칼로리:')[1].strip()
                            current_item['calories'] = calories.replace('kcal', '').strip()
                        elif '단백질:' in line:
                            protein = line.split('단백질:')[1].strip()
                            current_item['protein'] = protein.replace('g', '').strip()
                        elif '탄수화물:' in line:
                            carbs = line.split('탄수화물:')[1].strip()
                            current_item['carbs'] = carbs.replace('g', '').strip()
                        elif '지방:' in line:
                            fat = line.split('지방:')[1].strip()
                            current_item['fat'] = fat.replace('g', '').strip()
                    except ValueError as ve:
                        st.warning(f"값 파싱 오류 (무시하고 계속): {str(ve)}")
                        continue
                
                if 'food' in current_item and 'bbox' in current_item:
                    detected_items.append(current_item)

            return detected_items
            
        except Exception as e:
            st.error(f"분석 결과 파싱 중 오류 발생: {str(e)}")
            st.error(f"에러 발생 위치: {e.__traceback__.tb_frame.f_code.co_name}")
            return []

def display_results(image, detected_foods, nutrition_info):
    try:
        st.write("🖥 결과 표시 시작...")
        
        if not detected_foods:
            st.warning("감지된 음식이 없습니다.")
            st.image(image, caption="원본 이미지", use_column_width=True)
            return
            
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("🖼 분석된 이미지 표시")
            st.image(image, caption="분석된 음식", use_column_width=True)
        
        with col2:
            st.write("📊 영양 정보 표시")
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
                st.write(f"✅ {len(results_data)}개 음식의 영양 정보 표시 완료")
            else:
                st.warning("영양 정보를 표시할 수 없습니다.")
        
        st.write("🎉 결과 표시 완료")
        
    except Exception as e:
        st.error(f"결과 표시 중 오류 발생: {str(e)}")

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
