import os
import sys
import datetime
import json
import logManager

from dotenv import load_dotenv
from pathlib import Path
from apiManager import baixarBancoScryfall
from metadadosManager import atualizarDataDownloadMetadados, getDataDownloadMetadados


def configurarPrograma(urlScryfall, maxDias):
    cartasJson = "data/raw/todasAsCartas.json"
    criarPastas()
    logManager.manutencaoLogs()

    criarEnv()
    inicializarMetadados()

    agoraMs = int(datetime.datetime.now().timestamp() * 1000)
    diferencaMs = agoraMs - getDataDownloadMetadados()
    maxMs = maxDias * 24 * 60 * 60 * 1000

    if diferencaMs >= maxMs or not os.path.exists(cartasJson):
       baixarBancoScryfall(urlScryfall, cartasJson)
       atualizarDataDownloadMetadados()

def criarPastas():
    logManager.logMensagemInfo("Tentando Criar as Pastas")
    try:
        Path("data/raw").mkdir(parents=True, exist_ok=True)
        Path("data/db").mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(parents=True, exist_ok=True)
        Path("logs/new").mkdir(parents=True, exist_ok=True)
        Path("logs/old").mkdir(parents=True, exist_ok=True)
        Path("configs").mkdir(parents=True, exist_ok=True)
        logManager.logMensagemSucesso("Pastas Criadas com Sucesso")
    except Exception as e:
        logManager.logMensagemFatal(f"Falha ao Crias as Pastas: {e}")
        sys.exit(f"Erro Critico na Criação das Pastas. Olhe os logs.")

def criarEnv():
    if not os.path.exists(".env"):
        logManager.logMensagemInfo("Tentando Criar o .env")
        try:
            with open(".env", "w", encoding="utf-8") as arquivo:

                arquivo.write("TITULO_SITE=COLOQUE O NOME PARA APARECER NO TOPO DO SITE\n")
                arquivo.write("SENHA_ADMIN=COLOQUE A SENHA DESEJADA DE ADMIN\n")
                arquivo.write("BD_CONEXAO=COLOQUE AQUI A CONEXÃO COM O SEU BANCO DE DADOS\n")

            logManager.logMensagemSucesso(".env não existia e foi criado")
            sys.exit("Configure o arquivo .env antes de executar o programa")
        except Exception as e:
            logManager.logMensagemErro(f"Erro na hora de criar o .env: {e}")

    logManager.logMensagemInfo("Tentando Carregar o .env")
    try:
        load_dotenv()
        logManager.logMensagemSucesso(".env carregado")
    except Exception as e:
        logManager.logMensagemErro(f"Erro na hora de carregar o .env: {e}")

def inicializarMetadados():
    metaDados = {
        "ultimoDownloadScryfall" : "2000-01-01T00:00:00"
    }
    logManager.logMensagemInfo("Tentando criar os MetaDados")
    try:
        if not os.path.exists("configs/metadados.json"):
            with open("configs/metadados.json", "w", encoding="utf-8") as arquivo:
                json.dump(metaDados, arquivo, indent=4)
            logManager.logMensagemSucesso("Arquivos de Metadados criado com sucesso")
        else:
            logManager.logMensagemInfo("Arquivos Metadados Já Existem")
    except Exception as e:
        logManager.logMensagemFatal(f"Falha ao criar metadados. O programa não pode continuar: {e}")
        sys.exit("Erro crítico na inicialização. Verifique os logs.")


if __name__ == "__main__":
    configurarPrograma("https://api.scryfall.com/bulk-data/default-cards", 15)