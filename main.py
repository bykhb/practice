# main.py
import streamlit as st
import importlib
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

PAGES = {
    "🏠 홈": "Home",
    "📸 음식 스캔": "FoodScan",
    "🍳 음식 레시피": "FoodRecipe",
    "💡 음식 컨설턴트": "FoodConsultant",
    "💬 공유하기": "Share",
    "📚 지식DB": "KnowledgeDB"
}


def collect_yes24_bestsellers():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    with st.spinner('베스트셀러 정보를 수집하고 있습니다...'):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        data = []

        try:
            base_url = "https://www.yes24.com"
            url = f"{base_url}/Product/Category/BestSeller?CategoryNumber=001&sumgb=06"
            driver.get(url)

            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item_info")))

            items = driver.find_elements(By.CLASS_NAME, "item_info")

            for item in items:
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, ".info_name .gd_name")
                    title = title_elem.text.strip()
                    link = title_elem.get_attribute("href")
                    if link.startswith('/'):
                        link = base_url + link
                    
                    author = item.find_element(By.CSS_SELECTOR, ".info_pubGrp .info_auth a").text.strip()
                    price = item.find_element(By.CSS_SELECTOR, ".info_price .txt_num .yes_b").text.strip()

                    data.append({
                        "title": title,
                        "author": author,
                        "price": price,
                        "link": link
                    })
                except Exception as e:
                    continue

        except Exception as e:
            st.error(f"데이터 수집 중 오류가 발생했습니다: {e}")
        finally:
            driver.quit()

        return data

def show_bestsellers():
    st.title("📚 YES24 베스트셀러")
    st.write("현재 YES24의 베스트셀러 목록입니다.")

    if st.button("베스트셀러 목록 새로고침"):
        bestsellers = collect_yes24_bestsellers()
        
        for book in bestsellers:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### [{book['title']}]({book['link']})")
                    st.write(f"저자: {book['author']}")
                with col2:
                    st.write(f"가격: {book['price']}원")
                st.divider()


def show_home():
    st.title("🏠 Food Analzyer")
    st.write("Food Analzyer에 오신 것을 환영합니다! 음식 이미지를 업로드하여 영양 분석을 받아보세요.")
    st.write("### 주요 기능:")
    st.write("- 📸 음식 스캔")
    st.write("- 💡 음식 컨설턴트")
    st.write("- 🍳 음식 레시피 추천")
    st.write("- 📚 음식도서")
    st.write("- 💬 공유하기")
    st.write("- 📚 지식DB")


def show_opendata():
    st.title("📊 공공데이터 분석")
    st.write("식품 관련 공공데이터를 분석하고 시각화합니다.")

    # 데이터 로드 (예시 - 실제 데이터 경로로 수정 필요)
    try:
        # 여러 데이터 소스 선택 옵션
        data_source = st.selectbox(
            "데이터 소스 선택",
            ["식품영양성분", "식당위생정보", "농산물가격정보"]
        )

        if data_source == "식품영양성분":
            # 예시 데이터 생성 (실제 데이터로 교체 필요)
            df = pd.DataFrame({
                '식품명': ['사과', '바나나', '오렌지', '포도', '키위'],
                '칼로리': [52, 89, 47, 69, 61],
                '당류': [10.4, 12.2, 9.3, 15.5, 9.0],
                '단백질': [0.3, 1.1, 0.9, 0.7, 1.1]
            })

            st.subheader("식품영양성분 데이터")
            st.dataframe(df)

            # 시각화
            chart_type = st.selectbox(
                "차트 유형 선택",
                ["막대 그래프", "선 그래프", "산점도"]
            )

            if chart_type == "막대 그래프":
                fig = px.bar(df, x='식품명', y='칼로리', title='식품별 칼로리 함량')
                st.plotly_chart(fig)

            elif chart_type == "선 그래프":
                fig = px.line(df, x='식품명', y='칼로리', title='식품별 칼로리 함량')
                st.plotly_chart(fig)

            elif chart_type == "산점도":
                fig = px.scatter(df, x='당류', y='단백질', title='당류와 단백질 관계')
                st.plotly_chart(fig)

def main():
    st.set_page_config(
        page_title="Food Analzyer",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )
    
    # Hide default Streamlit pages navigation
    hide_pages = """
        <style>
            div[data-testid="stSidebarNav"] {display: none !important;}
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_pages, unsafe_allow_html=True)
    
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("이동하기", list(PAGES.keys()))
    
    # Home 페이지는 main.py에서 직접 처리
    if selection == "🏠 홈":
        show_home()
    elif selection == "📚 베스트셀러":
        show_bestsellers()
    elif selection == "📚 오픈데이터":
        show_opendata()
    else:
        try:
            page_module = importlib.import_module(f"pages.{PAGES[selection]}")
            page_module.show()
        except Exception as e:
            st.error(f"Error loading page: {str(e)}")
            
    st.sidebar.divider()
    st.sidebar.title("소개")
    st.sidebar.info(
        """
        이 서비스는 음식 이미지를 분석하고 영양 정보를 추적하는 것에 도움을 줍니다.
        식사 사진을 업로드하여 즉시 영양 정보와 맞춤형 조언을 받아보세요!
        """
    )

if __name__ == "__main__":
    main()