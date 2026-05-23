import requests
import json
import datetime
import os
from app import logManager
import sys
import time
from app import metadadosManager

def baixarMTGJson(cartasJsonNome, jaExisteJSON):
    urlMTGJson = "https://mtgjson.com/api/v5/AllPrintings.json"
    tentativas = [10, 5, 2] #Em segundos
    header = {"user-Agent": "colecaoMTG"}
    #Para cada tentativa que falhou em obter resposta tentamos novamente mas cada vez em um tempo menor
    logManager.logMensagemInfo("Tentando Baixar A API do MTGJson")
    try:
        tamanhoAtual = 0
        logManager.logMensagemInfo("Tentando Baixar Card Set")
        for segundos in tentativas:
            try:
                resposta = requests.get(urlMTGJson, headers=header, stream = True, timeout=segundos)
                if resposta.status_code == 200:
                    logManager.logMensagemSucesso("O Card Set Foi Baixado Com Sucesso")
                    break
            except requests.exceptions.Timeout:
                logManager.logMensagemAviso(f"O MTGJson demorou mais de {segundos} segundos para responder, tentando novamente")
            except requests.exceptions.RequestException as e:
                logManager.logMensagemFatal(f"Erro Crítico de Conexão: {e}")
                sys.exit("Erro Fatal de Rede. Olhe o log para mais informação")
        else:
            logManager.logMensagemFatal(f"Não Foi Possível Baixar O Card Set. O MTGJson Demorou Demais Para Responder, Verifique a Conexão com a Internet e Tente Novamente")
            sys.exit("Erro Fatal. Verifique Os Logs")

        logManager.logMensagemInfo("Tentando Salvar No HD O Card Set")
        try:
            with open(cartasJsonNome, "wb") as arquivo:
                for parte in resposta.iter_content(chunk_size=(1024 * 1024)):
                    arquivo.write(parte)
                    tamanhoAtual += len(parte)
                    print(f"Baixando... {tamanhoAtual / (1024*1024):.2f} MB", end="\r")
                print("Download Concluido")
            logManager.logMensagemSucesso("Card Set Salvo No HD com Sucesso")
            baixarHash()
        except Exception as e:
            logManager.logMensagemFatal(f"Erro Na Hora de Salvar O Card Set No HD: {e}")
            sys.exit("Erro Fatal. Não Foi Possivel Salvar O Card Set. Verifique O Log")
    except Exception as e:
        logManager.logMensagemFatal(f"Erro Na Hora de Baixar os Dados da API do MTG Json: {e}")
        sys.exit("Erro Crítico Para Baixar Os Dados da API do MTG Json. Abra o LOG para ver.")

def baixarHash():
    urlHash = "https://mtgjson.com/api/v5/AllPrintings.json.sha256"
    logManager.logMensagemInfo("Tentando Pegar O Valor Hash")
    try:
        hashMtgJson = requests.get(urlHash)
        metadadosManager.atualizarHashMtgjson(hashMtgJson.text)
        logManager.logMensagemSucesso("Hash Pego Com Sucesso")
    except Exception as e:
        logManager.logMensagemFatal(f"Não Foi Possível ABaixar O Valir Hash: {e}")
        sys.exit("Erro Crítico Na Hora De Baixar O Hash. Verifique Os Logs.")

def inicializarEdicoes(path, jaExisteJSON):

    header = {"user-Agent": "colecaoMTG"}
    url = "https://api.scryfall.com/sets"
    tentativas = [10, 5, 2]
    dictEdicao = {}
    logManager.logMensagemInfo("Tentando Baixar As Edições")
    try:
        for segundos in tentativas:
            try:
                pedidoHash = requests.head(url)
                hashEdicoes = pedidoHash.headers.get('ETag')
                if hashEdicoes:
                    hashEdicoes = hashEdicoes.strip('"').lstrip('W/"')
                metadadosManager.atualizarHashEdicoesScryfall(hashEdicoes)

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
    valor = metadadosManager.getCotacaoDollarFinancas()
    logManager.logMensagemInfo("Tentando Baixar A Cotação Do Dollar")
    try:
        for segundos in tentativas:
            try:
                resposta = requests.get(url, timeout=segundos)
                if resposta.status_code == 200:
                    dados = resposta.json()
                    valor = float(dados["USDBRL"]["bid"])
                    logManager.logMensagemSucesso("Cotação Do Dollar Obtida Com Sucesso")
                    metadadosManager.atualizarCotacaoDollarFinancas(valor)
                    metadadosManager.atualizarDataUltimaColetaFinancas()
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
    baixarHash()