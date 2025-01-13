from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
import pandas as pd
from models.emotion_model import SentimentAnalyzer
import sqlite3
import torch
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# 정적 파일 및 템플릿 경로 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates/")


# 데이터베이스 연결 및 테이블 확인/생성
def setup_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)

    username = "testuser"
    password = "testpassword"

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        print(f"사용자 '{username}'가 추가되었습니다.")
    else:
        print(f"사용자 '{username}'가 이미 존재합니다.")

    conn.commit()
    conn.close()

setup_database()

# 데이터베이스 연결 함수
def get_db_connection():
    import sqlite3
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# CSV 데이터 로드
songs_data = pd.read_csv("data/songs.csv")

# 메인 페이지
@app.get("/")
async def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/main")
def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

# 회원가입 페이지
@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# 회원가입 처리
@app.post("/signup")
async def signup(username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if password != confirm_password:
        return JSONResponse(content={"message": "비밀번호가 일치하지 않습니다."}, status_code=400)

    conn = get_db_connection()
    cursor = conn.cursor()

    # 중복 확인
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        return JSONResponse(content={"message": "이미 존재하는 아이디입니다."}, status_code=400)

    # 사용자 추가
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/", status_code=302)

# 로그인 엔드포인트
@app.post("/login")
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return JSONResponse(content={"message": "로그인 실패: 잘못된 아이디 또는 비밀번호"}, status_code=401)

    # 로그인 성공 시 세션에 username 저장
    request.session["username"] = username
    return RedirectResponse(url="/home", status_code=303)

# 홈 페이지
@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "username": "Guest"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear() 
    return RedirectResponse(url="/login", status_code=302)

# 회원가입 엔드포인트
@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# 환영 페이지
@app.get("/welcome")
def welcome_page(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request, "username": "로그인 성공!"})

# 비밀번호 찾기 페이지
@app.get("/forgot-password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

# 비밀번호 재설정 처리
@app.post("/reset-password")
def reset_password(username: str = Form(...), new_password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 사용자 존재 여부 확인
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if not cursor.fetchone():
        conn.close()
        return {"error": "존재하지 않는 아이디입니다."}

    # 비밀번호 업데이트
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}

@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request, username: str = None):
    """
    /home 엔드포인트
    """
    if not username:
        username = "Guest" 
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "username": username
    })

@app.get("/other_page", response_class=HTMLResponse)
async def other_page(request: Request, username: str):
    return templates.TemplateResponse("other_page.html", {"request": request, "username": username})

@app.post("/redirect-to-home")
async def redirect_to_home(username: str = Form(...)):
    """
    헤더 클릭 시 username을 포함하여 home.html로 이동
    """
    url = f"/home?username={username}"
    return RedirectResponse(url=url, status_code=302)

# 감정별 노래리스트 box
@app.get("/box1", response_class=HTMLResponse)
async def box1_page(request: Request):
    return await render_box_page(request, mood="Happy", title="Happy Mood Playlist")

@app.get("/box2", response_class=HTMLResponse)
async def box2_page(request: Request):
    return await render_box_page(request, mood="Sentimental", title="Sentimental Mood Playlist")

@app.get("/box3", response_class=HTMLResponse)
async def box3_page(request: Request):
    return await render_box_page(request, mood="Angry", title="Angry Mood Playlist")

@app.get("/box4", response_class=HTMLResponse)
async def box4_page(request: Request):
    return await render_box_page(request, mood="Sad", title="Sad Mood Playlist")

async def render_box_page(request: Request, mood: str, title: str):
    try:
        print(f"DEBUG: mood = {mood}, title = {title}") 
        filtered_songs = songs_data[songs_data["Mood"] == mood]
        selected_songs = filtered_songs.sample(n=min(8, len(filtered_songs))).to_dict(orient="records")

        playlist = selected_songs[:4]
        top_songs = selected_songs[:5]

        return templates.TemplateResponse("box.html", {
            "request": request,
            "playlist": playlist,
            "top_songs": top_songs,
            "title": title,
            "mood": mood  
        })
    except Exception as e:
        print(f"오류 발생: {e}")
        return {"error": str(e)}

# 메인 페이지 라우트
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/main_home_pli", response_class=HTMLResponse)
async def read_main_home_pli(request: Request):
    return templates.TemplateResponse("main_home_pli.html", {"request": request})

@app.get("/sing", response_class=HTMLResponse)
async def read_sing(request: Request):
    return templates.TemplateResponse("sing.html", {"request": request})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

############ 추천
# 감정 매핑
MOOD_MAPPING = {
    "Anger": "Angry",
    "Fear": "Sentimental",
    "Happy": "Happy",
    "Tender": "Sentimental",
    "Sad": "Sad"
}

# 감정 피드백 메시지
MOOD_COMMENTS = {
    "Happy": "오늘 당신의 기분은 행복하군요! 신나는 노래로 기분을 더 업그레이드해보세요!",
    "Sentimental": "오늘은 감성적인 하루를 보내고 계신가요? 마음을 따뜻하게 할 노래들을 준비했어요.",
    "Angry": "화가 난 마음, 음악으로 풀어보는 건 어떨까요? 강렬한 비트가 기다리고 있어요!",
    "Sad": "조금 우울한 하루였나요? 감정을 위로해줄 곡을 추천드려요. 편히 쉬면서 들어보세요."
}

# SentimentAnalyzer 클래스 정의
def analyze_sentiment(self, text: str) -> str:
    if not text.strip():
        raise ValueError("입력된 텍스트가 비어 있습니다.")

    # 텍스트를 토큰화
    inputs = self.tokenizer(
        text,
        return_tensors="pt",
        max_length=128,
        truncation=True,
        padding="max_length"
    )

    # 모델 예측
    with torch.no_grad():
        outputs = self.model(**inputs)
        if not hasattr(outputs, "last_hidden_state"):
            raise ValueError("모델 출력값이 유효하지 않습니다.")
        
        logits = outputs.last_hidden_state.mean(dim=1)
        if logits.size(0) == 0:
            raise ValueError("모델 출력값이 비어 있습니다.")

    predicted_label = logits.argmax(dim=1).item()
    if predicted_label >= len(self.emotion_labels):
        raise ValueError("예측된 레이블이 감정 레이블 범위를 벗어났습니다.")

    return self.emotion_labels[predicted_label]

# SentimentAnalyzer 초기화
analyzer = SentimentAnalyzer()

@app.post("/analyze")
async def analyze_sentiment(user_text: str = Form(...)):
    try:
        sentiment = analyzer.analyze_sentiment(user_text)
        return {"text": user_text, "sentiment": sentiment}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"알 수 없는 오류가 발생했습니다: {str(e)}"}

# 공통 데이터 필터링 함수
def get_filtered_songs(mood: str, limit: int = 12):
    """
    주어진 Mood 값에 따라 CSV 데이터를 필터링하고 상위 n개 반환
    """
    filtered_songs = songs_data[songs_data["Mood"].str.lower() == mood.lower()]
    return filtered_songs.head(limit).to_dict(orient="records")

@app.post("/recommend", response_class=HTMLResponse)
async def recommend_songs(request: Request, user_text: str = Form(...)):
    try:
        # Step 1: 감정 분석
        analyzed_sentiment = analyzer.analyze_sentiment(user_text)
        print(f"분석된 감정: {analyzed_sentiment}")

        # Step 2: 감정 매핑
        mood = MOOD_MAPPING.get(analyzed_sentiment, None)
        print(f"매핑된 Mood: {mood}")
        if not mood:
            return templates.TemplateResponse("main_home_pli.html", {
                "request": request,
                "songs": [],
                "message": f"'{analyzed_sentiment}'에 해당하는 노래를 찾을 수 없습니다.",
                "feedback": "감정을 파악하지 못했어요. 😅 다시 시도해보세요."
            })

        # Step 3: CSV 데이터에서 감정 필터링
        filtered_songs = songs_data[songs_data["Mood"] == mood]
        print(f"필터링된 노래 데이터:\n{filtered_songs}")

        # Step 4: 상위 12개의 노래 선택
        filtered_songs = filtered_songs.head(12).to_dict(orient="records")
        print(f"추천된 노래:\n{filtered_songs}")

        # Step 5: 피드백 메시지
        feedback_message = MOOD_COMMENTS[mood]

        # Step 6: main_home_pli.html 렌더링
        return templates.TemplateResponse("main_home_pli.html", {
            "request": request,
            "songs": filtered_songs,
            "mood": mood,
            "feedback": feedback_message
        })

    except Exception as e:
        print(f"오류 발생: {e}")
        return templates.TemplateResponse("main_home_pli.html", {
            "request": request,
            "songs": [],
            "message": f"오류 발생: {str(e)}",
            "feedback": "문제가 발생했습니다. 😥 다시 시도해주세요."
        })
    
@app.get("/list", response_class=HTMLResponse)
async def list_page(request: Request, mood: str):
    try:
        filtered_songs = songs_data[songs_data["Mood"].str.lower() == mood.lower()]
        filtered_songs = filtered_songs.head(12).to_dict(orient="records") 
        print(f"Filtered songs for Mood '{mood}':", filtered_songs)
        
        return templates.TemplateResponse("list.html", {
            "request": request,
            "songs": filtered_songs,
            "mood": mood
        })
    except Exception as e:
        print(f"Error in /list route: {e}") 
        return templates.TemplateResponse("list.html", {
            "request": request,
            "songs": [],
            "mood": mood,
            "message": "추천된 노래를 불러오는 데 실패했습니다."
        })
