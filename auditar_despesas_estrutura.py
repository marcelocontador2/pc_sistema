import re, os

print("=" * 70)
print("AUDITORIA: ESTRUTURA DO CSV DE DESPESAS")
print("=" * 70)

# Procura o CSV de despesas na pasta
pasta = r"pc_storage\uploads_raw"
arquivos = [f for f in os.listdir(pasta) if "DESPESA" in f.upper() and f.endswith(".csv")]

if not arquivos:
    print("[AVISO] Nenhum CSV de despesas encontrado.")
else:
    arquivo = os.path.join(pasta, arquivos[0])
    print(f"Arquivo: {arquivos[0]}\n")
    
    try:
        with open(arquivo, "r", encoding="utf-8-sig") as f:
            linhas = f.readlines()
    except:
        with open(arquivo, "r", encoding="latin-1") as f:
            linhas = f.readlines()
    
    print("--- PRIMEIRAS 15 LINHAS ---")
    for i, linha in enumerate(linhas[:15]):
        print(f"[{i}] {linha.rstrip()[:200]}")
    
    print(f"\nTotal de linhas: {len(linhas)}")
    
    # Conta colunas da primeira linha com ';'
    for linha in linhas:
        if ";" in linha and ("Despesa" in linha or "CREDITO" in linha or "TOTAL" in linha):
            partes = linha.strip().split(";")
            print(f"\n--- ESTRUTURA (linha com {len(partes)} colunas) ---")
            for i, p in enumerate(partes):
                print(f"  Coluna {i}: {p.strip()[:80]}")
            break
    
    # Mostra os grupos contábeis (linhas que têm valor mas não são detalhes)
    print("\n--- POSSÍVEIS GRUPOS CONTÁBEIS ---")
    grupos_sugeridos = ["PESSOAL", "JUROS", "OUTRAS DESPESAS", "INVESTIMENTOS", "INVERSOES", "AMORTIZACAO", "CREDITO DISPONIVEL"]
    for linha in linhas:
        for g in grupos_sugeridos:
            if g in linha.upper() and ";" in linha:
                partes = linha.strip().split(";")
                print(f"  {partes[0].strip()[:60]} -> orcado={partes[1] if len(partes) > 1 else '?'} | empenhado={partes[2] if len(partes) > 2 else '?'}")
                break

print("\n" + "=" * 70)
print("ESTRUTURA DA API (o que o backend já retorna)")
print("=" * 70)

c_back = open(r"pc_backend\main.py", encoding='utf-8-sig').read()

# Verifica o que a API retorna
if "def api_comparativo_despesas_v2" in c_back:
    print("[OK] Função api_comparativo_despesas_v2 existe")
    
    # Procura o return e vê quais campos são retornados
    match = re.search(r'def api_comparativo_despesas_v2.*?return \{.*?\}', c_back, re.DOTALL)
    if match:
        trecho = match.group(0)
        campos = re.findall(r'"(\w+)":', trecho)
        print(f"Campos retornados: {list(set(campos))}")
else:
    print("[FALTA] Função api_comparativo_despesas_v2 NÃO existe")

# Verifica se a função preencherConclusao existe no relatório
rel = open(r"pc_frontend\relatorio_comparativo_despesas.html", encoding='utf-8').read()
if "preencherConclusao" in rel:
    print("[OK] Relatório de despesas tem função preencherConclusao")
else:
    print("[INFO] Relatório de despesas não tem função preencherConclusao (vai precisar)")
