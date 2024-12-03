import streamlit as st
from openai import OpenAI
import re
import os

# 페이지 설정을 가장 먼저 실행
# st.set_page_config(
#     page_title="Food Consultant",
#     page_icon="🍜",
#     layout="centered",
#     initial_sidebar_state="collapsed"
# )

# 모든 상수와 데이터 구조를 그 다음에 정의
DAILY_RECOMMENDED_CALORIES = 2000
CHARACTERS = ['Gordon (전문적인 조언)', 'Baek (친근한 설명)', 'Morimoto (정교한 분석)']
FOOD_CATEGORIES = ['한식', '일식', '양식']

# 음식 목록 정의
food_lists = {
    '한식': ['김치찌개', '된장찌개', '비빔밥', '불고기', '삼겹살', '떡볶이', '냉면'],
    '일식': ['초밥', '라멘', '우동', '돈카츠', '오니기리', '규동'],
    '양식': ['파스타', '피자', '스테이크', '햄버거', '샐러드', '리조또']
}

# 음식 정보 정의
food_info = {
    '김치찌개': {
        '칼로리': 500,
        '설명': {
            'Gordon': "이 김치찌개의 매콤한 맛과 깊은 감칠맛이 일품입니다. 신선한 재료 선택이 핵심이죠.",
            'Baek': "김치는 잘 익은 걸 쓰시고, 돼지고기는 삼겹살이 가장 좋아요. 된장도 조금 넣어보세요.",
            'Morimoto': "김치의 발효 정도와 육수의 밸런스가 완벽하게 조화를 이루고 있습니다."
        }
    },
    '된장찌개': {
        '칼로리': 450,
        '설명': {
            'Gordon': "된장의 깊은 풍미가 일품입니다. 신선한 해산물을 추가하면 더욱 좋겠네요.",
            'Baek': "구수한 된장찌개의 맛을 살리려면 멸치육수가 중요해요. 채소는 듬뿍 넣으세요.",
            'Morimoto': "된장의 발효향과 채소의 단맛이 조화롭게 어우러져 있습니다."
        }
    },
    '비빔밥': {
        '칼로리': 600,
        '설명': {
            'Gordon': "다양한 채소와 고기의 조화가 환상적입니다. 고추장의 양이 핵심이죠.",
            'Baek': "나물은 계절별로 신선한 걸 쓰세요. 고슬고슬한 밥이 포인트예요.",
            'Morimoto': "각 재료의 식감과 맛이 완벽한 균형을 이루고 있습니다."
        }
    },
    '불고기': {
        '칼로리': 550,
        '설명': {
            'Gordon': "마리네이드의 균형이 완벽합니다. 고기의 선택이 중요하죠.",
            'Baek': "배즙을 넣으면 고기가 더 부드러워져요. 양파는 듬뿍 넣으세요.",
            'Morimoto': "한국식 숙성 방식이 육질의 풍미를 극대화했습니다."
        }
    },
    '삼겹살': {
        '칼로리': 750,
        '설명': {
            'Gordon': "완벽한 마블링과 구워진 상태가 일품입니다.",
            'Baek': "두께 1.5cm로 썰어서 중간 불에 구워야 제맛이에요.",
            'Morimoto': "지방과 살코기의 비율이 이상적인 밸런스를 보여줍니다."
        }
    },
    '떡볶이': {
        '칼로리': 400,
        '설명': {
            'Gordon': "소스의 농도와 매콤달콤한 맛이 완벽한 밸런스를 이룹니다.",
            'Baek': "쌀떡을 사용하고, 고추장과 고춧가루의 비율이 중요해요.",
            'Morimoto': "떡의 쫄깃함과 소스의 농도가 이상적으로 조화됩니다."
        }
    },
    '냉면': {
        '칼로리': 480,
        '설명': {
            'Gordon': "육수의 깊이가 인상적입니다. 면의 탄력도 완벽하네요.",
            'Baek': "동치미 국물을 섞으면 더 시원해져요. 식초와 겨자는 기호대로!",
            'Morimoto': "면의 식감과 육수의 청량감이 완벽한 조화를 이룹니다."
        }
    },
    
    # 일식
    '초밥': {
        '칼로리': 350,
        '설명': {
            'Gordon': "신선한 생선의 품질이 돋보입니다. 와사비의 양이 절묘하네요.",
            'Baek': "샤리는 체온보다 살짝 낮게, 생선은 신선한 걸로!",
            'Morimoto': "쌀의 온도와 생선의 신선도가 완벽한 밸런스를 이룹니다."
        }
    },
    '라멘': {
        '칼로리': 550,
        '설명': {
            'Gordon': "스프의 깊이가 인상적입니다. 차슈의 부드러움도 일품이네요.",
            'Baek': "돼지뼈로 우려낸 육수가 진한 맛을 내요.",
            'Morimoto': "면의 탄력도와 육수의 농도가 이상적인 조화를 이룹니다."
        }
    },
    '우동': {
        '칼로리': 400,
        '설명': {
            'Gordon': "다시마와 가츠오부시의 풍미가 완벽합니다.",
            'Baek': "면의 쫄깃함이 중요해요. 육수는 깔끔하게!",
            'Morimoto': "면의 굵기와 육수의 맛이 이상적으로 어우러집니다."
        }
    },
    '돈카츠': {
        '칼로리': 650,
        '설명': {
            'Gordon': "바삭한 튀김옷과 부드러운 고기의 조화가 완벽합니다.",
            'Baek': "돼지고기는 등심으로, 빵가루는 신선한 걸로!",
            'Morimoto': "튀김옷의 바삭함과 고기의 육즙이 완벽하게 보존되었습니다."
        }
    },
    '오니기리': {
        '칼로리': 250,
        '설명': {
            'Gordon': "심플하지만 완벽한 밸런스의 맛입니다.",
            'Baek': "밥은 따뜻할 때 만들고, 김은 나중에 싸세요.",
            'Morimoto': "밥의 압축도와 속재료의 조화가 이상적입니다."
        }
    },
    '규동': {
        '칼로리': 600,
        '설명': {
            'Gordon': "소고기의 부드러움과 간장 소스의 조화가 일품입니다.",
            'Baek': "양파는 충분히 볶아서 단맛을 내는 게 포인트!",
            'Morimoto': "고기의 식감과 양파의 단맛이 완벽한 밸런스를 이룹니다."
        }
    },

    # 양식
    '파스타': {
        '칼로리': 550,
        '설명': {
            'Gordon': "알덴테로 삶은 면과 소스의 조화가 완벽합니다.",
            'Baek': "면을 삶을 때 소금을 넉넉히 넣어주세요.",
            'Morimoto': "면의 식감과 소스의 농도가 이상적으로 어우러집니다."
        }
    },
    '피자': {
        '칼로리': 800,
        '설명': {
            'Gordon': "도우의 바삭함과 토핑의 조화가 일품입니다.",
            'Baek': "치즈는 모짜렐라와 체다를 섞어서 사용하세요.",
            'Morimoto': "도우의 식감과 토핑의 밸런스가 완벽합니다."
        }
    },
    '스테이크': {
        '칼로리': 700,
        '설명': {
            'Gordon': "미디엄 레어로 조리된 완벽한 굽기입니다.",
            'Baek': "고기는 실온에 30분 두었다가 구워주세요.",
            'Morimoto': "육질의 마블링과 굽기 정도가 이상적입니다."
        }
    },
    '햄버거': {
        '칼로리': 650,
        '설명': {
            'Gordon': "패티의 육즙과 소스의 조화가 환상적입니다.",
            'Baek': "패티는 두껍게, 채소는 신선하게!",
            'Morimoto': "빵, 패티, 채소의 밸런스가 완벽합니다."
        }
    },
    '샐러드': {
        '칼로리': 200,
        '설명': {
            'Gordon': "신선한 채소와 드레싱의 조화가 일품입니다.",
            'Baek': "채소는 차가운 물에 담가두었다가 사용하세요.",
            'Morimoto': "채소의 신선도와 드레싱의 밸런스가 이상적입니다."
        }
    },
    '리조또': {
        '칼로리': 500,
        '설명': {
            'Gordon': "크리미한 텍스처와 파르메산의 풍미가 완벽합니다.",
            'Baek': "쌀은 충분히 볶아주고, 육수는 천천히 부어가며 저어주세요.",
            'Morimoto': "쌀의 알덴테한 식감과 크림소스가 이상적으로 어우러집니다."
        }
    }
}

# CSS 스타일
st.markdown("""
    <style>
    .main { 
        padding: 20px;
        max-width: 1200px;
        margin: 0 auto;
    }
    .stProgress > div > div > div > div { 
        background-color: #FF4B4B; 
    }
    .css-1kyxreq { 
        margin-top: 0;
        padding-top: 2rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 80rem;
    }
    .st-emotion-cache-16idsys p {
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# UI 구성
st.title('🍜 Food Consultant')

# 전문가 선택
st.header('👨‍🍳 요리 전문가 선택')
character = st.radio(
    "조언을 들을 전문가를 선택하세요:",
    CHARACTERS,
    horizontal=True
)
character_name = character.split(' ')[0]

st.divider()

# 음식 선택
st.header('🍱 음식 선택')
col1, col2 = st.columns(2)
with col1:
    food_category = st.selectbox('카테고리 선택:', FOOD_CATEGORIES)
with col2:
    food = st.selectbox('음식 선택:', food_lists[food_category])

st.divider()

# 분석 결과 섹션
st.header('📊 분석 결과')

# 전문가 의견
st.subheader("💬 전문가의 조언")
if food in food_info:
    st.write(food_info[food]['설명'][character_name])

    # 칼로리 정보
    st.subheader("🔥 칼로리 정보")
    calories = food_info[food]['칼로리']
    progress = calories / DAILY_RECOMMENDED_CALORIES
    percentage = progress * 100
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(progress)
    with col2:
        st.metric("섭취 칼로리", f"{calories}kcal")
    
    st.info(f'💡 일일 권장 칼로리 {DAILY_RECOMMENDED_CALORIES}kcal 기준, {food}는 {percentage:.1f}%를 차지합니다.')

st.divider()

# AI 분석 섹션
st.divider()
st.header("🤖 AI 음식 분석")

# 사용자 입력
custom_food = st.text_input("분석하고 싶은 음식을 입력하세요:", placeholder="예: 김치찌개, 라멘, 피자 등")
api_key = st.text_input("OpenAI API 키를 입력하세요:", type="password", help="OpenAI API 키가 필요합니다.")

# AI 분석 버튼과 결과 표시
if st.button("AI 분석 시작"):
    if not custom_food:
        st.warning("음식 이름을 입력해주세요.")
    elif not api_key:
        st.warning("API 키를 입력해주세요.")
    else:
        with st.spinner("AI 분석 중..."):
            try:
                # OpenAI API 호출
                client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 음식 전문가입니다. 음식의 분석과 함께 대략적인 칼로리 정보도 제공해주세요."},
                        {"role": "user", "content": f"'{custom_food}'에 대해 다음 정보를 제공해주세요:\n1. 맛과 특징\n2. 영양 성분\n3. 조리법 특징\n4. 1인분 기준 칼로리"}
                    ],
                    temperature=0.7
                )
                analysis_result = response.choices[0].message.content
                
                # 칼로리 정보 추출 (정규식 사용)
                import re
                calories_match = re.search(r'(\d+)\s*kcal', analysis_result)
                if calories_match:
                    calories = int(calories_match.group(1))
                    
                    # 칼로리 정보 표시
                    st.success("분석이 완료되었습니다!")
                    st.subheader("AI 분석 결과")
                    st.write(analysis_result)
                    
                    # 칼로리 프로그레스 바 표시
                    st.subheader("🔥 칼로리 정보")
                    progress = calories / DAILY_RECOMMENDED_CALORIES
                    percentage = progress * 100
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.progress(progress)
                    with col2:
                        st.metric("섭취 칼로리", f"{calories}kcal")
                    
                    st.info(f'💡 일일 권장 칼로리 {DAILY_RECOMMENDED_CALORIES}kcal 기준, {custom_food}는 {percentage:.1f}%를 차지합니다.')
                else:
                    st.success("분석이 완료되었습니다!")
                    st.subheader("AI 분석 결과")
                    st.write(analysis_result)
                    st.warning("칼로리 정보를 추출할 수 없습니다.")
                    
            except Exception as e:
                st.error(f"API 호출 중 오류가 발생했습니다: {str(e)}")

def show():
    st.title("💡 음식 컨설턴트")
    # 여기에 페이지의 주요 내용을 구현
    # 기존의 메인 로직을 이 함수 안으로 이동

    # 예시:
    st.write("음식 컨설턴트 페이지입니다.")
    # ... 나머지 페이지 구현 코드 ...