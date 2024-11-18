import streamlit as st
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import io

def share_to_slack(image, analysis_text):
    try:
        client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
        
        # 이미지를 바이트로 변환
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # 이미지 업로드
        image_upload = client.files_upload_v2(
            channel=os.getenv('SLACK_CHANNEL_ID'),
            file=img_byte_arr,
            filename="food_analysis.png",
            initial_comment=analysis_text
        )
        return True
    except SlackApiError as e:
        st.error(f"Slack 공유 중 오류 발생: {str(e)}")
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
        
        if st.button("Slack으로 공유하기"):
            analysis_text = f"""
            분석 시간: {latest_analysis['datetime']}
            감지된 음식: {latest_analysis['detected_foods']}
            영양 요약: {latest_analysis['summary']}
            """
            
            if share_to_slack(latest_analysis["image"], analysis_text):
                st.success("Slack에 성공적으로 공유되었습니다!")
            else:
                st.error("Slack 공유 중 오류가 발생했습니다.")
            
    except Exception as e:
        st.error(f"결과를 표시하는 중 오류가 발생했습니다: {str(e)}")
