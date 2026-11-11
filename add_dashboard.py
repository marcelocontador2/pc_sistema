import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. CSS para os novos cards
css_dashboard = """
<style>
    .dashboard-welcome { padding: 30px; background: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; text-align: center; }
    .dashboard-welcome h1 { color: #003366; margin-top: 0; }
    .dashboard-welcome p { color: #666; font-size: 16px; }
    .dashboard-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .dash-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 4px solid #0056b3; }
    .dash-card h3 { margin: 0 0 10px 0; font-size: 14px; color: #666; }
    .dash-card .value { font-size: 24px; font-weight: bold; color: #003366; }
    .shortcuts { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
    .shortcut-btn { display: flex; align-items: center; justify-content: center; padding: 15px; background: #003366; color: #fff; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 14px; transition: 0.2s; text-align: center; }
    .shortcut-btn:hover { background: #0056b3; transform: translateY(-2px); }
</style>
"""

if 'dashboard-welcome' not in html:
    html = html.replace('</head>', css_dashboard + '</head>')

# 2. HTML do Dashboard (inserido após o header)
dashboard_html = """
<div id="tela-dashboard-welcome" class="content-area active" style="padding: 30px;">
    <div class="dashboard-welcome">
        <h1>Bem-vindo ao SGPC</h1>
        <p>Sistema de Gestão de Prestação de Contas - COFEN</p>
    </div>
    
    <div class="dashboard-cards">
        <div class="dash-card">
            <h3>Ativo Total</h3>
            <div class="value" id="dash-ativo">R$ --</div>
        </div>
        <div class="dash-card">
            <h3>Passivo Total</h3>
            <div class="value" id="dash-passivo">R$ --</div>
        </div>
        <div class="dash-card">
            <h3>Receita Realizada</h3>
            <div class="value" id="dash-receita">R$ --</div>
        </div>
        <div class="dash-card">
            <h3>Despesa Empenhada</h3>
            <div class="value" id="dash-despesa">R$ --</div>
        </div>
    </div>
    
    <h3 style="color: #003366; margin-bottom: 15px;">Atalhos Rápidos</h3>
    <div class="shortcuts">
        <a href="/analise_bp" class="shortcut-btn">📊 Análise BP</a>
        <a href="/analise_dfc" class="shortcut-btn">💵 Análise DFC</a>
        <a href="/liquidez" class="shortcut-btn">📈 Índices de Liquidez</a>
        <a href="/relatorio_consolidado" class="shortcut-btn">📄 Relatório Consolidado</a>
        <a href="/notas_explicativas" class="shortcut-btn">📝 Notas Explicativas</a>
        <a href="/analise_custo_pessoal" class="shortcut-btn">👥 Custo de Pessoal</a>
    </div>
</div>
"""

# Insere o dashboard após o <main class="main-content">
if 'tela-dashboard-welcome' not in html:
    html = html.replace('<div id="tela-dashboard"', dashboard_html + '\n<div id="tela-dashboard"')
    # Remove a tela-dashboard antiga
    html = re.sub(r'<div id="tela-dashboard" class="content-area active">.*?</div>', '', html, flags=re.DOTALL)

# 3. Script para preencher os cards com os dados do banco
script_dados = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    fetch('/api/relatorio_consolidado/2026-TRIMESTRE-3')
        .then(r => r.json())
        .then(data => {
            if (data.encontrados && data.encontrados.analise_bp) {
                const bp = data.encontrados.analise_bp.dados.dados;
                const orc = data.encontrados.analise_orcamentaria ? data.encontrados.analise_orcamentaria.dados.atual : {};
                
                const fmt = (v) => v ? 'R$ ' + Number(v).toLocaleString('pt-BR', {minimumFractionDigits: 2}) : 'R$ --';
                
                document.getElementById('dash-ativo').innerText = fmt(bp.total_ativo?.atual);
                document.getElementById('dash-passivo').innerText = fmt(bp.total_passivo?.atual);
                document.getElementById('dash-receita').innerText = fmt(orc.receita_realizada);
                document.getElementById('dash-despesa').innerText = fmt(orc.despesa_empenhada);
            }
        })
        .catch(err => console.log('Dashboard:', err));
});
</script>
"""

if 'dash-ativo' not in html:
    html = html.replace('</body>', script_dados + '</body>')

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Dashboard de boas-vindas adicionado.")
