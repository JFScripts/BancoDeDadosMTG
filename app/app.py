import sqlite3
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.gerenciadorBD import lerTabela 
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"),name="static")
templates = Jinja2Templates(directory="app\\templates")

with open("Catalogo.json", "r", encoding="utf-8") as arquivo:
                catalogo = json.load(arquivo)
with open("edicoes.json", "r", encoding="utf-8") as arquivo:
                allEdicoes = json.load(arquivo)

class NovaCarta(BaseModel):
        nome: str
        qnt: int
        senha: str
        
@app.get("/")
def home(request: Request):
    titulo = os.getenv("TITULO_SITE", "Minha Coleção MTG")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "titulo": titulo
        }
    )

@app.get("/cartas")
def listar_todas_as_cartas():

    conexao = sqlite3.connect("colecao.db")
    
    minhasCartas = lerTabela(conexao, "cartas")
    conexao.close()
    
    return {"total": len(minhasCartas), "colecao": minhasCartas}

@app.get("/adicionar")
def mostrarAdicionarCarta(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="adicionar.html",
        context={"request": request}
    )

@app.post("/adicionar")
def adicionarCarta(pacote: NovaCarta):
    senha = os.getenv("SENHA_ADMIN")
    if pacote.senha != senha:
        return {"mensagem": "Acesso Negado! Senha Incorreta."}
    dictNovaCarta = {
        "nome": pacote.nome,
        "qnt": pacote.qnt
    }
    print(dictNovaCarta)
    return {"mensagem": f"A carta foi adicionada com sucesso"}

@app.get("/buscar-foto")
def devolverFoto(nome: str):
    try:
        if nome in catalogo:
            cartaAtual = catalogo[nome]
            versoes = []
            dictEdicao = {}
            for edicaoItem in cartaAtual:
                sigla = edicaoItem["edicao"]
                dictEdicao[sigla] = {
                    "nome": allEdicoes[sigla]["nome"],
                    "icone": allEdicoes[sigla]["icone"],
                    "imagemEdicao": edicaoItem["imagem"],
                    "acabamentos": edicaoItem["acabamento"]
                }
                
        primeiraImagem = catalogo[nome.lower()][0]["imagem"]

        return {"urlImagem": primeiraImagem, "edicoes":dictEdicao}
    except:
        return {"urlImagem": "/static/inexistente.jpg", "edicoes": {}}