import os

caminho_arquivo = "pc_backend/matriz_integridade.py"

if os.path.exists(caminho_arquivo):
    print(f"✅ ARQUIVO ENCONTRADO: {caminho_arquivo}\n")
    print("-" * 60)
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        print(f.read())
    print("-" * 60)
else:
    print(f"❌ Arquivo {caminho_arquivo} não encontrado. Procurando...")
    for root, dirs, files in os.walk("pc_backend"):
        if "matriz_integridade.py" in files:
            caminho_real = os.path.join(root, "matriz_integridade.py")
            print(f"✅ Encontrado em: {caminho_real}\n")
            with open(caminho_real, "r", encoding="utf-8") as f:
                print(f.read())
            break
