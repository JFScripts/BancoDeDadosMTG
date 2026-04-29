import sqlite3
import os
from gerenciadorBD import criarColecao, lerTabela
from apiManager import inicializarCatalogo, pegarCotacaoDollar
from menu import adicionarNovaCarta, atualizarCarta, deletarCarta, listarCartas, gerarGraficoCores
from aiManager import consultarSinergias
from inicializer import inicializarArquivos

def main():
    inicializarArquivos()
    urlBulkData = "https://api.scryfall.com/bulk-data/default-cards"
    urlAwesomeapi = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
    colecaoNome = "colecao.db"
    dataBase = os.getenv("DB_NAME")
    geminiKey = os.getenv("GEMINI_API_KEY")
    maxDias = 15

    criarColecao(colecaoNome)
    catalogo = inicializarCatalogo(urlBulkData, dataBase, maxDias)
    cotacao = pegarCotacaoDollar(urlAwesomeapi)
    
    conexao = sqlite3.connect(colecaoNome)

    while True:
        print("[1] Adicionar Carta")
        print("[2] Ver Coleção")
        print("[3] Atualizar Carta")
        print("[4] Remover Carta")
        print("[5] Conferir Sinergias")
        print("[6] Gerar Grafico de Cores")
        print("[0] Sair")
        
        try:
            escolha = int(input("Digite a opção desejada:\n> "))
        except ValueError:
            print("\nOpção Inválida\n")
            continue

        match escolha:
            case 0:
                print("Encerrando...")
                break
            case 1:
                adicionarNovaCarta(conexao, catalogo)
            case 2:
                minhaPasta = lerTabela(conexao, "cartas")
                listarCartas(minhaPasta, cotacao, catalogo)
            case 3:
                atualizarCarta(conexao, cotacao, catalogo)
            case 4:
                deletarCarta(conexao, cotacao, catalogo)
            case 5:
                print("\n--- ANALISANDO SUA COLEÇÃO COM IA ---")
                print(consultarSinergias(lerTabela(conexao, "cartas"), geminiKey))
            case 6:
                gerarGraficoCores(conexao)
            case _:
                print("\nOpção Inválida\n")
                
    conexao.close()

if __name__ == "__main__":
    main()