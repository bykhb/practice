import streamlit as st

def show():
    st.title("🍳 Food Recipe")
    
    # 세션 상태 확인
    if 'history' not in st.session_state or not st.session_state.history:
        st.info("No food analysis history found. Try analyzing some food images first!")
        return
        
    try:
        # 가장 최근 분석된 음식 가져오기
        latest_analysis = st.session_state.history[-1]
        detected_food = latest_analysis.get("detected_foods", "")
        
        st.subheader(f"Recipe Suggestions for: {detected_food}")
        
        # 레시피 검색 기능
        search_term = st.text_input("Search for recipes:", value=detected_food)
        
        if search_term:
            st.write("### Found Recipes:")
            # 여기에 실제 레시피 검색 및 표시 로직 구현
            # 임시 예시 데이터
            st.write(f"1. Basic {search_term} Recipe")
            st.write(f"2. Healthy {search_term}")
            st.write(f"3. Quick {search_term}")
            
            # 레시피 상세 정보 (예시)
            with st.expander(f"Basic {search_term} Recipe"):
                st.write("### Ingredients:")
                st.write("- Ingredient 1")
                st.write("- Ingredient 2")
                st.write("### Instructions:")
                st.write("1. Step 1")
                st.write("2. Step 2")
                
    except Exception as e:
        st.error(f"An error occurred while loading recipes: {str(e)}") 