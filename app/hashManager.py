import hashlib
import logManager

def gerarHashArquivo(path):
    hasher = hashlib.sha256()
    logManager.logMensagemInfo("Tentando Gerar Um Hash")
    try:
        with open(path, "rb") as arquivo:
            for pedaco in iter(lambda: arquivo.read(4096), b""):
                hasher.update(pedaco)
        logManager.logMensagemSucesso("Hash Gerado Com Sucesso")
        return hasher.hexdigest()
    except FileNotFoundError:
        logManager.logMensagemErro(f"Não Foi Possivel Gerar O Hash. {path} Não Encontrado")
        return None
    except Exception as e:
        logManager.logMensagemErro(f"Não Foi Possível Gerar O Hash: {e}")
        return None

if __name__ == "__main__":
    print(gerarHashArquivo("data/db/edicoes.json"))