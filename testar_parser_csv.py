import os

upload_dir = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"
arquivo = os.path.join(upload_dir, "COMPARATIVO_RECEITAS_2026_TRIMESTRE_3.csv")

print("=" * 80)
print(f"📄 Analisando: {arquivo}")
print("=" * 80)

if not os.path.exists(arquivo):
    print("❌ Arquivo não encontrado!")
    exit()

# Lê o conteúdo com fallback de encoding (igual ao backend)
try:
    with open(arquivo, "r", encoding="utf-8-sig") as f:
        linhas = f.readlines()
    print("✅ Encoding usado: utf-8-sig")
except UnicodeDecodeError:
    with open(arquivo, "r", encoding="latin-1") as f:
        linhas = f.readlines()
    print("✅ Encoding usado: latin-1")

print(f"Total de linhas: {len(linhas)}")
print()

print("🔍 Primeiras 15 linhas do CSV (bruto):")
print("-" * 80)
for i, linha in enumerate(linhas[:15]):
    print(f"   {i+1:3d}: {repr(linha[:120])}")
print("-" * 80)
print()

# Simula o parser do backend
def parse_valor(s):
    s = s.strip().strip('"').replace(".", "").replace(",", ".").replace("R$", "").strip()
    try:
        return float(s)
    except:
        return 0.0

def parse_pct(s):
    s = s.strip().strip('"').replace("%", "").replace(",", ".").strip()
    try:
        return float(s)
    except:
        return 0.0

grupos_nomes = ["RECEITAS PATRIMONIAIS", "TRANSFERÊNCIAS CORRENTES", "RECEITAS DE SERVIÇOS", "OUTRAS RECEITAS CORRENTES", "RECEITAS DE CAPITAL", "RECEITAS DE CONTRIBUIÇÕES"]

dados = {
    "orcado_total": 0.0,
    "realizado_total": 0.0,
    "percentual_total": 0.0,
    "grupos": [],
    "cores": []
}

print("🧪 Simulando o parser do backend:")
print("-" * 80)

linhas_com_processamento = 0
for i, linha in enumerate(linhas):
    if ";" not in linha:
        continue
    partes_linha = linha.strip().split(";")
    if len(partes_linha) < 4:
        continue

    nome = partes_linha[0].strip().strip('"')
    if not nome:
        continue

    if nome == "RECEITA REALIZADA":
        dados["orcado_total"] = parse_valor(partes_linha[1])
        dados["realizado_total"] = parse_valor(partes_linha[2])
        dados["percentual_total"] = parse_pct(partes_linha[3])
        print(f"   ✅ Linha {i+1}: 'RECEITA REALIZADA' encontrada!")
        print(f"      Orçado:    {dados['orcado_total']}")
        print(f"      Realizado: {dados['realizado_total']}")
        print(f"      %:         {dados['percentual_total']}")
        linhas_com_processamento += 1

    elif nome in grupos_nomes:
        dados["grupos"].append({
            "nome": nome,
            "orcado": parse_valor(partes_linha[1]),
            "realizado": parse_valor(partes_linha[2]),
            "percentual": parse_pct(partes_linha[3])
        })
        print(f"   ✅ Linha {i+1}: Grupo '{nome}' encontrado!")
        linhas_com_processamento += 1

    elif nome.upper().startswith("COREN "):
        dados["cores"].append({
            "nome": nome.replace("COREN ", "").strip(),
            "orcado": parse_valor(partes_linha[1]),
            "realizado": parse_valor(partes_linha[2]),
            "percentual": parse_pct(partes_linha[3])
        })
        print(f"   ✅ Linha {i+1}: Coren '{nome}' encontrado!")
        linhas_com_processamento += 1

print("-" * 80)
print(f"Total de linhas processadas: {linhas_com_processamento}")
print(f"Total de grupos encontrados: {len(dados['grupos'])}")
print(f"Total de cores encontrados: {len(dados['cores'])}")
print()

print("=" * 80)
print("📊 RESULTADO QUE O BACKEND RETORNARIA:")
print("=" * 80)
print(f"   orcado_total:     {dados['orcado_total']}")
print(f"   realizado_total:  {dados['realizado_total']}")
print(f"   percentual_total: {dados['percentual_total']}")
print(f"   grupos:           {len(dados['grupos'])} itens")
for g in dados['grupos']:
    print(f"      - {g['nome']}: orçado={g['orcado']}, realizado={g['realizado']}, %={g['percentual']}")
print(f"   cores:            {len(dados['cores'])} itens")
for c in dados['cores']:
    print(f"      - COREN {c['nome']}: orçado={c['orcado']}, realizado={c['realizado']}, %={c['percentual']}")

print()
if dados['orcado_total'] == 0 and dados['realizado_total'] == 0:
    print("⚠️ PROBLEMA IDENTIFICADO: o parser NÃO encontrou a linha 'RECEITA REALIZADA'.")
    print("   Verifique se o CSV tem essa linha com esse nome EXATO (pode estar com acento, espaço extra ou nome diferente).")
elif not dados['grupos']:
    print("⚠️ PROBLEMA IDENTIFICADO: o parser NÃO encontrou nenhum grupo de receita.")
    print("   Os nomes dos grupos no CSV podem estar diferentes dos esperados pelo backend.")
    print(f"   Nomes esperados: {grupos_nomes}")
else:
    print("✅ O parser está funcionando corretamente. O CSV está no formato esperado.")
    print("   Se a tela ainda mostra vazio, o problema está no FRONTEND (a chamada à API ou a renderização).")
