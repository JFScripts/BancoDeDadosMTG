# iaManager.py
import google.generativeai as genai

def consultarSinergias(listaDeCartas, CHAVE_API):
    nomesCartas = [carta['nome'] for carta in listaDeCartas]
    nomesUnicos = list(set(nomesCartas))
    genai.configure(api_key=CHAVE_API)
    
    modelo = genai.GenerativeModel('gemini-3-flash-preview')
    
    prompt = f"""
    Aja como um jogador profissional de Magic: The Gathering.
    Eu tenho as seguintes cartas na minha coleção: {nomesUnicos}.
    
    Por favor:
    1. Sugira 1 sinergia ou combo forte usando apenas as cartas que eu já tenho.
    2. Sugira 2 cartas que eu NÃO tenho, mas que seriam compras perfeitas para combar com a minha coleção.
    Seja direto e explique o funcionamento do combo de forma clara.
    """
    
    print("Pensando em estratégias... (Isso pode levar alguns segundos)")
    resposta = modelo.generate_content(prompt)
    
    return resposta.text