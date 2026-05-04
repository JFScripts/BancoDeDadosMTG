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

    cartasExistente = lerTabela(conexao, "cartas", {"nome":nomeCarta, "edicao": edicaoAtual, "material": acabamento})
    
    if cartasExistente:
        cartasExistente = cartasExistente[0]
        idBD = int(cartasExistente["id"])
        novaQnt = qnt + cartasExistente["qnt"]
        atualizarTabela(conexao, "cartas", {"qnt": novaQnt}, idBD)
    else:
        cartaAtual = catalogo[nomeCarta]
        idScryfall = ""
        preco = 0.0
        cor = ""
        imagem = ""
        for edicao in cartaAtual:
            if edicao["edicao"] == edicaoAtual:
                idScryfall = edicao["idScryfall"]
                preco = edicao["precos"][acabamento]
                cor = edicao["cor"]
                imagem = edicao["imagem"]
                break
        dictNovaCarta = {
            "idScryfall": idScryfall,
            "nome": nomeCarta,
            "edicao": edicaoAtual,
            "qnt": qnt,
            "preco": preco,
            "material": acabamento,
            "cor": cor,
            "imagem": imagem
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
