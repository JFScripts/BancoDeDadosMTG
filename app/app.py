import sqlite3
import app.menu as menu

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

conexao = sqlite3.connect("data/db/bdMTG.db", check_same_thread=False)
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

class AdicionarCarta(BaseModel):
    nome: str
    edicao: str
    acabamento: str
    quantidade: int

class BuscarCarta(BaseModel):
    nome: str

@app.get("/")
def paginaInicial(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="paginaInicial.html"
    )

@app.post("/botaoClicado")
def botaoClicado(dadosRecebido: AdicionarCarta):
    print(dadosRecebido)
    return {"status": "sucesso"}

@app.get("/buscarCartas")
def buscarCarta():
    listaCartas = menu.buscarNomesCartas(conexao)
    return listaCartas