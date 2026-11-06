import urllib.request, json, os

# Busca o histórico ID 2 para testar a leitura
url = "http://127.0.0.1:9994/historico_comparativo_despesas/2"
try:
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read().decode())
    print("[OK] Histórico acessível")
except Exception as e:
    print(f"[ERRO] {e}")
    exit(1)

# Testa a correção de encoding
def corrigir(txt):
    try:
        return txt.encode("latin-1", "ignore").decode("utf-8", "ignore")
    except:
        return txt

# Testa com exemplo
exemplo = "BalanÃ§o OrÃ§amentÃ¡rio"
print(f"Antes:  {exemplo}")
print(f"Depois: {corrigir(exemplo)}")
