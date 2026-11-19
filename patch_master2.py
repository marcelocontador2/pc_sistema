import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)

# ---------------------------------------------------------
# PASSO 1: Corrigir tabelas e nome da Liquidez
# ---------------------------------------------------------
nome_liquidez_correto = "\u00cdndices de Liquidez"
for i, linha in enumerate(linhas):
    if '"panorama": "historico_panorama"' in linha:
        linhas[i] = linha.replace('"panorama": "historico_panorama"', '"panorama": "historico_panorama_resultados"')
    if '"integridade": "historico_integridade_matriz"' in linha:
        linhas[i] = linha.replace('"integridade": "historico_integridade_matriz"', '"integridade": "historico_integridade"')
    if '"dmpl": "historico_analise_dmpl"' in linha:
        linhas[i] = linha.replace('"dmpl": "historico_analise_dmpl"', '"dmpl": "historico_dmpl"')
        
    if "ndices de Liquidez" in linha:
        if '"liquidez":' in linha:
            linhas[i] = '        "liquidez": "' + nome_liquidez_correto + '",\n'
        elif 'nome_interno ==' in linha:
            prefixo = linha.split('==')[0]
            linhas[i] = prefixo + '== "' + nome_liquidez_correto + '":\n'
        elif '("' in linha:
            prefixo = linha.split('("')[0]
            linhas[i] = prefixo + '("' + nome_liquidez_correto + '", "11. ' + nome_liquidez_correto + ' e Estrutura"),\n'

texto = "".join(linhas)

# ---------------------------------------------------------
# PASSO 2: PATCH 3 - DFC (sem acentos na string de saida)
# ---------------------------------------------------------
padrao_dfc = re.compile(
    r'( +)# Apura[^\n]*\n'
    r' +\s*if "caixa" in dados_dfc:\s*\n'
    r'(?: +.*\n)+?'
    r' +\s*html_parts\.append\("</tbody></table>"\)',
    re.MULTILINE
)

novo_dfc = '''                    # [FIX] Apuracao de Caixa
                    grupos_dfc = [
                        ("Operacional", dados_dfc.get("operacional") or {}),
                        ("Investimento", dados_dfc.get("investimento") or {}),
                        ("Financiamento", dados_dfc.get("financiamento") or {}),
                    ]
                    grupos_dfc = [(n, g) for n, g in grupos_dfc if isinstance(g, dict) and g]
                    if grupos_dfc:
                        html_parts.append("<h3>Apuracao de Caixa</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                        for grupo_nome, grupo in grupos_dfc:
                            for k, v in grupo.items():
                                if isinstance(v, dict):
                                    a = v.get("atual", 0)
                                    ant = v.get("anterior", 0)
                                    var = calc_var(a, ant)
                                    rotulo = f"{grupo_nome} - {k.title()}"
                                    html_parts.append(f"<tr><td>{rotulo}</td><td class='text-right'>{fmt_sem_rs(a)}</td><td class='text-right'>{fmt_sem_rs(ant)}</td><td class='text-right'>{pct(var)}</td></tr>")
                                    if abs(var) > 0.01:
                                        direcao = "positiva" if var > 0 else "negativa"
                                        textos.append(f"<li>{rotulo}: variacao {direcao} de {pct(var)} (de {fmt_sem_rs(ant)} para {fmt_sem_rs(a)}).</li>")
                        html_parts.append("</tbody></table>")'''

if padrao_dfc.search(texto):
    texto = padrao_dfc.sub(novo_dfc, texto, count=1)
    print("[OK] Patch 3 (DFC) aplicado.")
else:
    print("[AVISO] Patch 3 (DFC) nao encontrado.")

# ---------------------------------------------------------
# PASSO 3: PATCH 2 - Funcao B (Lista de modulos)
# ---------------------------------------------------------
texto_b = '''        for chave, tabela in modulos.items():
            try:
                # [FIX] Busca o resultado_json
                try:
                    cursor.execute(f"SELECT id, data_geracao, resultado_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                except Exception:
                    try:
                        cursor.execute(f"SELECT id, data_geracao, dados_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                    except Exception:
                        cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                
                row = cursor.fetchone()
                
                if row:
                    item = {
                        "nome": nomes_amigaveis.get(chave, chave),
                        "data_geracao": row[1] if len(row) > 1 else "Disponivel",
                        "id": row[0]
                    }
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
                faltando.append({"nome": nomes_amigaveis.get(chave, chave)})
'''

matches = list(re.finditer(r'( +)for chave, tabela in modulos\.items\(\):\n(?: +.*\n)+? +faltando\.append\(\{"nome": nomes_amigaveis\.get\(chave, chave\)\}\)\n', texto))
if matches:
    ultimo = matches[-1]
    inicio, fim = ultimo.span()
    texto = texto[:inicio] + texto_b + texto[fim:]
    print("[OK] Patch 2 (Funcao B) aplicado.")
else:
    print("[AVISO] Patch 2 (Funcao B) nao encontrado.")

# ---------------------------------------------------------
# PASSO 4: Salvar o arquivo
# ---------------------------------------------------------
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
