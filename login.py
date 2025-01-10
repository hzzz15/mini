from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

# Static 파일 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="templates")

# 로그인 페이지
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 로그인 처리
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    # 예시로 간단한 사용자 인증 로직 추가
    if username == "admin" and password == "password":
        return RedirectResponse(url="/welcome", status_code=302)
    return {"error": "Invalid credentials"}

# 로그인 성공 후 환영 페이지
@app.get("/welcome")
def welcome_page(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request, "username": "admin"})