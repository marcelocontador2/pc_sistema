import re

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Encontra todos os blocos <script>...</script>
scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', s, re.DOTALL | re.IGNORECASE)

print(f"Total de blocos <script> encontrados: {len(scripts)}")

for i, script in enumerate(scripts):
    print(f"\n=== SCRIPT {i+1} ===")
    # Conta chaves
    abre = script.count('{')
    fecha = script.count('}')
    print(f"Chaves abertas: {abre}, Chaves fechadas: {fecha}")
    if abre != fecha:
        print("-> ERRO: Numero de chaves desbalanceado!")
        # Mostra o final do script para ver onde esta o problema
        print("Ultimos 500 caracteres do script:")
        print(script[-500:])
    else:
        print("-> Chaves balanceadas.")
