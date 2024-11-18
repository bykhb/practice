import streamlit as st

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
        
        if st.button("결과 공유하기"):
            st.success("결과가 성공적으로 공유되었습니다! (임시 메시지)")
            
    except Exception as e:
        st.error(f"결과를 표시하는 중 오류가 발생했습니다: {str(e)}")
