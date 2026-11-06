import re

arq = r"pc_frontend\analise_comparativo_despesas.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Extrai todos os blocos <script>
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)

print(f"Total de blocos <script>: {len(scripts)}\n")

for i, s in enumerate(scripts):
    print(f"--- BLOCO {i+1} ({len(s)} chars) ---")
    # Mostra as primeiras 500 e últimas 500 chars
    if len(s) > 1000:
        print(s[:500])
        print("\n[... CORTADO ...]\n")
        print(s[-500:])
    else:
        print(s)
    print("=" * 60)

# Verifica erros comuns de sintaxe
print("\n=== VERIFICAÇÃO DE SINTAXE ===")
for i, s in enumerate(scripts):
    if 'carregarHistorico' in s:
        # Checa crases desbalanceadas (template literals)
        crases = s.count('`')
        if crases % 2 != 0:
            print(f"[ERRO] Bloco {i+1}: Crases (template literals) desbalanceadas: {crases}")
        else:
            print(f"[OK] Bloco {i+1}: Crases OK ({crases})")
        
        # Checa chaves
        abre = s.count('{')
        fecha = s.count('}')
        if abre != fecha:
            print(f"[ERRO] Bloco {i+1}: Chaves desbalanceadas: {{ {abre} x }} {fecha}")
        else:
            print(f"[OK] Bloco {i+1}: Chaves OK ({abre})")
        
        # Checa parênteses
        abre_p = s.count('(')
        fecha_p = s.count(')')
        if abre_p != fecha_p:
            print(f"[ERRO] Bloco {i+1}: Parênteses desbalanceados: ( {abre_p} x ) {fecha_p}")
        else:
            print(f"[OK] Bloco {i+1}: Parênteses OK ({abre_p})")
        
        # Verifica se a função carregarHistorico está no bloco
        idx_fn = s.find('carregarHistorico')
        print(f"\nTrecho da função (a partir de 'carregarHistorico'):")
        print(s[idx_fn:idx_fn+1500] if idx_fn != -1 else "Não encontrada.")
