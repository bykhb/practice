import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import os
import io
from openai import OpenAI

def send_email(recipient_email, image, analysis_text):
    try:
        # 이메일 서버 설정
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv('EMAIL_ADDRESS')
        sender_password = os.getenv('EMAIL_PASSWORD')

        # 이메일 메시지 생성
        msg = MIMEMultipart()
        msg['Subject'] = '음식 분석 결과'
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # 분석 텍스트 추가
        text_part = MIMEText(analysis_text, 'plain', 'utf-8')
        msg.attach(text_part)

        # 이미지 첨부
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        image_part = MIMEImage(img_byte_arr)
        image_part.add_header('Content-Disposition', 'attachment', filename='food_analysis.png')
        msg.attach(image_part)

        # 이메일 전송
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.error(f"이메일 전송 중 오류 발생: {str(e)}")
        return False

def get_nutrition_summary(detected_foods, nutrition_info):
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # 영양 정보를 문자열로 구성
        foods_info = []
        for food in detected_foods:
            if food['food'] in nutrition_info:
                nutri = nutrition_info[food['food']]
                foods_info.append(f"""
                음식: {food['food']}
                칼로리: {nutri['calories']}
                단백질: {nutri['protein']}
                탄수화물: {nutri['carbs']}
                지방: {nutri['fat']}
                """)
        
        # GPT-4에 요약 요청
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": f"""다음 음식들의 영양 정보를 바탕으로 전체적인 영양 분석 요약을 작성해주세요:

{'\n'.join(foods_info)}

다음 내용을 포함해주세요:
1. 전체 칼로리 합계
2. 영양 균형 평가
3. 건강 관점에서의 조언
"""
                }
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"영양 정보 요약 생성 중 오류 발생: {str(e)}"

def show():
    st.title("💬 공유하기")
    
    if 'history' not in st.session_state or not st.session_state.history:
        st.info("공유할 분석 기록이 없습니다. 먼저 음식 이미지를 분석해보세요!")
        return
    
    try:    
        latest_analysis = st.session_state.history[-1]
        
        st.subheader("최근 분석 결과")
        
        col1, col2 = st.columns(2)
        
        if not all(key in latest_analysis for key in ["image", "datetime", "detected_foods", "summary"]):
            st.error("일부 분석 데이터가 누락되었습니다. 이미지를 다시 분석해주세요.")
            return
            
        with col1:
            st.image(latest_analysis["image"], caption="분석된 음식", use_column_width=True)
            
        with col2:
            st.write(f"**분석 시간:** {latest_analysis['datetime']}")
            st.write(f"**감지된 음식:** {', '.join([food['food'] for food in latest_analysis['detected_foods']])}")
            
            # GPT-4를 사용한 영양 정보 요약
            nutrition_summary = get_nutrition_summary(
                latest_analysis['detected_foods'],
                latest_analysis['summary']
            )
            st.write("**영양 분석 요약:**")
            st.write(nutrition_summary)
        
        # 이메일 입력 필드 추가
        recipient_email = st.text_input("분석 결과를 받을 이메일 주소를 입력하세요:", key="email_input")
        
        if recipient_email:
            if st.button("이메일로 전송하기", key="send_email_button"):
                analysis_text = f"""
                음식 분석 결과

                분석 시간: {latest_analysis['datetime']}
                감지된 음식: {', '.join([food['food'] for food in latest_analysis['detected_foods']])}

                영양 분석 요약:
                {nutrition_summary}
                """
                
                if send_email(recipient_email, latest_analysis["image"], analysis_text):
                    st.success("분석 결과가 이메일로 전송되었습니다!")
                else:
                    st.error("이메일 전송 중 오류가 발생했습니다.")
        else:
            if st.button("이메일로 전송하기", key="empty_email_button"):
                st.warning("이메일 주소를 입력해주세요.")
            
    except Exception as e:
        st.error(f"결과를 표시하는 중 오류가 발생했습니다: {str(e)}")
