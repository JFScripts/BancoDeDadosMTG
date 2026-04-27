import requests
import json
import datetime
import os

def inicializarCatalogo(url, dbNome,maxDias):
    precisaLimpar = False
    if os.path.exists(dbNome):
        ultimaModificacao = os.path.getmtime(dbNome)
        ultimaModificacao = datetime.datetime.fromtimestamp(ultimaModificacao)
        tempoAtual = datetime.datetime.now()
        diferencaDias = tempoAtual - ultimaModificacao

        if diferencaDias.days >= maxDias:
            baixarDB(url)
            precisaLimpar = True
    else: 
        baixarDB(url)
        precisaLimpar = True
    
    return carregarCatalogo(dbNome, "Catalogo.json", precisaLimpar)
        

def baixarDB(url):
    request = requests.get(url)
    dados = request.json()
    linkDownload = dados["download_uri"]
    tamanhoTotal = int(dados["size"])
    download = requests.get(linkDownload, stream = True)
    tamanhoAtual = 0

    with open("dataBase.json", "wb") as arquivo:
        for parte in download.iter_content(chunk_size=8192):
            arquivo.write(parte)
            tamanhoAtual += len(parte)
            porcentagem = (tamanhoAtual/tamanhoTotal) * 100
            print(f"Baixando: {porcentagem:.2f}%", end="\r")
        print()
        print("Download Concluido")

def carregarCatalogo(dataBase, catalogoNome, precisaLimpar):
    catalogo = {}
    if not precisaLimpar and os.path.exists(catalogoNome):
        with open(catalogoNome, "r", encoding="utf-8") as arquivo:
            catalogo = json.load(arquivo)
        return catalogo
    with open(dataBase, "r", encoding="utf-8") as arquivo:
        dadosBrutos = json.load(arquivo)
        for carta in dadosBrutos:
            cartaNome = carta["name"].lower()
            if cartaNome not in catalogo:
                catalogo[cartaNome] = []
            catalogo[cartaNome].append({"edicao":carta["set"], "idScryfall":carta["id"], "preco": carta["prices"]["usd"] or 0.0})
    with open(catalogoNome, "w", encoding="utf-8") as arquivo:
        json.dump(catalogo, arquivo)
    return catalogo

def pegarCotacaoDollar(url):
    try:
        resposta = requests.get(url, timeout=5)
        dados = resposta.json()
        valor = float(dados["USDBRL"]["bid"])
        return valor
    except Exception as e:
        return 5.00
