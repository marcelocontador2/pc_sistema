import re
import shutil
import sys
from pathlib import Path

# Configura encoding do terminal
sys.stdout.reconfigure(encoding="utf-8")

arquivo = Path("pc_backend/main_legado.py")
backup = Path("pc_backend/main_legado.py.bak")

if not arquivo.exists():
    print("[ERRO] Arquivo não encontrado:", arquivo)
    sys.exit(1)

# 1. Faz backup
shutil.copy2(arquivo, backup)
print(f"[OK] Backup criado em: {backup}")

# 2. Lê o arquivo como utf-8 (com errors='replace' para não quebrar se houver byte sujo)
texto = arquivo.read_text(encoding="utf-8", errors="replace")

# --- PATCH 1: Corrigir nome 'Índices de Liquidez' ---
# Remove caracteres de controle invisíveis (soft hyphen, etc) e normaliza
linhas = texto.splitlines(keepends=True)
linhas_corrigidas = []
count_patch1 = 0

for linha in linhas:
    if "ndices de Liquidez" in linha:
        # Remove \xad, \x8d e outros caracteres invisíveis quebrando a string
        linha_limpa = re.sub(r'[^\x20-\x7E\u00C0-\u017F\u4e00-\u9fff]', '', linha)
        # Substitui a parte estragada por 'Índices'
        if "índices de Liquidez" in linha_limpa:
            linha_limpa = linha_limpa.replace("índices de Liquidez", "Índices de Liquidez")
        elif "índices de Liquidez" in linha_limpa:
            linha_limpa = linha_limpa.replace("índices de Liquidez", "Índices de Liquidez")
        elif "indices de Liquidez" in linha_limpa:
            linha_limpa = linha_limpa.replace("indices de Liquidez", "Índices de Liquidez")
        else:
            # Fallback: troca tudo até "ndices de Liquidez" por "Índices de Liquidez"
            linha_limpa = re.sub(r'[^"]*ndices de Liquidez', 'Índices de Liquidez', linha_limpa, count=1)
        
        linhas_corrigidas.append(linha_limpa)
        count_patch1 += 1
    else:
        linhas_corrigidas.append(linha)

texto = "".join(linhas_corrigidas)
print(f"[OK] Patch 1: {count_patch1} linha(s) com 'Índices de Liquidez' corrigida(s).")


# --- PATCH 2: Função B (linha ~8866) ---
antigo_patch2 = '''        for chave, tabela in modulos.items():
            try:
                # Verifica se a tabela existe e tem dados para o periodo
                if chave == "analise_financeira_bf":
                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                elif chave == "dmpl":
                    # O DMPL pode ter o periodo em formato ligeiramente diferente, tenta LIKE
                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                else:
                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))
                row = cursor.fetchone()
                
                if row:
                    encontrados.append({
                        "nome": nomes_amigaveis.get(chave, chave),
                        "data_geracao": row[1] if len(row) > 1 else "Disponível",
                        "id": row[0]
                    })
                else:
                    faltando.append({
                        "nome": nomes_amigaveis.get(chave, chave)
                    })
            except Exception as e:
                faltando.append({"nome": nomes_amigaveis.get(chave, chave)})'''

novo_patch2 = '''        for chave, tabela in modulos.items():
            try:
                # [FIX] Busca o resultado_json e usa LIKE para não falhar por causa de espaços
                try:
                    cursor.execute(f"SELECT id, data_geracao, resultado_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                except Exception:
                    cursor.execute(f"SELECT id, data_geracao, dados_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                
                row = cursor.fetchone()
                
                if row:
                    item = {
                        "nome": nomes_amigaveis.get(chave, chave),
                        "data_geracao": row[1] if len(row) > 1 else "Disponível",
                        "id": row[0]
                    }
                    # [FIX] Adiciona os dados do relatório na resposta
                    if len(row) > 2 and row[2] is not None:
                        try:
                            item["dados"] = json.loads(row[2]) if isinstance(row[2], str) else row[2]
                        except Exception:
                            item["dados"] = row[2]
                    
                    encontrados.append(item)
                else:
                    faltando.append({
                        "nome": nomes_amigaveis.get(chave, chave)
                    })
            except Exception as e:
                faltando.append({"nome": nomes_amigaveis.get(chave, chave)})'''

if antigo_patch2 in texto:
    texto = texto.replace(antigo_patch2, novo_patch2, 1)
    print("[OK] Patch 2 aplicado na Função B.")
else:
    print("[AVISO] Bloco do Patch 2 não encontrado (pode já ter sido alterado).")


# --- PATCH 3: DFC Apuração de Caixa (linha ~7061) ---
# O bloco original tem "caixa", então vamos achar e substituir
padrao_patch3 = re.compile(
    r'( +)# Apuração de Caixa\s*\n'
    r' +\s*if "caixa" in dados_dfc:\s*\n'
    r' +\s*html_parts\.append\("<h3>Apuração de Caixa</h3>.*?)\n'
    r' +\s*html_parts\.append\("</tbody></table>"\)',
    re.DOTALL
)

novo_patch3 = r'''\1# [FIX] Apuração de Caixa (o JSON tem 'operacional', 'investimento', 'financiamento', não 'caixa')
\1grupos_dfc = [
\1    ("Operacional", dados_dfc.get("operacional") or {}),
\1    ("Investimento", dados_dfc.get("investimento") or {}),
\1    ("Financiamento", dados_dfc.get("financiamento") or {}),
\1]
\1grupos_dfc = [(n, g) for n, g in grupos_dfc if isinstance(g, dict) and g]
\1if grupos_dfc:
\1    html_parts.append("<h3>Apuração de Caixa</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
\1    for grupo_nome, grupo in grupos_dfc:
\1        for k, v in grupo.items():
\1            if isinstance(v, dict):
\1                a = v.get("atual", 0)
\1                ant = v.get("anterior", 0)
\1                var = calc_var(a, ant)
\1                rotulo = f"{grupo_nome} - {k.title()}"
\1                html_parts.append(f"<tr><td>{rotulo}</td><td class='text-right'>{fmt_sem_rs(a)}</td><td class='text-right'>{fmt_sem_rs(ant)}</td><td class='text-right'>{pct(var)}</td></tr>")
\1                if abs(var) > 0.01:
\1                    direcao = "positiva" if var > 0 else "negativa"
\1                    textos.append(f"<li>{rotulo}: variação {direcao} de {pct(var)} (de {fmt_sem_rs(ant)} para {fmt_sem_rs(a)}).</li>")
\1    html_parts.append("</tbody></table>")'''

if padrao_patch3.search(texto):
    texto = padrao_patch3.sub(novo_patch3, texto, count=1)
    print("[OK] Patch 3 aplicado no bloco do DFC.")
else:
    print("[AVISO] Bloco do Patch 3 não encontrado (pode já ter sido alterado ou o texto está diferente).")


# 3. Grava o arquivo corrigido em UTF-8
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo main_legado.py salvo em UTF-8.")
