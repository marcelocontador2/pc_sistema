import os, glob, shutil

print("Buscando backups que contenham 'Análises Contábeis'...\n")

# Lista todos os backups do index.html
backups = glob.glob(r"pc_frontend\index*.html")

# Filtra apenas os que tem o menu completo
validos = []
for b in backups:
    try:
        with open(b, "r", encoding="utf-8", errors="ignore") as f:
            conteudo = f.read()
            if "Análises Contábeis" in conteudo and "Conferência das Demonstrações" in conteudo:
                validos.append(b)
    except:
        pass

if validos:
    # Pega o mais antigo (para garantir que é o original) ou o mais recente que tenha tudo
    # Vamos pegar o mais recente que esteja válido
    melhor = max(validos, key=os.path.getctime)
    print(f"O melhor backup encontrado é: {melhor}")
    
    shutil.copy2(melhor, r"pc_frontend\index.html")
    print("[OK] Arquivo restaurado! Agora o menu deve estar completo.")
else:
    print("[ERRO] Não encontrei nenhum backup válido com o menu completo.")
    print("Backups encontrados:", backups)
