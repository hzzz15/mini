from fastapi import FastAPI, Form, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
import pandas as pd
from models.kobert_model import SentimentAnalyzer

app = FastAPI()

# 정적 파일 및 템플릿 경로 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates/")

# 간단한 메모리 기반 사용자 저장소
users_db = {"admin": "password"}

# 메인 페이지
@app.get("/")
def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 로그인 페이지
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 회원가입 페이지
@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# 회원가입 처리
@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if username in users_db:
        return {"error": "이미 존재하는 아이디입니다."}
    if password != confirm_password:
        return {"error": "비밀번호가 일치하지 않습니다."}
    
    # 사용자 저장
    users_db[username] = password
    
    # 회원가입 성공 후 메인 페이지로 리다이렉트
    return RedirectResponse(url="/", status_code=302)

# 로그인 처리
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username not in users_db:
        return {"error": "존재하지 않는 아이디입니다."}
    if users_db[username] != password:
        return {"error": "비밀번호가 틀렸습니다."}
    
    return RedirectResponse(url="/welcome", status_code=302)

# 환영 페이지
@app.get("/welcome")
def welcome_page(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request, "username": "admin"})

# 비밀번호 찾기 페이지
@app.get("/forgot-password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

# 비밀번호 재설정 처리
@app.post("/reset-password")
def reset_password(username: str = Form(...), new_password: str = Form(...)):
    if username not in users_db:
        return {"error": "존재하지 않는 아이디입니다."}
    
    # 비밀번호 업데이트
    users_db[username] = new_password
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}

# templates 디렉토리를 설정합니다.
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# 보관함 페이지 라우트
@app.get("/box")
def read_box(request: Request):
    return templates.TemplateResponse("box.html", {"request": request})

####################
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

############ 추천

# CSV 데이터 로드
songs_data = pd.read_csv("data/songs.csv")

# 감정 매핑 (모델의 출력값 → CSV의 Mood 값)
MOOD_MAPPING = {
    "Negative": "Sad",
    "Neutral": "Sentimental",
    "Positive": "Happy"
}

# 감정 분석기 초기화
analyzer = SentimentAnalyzer()

@app.post("/recommend", response_class=HTMLResponse)
async def recommend_songs(request: Request, user_text: str = Form(...)):
    try:
        # 1. 사용자 입력 확인
        print(f"사용자 입력: {user_text}")

        # Step 1: 감정 분석
        analyzed_sentiment = analyzer.analyze_sentiment(user_text)
        print(f"분석된 감정: {analyzed_sentiment}")

        # Step 2: 감정 매핑
        mood = MOOD_MAPPING.get(analyzed_sentiment, None)
        print(f"매핑된 Mood: {mood}")
        if not mood:
            print(f"'{analyzed_sentiment}'은 매핑되지 않은 감정입니다.")
            return templates.TemplateResponse("main_home_pli.html", {
                "request": request,
                "songs": [],
                "message": f"'{analyzed_sentiment}'에 해당하는 노래를 찾을 수 없습니다."
            })

        # Step 3: CSV 데이터에서 감정 필터링
        filtered_songs = songs_data[songs_data["Mood"] == mood]
        print(f"필터링된 노래 데이터:\n{filtered_songs}")

        # Step 4: 상위 12개의 노래 선택
        filtered_songs = filtered_songs.head(12)  # 상위 12개만 선택
        print(f"상위 12개 추천 노래 데이터:\n{filtered_songs}")

        if filtered_songs.empty:
            print(f"'{mood}'에 해당하는 노래가 없습니다.")
            return templates.TemplateResponse("main_home_pli.html", {
                "request": request,
                "songs": [],
                "message": f"'{mood}' 감정에 해당하는 노래가 없습니다."
            })

        # Step 4: 추천 결과 반환
        recommendations = filtered_songs[["Song", "Artist", "Image_URL"]].to_dict(orient="records")
        print(f"추천된 노래:\n{recommendations}")
        return templates.TemplateResponse("main_home_pli.html", {
            "request": request,
            "songs": recommendations,
            "mood": analyzed_sentiment
        })

    except Exception as e:
        print(f"오류 발생: {e}")
        return templates.TemplateResponse("main_home_pli.html", {
            "request": request,
            "songs": [],
            "message": f"오류 발생: {str(e)}"
        })

# list.html 연결 라우트
@app.get("/list", response_class=HTMLResponse)
async def list_page(request: Request):
    """
    list.html 파일로 연결
    """
    return templates.TemplateResponse("list.html", {"request": request})

