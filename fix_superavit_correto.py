import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_superavit_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Localiza o bloco do script que preenche o Superávit Financeiro
alvo = """// Busca o Superávit Financeiro no BP ou na Análise Financeira
                let superavit = bp.superavit_financeiro?.atual || 0;
                if (!superavit && data.encontrados.analise_financeira_bf) {
                    const bf = data.encontrados.analise_financeira_bf.dados || {};
                    superavit = bf.superavit_financeiro || bf.saldo_seguinte?.atual || 0;
                }
                document.getElementById('dash-superavit').innerText = fmt(superavit);"""

novo = """// Superávit Financeiro vem direto do Balanço Patrimonial
                const superavit = bp.superavit_financeiro?.atual || 0;
                document.getElementById('dash-superavit').innerText = fmt(superavit);"""

if alvo in html:
    html = html.replace(alvo, novo)
    print("[OK] Script do Superávit Financeiro corrigido para ler de bp.superavit_financeiro.")
else:
    # Tenta encontrar o bloco de fallback que adicionamos antes
    alvo_fallback = """// Fallback: se não encontrou, calcula manualmente
                if (!superavit) {
                    const ac = bp.ativo_circulante?.atual || 0;
                    const rlp = bp.ativo_realizavel?.atual || 0;
                    const pc = bp.passivo_circulante?.atual || 0;
                    const pnc = bp.passivo_nao_circulante?.atual || 0;
                    superavit = (ac + rlp) - (pc + pnc);
                }
                document.getElementById('dash-superavit').innerText = fmt(superavit);"""
    if alvo_fallback in html:
        html = html.replace(alvo_fallback, novo)
        print("[OK] Fallback incorreto removido e substituído pelo caminho correto.")
    else:
        print("[AVISO] Bloco do Superávit Financeiro não encontrado. Verifique manualmente.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html atualizado.")
