import json
import logManager
import sys
from datetime import datetime


def _carregarMetadados():
    try:
        with open("configs/metadados.json", "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except Exception as e:
        logManager.logMensagemFatal(f"Não Foi Possível Carregar os Metadados: {e}")
        sys.exit("Erro Crítico Ao Carregar Os Metadados. Confira os Logs")

def _escreverMetadados(metaDados):
    logManager.logMensagemInfo("Tentando Escrever Metadados")
    try:
        with open("configs/metadados.json", "w", encoding="utf-8") as arquivo:
            json.dump(metaDados, arquivo, indent=4)
        logManager.logMensagemSucesso("Escrever Nos Metadados Foi Um Sucesso")
    except Exception as e:
        logManager.logMensagemFatal(f"Não Foi Possível Escrever Nos Metadados: {e}")
        sys.exit("Erro Crítico Ao Escrever Nos Metadados. Confira os Logs")

def atualizarDataDownloadMetadados(data=None):
    metaDados = _carregarMetadados()
    if data is None:
        curData = datetime.now().isoformat()
        metaDados["ultimoDownloadMTGJson"] = curData
    else:
        curData = datetime.isoformat(data)
        metaDados["ultimoDownloadMTGJson"] = curData

    _escreverMetadados(metaDados)

def getDataDownloadMetadados():
    metaDados = _carregarMetadados()
    dataSalva = int(datetime.fromisoformat(metaDados["ultimoDownloadMTGJson"]).timestamp())*1000
    return dataSalva

def atualizarQntCartas(qnt):
    metadados = _carregarMetadados()
    metadados["qntCartasMTGJSON"] = qnt
    _escreverMetadados(metadados)

def atualizarHashDownload(hashDownload):
    metadados = _carregarMetadados()
    metadados["hashDownload"] = hashDownload
    _escreverMetadados(metadados)

def atualizarCotacaoDollar(valor):
    metadados = _carregarMetadados()
    metadados["cotacaoDollar"] = valor
    _escreverMetadados(metadados)

def getCotacaoDollar():
    metadados = _carregarMetadados()
    return metadados["cotacaoDollar"]
    
if __name__ == "__main__":
    atualizarDataMetadados()
    print(getDataMetadados())