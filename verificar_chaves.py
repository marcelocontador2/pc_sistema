import re

c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Encontra o bloco de código da função enviarArquivo
inicio = c.find('async function enviarArquivo')
if inicio != -1:
    fim = c.find('\n}', inicio)
    if fim != -1:
        bloco = c[inicio:fim+2]
        # Conta as chaves
        abre = bloco.count('{')
        fecha = bloco.count('}')
        print(f"Chaves abertas: {abre}, Chaves fechadas: {fecha}")
        if abre != fecha:
            print(f"[ERRO] Desbalanceamento! Sobrou {abre - fecha} chave(s).")
        else:
            print("[OK] Chaves balanceadas nesta função.")
    else:
        print("[ERRO] Fim da função não encontrado.")
else:
    print("[ERRO] Função enviarArquivo não encontrada.")
