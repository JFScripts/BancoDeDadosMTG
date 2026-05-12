import os
import zipfile
from datetime import datetime

def _getCaminho():
    dataAtual = datetime.now().strftime("%Y-%m-%d")
    caminho = f"logs/new/Log_{dataAtual}.txt"
    return caminho

def _getTime():
    return datetime.now().strftime("%H:%M:%S")

def _registrarLog(registro):
    caminho = _getCaminho()
    with open(caminho, "a", encoding="utf-8") as arquivo:
            arquivo.write(registro)

def manutencaoLogs():
    caminhoNovos = "logs/new"
    caminhoOld = "logs/old"
    removerLogsNovos(30, caminhoNovos, caminhoOld)
    removerLogsAntigos(180, caminhoOld)

def removerLogsNovos(tempoCompactar, caminhoNovos, caminhoOld):
    logMensagemInfo(f"Tentando fazer a manutenção dos Logs mais recentes")
    try:
        arquivos = [f for f in os.listdir(caminhoNovos) if os.path.isfile(os.path.join(caminhoNovos, f))]
        for arquivo in arquivos:
            if "Log_" in arquivo:
                nomeFormatado = arquivo.replace("Log_", "").replace(".txt", "")
                dataArquivo = datetime.strptime(nomeFormatado, "%Y-%m-%d")
                agora = datetime.now()
                idadeArquivo = (agora - dataArquivo).days
                if idadeArquivo > tempoCompactar:
                    logMensagemInfo(f"Tentando Compactar o Arquivo {arquivo}")
                    try:
                        with zipfile.ZipFile(f"{caminhoOld}/Log_{nomeFormatado}.zip", "w", compression=zipfile.ZIP_DEFLATED) as arquivoZip:
                            arquivoZip.write(f"{caminhoNovos}/Log_{nomeFormatado}.txt", arcname=f"Log_{nomeFormatado}.txt")
                        os.remove(f"{caminhoNovos}/Log_{nomeFormatado}.txt")
                        logMensagemSucesso(f"A compactação foi um sucesso")
                    except Exception as e:
                        logMensagemErro(f"Erro ao tentar compactar o arquivo: {arquivo}")
            else:
                logMensagemInfo(f"Tentando deletar um arquivo que não deveria existir {arquivo}")
                try:
                    os.remove(f"{caminhoNovos}/{arquivo}")
                    logMensagemSucesso(f"O arquivo {arquivo} foi deletado com sucesso")
                except Exception as e:
                    logMensagemErro(f"Erro ao tentar deletar o arquivo {arquivo}")
        logMensagemSucesso("Atualizar os logs novos foram um sucesso")

    except Exception as e:
        logMensagemErro(f"Não foi possivel fazer a manutenção dos logs mais novos: {e}")
                
def removerLogsAntigos(tempoDeletar, caminhoOld):
    logMensagemInfo(f"Tentando fazer a manutenção dos Logs mais antigos")
    try:
        arquivos = [f for f in os.listdir(caminhoOld) if os.path.isfile(os.path.join(caminhoOld, f))]
        for arquivo in arquivos:
            if "Log_" in arquivo:
                nomeFormatado = arquivo.replace("Log_", "").replace(".zip", "")
                dataArquivo = datetime.strptime(nomeFormatado, "%Y-%m-%d")
                agora = datetime.now()
                idadeArquivo = (agora - dataArquivo).days
                if idadeArquivo > tempoDeletar:
                    logMensagemInfo(f"Tentando Apagar o Arquivo {arquivo}")
                    try:
                        os.remove(f"{caminhoOld}/Log_{nomeFormatado}.zip")
                        logMensagemSucesso(f"O arquivo {arquivo} foi deletado com sucesso")
                    except Exception as e:
                        logMensagemErro(f"Erro ao tentar apagar o arquivo: {arquivo}")

            else:
                logMensagemInfo(f"Tentando deletar um arquivo que não deveria existir {arquivo}")
                try:
                    os.remove(f"{caminhoOld}/{arquivo}")
                    logMensagemSucesso(f"O arquivo {arquivo} foi deletado com sucesso")
                except:
                    logMensagemErro(f"Erro ao tentar deletar o arquivo {arquivo}")
        logMensagemSucesso("Atualizar os logs antigos foram um sucesso")
    except Exception as e:
        logMensagemErro(f"Não foi possivel fazer a manutenção dos logs antigos: {e}")

def logMensagemSucesso(mensagem="Isso é uma mensagem de sucesso"):
    mensagemSucesso = f"{_getTime()} | [SUCESSO] -> {mensagem}.\n"
    _registrarLog(mensagemSucesso)

def logMensagemInfo(mensagem="Isso é uma mensagem de informação"):
    mensagemInfo = f"{_getTime()} | [INFO] -> {mensagem}.\n"
    _registrarLog(mensagemInfo)

def logMensagemAviso(mensagem="Isso é uma mensagem de aviso"):
    mensagemAviso = f"{_getTime()} | [AVISO] -> {mensagem}.\n"
    _registrarLog(mensagemAviso)

def logMensagemErro(mensagem="Isso é uma mensagem de erro"):
    mensagemErro = f"{_getTime()} | [ERRO] -> {mensagem}.\n"
    _registrarLog(mensagemErro)
    
def logMensagemFatal(mensagem="Isso é uma mensagem fatal"):
    mensagemFatal = f"{_getTime()} | [FATAL] -> {mensagem}.\n"
    _registrarLog(mensagemFatal)

if __name__ == "__main__":
    manutencaoLogs()