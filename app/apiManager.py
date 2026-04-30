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
            baixarDB(url, dbNome)
            precisaLimpar = True
    else: 
        baixarDB(url, dbNome)
        precisaLimpar = True
    
    return carregarCatalogo(dbNome, "Catalogo.json", precisaLimpar)
        

def baixarDB(url, dbNome):
    request = requests.get(url)
    dados = request.json()
    linkDownload = dados["download_uri"]
    tamanhoTotal = int(dados["size"])
    header = {"user-Agent": "colecaoMTG"}
    download = requests.get(linkDownload, headers=header,stream = True)
    tamanhoAtual = 0

    with open(dbNome, "wb") as arquivo:
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
        try:
            with open(catalogoNome, "r", encoding="utf-8") as arquivo:
                catalogo = json.load(arquivo)
            return catalogo
        except json.JSONDecodeError:
            print(f"\nAviso: O arquivo {catalogoNome} está corrompido/vazio.Recriando")
            precisaLimpar = True
    try:
        with open(dataBase, "r", encoding="utf-8", errors="ignore") as arquivo:
            dadosBrutos = json.load(arquivo)
    except json.JSONDecodeError:
        print(f"\nERRO CRITICO: O arquivo {catalogoNome} está corrompido/vazio. Apague o arquivo e tente novamente\n")
        input("Pressione ENTER para continuar")
        return {}

    for carta in dadosBrutos:
        if carta["digital"]:
            continue
        cartaNome = carta["name"].lower()

        if cartaNome not in catalogo:
            catalogo[cartaNome] = []
        edicao = carta["set"]
        idScryfall = carta["id"]
        cor = carta["color_identity"]
        precoNormal = carta["prices"]["usd"]
        precoFoil = carta["prices"]["usd_foil"]
        precoEtched = carta["prices"]["usd_etched"]
        acabamentos = carta["finishes"]

        catalogo[cartaNome].append({"edicao": edicao, 
        "idScryfall": idScryfall, 
        "precoNormal": precoNormal or 0.0, 
        "precoFoil": precoFoil or 0.0, 
        "precoEtched": precoEtched or 0.0, 
        "cor": cor or [], 
        "acabamento": acabamentos})

    with open(catalogoNome, "w", encoding="utf-8") as arquivo:
        json.dump(catalogo, arquivo, ensure_ascii=False, indent=4)
    return catalogo

def baixarEdicoes(setJson, url):
    if not os.path.exists(setJson):
        request = requests.get(url)
        edicaoBruta = request.json()["data"]
        dictEdicao = {}

        for edicao in edicaoBruta:
            if not edicao["digital"] and edicao["set_type"] != "token":
                idScryfall = edicao["id"]
                codigo = edicao["code"]
                nome = edicao["name"]
                qntCartas = edicao["card_count"]
                dictEdicao[codigo] = []
                dictEdicao[codigo].append({"id":idScryfall, "nome":nome, "qntCartas":qntCartas})

        with open(setJson, "w", encoding="utf-8") as arquivo:
            json.dump(dictEdicao, arquivo, ensure_ascii=False, indent=4)
        return dictEdicao

    with open(setJson, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def pegarCotacaoDollar(url):
    try:
        resposta = requests.get(url, timeout=5)
        dados = resposta.json()
        valor = float(dados["USDBRL"]["bid"])
        return valor
    except Exception as e:
        return 5.00
