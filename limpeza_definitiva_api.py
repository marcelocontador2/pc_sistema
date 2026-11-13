import re
import shutil

caminho = "pc_backend/main.py"

with open(caminho, "r", encoding="utf-8") as f:
    content = f.read()

shutil.copy(caminho, caminho + ".bak_limpeza_lixo_api")

# Localiza a definição da função api_comparativo_receitas_v2 (a versão limpa que inserimos)
padrao = r'(@app\.get\("/api/comparativo_receitas_v2/\{periodo\}"\)\s*\ndef\s+api_comparativo_receitas_v2\(periodo:\s*str\):)'
match = re.search(padrao, content)

if not match:
    print("❌ Função não encontrada.")
    exit()

inicio = match.start()

# Encontra a próxima rota/decorator após o início da função
# Vamos procurar a próxima ocorrência de @app.get ou @app.post ou @app.route
proxima_rota = re.search(r'\n@app\.(get|post|put|delete|route)\(', content[inicio + 10:])
if proxima_rota:
    fim = inicio + 10 + proxima_rota.start()
else:
    # Se não achou, vai até o fim do arquivo
    fim = len(content)

# Verifica se o bloco tem parênteses/chaves desbalanceados (lixo)
bloco = content[inicio:fim]
chaves = bloco.count("{") - bloco.count("}")
parenteses = bloco.count("(") - bloco.count(")")

print(f"📊 Bloco da função:")
print(f"   Tamanho: {len(bloco)} caracteres")
print(f"   Chaves desbalanceadas: {chaves}")
print(f"   Parênteses desbalanceados: {parenteses}")

# Substitui o bloco inteiro pela nossa função limpa (sem o lixo do final)
nova_funcao = '''@app.get("/api/comparativo_receitas_v2/{periodo}")
def api_comparativo_receitas_v2(periodo: str):
    import os

    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")

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

    def ler_csv(p):
        if not p:
            return None
        periodo_formatado = p.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"COMPARATIVO_RECEITAS_{periodo_formatado}.csv")

        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f and "COMPARATIVO_RECEITAS" in f:
                    arquivo = os.path.join(upload_dir, f)
                    break

        if not os.path.exists(arquivo):
            return None

        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()

            dados = {
                "orcado_total": 0.0,
                "realizado_total": 0.0,
                "percentual_total": 0.0,
                "grupos": [],
                "cores": []
            }

            grupos_nomes = ["RECEITAS PATRIMONIAIS", "TRANSFERÊNCIAS CORRENTES", "RECEITAS DE SERVIÇOS", "OUTRAS RECEITAS CORRENTES", "RECEITAS DE CAPITAL", "RECEITAS DE CONTRIBUIÇÕES"]

            for linha in linhas:
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

                elif nome in grupos_nomes:
                    dados["grupos"].append({
                        "nome": nome,
                        "orcado": parse_valor(partes_linha[1]),
                        "realizado": parse_valor(partes_linha[2]),
                        "percentual": parse_pct(partes_linha[3])
                    })

                elif nome.upper().startswith("COREN "):
                    dados["cores"].append({
                        "nome": nome.replace("COREN ", "").strip(),
                        "orcado": parse_valor(partes_linha[1]),
                        "realizado": parse_valor(partes_linha[2]),
                        "percentual": parse_pct(partes_linha[3])
                    })

            return dados
        except Exception as e:
            print(f"[ERRO] Falha ao ler CSV {arquivo}: {e}")
            return None

    partes = periodo.split("-")
    if len(partes) == 3:
        ano = int(partes[0])
        tipo = partes[1]
        valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None

    atual = ler_csv(periodo)
    anterior = ler_csv(periodo_anterior)

    if not atual:
        return {"erro": True, "mensagem": f"Dados não encontrados para o período {periodo}."}

    retorno = {
        "orcado_total": atual["orcado_total"],
        "realizado_total": atual["realizado_total"],
        "percentual_total": atual["percentual_total"],
        "grupos": atual["grupos"],
        "cores": atual["cores"]
    }

    if anterior:
        retorno["anterior"] = {
            "orcado_total": anterior["orcado_total"],
            "realizado_total": anterior["realizado_total"],
            "percentual_total": anterior["percentual_total"],
            "grupos": anterior["grupos"]
        }
    else:
        retorno["anterior"] = None

    return retorno

'''

content = content[:inicio] + nova_funcao + content[fim:]

with open(caminho, "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ Função reescrita com sucesso!")

# Verifica a sintaxe
try:
    with open(caminho, "r", encoding="utf-8") as f:
        compile(f.read(), caminho, "exec")
    print("✅ Arquivo main.py está sintaticamente válido!")
except SyntaxError as e:
    print(f"\n❌ Ainda há erro na linha {e.lineno}: {e.msg}")
    print(f"   Texto: {e.text}")
    with open(caminho, "r", encoding="utf-8") as f:
        linhas_atuais = f.readlines()
    inicio_ctx = max(0, e.lineno - 5)
    fim_ctx = min(len(linhas_atuais), e.lineno + 5)
    print("\n📋 Contexto do erro:")
    for i in range(inicio_ctx, fim_ctx):
        marcador = ">>>" if i == e.lineno - 1 else "   "
        print(f"{marcador} {i+1:5d}: {linhas_atuais[i]}", end="")
