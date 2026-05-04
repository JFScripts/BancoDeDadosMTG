import sqlite3
import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.gerenciadorBD import lerTabela, deletarItemTabela
from dotenv import load_dotenv
from pydantic import BaseModel
from app.service import adicionarNovaCarta


class NovaCarta(BaseModel):
        nome: str
        qnt: int
        senha: str
        edicao: str
        acabamento: str
        idScryfall: str

class ApagarCarta(BaseModel):
    id: int
    senha: str

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"),name="static")
templates = Jinja2Templates(directory="app\\templates")

with open("Catalogo.json", "r", encoding="utf-8") as arquivo:
                catalogo = json.load(arquivo)
with open("edicoes.json", "r", encoding="utf-8") as arquivo:
                allEdicoes = json.load(arquivo)
      
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
        "qnt": pacote.qnt,
        "edicao": pacote.edicao,
        "acabamento": pacote.acabamento,
        "idScryfall": pacote.idScryfall
    }

    adicionarNovaCarta(dictNovaCarta, catalogo)
    return {"mensagem": f"A carta foi adicionada com sucesso"}

@app.delete("/deletar")
def apagarCarta(pacote: ApagarCarta):
    senhaAdmin = os.getenv("SENHA_ADMIN")
    if pacote.senha != senhaAdmin:
        raise HTTPException(status_code=401, detail="Senha Incorreta!")
    
    bdNome = os.getenv("BD_CONEXAO")
    conexao = sqlite3.connect(bdNome)
    
    sucesso = deletarItemTabela(conexao, "cartas", pacote.id)
    conexao.close()
    
    if sucesso:
        return {"mensagem": "Carta deletada com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao deletar a carta no banco.")

@app.get("/buscar-foto")
def devolverFoto(nome: str):
    try:
        nome_busca = nome.lower()
        if nome_busca in catalogo:
            cartaAtual = catalogo[nome_busca]
            dictEdicao = {}
            
            for edicaoItem in cartaAtual:
                sigla = edicaoItem["edicao"]
                id_scryfall = edicaoItem["idScryfall"]
                
                dictEdicao[id_scryfall] = {
                    "sigla": sigla,
                    "nome": allEdicoes[sigla]["nome"],
                    "icone": allEdicoes[sigla]["icone"],
                    "imagemEdicao": edicaoItem["imagem"],
                    "acabamentos": edicaoItem["acabamento"]
                }
                
            primeiraImagem = cartaAtual[0]["imagem"]
            return {"urlImagem": primeiraImagem, "edicoes": dictEdicao}
    except Exception as e:
        print("Erro ao buscar:", e)
    
    return {"urlImagem": "/static/inexistente.jpg", "edicoes": {}}