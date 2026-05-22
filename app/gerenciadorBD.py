import sqlite3
import inspect

def criarTabelas(conexao, querySQL):
    try:
        conexao.execute("PRAGMA foreign_keys = ON")
        cursor = conexao.cursor()
        cursor.execute(querySQL)
        conexao.commit()
        return True, None
    except Exception as e:
        return False, e

def adicionarValorTabela(con, nomeTabela, dictTabela, autoCommit=True):
    try:
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()

        colunas = ",".join(dictTabela.keys())
        valores = ", ".join(["?"] * len(dictTabela))
        query = f"INSERT OR REPLACE INTO {nomeTabela} ({colunas}) VALUES ({valores})"

        cur.execute(query, tuple(dictTabela.values()))
        if autoCommit:
            con.commit()
        return True
    except Exception as e:
        nomeFuncao = inspect.currentframe().f_code.co_name
        print(f"Erro na Função {nomeFuncao}: {e}")
        return False

def lerTabela(con, nomeTabela, filtro=None, ordem=None):
    try:
        con.execute("PRAGMA foreign_keys = ON")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        query = f"SELECT * FROM {nomeTabela}"
        valores = ()
        if filtro:
            if isinstance(filtro, tuple):
                query += f" WHERE {filtro[0]}"
                valores = filtro[1]
            elif isinstance(filtro, dict):
                listaCondicoes = [f"{i} = ?" for i in filtro.keys()]
                condicao = " AND ".join(listaCondicoes)
                query = query + " WHERE " + condicao
                valores = tuple(filtro.values())

        if ordem:
            query = query + f" ORDER BY {ordem}"
        print(query)
        cur.execute(query, valores)
        resultadoBruto = cur.fetchall()
        listaFinal = [dict(linha) for linha in resultadoBruto]
        return listaFinal
    except Exception as e:
        nomeFuncao = inspect.currentframe().f_code.co_name
        print(f"Erro na Função {nomeFuncao}: {e}")
        return False

def atualizarTabela(con, nomeTabela, dictFiltro, dictNDados=None, dictIncrementos=None):
    if not dictNDados and not dictIncrementos:
        print("Erro: Nenhum dado para atualizar foi passado.")
        return False
        
    if not dictFiltro:
        print("Erro: Nenhum filtro passado. Atualizar o banco sem WHERE é perigoso.")
        return False

    try:
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()
        
        listaCondicoesSet = []
        listaValores = []
        if dictNDados:
            for key, value in dictNDados.items():
                listaCondicoesSet.append(f"{key} = ?")
                listaValores.append(value)
        if dictIncrementos:
            for key, value in dictIncrementos.items():
                listaCondicoesSet.append(f"{key} = {key} + ?")
                listaValores.append(value)

        strSet = ", ".join(listaCondicoesSet)
        
        listaCondicoesWhere = [f"{key} = ?" for key in dictFiltro.keys()]
        strWhere = " AND ".join(listaCondicoesWhere)
        
        listaValores.extend(dictFiltro.values())

        query = f"UPDATE {nomeTabela} SET {strSet} WHERE {strWhere}"
        
        cur.execute(query, listaValores)
        con.commit()
        return True
        
    except Exception as e:
        nomeFuncao = inspect.currentframe().f_code.co_name
        print(f"Erro na Função {nomeFuncao}: {e}")
        return False

def deletarItemTabela(con, nomeTabela, valorAlvo, colunaAlvo="id"):
    try:
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()
        query = f"DELETE FROM {nomeTabela} WHERE {colunaAlvo} = ?"
        cur.execute(query, (valorAlvo, ))
        if cur.rowcount > 0:
            con.commit()
            return True
        else:
            return False
    except Exception as e:
        nomeFuncao = inspect.currentframe().f_code.co_name
        print(f"Erro na Função {nomeFuncao}: {e}")
        return False