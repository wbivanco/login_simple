from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import bcrypt

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="ajdkajdklaaswewpojq2dmqd")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Encriptar las contraseñas
users = {
    "user1": bcrypt.hashpw("pass1".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
    "user2": bcrypt.hashpw("pass2".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if "username" in request.session:
        return templates.TemplateResponse("index.html", {"request": request})
    return RedirectResponse("/login")
from random import randint

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    # Generar dos números aleatorios para el captcha
    num1, num2 = randint(1, 10), randint(1, 10)
    captcha_answer = num1 + num2
    # Almacenar la respuesta correcta en la sesión
    request.session["captcha_answer"] = captcha_answer
    captcha_question = f"{num1} + {num2} = ?"
    return templates.TemplateResponse("login.html", {"request": request, "captcha_question": captcha_question})

@app.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...), 
    captcha: str = Form(...)
):
    # Verificar la respuesta del captcha
    correct_answer = request.session.get("captcha_answer")
    if correct_answer is None or int(captcha) != correct_answer:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Captcha incorrecto. Inténtalo de nuevo."
        })

    # Verificar las credenciales
    if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username].encode('utf-8')):
        request.session["username"] = username
        return RedirectResponse("/", status_code=303)
    
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "error": "Credenciales inválidas."
    })

@app.get("/logout")
async def logout(request: Request):
    request.session.pop("username", None)
    return RedirectResponse("/login")