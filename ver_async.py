c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

# Verifica se a funcao enviarArquivo esta com async
if "async function enviarArquivo" in c:
    print("[OK] A funcao enviarArquivo esta com 'async'.")
else:
    print("[ERRO] A funcao enviarArquivo NAO esta com 'async'.")
    # Mostra o trecho
    idx = c.find("function enviarArquivo")
    if idx != -1:
        print("Trecho atual:")
        print(c[idx:idx+100])
