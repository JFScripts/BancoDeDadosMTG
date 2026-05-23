import json
from app import logManager
import sys
from datetime import datetime

#Ferramentas

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

#MTG Json

def atualizarDataDownloadMtgjson(data=None):
    metaDados = _carregarMetadados()
    if data is None:
        curData = datetime.now().isoformat()
        metaDados["mtgjson"]["ultimoDownload"] = curData
    else:
        curData = datetime.isoformat(data)
        metaDados["mtgjson"]["ultimoDownload"] = curData
    _escreverMetadados(metaDados)

def getDataDownloadMtgjson():
    metaDados = _carregarMetadados()
    dataSalva = int(datetime.fromisoformat(metaDados["mtgjson"]["ultimoDownload"]).timestamp())*1000
    return dataSalva

def atualizarQntCartasMtgjson(qnt):
    metadados = _carregarMetadados()
    metadados["mtgjson"]["qntCartas"] = qnt
    _escreverMetadados(metadados)

def atualizarHashMtgjson(hashDownload):
    metadados = _carregarMetadados()
    metadados["mtgjson"]["hash"] = hashDownload
    _escreverMetadados(metadados)
#scryfall

def atualizarHashEdicoesScryfall(hashDownload):
    metadados = _carregarMetadados()
    metadados["scryfall"]["edicoes"]["hash"] = hashDownload
    _escreverMetadados(metadados)

# Finanças

def atualizarCotacaoDollarFinancas(valor):
    metadados = _carregarMetadados()
    metadados["financas"]["cotacaoDollar"] = valor
    _escreverMetadados(metadados)

def atualizarDataUltimaColetaFinancas(data=None):
    metaDados = _carregarMetadados()
    if data is None:
        curData = datetime.now().isoformat()
        metaDados["financas"]["dataUltimaColeta"] = curData
    else:
        curData = datetime.isoformat(data)
        metaDados["financas"]["dataUltimaColeta"] = curData
    _escreverMetadados(metaDados)

def getCotacaoDollarFinancas():
    metadados = _carregarMetadados()
    return metadados["financas"]["cotacaoDollar"]
    
#if __name__ == "__main__":
#    atualizarDataMetadados()
#    print(getDataMetadados())