import os
import json
from google import genai

def consultarSinergias(listaDeCartas, CHAVE_API):
    try:
        nomesCartas = [carta['nome'] for carta in listaDeCartas]
        nomesUnicos = sorted(list(set(nomesCartas)))
        arquivoCache = "arquivoCache.json"
        if not nomesUnicos:
            print("A Lista Está Vazia, Adicione cartas para utilizar a analise por IA")
            return
        
        if os.path.exists(arquivoCache):
            with open(arquivoCache, "r", encoding="utf-8") as arquivo:
                dadosCache = json.load(arquivo)
                if dadosCache.get("colecao") == nomesUnicos:
                    print(dadosCache.get("resposta"))
                    return
        
        client = genai.Client(api_key=CHAVE_API)
        prompt = f"""
        Aja como um jogador profissional de Magic: The Gathering.
        Eu tenho as seguintes cartas na minha coleção: {nomesUnicos}.
        
        Por favor:
        1. Sugira 1 sinergia ou combo forte usando apenas as cartas que eu já tenho.
        2. Sugira 2 cartas que eu NÃO tenho, mas que seriam compras perfeitas para combar com a minha coleção.
        Seja direto e explique o funcionamento do combo de forma clara seguindo essas regras

        Regras:
        1. Mantenha as suas respostar curtas e concisas no maximo 3 parágrafos.
        2. Não use introduções ou apresentações
        3. A resposta será exposta em um terminal então não use simbolos de .md
        4. Explique a sinergia passoa a passo por exemplo:
        'Sinergia 1 - Carta A + Carta B + Carta C....:
        - Passo 1: Jogue a Carta A fazendo tal ação
        - Passo 2: Quando condição X acontecer utilize a Carta B
        - Passo 3: Então utilize a Carta C'

        """
        print("Pensando em estratégias... (Isso pode levar alguns segundos)")
        
        respostaStream = client.models.generate_content_stream(
            model=os.getenv("AI_MODEL"),
            contents=prompt
        )
        
        respostaCompleta = ""
        print("\n")
        for pedaco in respostaStream:
            print(pedaco.text, end="", flush=True)
            respostaCompleta += pedaco.text
        print("\n")

        with open(arquivoCache, "w", encoding="utf-8") as arquivo:
            print("Arquivo Criado")
            novoCache = {"colecao":nomesUnicos, "resposta": respostaCompleta}
            json.dump(novoCache, arquivo, ensure_ascii=False, indent=4)
        
    except Exception as e:
        return f"Não foi possível utilizar a IA devido a {e}"