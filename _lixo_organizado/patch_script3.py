import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# Encontra o início do bloco que inserimos antes
index_inicio = -1
for i in range(8800, len(linhas)):
    if "for chave, tabela in modulos.items():" in linhas[i] and "# [FIX] Busca o resultado_json" in linhas[i+2]:
        index_inicio = i
        break

if index_inicio != -1:
    index_fim = index_inicio
    for i in range(index_inicio, len(linhas)):
        if 'faltando.append({"nome": nomes_amigaveis.get(chave, chave)})' in linhas[i] and i > index_inicio + 10:
            index_fim = i
            break
    
    # Novo bloco ultra-robusto
    novo_bloco_b = '''        for chave, tabela in modulos.items():
            try:
                # [FIX] Tenta buscar resultado_json, se a tabela não tiver essa coluna, tenta dados_json
                try:
                    cursor.execute(f"SELECT id, data_geracao, resultado_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                except Exception:
                    # Se der erro (ex: coluna resultado_json não existe), tenta dados_json
                    try:
                        cursor.execute(f"SELECT id, data_geracao, dados_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                    except Exception:
                        # Se nem dados_json existir, busca só o id e data (para não quebrar a lista)
                        cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                
                row = cursor.fetchone()
                
                if row:
                    item = {
                        "nome": nomes_amigaveis.get(chave, chave),
                        "data_geracao": row[1] if len(row) > 1 else "Disponível",
                        "id": row[0]
                    }
                    # Se a tabela tem a coluna de JSON (índice 2), adiciona aos dados
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
                # Captura erro geral da tabela (ex: tabela não existe)
                faltando.append({"nome": nomes_amigaveis.get(chave, chave)})
'''
    linhas[index_inicio:index_fim+1] = [novo_bloco_b]
    arquivo.write_text("".join(linhas), encoding="utf-8")
    print(f"[OK] Patch 2 REFEITO com sucesso (linha {index_inicio+1}).")
else:
    print("[AVISO] Não encontrei o bloco do Patch 2 para refazer. O arquivo pode ter mudado.")
