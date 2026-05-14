import os
import sys
import datetime
import json
import logManager

from dotenv import load_dotenv
from pathlib import Path
from apiManager import baixarBancoScryfall, pegarCotacaoDollar, inicializarEdicoes
from metadadosManager import atualizarDataDownloadMetadados, getDataDownloadMetadados


def configurarPrograma(maxDias):
    bulkdataPath = "data/raw/bulkdata.json"
    edicoesPath = "data/raw/edicoes.json"
    criarPastas()
    logManager.manutencaoLogs()

    criarEnv()
    inicializarMetadados()

    agoraMs = int(datetime.datetime.now().timestamp() * 1000)
    diferencaMs = agoraMs - getDataDownloadMetadados()
    maxMs = maxDias * 24 * 60 * 60 * 1000

    bulkdataExiste = os.path.exists(bulkdataPath)
    edicoesExiste = os.path.exists(edicoesPath)
    precisaAtualizarTudo = (diferencaMs >= maxMs)

    if  precisaAtualizarTudo or not bulkdataExiste:
        logManager.logMensagemAviso("Bulkdata Muito Antigo ou Inexistente. Atualizando Ele")
        baixarBancoScryfall(bulkdataPath, bulkdataExiste)
        atualizarDataDownloadMetadados()
        logManager.logMensagemSucesso("Bulkdata Atualizada ou Criada Com Sucesso")
    if precisaAtualizarTudo or not edicoesExiste:
        inicializarEdicoes(edicoesPath, edicoesExiste)
    pegarCotacaoDollar()

def criarPastas():
    logManager.logMensagemInfo("Tentando Criar as Pastas")
    try:
        Path("data/raw").mkdir(parents=True, exist_ok=True)
        Path("data/db").mkdir(parents=True, exist_ok=True)
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
        "ultimoDownloadScryfall" : "2000-01-01T00:00:00",
        "tamanhoDownloadScryfall" : 0,
        "cotacaoDollar" : 0
    }
    caminho = "configs/metadados.json"
    logManager.logMensagemInfo("Tentando criar os MetaDados")
    try:
        if not os.path.exists("configs/metadados.json"):
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump(metaDados, arquivo, indent=4)
            logManager.logMensagemSucesso("Arquivos de Metadados criado com sucesso")
        else:
            logManager.logMensagemInfo("Arquivos Metadados Já Existem. Verificando A Validação de Estado")
            try:
                with open(caminho, "r", encoding="utf-8") as arquivo:
                    metadadosCarregados = json.load(arquivo)
                logManager.logMensagemSucesso("Arquivos de Metadados Carregado com Sucesso")
                diferenca = metaDados.keys() - metadadosCarregados.keys()
                if not diferenca:
                    return
                for chave in diferenca:
                    metadadosCarregados[chave] = metaDados[chave]
                logManager.logMensagemInfo("Os Metadados Estão Desatualizando, tentando atualiza-los")
                try:
                    with open(caminho, "w", encoding="utf-8") as arquivo:
                        json.dump(metadadosCarregados, arquivo, indent=4)
                    logManager.logMensagemSucesso("Metadados Atualizados Com Sucesso")
                except Exception as e:
                    logManager.logMensagemFatal(f"Falha Crítica. Os Metadados Estão Desatualizados e Não Foi Possível Atualiza-los: {e}")
                    sys.exit("Erro Crítico na Atualização dos Metadados. Verifique os logs")
            except Exception as e:
                logManager.logMensagemFatal(f"Falha Critica. Não foi possivel ler os Metadados: {e}")
                sys.exit("Erro Crítico na Leitura dos Metadados. Verifique os logs")
    except Exception as e:
        logManager.logMensagemFatal(f"Falha ao criar metadados. O programa não pode continuar: {e}")
        sys.exit("Erro crítico na inicialização. Verifique os logs.")


if __name__ == "__main__":
    configurarPrograma(15)