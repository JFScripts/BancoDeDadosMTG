import sqlite3
import inspect

def criarColecao(dataBase):
    conexao = sqlite3.connect(dataBase)
    cursor = conexao.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS cartas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idScryfall TEXT,
        nome TEXT,
        edicao TEXT,
        qnt INTEGER,
        preco REAL,
        material TEXT,
        cor TEXT,
        imagem TEXT
    )""")
    conexao.commit()
    conexao.close()

def adicionarValorTabela(con, nomeTabela, dictTabela):
    try:
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()

        colunas = ",".join(dictTabela.keys())
        valores = ", ".join(["?"] * len(dictTabela))
        query = f"INSERT INTO {nomeTabela} ({colunas}) VALUES ({valores})"

        cur.execute(query, tuple(dictTabela.values()))
        con.commit()
        return True
    except Exception as e:
        nomeFuncao = inspect.currentframe().f_code.co_name
        print(f"Erro na Função {nomeFuncao}: {e}")
        return False

def lerTabela(con, nomeTabela, filtro=None):
    try:
        con.execute("PRAGMA foreign_keys = ON")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        query = f"SELECT * FROM {nomeTabela}"
        valores = ()
        if filtro:
            listaCondicoes = [f"{i} = ?" for i in filtro.keys()]
            condicao = " AND ".join(listaCondicoes)
            query = query + " WHERE " + condicao
            valores = tuple(filtro.values())
        cur.execute(query, valores)
        resultadoBruto = cur.fetchall()
        listaFinal = [dict(linha) for linha in resultadoBruto]
        return listaFinal
    except Exception as e:
        nomeFuncao = inspect.currentframe().f_code.co_name
        print(f"Erro na Função {nomeFuncao}: {e}")
        return False

def atualizarTabela(con, nomeTabela, dictNDados, idALvo):
    try:
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()
        novosDados = ""
        for key in dictNDados:
            novosDados = novosDados + ", " + key + " = ?"
        novosDados = novosDados[2:] #Não é a melhor abordagem mas da pro gasto
        listaValores = list(dictNDados.values())
        listaValores.append(idALvo)

        query = f"UPDATE {nomeTabela} SET {novosDados} WHERE ID = ?"
        cur.execute(query, listaValores)
        con.commit()
        return True
    except Exception as e:
        nomeFuncao = inspect.currentframe().f_code.co_name
        print(f"Erro na Função {nomeFuncao}: {e}")
        return False

def deletarItemTabela(con, nomeTabela, idALvo):
    try:
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()
        query = f"DELETE FROM {nomeTabela} WHERE ID = ?"
        cur.execute(query, (idALvo, ))
        if cur.rowcount > 0:
            con.commit()
            return True
        else:
            return False
    except Exception as e:
        nomeFuncao = inspect.currentframe().f_code.co_name
        print(f"Erro na Função {nomeFuncao}: {e}")
        return False