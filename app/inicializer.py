import os
import sys
from dotenv import load_dotenv

def inicializarArquivos():
    if not os.path.exists(".env"):
        with open(".env", "w") as arquivo:
            arquivo.write("GEMINI_API_KEY=ESCREVA A SUA CHAVE AQUI\n")
            arquivo.write("DB_NAME=colecao.db\n")
            arquivo.write("AI_MODEL=gemini-2.5-flash\n")
        sys.exit("Configure o arquivo .env antes de executar o programa")
    load_dotenv()

if __name__ == "__main__":
    print(os.getenv("GEMINI_API_KEY"))
    inicializarArquivos()
    print(os.getenv("GEMINI_API_KEY"))
