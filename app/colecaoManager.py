import ijson
import json

def limparCatalogo(bulkdataPath):
    dictCartas = {}
    contagem = 0
    with open(bulkdataPath, "rb") as arquivo:
        edicoes = ijson.kvitems(arquivo, "data")
        for sigla, dadosEdicao in edicoes:
            cartas = dadosEdicao.get("cards", [])
            for carta in cartas:
                if not "paper" in carta.get("availability", []):
                    continue
                nomeEn = carta.get("name").lower()

                if not nomeEn in dictCartas:
                    dictCartas[nomeEn] = {
                        "nome_pt": "",
                        "idScryfall": "",
                        "cmc": "",
                        "identidadeCor": "",
                        "cores": "",
                        "edicoes": {}
                    }

                dadosEstrangeiros = carta.get("foreignData", [])
                nomePt = ""
                for dados in dadosEstrangeiros:
                    if dados.get("language") != "Portuguese (Brazil)":
                        continue
                    nomePt = dados.get("name").lower()
                    dictCartas[nomeEn]["nome_pt"] = nomePt

                identificacoes = carta.get("identifiers", {})
                scryfallId = identificacoes.get("scryfallId", "")
                cmc = carta.get("convertedManaCost")
                identidadeCor = carta.get("colorIdentity")
                cores = carta.get("colors")

                dictCartas[nomeEn]["idScryfall"] = scryfallId
                dictCartas[nomeEn]["cmc"] = float(cmc)
                dictCartas[nomeEn]["identidadeCor"] = identidadeCor
                dictCartas[nomeEn]["cores"] = cores
                
                cartaUUID = carta.get("uuid")
                acabamentos = carta.get("finishes")
                numeroEdicao = carta.get("number")

                dictCartas[nomeEn]["edicoes"][sigla] = {
                    "uuid": cartaUUID,
                    "acabamentos": acabamentos,
                    "numeroColecao": numeroEdicao
                }
                contagem +=1
                if contagem % 1000 == 0:
                    print(f"Foram Lidas {contagem} cartas")
             
        with open("data/db/catalogo.json", "w", encoding="utf-8") as arquivo:
            json.dump(dictCartas, arquivo, ensure_ascii=False, indent=4)
                    
            

if __name__ == "__main__":
    limparCatalogo("data/raw/mtgJson.json")