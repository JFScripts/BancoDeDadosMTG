import difflib
import matplotlib.pyplot as plt
from gerenciadorBD import adicionarValorTabela, lerTabela, atualizarTabela, deletarItemTabela

def adicionarNovaCarta(conexao, catalogo):
    nomeCarta = ""
    listaNomes = []
    
    for nome in catalogo.keys():
        listaNomes.append(nome)

    while True:
        nomeCarta = input("\nDigite o nome da carta ou digite 0 para sair:\n> ").lower()
        if nomeCarta == "0":
            print("\nRetornando para o menu")
            return
        if nomeCarta in listaNomes:
            break
        sugestoes = difflib.get_close_matches(nomeCarta, listaNomes, n=1, cutoff=0.6)
        sugestao = sugestoes[0]
        if sugestoes:
            aceitarSugestao = input((f"Você quis dizer {sugestao}?(S/N)\n> ")).lower()
            if aceitarSugestao == "s":
                nomeCarta = sugestao
                break
                    
    versoes = catalogo[nomeCarta]
    vEscolhida = -1
    while vEscolhida < 0 or vEscolhida >= len(versoes):
        print("\n")
        for i, versao in enumerate(versoes):
            print(f"[{i}] Edição: {versao['edicao']}")
        vEscolhida = int(input("\nDigite o número da versão:\n> "))
    
    cartaSelecionada = catalogo[nomeCarta][vEscolhida]

    acabamento = cartaSelecionada["acabamento"]
    if len(acabamento) > 1:
        materialEscolhido = ""
        while materialEscolhido not in acabamento:
            print("\n")
            for i, material in enumerate(acabamento):
                print(f"[{i}] - {material}")
            materialEscolhido = acabamento[int(input("\nSelecione o tipo da carta:\n>"))]
    else:
        materialEscolhido = acabamento[0]

    qntCartas = -1
    while qntCartas <= 0:
        qntCartas = int(input("\nDigite a quantidade de cartas:\n>"))
     
    preco = cartaSelecionada["precos"][materialEscolhido]
    idScryfall = cartaSelecionada["idScryfall"]
    edicao = cartaSelecionada["edicao"]
    cor = cartaSelecionada["cor"]
    imagem = cartaSelecionada["imagem"]
   
    dictNovaCarta = {"nome":nomeCarta, 
    "idScryfall": idScryfall, 
    "material": materialEscolhido, 
    "qnt": qntCartas,
    "preco": preco, 
    "edicao": edicao, 
    "cor": cor,
    "imagem": imagem}
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

def listarCartas(lista, valorDollar, catalogo, edicoes):
    print(f"{'NOME':^25} | {'EDIÇÃO':^40} | {'METERIAL':^10} | {'QTD':^8} | {'PRECO':^9} | {'PREÇO TOTAL (R$)'}")
    print("-" * 150)
    
    valorTotalColecao = 0.0
    
    for carta in lista:
        qnt = carta["qnt"]
        nomeCarta = carta["nome"]
        edicao = edicoes[carta["edicao"]]["nome"]
        material = carta["material"]
        precoReal = carta["preco"] * valorDollar
        valorDaLinha = precoReal * qnt
        
        valorTotalColecao += valorDaLinha
        
        print(f"{nomeCarta.title():^25} | {edicao:^40} | {material:^10} | {qnt:^8} | R${precoReal:9.2f} | R$ {valorDaLinha:10.2f}")
        
    print("-" * 150)
    print(f"VALOR TOTAL DA COLEÇÃO: R$ {valorTotalColecao:.2f}\n")
    input("\nPressione ENTER para voltar ao menu.\n")

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

