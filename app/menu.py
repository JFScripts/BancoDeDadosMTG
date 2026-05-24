from app import gerenciadorBD
import sqlite3

# buscamos o nome no BD procurando o nome em PT e em ENG
        # Verificamos se ja está salvo
            # Se Está atualizamos
            # Se não adicionamos
    #Se não Encontramos o nome na bulkdata buscamos em nomes alternativos
        # Se encontramos
            #Verifica Se Já Existe
                #Se Existe Atualizamos
                # Se não Adicionamos
            # Não Existe Retorna erro
def adicionarCarta(conexao, pacote):
    if not pacote.get("nome"):
        return False
    nomeDigitado = f"%{pacote.get('nome')}%"
    edicao = pacote.get("edicao")
    acabamento = pacote.get("acabamento")
    qnt = pacote.get("quantidade")
    
    uuidEncontrado = None
    queryPrimeiraBusca = ("(nome_en LIKE ? OR nome_pt LIKE ?) AND edicao = ?",(nomeDigitado, nomeDigitado, edicao))
    primeiroResultado = gerenciadorBD.lerTabela(conexao, "bulkdata", filtro=queryPrimeiraBusca)
    if primeiroResultado:
        uuidEncontrado = primeiroResultado[0]["uuid"]
    else:
        querySegundaBusca = ("nome_variacao LIKE ?", (nomeDigitado,))
        segundoResultado = gerenciadorBD.lerTabela(conexao, "nomes_alternativos", filtro=querySegundaBusca)
        if segundoResultado:
            uuidEncontrado = segundoResultado[0]["uuid"]
    if uuidEncontrado:
        jaExiste = gerenciadorBD.lerTabela(conexao, "colecao_usuario", filtro={"uuid": uuidEncontrado, "acabamento": acabamento})
        if jaExiste:
            gerenciadorBD.atualizarTabela(conexao, "colecao_usuario", dictFiltro={"uuid": uuidEncontrado, "acabamento": acabamento}, dictIncrementos={"quantidade": qnt})
        else:
            dictAdicionar = {
                "uuid": uuidEncontrado,
                "acabamento": acabamento,
                "quantidade": qnt
            }
            gerenciadorBD.adicionarValorTabela(conexao, "colecao_usuario", dictAdicionar)
        return True
    else:
        return False

def buscarNomesCartas(conexao):
    nomeCartas = gerenciadorBD.lerTabela(conexao, "bulkdata", colunas="nome_en, nome_pt")
    if not nomeCartas:
        return []
    nomesUnicos = set()
    for nome in nomeCartas:
        if nome["nome_en"]:
            nomesUnicos.add(nome["nome_en"])
        if nome["nome_pt"]:
            nomesUnicos.add(nome["nome_pt"])
    return list(nomesUnicos)

def buscarEdicoes(conexao, nome):
    query = """
    SELECT 
        edicoes.codigo,
        edicoes.nome, 
        edicoes.icone_url AS linkImagem,
        bulkdata.acabamentos 
    FROM bulkdata
    JOIN edicoes ON bulkdata.edicao = edicoes.codigo
    WHERE bulkdata.nome_en COLLATE NOCASE = ? OR bulkdata.nome_pt COLLATE NOCASE = ?
    """
    return gerenciadorBD.lerQueryPersonalizada(conexao, query, (nome, nome))
    
if __name__ == "__main__":
    pacote = {
        "nome": "monólito de basalto",
        "edicao": "2ED",
        "acabamento": "nonfoil",
        "quantidade": 1
    }
    conexao = sqlite3.connect("data/db/bdMTG.db")
    adicionarCarta(conexao, pacote)
    
