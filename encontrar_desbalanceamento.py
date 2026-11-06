import re

arq = r"pc_frontend\analise_comparativo_despesas.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Extrai o bloco <script>
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
s = scripts[0]

# Lista todas as funções e seu status de chaves
print("=== FUNÇÕES E SUAS CHAVES ===\n")

# Encontra todas as funções
funcs = re.finditer(r'(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{', s)
func_positions = [(m.start(), m.group(1)) for m in funcs]
func_positions.append((len(s), "FIM_DO_SCRIPT"))

for i in range(len(func_positions) - 1):
    start, nome = func_positions[i]
    end = func_positions[i+1][0]
    bloco = s[start:end]
    
    abre = bloco.count('{')
    fecha = bloco.count('}')
    
    if abre != fecha:
        print(f"[DESBALANCEADA] {nome}: {{ {abre} x }} {fecha}")
        # Mostra o bloco completo
        print(f"  Bloco (primeiros 500 chars): {bloco[:500].strip()}")
        print(f"  ...")
    else:
        print(f"[OK] {nome}: {{ {abre} x }} {fecha}")

# Verifica se há chaves sobrando fora de funções
print("\n=== PROCURA DE CHAVES SOBRANDO ===")
# Remove todas as funções do texto para ver o que sobra
s_sem_funcs = s
for i in range(len(func_positions) - 2, -1, -1):
    start, nome = func_positions[i]
    end = func_positions[i+1][0] if i+1 < len(func_positions) else len(s)
    s_sem_funcs = s_sem_funcs[:start] + s_sem_funcs[end:]

abre_resto = s_sem_funcs.count('{')
fecha_resto = s_sem_funcs.count('}')
print(f"Chaves fora das funções: {{ {abre_resto} x }} {fecha_resto}")
if abre_resto > fecha_resto:
    print(f"[INFO] Há {abre_resto - fecha_resto} chave(s) '{{' aberta(s) sem fechar no escopo global.")
elif fecha_resto > abre_resto:
    print(f"[INFO] Há {fecha_resto - abre_resto} chave(s) '}}' fechando sem abrir no escopo global.")
