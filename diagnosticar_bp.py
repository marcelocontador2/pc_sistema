import re
import json

arq_template = r"pc_frontend\relatorio_consolidado_template.html"
arq_saida = "diagnostico_bp.txt"

with open(arq_template, "r", encoding="utf-8") as f:
    html = f.read()

with open(arq_saida, "w", encoding="utf-8") as out:
    out.write("=== 1. CÓDIGO ATUAL DA SEÇÃO 2 NO TEMPLATE ===\n")
    # Pega o bloco da Seção 2
    padrao = re.compile(r"(// ===== 2\. ANÁLISE BP =====.*?)(?=\n// ===== 3\.)", re.DOTALL)
    m = padrao.search(html)
    if m:
        out.write(m.group(1) + "\n\n")
    else:
        out.write("Bloco da Seção 2 não encontrado no template.\n\n")

    out.write("=== 2. TENTATIVA DE LER O JSON DO BACKEND ===\n")
    # Tenta achar o arquivo JSON que o backend gera para alimentar o template
    # Geralmente é algo como dados.json, relatorio.json, ou está embutido no HTML.
    # Vamos procurar no HTML a declaração 'const D = '
    match_json = re.search(r"const D = (\{.*?\});", html, re.DOTALL)
    if match_json:
        try:
            # Tenta formatar o JSON bonitinho para ler
            dados = json.loads(match_json.group(1))
            out.write("Chaves principais do JSON D:\n")
            out.write(json.dumps(list(dados.keys()), indent=2) + "\n\n")
            
            if "analise_bp" in dados:
                out.write("Estrutura de 'analise_bp':\n")
                out.write(json.dumps(dados["analise_bp"], indent=2)[:2000] + "\n\n") # Limita a 2000 caracteres para não ficar gigante
            elif "balanco_patrimonial" in dados:
                 out.write("Estrutura de 'balanco_patrimonial':\n")
                 out.write(json.dumps(dados["balanco_patrimonial"], indent=2)[:2000] + "\n\n")
            else:
                out.write("Não achei 'analise_bp' nem 'balanco_patrimonial' no JSON. Mostrando as primeiras chaves.\n")
        except Exception as e:
            out.write("Erro ao ler o JSON embutido: " + str(e) + "\n")
    else:
        out.write("Não encontrei a declaração 'const D = ...' no template.\n")

print("[OK] Diagnóstico gerado no arquivo diagnostico_bp.txt")
