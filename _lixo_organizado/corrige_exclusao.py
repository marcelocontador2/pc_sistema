import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# Encontra a funcao excluir_multiplos_relatorio_consolidado
alvo = -1
for i, l in enumerate(linhas):
    if 'async def excluir_multiplos_relatorio_consolidado(request: Request):' in l:
        alvo = i
        break

if alvo == -1:
    print("[ERRO] Funcao nao encontrada.")
    sys.exit(1)

# O bloco vai do @app.post ate o final do except (encontra a linha em branco dupla)
inicio = alvo - 1  # a linha do @app.post
fim = alvo
for i in range(alvo, len(linhas)):
    if 'return {"erro": True, "mensagem": str(e)}' in linhas[i]:
        fim = i + 1
        break

print(f"[INFO] Substituindo linhas {inicio+1} a {fim}")

novo = '''@app.post("/excluir_multiplos_relatorio_consolidado")
async def excluir_multiplos_relatorio_consolidado(request: Request):
    import psycopg2
    from pc_backend.app.config import PG_CONFIG
    try:
        dados = await request.json()
        ids = [int(i) for i in dados.get("ids", []) if str(i).isdigit()]
        if not ids:
            return {"erro": True, "mensagem": "Nenhum ID valido"}
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(f"DELETE FROM historico_relatorio_consolidado WHERE id IN ({placeholders})", ids)
        rowcount = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return {"ok": True, "mensagem": f"{rowcount} itens excluidos"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''

linhas[inicio:fim] = [novo]
arquivo.write_text("".join(linhas), encoding="utf-8")
print("[OK] Rota de exclusao multipla corrigida (SQLite -> PostgreSQL).")
