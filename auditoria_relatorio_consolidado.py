import re

caminho_main = "pc_backend/main.py"
with open(caminho_main, "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("🔍 AUDITORIA DO RELATÓRIO CONSOLIDADO (ONDE ESTÃO OS MÓDULOS):\n")

# Busca por termos que remetem ao relatório consolidado
for i, linha in enumerate(linhas):
    if "consolidado" in linha.lower() and ("def " in linha or "@app." in linha):
        print(f"Linha {i+1}: {linha.strip()}")
        # Mostra as próximas 30 linhas da função para entender o que ela checa
        for j in range(i+1, min(i+30, len(linhas))):
            if "def " in linhas[j] and j > i+1:
                break
            print(f"   {j+1}: {linhas[j].rstrip()}")
        print("-" * 60)

# Busca por consultas que citam os módulos que faltam
print("\n🔍 BUSCANDO REFERÊNCIAS AOS MÓDULOS FALTANTES:\n")
termos = ["comparativo_receitas", "comparativo_despesas", "centro_custos"]
for termo in termos:
    print(f"➔ Termo: {termo}")
    for i, linha in enumerate(linhas):
        if termo in linha.lower() and ("SELECT" in linha or "FROM " in linha or "def " in linha or "@app." in linha):
            print(f"   Linha {i+1}: {linha.strip()}")
    print("-" * 60)
