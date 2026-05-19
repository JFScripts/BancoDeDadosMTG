import requests
import json
import datetime
import os
import logManager
import sys
import time
from metadadosManager import atualizarTamanhoDownload, atualizarCotacaoDollar, getCotacaoDollar

def baixarMTGJson(cartasJsonNome, jaExisteJSON):
    urlMTGJson = "https://mtgjson.com/api/v5/AllPrintings.json"
    tentativas = [10, 5, 2] #Em segundos
    header = {"user-Agent": "colecaoMTG"}
    #Para cada tentativa que falhou em obter resposta tentamos novamente mas cada vez em um tempo menor
    logManager.logMensagemInfo("Tentando Baixar A API do Scryfall")
    try:
        tamanhoAtual = 0
        logManager.logMensagemInfo("Tentando Baixar O Bulkdata")
        for segundos in tentativas:
            try:
                resposta = requests.get(urlMTGJson, headers=header, stream = True, timeout=segundos)
                if resposta.status_code == 200:
                    logManager.logMensagemSucesso("O Bulkdata Foi Baixado Com Sucesso")
                    tamanhoTotal = int(resposta.headers.get("Content-Length", 0))
                    atualizarTamanhoDownload(tamanhoTotal)
                    break
            except requests.exceptions.Timeout:
                logManager.logMensagemAviso(f"O Scryfall demorou mais de {segundos} segundos para responder, tentando novamente")
            except requests.exceptions.RequestException as e:
                logManager.logMensagemFatal(f"Erro Crítico de Conexão: {e}")
                sys.exit("Erro Fatal de Rede. Olhe o log para mais informação")
        else:
            logManager.logMensagemFatal(f"Não Foi Possível Baixar O Bulkdata. O Scryfall Demorou Demais Para Responder, Verifique a Conexão com a Internet e Tente Novamente")
            sys.exit("Erro Fatal. Verifique Os Logs")

        logManager.logMensagemInfo("Tentando Salvar No HD O Bulkdata")
        try:
            with open(cartasJsonNome, "wb") as arquivo:
                for parte in resposta.iter_content(chunk_size=(1024 * 1024)):
                    arquivo.write(parte)
                    tamanhoAtual += len(parte)
                    if tamanhoTotal > 0:
                        porcentagem = (tamanhoAtual/tamanhoTotal) * 100
                        print(f"Baixando: {porcentagem:.2f}%", end="\r")
                    else:
                        print(f"Baixando... {tamanhoAtual / (1024*1024):.2f} MB", end="\r")
                atualizarTamanhoDownload(tamanhoAtual)
                print("Download Concluido")
            logManager.logMensagemSucesso("Bulkdata Salvo No HD com Sucesso")
        except Exception as e:
            logManager.logMensagemFatal(f"Erro Na Hora de Salvar O Bulkdata No HD: {e}")
            sys.exit("Erro Fatal. Não Foi Possivel Salvar O Bulkdata. Verifique O Log")
    except Exception as e:
        logManager.logMensagemFatal(f"Erro Na Hora de Baixar os Dados da API do Scryfall: {e}")
        sys.exit("Erro Crítico Para Baixar Os Dados da API do Scryfall. Abra o LOG para ver")

def baixarCartasPT():
    url = "https://api.scryfall.com/cards/search?q=lang:pt"
    path = "data/raw/cartasPT.json"
    pedido = requests.get(url)
    dados = pedido.json()
    dictCartasPT = {}
    curPagina = 0
    while True:
        cartasPagina = dados.get("data")
        totalCartas = dados.get("total_cards")
        for carta in cartasPagina:
            dictCartasPT[carta["id"]] = carta.get("printed_name")
        with open(path, "w", encoding="utf-8") as arquivo:
            json.dump(dictCartasPT, arquivo,ensure_ascii=False, indent=4)
            print(f"Pagina {curPagina} Salva")
        if dados.get("has_more") == True and dados.get("next_page"):
            url = dados["next_page"]
            time.sleep(0.2)
            pedido = requests.get(url)
            dados = pedido.json()
        else:
            break
        


def inicializarEdicoes(path, jaExisteJSON):

    header = {"user-Agent": "colecaoMTG"}
    url = "https://api.scryfall.com/sets"
    tentativas = [10, 5, 2]
    dictEdicao = {}
    logManager.logMensagemInfo("Tentando Baixar As Edições")
    try:
        for segundos in tentativas:
            try:
                pedido = requests.get(url, timeout=segundos, headers=header)
                if pedido.status_code == 200:
                    logManager.logMensagemSucesso("As Edições Foram Baixadas Com Sucesso")
                    edicaoBruta = pedido.json()["data"]
                    break
            except requests.exceptions.Timeout:
                logManager.logMensagemAviso(f"O Scryfall demorou mais de {segundos} segundos para responder, tentando novamente")
            except requests.exceptions.RequestException as e:
                logManager.logMensagemFatal(f"Erro Crítico de Conexão: {e}")
                sys.exit("Erro Fatal de Rede. Olhe o log para mais informação")
        else:
            if jaExisteJSON:
                logManager.logMensagemAviso("Não Foi Possível Se Comunicar Com O Scryfall Então Será Utilizado Dados Antigos")
                return
            logManager.logMensagemFatal("Não Foi Possível Se Comunicar Com O Scryfall. Verifique Sua Internet E Tente Novamente")
            sys.exit("Erro Crítico Na Comunicação Com O Scryfall. Olhe Os Logs")
        for edicao in edicaoBruta:
            if not edicao["digital"] and edicao["set_type"] != "token":
                idScryfall = edicao["id"]
                codigo = edicao["code"]
                nome = edicao["name"]
                qntCartas = edicao["card_count"]
                icone = edicao["icon_svg_uri"]
                dictEdicao[codigo] = {"id":idScryfall, "nome":nome, "qntCartas":qntCartas, "icone": icone}
    except Exception as e:
        logManager.logMensagemFatal(f"Não Foi Possível Fazer O Download Das Edições: {e}")
        sys.exit("Erro Crítico Na Hora De Baixar As Edições. Verifique Os Logs")
    logManager.logMensagemInfo("Tentando Salvar As Edições No HD")
    try:
        with open(path, "w", encoding="utf-8") as arquivo:
            json.dump(dictEdicao, arquivo, ensure_ascii=False, indent=4)
        logManager.logMensagemSucesso("Edições Salvas Com Sucesso")
    except Exception as e:
        logManager.logMensagemFatal(f"Não Foi Possível Salvar As Edições No HD: {e}")
        sys.exit("Erro Crítico Na Hora De Salvar As Edições No HD. Verifique O Log")

def pegarCotacaoDollar():
    url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
    tentativas = [10, 5, 2]
    valor = getCotacaoDollar()
    logManager.logMensagemInfo("Tentando Baixar A Cotação Do Dollar")
    try:
        for segundos in tentativas:
            try:
                resposta = requests.get(url, timeout=segundos)
                if resposta.status_code == 200:
                    dados = resposta.json()
                    valor = float(dados["USDBRL"]["bid"])
                    logManager.logMensagemSucesso("Cotação Do Dollar Obtida Com Sucesso")
                    atualizarCotacaoDollar(valor)
                    break
            except requests.exceptions.Timeout:
                logManager.logMensagemAviso(f"O Awesomeapi demorou mais de {segundos} segundos para responder, tentando novamente")
            except requests.exceptions.RequestException as e:
                logManager.logMensagemFatal(f"Erro Crítico de Conexão: {e}")
        else:
            logManager.logMensagemAviso(f"Não Foi Possível Estabelecer O Valor Do Dollar. Será Usado o Valor de {valor}")
    except Exception as e:
        logManager.logMensagemErro(f"Não Foi Possível Atualizar O Valor Do Dollar, Será Usado O Valor Salvo: {e}")


if __name__ == "__main__":
    baixarCartasPT()