import sqlite3
import os
from app.gerenciadorBD import lerTabela, atualizarTabela, adicionarValorTabela
from dotenv import load_dotenv

def adicionarNovaCarta(pacote, catalogo):
    load_dotenv()
    bdNome = os.getenv("BD_CONEXAO")
    conexao = sqlite3.connect(bdNome)
    
    nomeCarta = pacote["nome"]
    qnt = pacote["qnt"]
    edicaoAtual = pacote["edicao"]
    acabamento = pacote["acabamento"]
    idScryfall = pacote["idScryfall"]

    cartasExistente = lerTabela(conexao, "cartas", {"idScryfall": idScryfall, "material": acabamento})
    
    if cartasExistente:
        cartasExistente = cartasExistente[0]
        idBD = int(cartasExistente["id"])
        novaQnt = qnt + cartasExistente["qnt"]
        atualizarTabela(conexao, "cartas", {"qnt": novaQnt}, idBD)
    else:
        cartaAtual = catalogo[nomeCarta.lower()]
        preco = 0.0
        cor = ""
        imagem = ""
        for versao in cartaAtual:
            if versao["idScryfall"] == idScryfall:
                preco = versao["precos"][acabamento]
                cor = versao["cor"]
                imagem = versao["imagem"]
                numeroColecao = versao["numeroColecao"]
                break
        dictNovaCarta = {
            "idScryfall": idScryfall,
            "nome": nomeCarta,
            "edicao": edicaoAtual,
            "qnt": qnt,
            "preco": preco,
            "material": acabamento,
            "cor": cor,
            "imagem": imagem,
            "numeroColecao" : numeroColecao
        }

        adicionarValorTabela(conexao, "cartas", dictNovaCarta)
            


if __name__ == "__main__": 
    dictTeste = {
        "nome": "merrow wavebreakers",
        "qnt": -5,
        "edicao": "shm",
        "acabamento": "nonfoil" 
    }
    adicionarNovaCarta(dictTeste)
