import json
from datetime import datetime

def _carregarMetadados():
    with open("configs/metadados.json", "r") as arquivo:
        return json.load(arquivo)

def _escreverMetadados(metaDados):
    with open("configs/metadados.json", "w") as arquivo:
        json.dump(metaDados, arquivo, indent=4)

def atualizarDataDownloadMetadados(data=None):
    metaDados = _carregarMetadados()
    if data is None:
        curData = datetime.now().isoformat()
        metaDados["ultimoDownloadScryfall"] = curData
    else:
        curData = datetime.isoformat(data)
        metaDados["ultimoDownloadScryfall"] = curData

    _escreverMetadados(metaDados)

def getDataDownloadMetadados():
    metaDados = _carregarMetadados()
    dataSalva = int(datetime.fromisoformat(metaDados["ultimoDownloadScryfall"]).timestamp())*1000
    return dataSalva

if __name__ == "__main__":
    atualizarDataMetadados()
    print(getDataMetadados())