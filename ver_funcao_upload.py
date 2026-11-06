c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

# Procura a funcao enviarArquivo
idx = c.find("function enviarArquivo")
if idx == -1:
    print("[ERRO] Funcao enviarArquivo nao encontrada.")
else:
    fim = c.find("}", idx) + 1
    # Procura o final da funcao (proximo "function" ou fim do script)
    proximo = c.find("function ", idx + 20)
    if proximo != -1 and proximo < fim + 2000:
        fim = proximo
    else:
        fim = idx + 2000
    
    print("=" * 70)
    print("FUNCAO enviarArquivo")
    print("=" * 70)
    print(c[idx:fim])
