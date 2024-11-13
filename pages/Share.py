import streamlit as st

def show():
    st.title("💬 Share")
    
    if 'history' not in st.session_state or not st.session_state.history:
        st.info("No analysis history to share. Try analyzing some food images first!")
        return
        
    # 가장 최근 분석 결과 선택
    latest_analysis = st.session_state.history[-1]
    
    st.subheader("Latest Analysis Results")
    
    # 이미지와 분석 결과 표시
    col1, col2 = st.columns(2)
    with col1:
        st.image(latest_analysis["image"], caption="Analyzed Food", use_column_width=True)
    with col2:
        st.write(f"**Analyzed on:** {latest_analysis['datetime']}")
        st.write(f"**Detected Food:** {latest_analysis['detected_foods']}")
        
        if latest_analysis["summary"]:
            st.write("**Nutrition Summary:**")
            st.write(latest_analysis["summary"])
    
    # 공유 버튼
    if st.button("Share Results"):
        st.success("Results shared successfully! (This is a placeholder message)")
