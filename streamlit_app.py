import streamlit as st
import requests
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import pyperclip
from openai import OpenAI

# Load environment variables
load_dotenv()

# Load API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
upstage_api_key = os.getenv("UPSTAGE_API_KEY")

if not openai_api_key:
    st.error("OpenAI API key not found. Please set the API key in the .env file.")
if not upstage_api_key:
    st.error("Upstage API key not found. Please set the API key in the .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Function to generate image
def generate_image(who, what):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"A {who} studying {what}",
            n=1,
            quality="standard", 
            size="1024x1024"
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

# Function to make request to Upstage API
def upstage_client_request(endpoint, payload):
    try:
        response = requests.post(
            f"https://api.upstage.ai/v1/solar{endpoint}",
            headers={"Authorization": f"Bearer {upstage_api_key}"},
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Function to generate greeting
def hello(where, tmi):
    model_engine = "solar-1-mini-chat"
    prompt = prompt_hello.format(where, tmi, where, tmi, where, tmi, where, tmi)

    payload = {
        "model": model_engine,
        "messages": [
            {"role": "system", "content": "당신은 공부 일기 블로그 포스팅의 인삿말을 생성하는 20대 대학생입니다."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1028
    }

    response = upstage_client_request("/chat/completions", payload)
    if response:
        return response['choices'][0]['message']['content']
    return None

# Greeting prompt
prompt_hello = '''
내가 제공하는 예시 문장들 중에 하나를 출력해

### 예시 문장 
- "안니옹하세용~~ 다들 좋은 하루 보내셨나요?! 오늘은 {}에서 공부 일기나 써보려구요!! 아 맞다 저 오늘 {},,, 여튼 일기 시작해볼게요~" 
- "안녕하세요! {}에서 일기 작성하기 프로젝트~ 원래 더 일찍 쓰려고 했는데 너무 피곤해서 이제야 쓰네요 ㅎㅎ;;; 아 근데 저 오늘 {},, 여튼 일기 써볼게요~"
- "{}는 다 좋은데 맨날 오니까 질리네요 질려... 그냥 집갈까 하다가 공부 일기만 후딱 쓰고 가겠습니다. 아니 근데 저 오늘 {},, 진짜 열 받네요;;;; 일기로 달래보겠습니다!!!!"
- "안녕하세요~~ {}에서 공부하는 사람들이 진짜 많네요?? 저는 커피나 마시면서 공부 일기쓰러 왔는데,, 아 그리고 저 오늘 {},, 쩝 암튼 일기 써볼게욥"
'''

# Function to generate blog content
def generate_blog(greeting, tmi, who, what, why, where, when, how, prompt_template):
    model_engine = "solar-1-mini-chat"
    prompt_korean = prompt_template.format(who, what, why, where, when, how, what, what, what, what, what, what, what)

    payload = {
        "model": model_engine,
        "messages": [
            {"role": "system", "content": "공부 일기 블로그 포스팅을 생성하는 AI 시스템입니다."},
            {"role": "user", "content": prompt_korean}
        ],
        "max_tokens": 4096,
        "temperature": 0.8
    }

    response = upstage_client_request("/chat/completions", payload)
    if response:
        text = response['choices'][0]['message']['content']
        pyperclip.copy(text)  # Copy text to clipboard
        return text
    return None

# Blog content prompt template
prompt_korean_template = '''
아웃라인 구성 : 제목 - 인사 - 본문(섹션1~7) - 맺음말로 구성해.

블로그 포스트를 마크다운 형식으로 작성해. 중요한 단어나 문장을 굵게, 기울임꼴 또는 밑줄로 강조해.
제목은 블로그 게시물에 대한 눈에 띄고 SEO 친화적인 제목을 생성해.

인사는 항상 "안니옹하세용. 한량 규 입니다. 요즘 제가 정신이 하나도 없는데요! 이 일기 생성이 너~~~무 안되서 머리가 터질 것 같아요! 그래도 다시 한 번 힘내보겠습니다!" 로 출력해.

다음 줄에는 {{tmi}}에 대해서 언급을 해주고, "오늘은 {{what}}에 대해서 공부해봤습니다~ 이게 뭔지 이제 설명해드릴게요!" 출력해

일기 형식으로 작성하고 말투는 친근한 말투를 사용하며, 상세한 설명을 해주는 것이 특징이야.

자주 쓰는 표현은 "~했다.", "~였는데, ~다." 

표현의 예시 1 : "오늘은 what에 대한 공부를 했다. 사실 what에 대해서 관심을 가지고 있었는데, 시간이 없어서 하지 못했다."
표현의 예시 2 : "어제는 PostgreSQL에 대한 공부를 했는데, 무슨 말인지 못 알아먹겠다."
표현의 예시 3 : "앞으로 공부를 열심히 하겠다고 다짐했다!! 지금까지는 대충했었는데, 앞으론 진짜 빡공간다!!"

작성자는 "{}"야.
"{}"에 대한 공부를 했고, 공부를 한 이유는 "{}", "{}"에서 "{}" 공부를 했어, "{}" 방식으로 공부를 했어. 이것에 대한 공부 일기를 작성해.

### 섹션 1: 
"{}"에 대한 기본 이해
(섹션 1에서는 {{what}}이 무엇인지 정의하고, 기본적인 개념을 설명해. 그 다음 이 기술이 왜 중요한지 설명해.)

### 섹션 2:
"{}"와 역사와 발전 과정
(섹션 2에서는 {{what}} 기술 or 프로그래밍이 어떻게 시작되었는지에 대한 역사적 배경을 설명해. 그 다음 중요한 마일스톤과 최근 혁신적 발전들을 강조해.)

### 섹션 3: 
"{}"에 대한 원리와 구조
({{what}}을 구성하는 기본적인 알고리즘과 원리에 대해 설명해. 그 다음 이러한 원리가 실제로 어떻게 작동하는지 예를 들어 설명해.)

### 섹션 4: 
"{}"을 활용한 사례
(실제 {{what}} 기술 or 프로그래밍이 적용된 다양한 사례들을 소개해. 그 다음 각 사례에서 {{what}}이 어떻게 문제를 해결했는지 설명해.)

### 섹션 5: 
"{}"을 활용할만한 창의적 아이디어
({{what}} 기술을 사용하여 해결할 수 있는 새로운 문제나 창의적 프로젝트 아이디어를 제시해.)

### 섹션 6: 
"{}"에 대한 꿀팁
({{what}} 공부를 시작하는 데 도움이 될 수 있는 팁과 리소스를 하이퍼링크 형태로 제공해. 그 다음 공부를 하는 동안 추천하는 학습 방법을 공유해.)

### 섹션 7: 
"{}"을 주제로 한 질의응답
(3개 이상의 질문과 답변으로 구성해)

각 섹션마다 자세한 설명과 함께 100단어 이상의 설명으로 구성해

글의 끝에 각 섹션에서 논의한 주제에 대한 해시태그와 함께 내 생각을 맺음말로 정리해. 이렇게 각 섹션을 명확하게 구분하고 각각의 주제에 대해 상세하게 풀어나가는 구조를 사용해. 짧지 않게 상세히 퀄리티 높게 작성해.

맺음말에 대한 예시 말투를 참고해
ex 1) 오늘 NLP에서 중요하다고 생각하는 문장 토큰화에 대해 공부했다. 근데 생각보다 익숙한 내용이어서 엥 뭐지? 싶었는데, 알고보니까 단어 토큰화랑 매커니즘 자체는 동일하더라
그래서 오늘 공부는 조금 수월하게 했다. 다음 단원은 테이블 벡터에 대해서 공부하는데, 벡터에 대해서 잘 모르는 것 같아서 좀 더 집중해야겠다.
ex 2) 오늘 무슨 일로 공부를 많이 못했는데, 정말 바빴던 하루였다. 그래도 주말에 시간이 나면 꼭 다시 공부를 해야겠다. 마무리하고, 화이팅!!
'''

# Streamlit App
st.set_page_config(
    page_title="학습 일기 생성기",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar
st.sidebar.title("학습 일기 생성기 📘")
st.sidebar.markdown("학습한 내용에 대한 일기를 간편하게 작성하세요!")

# Main App
st.title("학습 일기 생성기 📘")

st.markdown("학습 일기 생성기는 귀찮은 일기 작성에 대한 틀을 잡아줍니다.")

# User Inputs
st.header("Diary Inputs")
greeting_tmi = st.text_input("당신의 TMI를 공유해주세요!")
diary_topic = st.text_input("어떤 것을 공부하셨나요?")

# Initialize session state for greeting
if "greeting" not in st.session_state:
    st.session_state.greeting = ""

# Greeting Generation
st.header("인삿말 생성")
if st.button("인삿말 생성"):
    if greeting_tmi and diary_topic:
        st.session_state.greeting = hello("Home", greeting_tmi)
        st.text_area("Generated Greeting", st.session_state.greeting, height=100)
    else:
        st.warning("Please enter both TMI and study topic.")

# Blog Generation
st.header("학습 일기 본문 생성")
diary_who = st.text_input("당신은 누구신가요?")
diary_what = st.text_input("무엇을 공부하셨죠?")
diary_why = st.text_input("왜 그걸 공부하셨나요?")
diary_where = st.text_input("어디서 공부하셨어요?")
diary_when = st.text_input("언제 공부하셨어요?")
diary_how = st.text_input("어떻게 공부하셨어요?")

if st.button("학습 일기 생성!"):
    if diary_who and diary_what and diary_why and diary_where and diary_when and diary_how:
        if st.session_state.greeting:  # Ensure greeting is generated before using it
            diary_content = generate_blog(
                st.session_state.greeting, 
                greeting_tmi, 
                diary_who, 
                diary_what, 
                diary_why, 
                diary_where, 
                diary_when, 
                diary_how, 
                prompt_korean_template
            )
            st.markdown(diary_content, unsafe_allow_html=True)
        else:
            st.warning("Please generate the greeting first.")
    else:
        st.warning("Please fill in all the diary details.")

# Chatbot Implementation
st.header("학습 일기 복습 챗봇 🤖")
st.markdown("작성된 일기에 대해 물어보세요! 다른 주제도 좋습니다!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Accept user input
if prompt := st.chat_input("What would you like to ask?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    st.chat_message("user").write(prompt)

    # Generate response
    with st.spinner("Thinking..."):
        response = upstage_client_request(
            "/chat/completions",
            {
                "model": "solar-1-mini-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1028,
            },
        )
    # Display assistant response in chat message container
    if response:
        response_content = response['choices'][0]['message']['content']
        st.chat_message("assistant").write(response_content)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_content})
    else:
        st.error("Failed to get a response from the chatbot.")
