import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import os
import io

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
            st.write(f"**감지된 음식:** {latest_analysis['detected_foods']}")
            
            if latest_analysis["summary"]:
                st.write("**영양 요약:**")
                st.write(latest_analysis["summary"])
        
        # 이메일 입력 필드 추가
        recipient_email = st.text_input("분석 결과를 받을 이메일 주소를 입력하세요:", key="email_input")
        
        # 이메일이 입력된 경우와 아닌 경우에 대한 버튼을 분리하고 각각 고유한 key 추가
        if recipient_email:
            if st.button("이메일로 전송하기", key="send_email_button"):
                analysis_text = f"""
                음식 분석 결과
                
                분석 시간: {latest_analysis['datetime']}
                감지된 음식: {latest_analysis['detected_foods']}
                영양 요약: {latest_analysis['summary']}
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
