c = open('../pc_frontend/analise_centro_custos.html', encoding='utf-8-sig').read()

# 1. Remove os 3 cards antigos e adiciona um único card com o Total Atual
import re
padrao_cards = r'<!-- RESUMO \(CARDS\) -->.*?</div>\s*</div>\s*</div>'
novo_card = """
    <!-- RESUMO (CARD ÚNICO) -->
    <div id="resumo-centro-custos" style="display: grid; grid-template-columns: 1fr; gap: 15px; margin-bottom: 20px;">
        <div style="background: #eef4f9; padding: 15px; border-radius: 6px; border-left: 4px solid #0a1c3a;">
            <div style="font-size: 11px; color: #718096; text-transform: uppercase; font-weight: 600;">Total Executado (Período Atual)</div>
            <div style="font-size: 24px; font-weight: bold; color: #0a1c3a;" id="resumo-total-atual">R$ 0,00</div>
        </div>
    </div>
"""
c = re.sub(padrao_cards, novo_card, c, flags=re.DOTALL)

# 2. Remove o botão antigo "Gerar Relatório" e adiciona os dois novos
c = c.replace(
    '<button class="btn btn-pdf" onclick="window.open(\'/relatorio_centro_custos\', \'_blank\')" style="background-color: #6f42c1; color: white;">📄 Gerar Relatório</button>',
    '<button class="btn btn-pdf" onclick="window.open(\'/relatorio_centro_custos\', \'_blank\')" style="background-color: #6f42c1; color: white; margin-right: 10px;">📄 Gerar Resumo</button>\n            <button class="btn btn-pdf" onclick="window.open(\'/relatorio_centro_custos_completo\', \'_blank\')" style="background-color: #17a2b8; color: white;">📊 Gerar Completo</button>'
)

# 3. Atualiza o JavaScript para preencher apenas o Total Atual
script_antigo = r'async function carregarResumo\(\) \{.*?document\.addEventListener\(\'DOMContentLoaded\'.*?\}\);\s*\}'
novo_script = """
        async function carregarResumo() {
            try {
                const r = await fetch('/api/relatorio_centro_custos?periodo_atual=2026-TRIMESTRE-3&periodo_anterior=2025-TRIMESTRE-3&_t=' + Date.now(), { cache: 'no-store' });
                const d = await r.json();
                
                const fmt = (v) => v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                
                document.getElementById('resumo-total-atual').innerText = 'R$ ' + fmt(d.atual.total);
            } catch (e) {
                console.error('Erro ao carregar resumo:', e);
            }
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            carregarResumo();
        });
"""
c = re.sub(script_antigo, novo_script, c, flags=re.DOTALL)

open('../pc_frontend/analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Tela de análise ajustada (card único e dois botões de relatório)!")
