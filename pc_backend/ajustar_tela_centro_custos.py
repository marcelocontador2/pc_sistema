c = open('../pc_frontend/analise_centro_custos.html', encoding='utf-8-sig').read()

# 1. Adiciona o botão "Gerar Relatório" na toolbar
if "Gerar Relatório" not in c:
    c = c.replace(
        '<button class="btn btn-excluir" onclick="excluirSelecionado()">Excluir Selecionado</button>',
        '<button class="btn btn-excluir" onclick="excluirSelecionado()">Excluir Selecionado</button>\n            <button class="btn btn-pdf" onclick="window.open(\'/relatorio_centro_custos\', \'_blank\')" style="background-color: #6f42c1; color: white;">📄 Gerar Relatório</button>'
    )
    print("[OK] Botão 'Gerar Relatório' adicionado à toolbar!")

# 2. Adiciona a seção de resumo (cards) antes da tabela
if "resumo-centro-custos" not in c:
    secao_resumo = """
    <!-- RESUMO (CARDS) -->
    <div id="resumo-centro-custos" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
        <div style="background: #eef4f9; padding: 15px; border-radius: 6px; border-left: 4px solid #0a1c3a;">
            <div style="font-size: 11px; color: #718096; text-transform: uppercase; font-weight: 600;">Total Atual</div>
            <div style="font-size: 20px; font-weight: bold; color: #0a1c3a;" id="resumo-total-atual">R$ 0,00</div>
        </div>
        <div style="background: #eef4f9; padding: 15px; border-radius: 6px; border-left: 4px solid #5b8fc9;">
            <div style="font-size: 11px; color: #718096; text-transform: uppercase; font-weight: 600;">Total Anterior</div>
            <div style="font-size: 20px; font-weight: bold; color: #0a1c3a;" id="resumo-total-anterior">R$ 0,00</div>
        </div>
        <div style="background: #eef4f9; padding: 15px; border-radius: 6px; border-left: 4px solid #28a745;">
            <div style="font-size: 11px; color: #718096; text-transform: uppercase; font-weight: 600;">Variação Global</div>
            <div style="font-size: 20px; font-weight: bold; color: #0a1c3a;" id="resumo-variacao">0,00%</div>
        </div>
    </div>
    """
    # Insere o resumo antes do container da tabela
    c = c.replace(
        '<div id="tabela-container">',
        secao_resumo + '\n        <div id="tabela-container">'
    )
    print("[OK] Seção de resumo (cards) adicionada à tela!")

# 3. Adiciona o JavaScript para preencher os cards com os dados da API
if "carregarResumo" not in c:
    script_resumo = """
        async function carregarResumo() {
            try {
                const r = await fetch('/api/relatorio_centro_custos?periodo_atual=2026-TRIMESTRE-3&periodo_anterior=2025-TRIMESTRE-3&_t=' + Date.now(), { cache: 'no-store' });
                const d = await r.json();
                
                const fmt = (v) => v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                
                document.getElementById('resumo-total-atual').innerText = 'R$ ' + fmt(d.atual.total);
                document.getElementById('resumo-total-anterior').innerText = d.anterior ? 'R$ ' + fmt(d.anterior.total) : 'N/A';
                
                const variacaoEl = document.getElementById('resumo-variacao');
                if (d.anterior && d.anterior.total > 0) {
                    variacaoEl.innerText = (d.variacao_pct >= 0 ? '▲ ' : '▼ ') + fmt(Math.abs(d.variacao_pct)) + '%';
                    variacaoEl.style.color = d.variacao_pct >= 0 ? '#dc3545' : '#28a745';
                } else {
                    variacaoEl.innerText = 'N/A';
                    variacaoEl.style.color = '#718096';
                }
            } catch (e) {
                console.error('Erro ao carregar resumo:', e);
            }
        }
        
        // Chama a função ao carregar a página
        document.addEventListener('DOMContentLoaded', function() {
            carregarResumo();
        });
    """
    pos = c.rfind("</script>")
    if pos != -1:
        c = c[:pos] + script_resumo + "\n" + c[pos:]
        print("[OK] Script de carregamento do resumo adicionado!")

open('../pc_frontend/analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Tela de Análise por Centro de Custos atualizada!")
