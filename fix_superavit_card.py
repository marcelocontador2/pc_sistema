import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_superavit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Altera o título do card de "Passivo Total" para "Superávit Financeiro"
alvo_titulo = '<h3>Passivo Total</h3>\n            <div class="value" id="dash-passivo">R$ --</div>'
novo_titulo = '<h3>Superávit Financeiro</h3>\n            <div class="value" id="dash-superavit">R$ --</div>'

if alvo_titulo in html:
    html = html.replace(alvo_titulo, novo_titulo)
    print("[OK] Título e ID do card alterados para Superávit Financeiro.")

# 2. Altera o JavaScript para preencher o Superávit Financeiro
alvo_js = """document.getElementById('dash-passivo').innerText = fmt(bp.total_passivo?.atual);"""
novo_js = """// Busca o Superávit Financeiro no BP ou na Análise Financeira
                let superavit = bp.superavit_financeiro?.atual || 0;
                if (!superavit && data.encontrados.analise_financeira_bf) {
                    const bf = data.encontrados.analise_financeira_bf.dados || {};
                    superavit = bf.superavit_financeiro || bf.saldo_seguinte?.atual || 0;
                }
                document.getElementById('dash-superavit').innerText = fmt(superavit);"""

if alvo_js in html:
    html = html.replace(alvo_js, novo_js)
    print("[OK] Script do Superávit Financeiro ajustado.")

# 3. (Opcional) Se a API não tiver o campo, calcula o superávit financeiro como (Ativo Circulante + Realizável LP) - (Passivo Circulante + Passivo Não Circulante)
# Vamos adicionar essa lógica como fallback
alvo_fallback = """document.getElementById('dash-superavit').innerText = fmt(superavit);"""
novo_fallback = """// Fallback: se não encontrou, calcula manualmente
                if (!superavit) {
                    const ac = bp.ativo_circulante?.atual || 0;
                    const rlp = bp.ativo_realizavel?.atual || 0;
                    const pc = bp.passivo_circulante?.atual || 0;
                    const pnc = bp.passivo_nao_circulante?.atual || 0;
                    superavit = (ac + rlp) - (pc + pnc);
                }
                document.getElementById('dash-superavit').innerText = fmt(superavit);"""

if alvo_fallback in html:
    html = html.replace(alvo_fallback, novo_fallback)
    print("[OK] Lógica de fallback adicionada.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html atualizado.")
