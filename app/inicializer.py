import os
import sys
import datetime
import json
import logManager
import sqlite3
import metadadosManager
import colecaoManager

from dotenv import load_dotenv
from pathlib import Path
from apiManager import baixarMTGJson, pegarCotacaoDollar, inicializarEdicoes
from gerenciadorBD import criarTabelas


def configurarPrograma(maxDias):
    criarEnv()
    mtgjsonPath = "data/raw/mtgJson.json"
    edicoesPath = "data/db/edicoes.json"
    catalogoPath = "data/db/catalogo.json"
    dbPath = os.getenv("DATABASE_URL")
        
    criarPastas()
    logManager.logNovaSessao()
    logManager.manutencaoLogs()

    inicializarMetadados()

    agoraMs = int(datetime.datetime.now().timestamp() * 1000)
    ultimoDownload = metadadosManager.getDataDownloadMtgjson()
    diferencaMs = agoraMs - ultimoDownload
    maxMs = maxDias * 24 * 60 * 60 * 1000

    mtgJsonExiste = os.path.exists(mtgjsonPath)
    edicoesExiste = os.path.exists(edicoesPath)
    catalogoExiste = os.path.exists(catalogoPath) 

    precisaAtualizarTudo = (diferencaMs >= maxMs)

    if  precisaAtualizarTudo or not mtgJsonExiste:
        logManager.logMensagemAviso("Bulkdata Muito Antigo ou Inexistente. Atualizando Ele")
        baixarMTGJson(mtgjsonPath, mtgJsonExiste)
        metadadosManager.atualizarDataDownloadMtgjson()
        logManager.logMensagemSucesso("MtgJson Atualizado ou Criado Com Sucesso")

    if precisaAtualizarTudo or not edicoesExiste:
        logManager.logMensagemAviso("Edicoes Muito Antiga ou Inexistente. Tentando Atualizar")
        inicializarEdicoes(edicoesPath, edicoesExiste)
        logManager.logMensagemSucesso("Edicoes Atualizada ou Criada Com Sucesso")

    pegarCotacaoDollar()
    conexao = sqlite3.connect(dbPath)
    #criar as tabelas
    inicializarBD(conexao)

    if precisaAtualizarTudo or not catalogoExiste:
        logManager.logMensagemAviso("Catalogo Desatualizado. Atualizando Ele")
        colecaoManager.limparCatalogo(mtgjsonPath)
        colecaoManager.popularTabelaEdicoes(edicoesPath, conexao)
        colecaoManager.popularTabelaBulkdata(mtgjsonPath, conexao)
        logManager.logMensagemSucesso("Catalogo Atualizado E Banco De Dados Populado")    

    conexao.commit()
    conexao.close()
    logManager.logMensagemSucesso("Inicialização Feita Com Sucesso")

def criarPastas():
    logManager.logMensagemInfo("Tentando Criar as Pastas")
    try:
        Path("data/raw").mkdir(parents=True, exist_ok=True)
        Path("data/db").mkdir(parents=True, exist_ok=True)
        Path("logs/new").mkdir(parents=True, exist_ok=True)
        Path("logs/old").mkdir(parents=True, exist_ok=True)
        Path("configs").mkdir(parents=True, exist_ok=True)
        logManager.logMensagemSucesso("Pastas Criadas com Sucesso")
    except Exception as e:
        logManager.logMensagemFatal(f"Falha ao Crias as Pastas: {e}")
        sys.exit(f"Erro Critico na Criação das Pastas. Olhe os logs.")

def criarEnv():
    if not os.path.exists(".env"):
        logManager.logMensagemInfo("Tentando Criar o .env")
        try:
            with open(".env", "w", encoding="utf-8") as arquivo:

                arquivo.write("TITULO_SITE=COLOQUE O NOME PARA APARECER NO TOPO DO SITE\n")
                arquivo.write("SENHA_ADMIN=COLOQUE A SENHA DESEJADA DE ADMIN\n")
                arquivo.write("DATABASE_URL=COLOQUE AQUI A CONEXÃO COM O SEU BANCO DE DADOS\n")

            logManager.logMensagemSucesso(".env não existia e foi criado")
            sys.exit("Configure o arquivo .env antes de executar o programa")
        except Exception as e:
            logManager.logMensagemErro(f"Erro na hora de criar o .env: {e}")

    logManager.logMensagemInfo("Tentando Carregar o .env")
    try:
        load_dotenv()
        logManager.logMensagemSucesso(".env carregado")
    except Exception as e:
        logManager.logMensagemErro(f"Erro na hora de carregar o .env: {e}")

def inicializarMetadados():
    metaDados = {
        "mtgjson":{
            "ultimoDownload": "2000-01-01T00:00:00",
            "qntCartas": 0,
            "hash": ""
        },
        "scryfall": {
            "edicoes":{
                "hash": ""
            }
        },
        "arquivosLocais": {
            "hashEdicoesJson": "",
            "hashCatalogoJson": ""
        },
        "financas": {
            "cotacaoDollar": 0.0,
            "dataUltimaColeta": "2000-01-01T00:00:00"
        },
        "sistema": {
            "versao": 0.2
        }
    }
    caminho = "configs/metadados.json"
    logManager.logMensagemInfo("Tentando criar os MetaDados")
    try:
        if not os.path.exists("configs/metadados.json"):
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump(metaDados, arquivo, indent=4)
            logManager.logMensagemSucesso("Arquivos de Metadados criado com sucesso")
        else:
            logManager.logMensagemInfo("Arquivos Metadados Já Existem. Verificando A Validação de Estado")
            try:
                with open(caminho, "r", encoding="utf-8") as arquivo:
                    metadadosCarregados = json.load(arquivo)
                logManager.logMensagemSucesso("Arquivos de Metadados Carregado com Sucesso")
                metadadosCarregados, foiAtualizado = atualizarMetadados(metaDados, metadadosCarregados)
                if not foiAtualizado:
                    return
                logManager.logMensagemInfo("Os Metadados Estão Desatualizando, tentando atualiza-los")
                try:
                    with open(caminho, "w", encoding="utf-8") as arquivo:
                        json.dump(metadadosCarregados, arquivo, indent=4)
                    logManager.logMensagemSucesso("Metadados Atualizados Com Sucesso")
                except Exception as e:
                    logManager.logMensagemFatal(f"Falha Crítica. Os Metadados Estão Desatualizados e Não Foi Possível Atualiza-los: {e}")
                    sys.exit("Erro Crítico na Atualização dos Metadados. Verifique os logs")
            except Exception as e:
                logManager.logMensagemFatal(f"Falha Critica. Não foi possivel ler os Metadados: {e}")
                sys.exit("Erro Crítico na Leitura dos Metadados. Verifique os logs")
    except Exception as e:
        logManager.logMensagemFatal(f"Falha ao criar metadados. O programa não pode continuar: {e}")
        sys.exit("Erro crítico na inicialização. Verifique os logs.")

def atualizarMetadados(padrao, carregado):
    mudou = False
    for chave, valor in padrao.items():
        if chave not in carregado:
            carregado[chave] = valor
            mudou = True
        elif isinstance(valor, dict) and isinstance(carregado[chave], dict):
            novoDict, novoMudou = atualizarMetadados(valor, carregado[chave])
            if novoMudou:
                mudou = True
    return carregado, mudou

def inicializarBD(conexao):

    queryEdicoes = ("""CREATE TABLE IF NOT EXISTS edicoes (
    codigo TEXT PRIMARY KEY,
    nome TEXT,
    id_scryfall TEXT,
    qnt_cartas INTEGER,
    icone_url TEXT);
    """)

    queryBulkdata = ("""CREATE TABLE IF NOT EXISTS bulkdata (
        uuid TEXT PRIMARY KEY,
        id_scryfall TEXT UNIQUE NOT NULL,
        nome_en TEXT NOT NULL,
        nome_pt TEXT,
        cmc REAL,
        identidade_cor TEXT,
        cores TEXT,
        tipos TEXT,
        raridade TEXT,
        acabamentos TEXT,
        n_colecao TEXT,
        edicao TEXT,
        FOREIGN KEY (edicao) REFERENCES edicoes (codigo) ON DELETE CASCADE
    );
    """)

    queryNomesAlternativos = ("""CREATE TABLE IF NOT EXISTS nomes_alternativos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_variacao TEXT UNIQUE NOT NULL);
    """)

    queryRelacaoNomeCartas = ("""CREATE TABLE IF NOT EXISTS relacao_nomes_cartas (
    uuid TEXT,
    id_nome_alternativo INTEGER,
    PRIMARY KEY (uuid, id_nome_alternativo),
    FOREIGN KEY (uuid) REFERENCES bulkdata (uuid) ON DELETE CASCADE,
    FOREIGN KEY (id_nome_alternativo) REFERENCES nomes_alternativos (id) ON DELETE CASCADE);
    """)

    queryColecaoUsuario = ("""CREATE TABLE IF NOT EXISTS colecao_usuario(
        uuid TEXT NOT NULL,
        acabamento TEXT NOT NULL,
        quantidade INTEGER NOT NULL CHECK (quantidade > 0),
        PRIMARY KEY (uuid, acabamento),
        FOREIGN KEY (uuid) REFERENCES bulkdata (uuid) ON DELETE CASCADE
    )
    
    """)
    
    tabelas = [
        ("Edições", queryEdicoes),
        ("BulkData", queryBulkdata),
        ("Nomes Alternativos", queryNomesAlternativos),
        ("Relação Nomes-Cartas", queryRelacaoNomeCartas),
        ("Coleção Usuário", queryColecaoUsuario)
    ]
    for nome, query in tabelas:
        sucesso, erro = criarTabelas(conexao, query)
        if sucesso:
            logManager.logMensagemSucesso(f"Tabela {nome} Criada Com Sucesso")
        else:
            logManager.logMensagemFatal(f"Falha Crítica Ao Criar A Tabela '{nome}': {erro}")
            sys.exit("Erro Crítico Na Construção Do Banco De Dados. Confira O LOG")


if __name__ == "__main__":
    configurarPrograma(15)