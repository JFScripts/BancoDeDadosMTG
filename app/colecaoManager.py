import ijson
import json
import logManager
import sys
import os
import gerenciadorBD
import sqlite3

from hashManager import gerarHashArquivo

def limparCatalogo(mtgJSONPath):
    dictCartas = {}
    cartasUnicas = 0
    logManager.logMensagemInfo("Tentando Gerar O Catálogo")
    try:
        with open(mtgJSONPath, "rb") as arquivo:
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
                            "cmc": "",
                            "identidadeCor": "",
                            "cores": "",
                            "tipos": "",
                            "edicoes": {}
                        }
                        cartasUnicas += 1
                    dadosEstrangeiros = carta.get("foreignData", [])
                    nomePt = ""
                    for dados in dadosEstrangeiros:
                        if dados.get("language") != "Portuguese (Brazil)":
                            continue
                        nomePt = dados.get("name").lower()
                        dictCartas[nomeEn]["nome_pt"] = nomePt
                    identificacoes = carta.get("identifiers", {})
                    idScryfall = identificacoes.get("scryfallId", "")
                    cmc = carta.get("convertedManaCost", 0.0)
                    identidadeCor = carta.get("colorIdentity")
                    cores = carta.get("colors")
                    tipos = carta.get("type")
                    raridade = carta.get("rarity")

                    dictCartas[nomeEn]["cmc"] = float(cmc)
                    dictCartas[nomeEn]["identidadeCor"] = identidadeCor
                    dictCartas[nomeEn]["cores"] = cores
                    dictCartas[nomeEn]["tipos"] = tipos
                    
                    cartaUUID = carta.get("uuid")
                    acabamentos = carta.get("finishes")
                    numeroEdicao = carta.get("number")

                    dictCartas[nomeEn]["edicoes"][sigla] = {
                        "uuid": cartaUUID,
                        "acabamentos": acabamentos,
                        "numeroColecao": numeroEdicao,
                        "raridade": raridade,
                        "idScryfall": idScryfall
                    }
        logManager.logMensagemSucesso(f"Catalogo Gerado Com Sucesso Com {cartasUnicas} Cartas")
    except Exception as e:
            logManager.logMensagemFatal(f"Não Foi Possível Gerar O Catálogo: {e}")
            sys.exit("Erro Critico Ao Gerar O Catálogo. Verifique Os Logs")
    
    logManager.logMensagemInfo("Tentando Salvar O Catalogo No HD")
    try:
        with open("data/db/catalogo.json", "w", encoding="utf-8") as arquivo:
            json.dump(dictCartas, arquivo, ensure_ascii=False, indent=4)
        logManager.logMensagemSucesso("Catálogo Salvo Com Sucesso")
    except Exception as e:
        if os.path.exists("data/db/catalogo.json"):
            logManager.logMensagemAviso(f"Erro Ao Tentar Salvar O Catálogo No HD, Será Utilizado O Antigo. Erro: {e}")
        else:
            logManager.logMensagemFatal(f"Não Foi Possível Salvar O Catálogo No HD")
            sys.exit("Falha Crítica Na Hora De Salvar O Catálogo No HD. Verifique Os Logs.")

def popularTabelaEdicoes(edicoesPath, conexao):
    
    logManager.logMensagemInfo("Tentando Ler Edicoes.json")
    try:
        with open(edicoesPath, "r", encoding="utf-8") as arquivo:
            edicoes = json.load(arquivo)
        logManager.logMensagemSucesso("Edicoes.json Lido Com Sucesso")
    except Exception as e:
        print(e)
    for sigla, dados in edicoes.items():
        dictEdicao = {
            "codigo": sigla.upper(),
            "nome": dados.get("nome"),
            "id_scryfall": dados.get("id"),
            "qnt_cartas": dados.get("qntCartas"),
            "icone_url": dados.get("icone")
        }

        gerenciadorBD.adicionarValorTabela(conexao, "edicoes", dictEdicao)
            #print(f"{dictEdicao['nome']} Adicionado")

def popularTabelaBulkdata(mtgJsonPath, conexao):
    contagemCartas = 0
    with open(mtgJsonPath, "r", encoding="utf-8") as arquivo:
        cartas = json.load(arquivo)
    for nomeEn, dadosCarta in cartas.items():
        edicoesCarta = dadosCarta.get("edicoes", {})
        for sigla, dadosEdicao in edicoesCarta.items():
            dictCarta = {
                "nome_en": nomeEn,
                "nome_pt": dadosCarta.get("nome_pt"),
                "cmc": dadosCarta.get("cmc"),
                "identidade_cor": ",".join(dadosCarta.get("identidadeCor", [])),
                "cores": ",".join(dadosCarta.get("cores", [])),
                "tipos": dadosCarta.get("tipos"),
                "edicao": sigla.upper(),
                "uuid": dadosEdicao.get("uuid"),
                "acabamentos": ",".join(dadosEdicao.get("acabamentos", [])),
                "n_colecao": dadosEdicao.get("numeroColecao"),
                "raridade": dadosEdicao.get("raridade"),
                "id_scryfall": dadosEdicao.get("idScryfall")
            }

            if gerenciadorBD.adicionarValorTabela(conexao, "bulkdata", dictCarta, autoCommit=False):
                contagemCartas += 1
            if contagemCartas % 1000 == 0:
                conexao.commit()
                print(f"{contagemCartas} cartas adicionadas")
    conexao.commit()

if __name__ == "__main__":
    conexao = sqlite3.connect("data/db/bdMTG.db")
    popularTabelaEdicoes("data/db/edicoes.json", conexao)
    popularTabelaBulkdata("data/db/catalogo.json", conexao)
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM bulkdata")
    resultados = cursor.fetchall()

    for linha in resultados:
        print(dict(linha))
    conexao.close()

    #limparCatalogo("data/raw/mtgJson.json")