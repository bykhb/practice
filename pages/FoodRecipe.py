import streamlit as st

def show():
    st.title("🍳 음식 레시피")
    
    if 'history' not in st.session_state or not st.session_state.history:
        st.info("분석된 음식 기록이 없습니다. 먼저 음식 이미지를 분석해보세요!")
        return
        
    try:
        latest_analysis = st.session_state.history[-1]
        detected_food = latest_analysis.get("detected_foods", "")
        
        st.subheader(f"추천 레시피: {detected_food}")
        
        search_term = st.text_input("레시피 검색:", value=detected_food)
        
        if search_term:
            st.write("### 검색된 레시피:")
            st.write(f"1. 기본 {search_term} 레시피")
            st.write(f"2. 건강한 {search_term}")
            st.write(f"3. 간편한 {search_term}")
            
            with st.expander(f"기본 {search_term} 레시피"):
                st.write("### 재료:")
                st.write("- 재료 1")
                st.write("- 재료 2")
                st.write("### 조리방법:")
                st.write("1. 단계 1")
                st.write("2. 단계 2")
                
    except Exception as e:
        st.error(f"레시피를 불러오는 중 오류가 발생했습니다: {str(e)}") 