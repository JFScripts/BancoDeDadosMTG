import matplotlib.pyplot as plt
from gerenciadorBD import adicionarValorTabela, lerTabela, atualizarTabela, deletarItemTabela

def adicionarNovaCarta(conexao, catalogo):
    nomeCarta = ""
    while nomeCarta not in catalogo:
        nomeCarta = input("\nDigite o nome da carta ou digite 0 para sair:\n> ").lower()
        if nomeCarta == "0":
            break
            
    if nomeCarta == "0":
        print("\nRetornando para o menu")
        return

    qntCartas = int(input("\nDigite a quantidade de cartas:\n> "))
    
    ehFoil = input("A Carta é FOIL? (S/N):\n> ").lower()
    qntNormal = 0
    qntFoil = 0
    if ehFoil == "s":
        qntFoil = qntCartas
    else:
        qntNormal = qntCartas

    versoes = catalogo[nomeCarta]

    vEscolhida = -1
    while vEscolhida < 0 or vEscolhida >= len(versoes):
        for i, versao in enumerate(versoes):
            print(f"[{i}] Edição: {versao['edicao']} - Preço {versao['preco']}")
        vEscolhida = int(input("\nDigite o número da versão:\n> "))
            
    idScryfall = catalogo[nomeCarta][vEscolhida]["idScryfall"]
    edicao = catalogo[nomeCarta][vEscolhida]["edicao"]
    corLista = catalogo[nomeCarta][vEscolhida]["cor"]
    cor = ""
    
    for identidade in corLista:
        cor += str(identidade)
    dictNovaCarta = {"nome":nomeCarta, "idScryfall": idScryfall, "qntNormal":qntNormal, "qntFoil":qntFoil, "edicao": edicao, "cor": cor}
    adicionarValorTabela(conexao, "cartas", dictNovaCarta)

def atualizarCarta(conexao, cotacao, catalogo):
    minhaPasta = lerTabela(conexao, "cartas")
    listarCartas(minhaPasta, cotacao, catalogo)
    cartaEscolhida = ""

    while True:
        cartaEscolhida = input("\nDigite a Carta que você quer atualizar ou digite 0 para cancelar:\n> ").lower()
        if cartaEscolhida == "0":
            break
        cartaAtual = lerTabela(conexao, "cartas", {"nome": cartaEscolhida})
        if cartaAtual:
            break
            
    if cartaEscolhida == "0":
        print("\nRetornando ao Menu\n")
        return
        
    versoes = cartaAtual
    vEscolhida = -1
    while vEscolhida < 0 or vEscolhida >= len(versoes):
        for i, versao in enumerate(versoes):
            print(f"[{i}] Edição: {versao['edicao']} - qntNormal {versao['qntNormal']} | qntFoil {versao['qntFoil']}")
        vEscolhida = int(input("\nDigite o número da versão:\n> "))
        
    novaQntNormal = -1
    novaQntFoil = -1
    while novaQntNormal < 0 or novaQntFoil < 0:
        novaQntNormal = int(input(f"Digite a nova quantidade de cartas normais:\n> "))
        novaQntFoil = int(input(f"Digite a nova quantidade de cartas foils:\n> "))
        
    idAlvo = versoes[vEscolhida]["id"]
    atualizarTabela(conexao, "cartas", {"qntNormal":novaQntNormal, "qntFoil":novaQntFoil}, idAlvo)
    print("\nQuantidade da carta atualizada com sucesso\n")

def deletarCarta(conexao, cotacao, catalogo):
    minhaPasta = lerTabela(conexao, "cartas")
    listarCartas(minhaPasta, cotacao, catalogo)
    cartaEscolhida = ""

    while True:
        cartaEscolhida = input("\nDigite a Carta que você quer deletar ou digite 0 para cancelar:\n> ").lower()
        if cartaEscolhida == "0":
            break
        cartaAtual = lerTabela(conexao, "cartas", {"nome": cartaEscolhida})
        if cartaAtual:
            break
            
    if cartaEscolhida == "0":
        print("\nRetornando ao Menu\n")
        return

    versoes = cartaAtual
    vEscolhida = -1
    while vEscolhida < 0 or vEscolhida >= len(versoes):
        for i, versao in enumerate(versoes):
            print(f"[{i}] Edição: {versao['edicao']} - qntNormal {versao['qntNormal']} | qntFoil {versao['qntFoil']}")
        vEscolhida = int(input("\nDigite o número da versão:\n> "))

    cartaDeletar = versoes[vEscolhida]["id"]
    qntNormal = versoes[vEscolhida]["qntNormal"]
    qntFoil = versoes[vEscolhida]["qntFoil"]
    qntDeletarNormal = -1
    qntDeletarFoil = -1

    while (qntDeletarNormal < 0 or qntDeletarNormal > qntNormal) or (qntDeletarFoil < 0 or qntDeletarFoil > qntFoil):
        qntDeletarNormal = int(input(f"Digite a quantidade de cartas normais para remover [qntAtual: {qntNormal}]:\n> "))
        qntDeletarFoil = int(input(f"Digite a quantidade de cartas foil para remover [qntAtual: {qntFoil}]:\n> "))
                
    novaQntNormal = qntNormal - qntDeletarNormal
    novaQntFoil = qntFoil - qntDeletarFoil
                
    if novaQntNormal + novaQntFoil <= 0:
        deletarItemTabela(conexao, "cartas", cartaDeletar)
        output = f"A Carta {cartaEscolhida.title()} Foi removida"
    else:
        dictAtualizado = {"qntNormal": novaQntNormal, "qntFoil": novaQntFoil}
        atualizarTabela(conexao, "cartas", dictAtualizado, cartaDeletar)
        output = f"Foram removidas {qntDeletarNormal} cartas normais e {qntDeletarFoil} cartas foil"
        
    print(output)

def listarCartas(lista, valorDollar, catalogo):
    print(f"{'NOME':25} | {'SET':6} | {'QTD NORMAL':10} | {'QTD FOIL':8} | {'QTD TOTAL':9} | {'PREÇO TOTAL (R$)'}")
    print("-" * 85)
    
    valorTotalColecao = 0.0
    
    for carta in lista:
        qntTotal = carta['qntNormal'] + carta['qntFoil']
        nomeBanco = carta['nome']
        edicaoBanco = carta['edicao']
        
        precoDolar = 0.0 
        if nomeBanco in catalogo:
            versoes = catalogo[nomeBanco]
            for versao in versoes:
                if versao['edicao'] == edicaoBanco:
                    precoDolar = float(versao['preco'])
                    break 
                    
        precoReal = precoDolar * valorDollar
        valorDaLinha = precoReal * qntTotal
        
        valorTotalColecao += valorDaLinha
        
        print(f"{nomeBanco.title():25} | {edicaoBanco:6} | {carta['qntNormal']:10} | {carta['qntFoil']:8} | {qntTotal:9} | R$ {valorDaLinha:8.2f}")
        
    print("-" * 85)
    print(f"VALOR TOTAL DA COLEÇÃO: R$ {valorTotalColecao:.2f}\n")

def gerarGraficoCores(conexao):
    cartas = lerTabela(conexao, "cartas")
    dictCor = {"incolor": 0, "preto": 0, "verde": 0, "vermelho": 0, "azul": 0, "branco": 0, "multicor": 0}
    for carta in cartas:
        corAtual = carta["cor"]
        match corAtual:
            case "":
                dictCor["incolor"] += 1
            case "B":
                dictCor["preto"] += 1
            case "G":
                dictCor["verde"] += 1
            case "R":
                dictCor["vermelho"] += 1
            case "U":
                dictCor["azul"] += 1
            case "W":
                dictCor["branco"] += 1
            case _:
                dictCor["multicor"] += 1
    nomeCores = list(dictCor.keys())
    valores = list(dictCor.values())
    coresGrafico = ['#90adbb', '#15110d', '#00733e', '#d3202a', '#0e68ab', '#f0f2c3', '#e5d164']

    plt.figure(figsize=(8, 8))
    plt.pie(valores, labels=nomeCores, autopct='%1.1f%%', colors=coresGrafico, startangle=140)
    plt.title("Distribuição de Cores da Coleção")
    plt.show()

