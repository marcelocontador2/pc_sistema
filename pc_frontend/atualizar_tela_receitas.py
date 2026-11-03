c = open('analise_comparativo_receitas.html', encoding='utf-8-sig').read()

# 1. Adiciona a seção de resumo (cards) antes da div da tabela
secao_resumo = """
    <!-- RESUMO (CARDS) -->
    <div id="resumo-receitas" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
        <div style="background: #eef4f9; padding: 15px; border-radius: 6px; border-left: 4px solid #0a1c3a;">
            <div style="font-size: 11px; color: #718096; text-transform: uppercase; font-weight: 600;">Receita Realizada</div>
            <div style="font-size: 24px; font-weight: bold; color: #0a1c3a;" id="resumo-realizado">R$ 0,00</div>
            <div style="font-size: 11px; color: #718096;" id="resumo-realizado-anterior">Anterior: R$ 0,00</div>
        </div>
        <div style="background: #eef4f9; padding: 15px; border-radius: 6px; border-left: 4px solid #5b8fc9;">
            <div style="font-size: 11px; color: #718096; text-transform: uppercase; font-weight: 600;">Receita Orçada</div>
            <div style="font-size: 24px; font-weight: bold; color: #0a1c3a;" id="resumo-orcado">R$ 0,00</div>
            <div style="font-size: 11px; color: #718096;" id="resumo-orcado-anterior">Anterior: R$ 0,00</div>
        </div>
        <div style="background: #eef4f9; padding: 15px; border-radius: 6px; border-left: 4px solid #28a745;">
            <div style="font-size: 11px; color: #718096; text-transform: uppercase; font-weight: 600;">Execução Orçamentária</div>
            <div style="font-size: 24px; font-weight: bold; color: #0a1c3a;" id="resumo-execucao">0,00%</div>
            <div style="font-size: 11px; color: #718096;" id="resumo-execucao-delta">—</div>
        </div>
    </div>
"""

if 'id="resumo-receitas"' not in c:
    c = c.replace(
        '<div id="tabela-container">',
        secao_resumo + '\n        <div id="tabela-container">'
    )
    print("[OK] Cards de resumo adicionados!")

# 2. Adiciona o script para preencher os cards e gerar o PDF
script = """
        async function carregarResumo() {
            const ano = document.getElementById('filtro-ano').value;
            const tipo = document.getElementById('filtro-tipo').value;
            const trimestre = document.getElementById('filtro-trimestre').value;
            const periodo = `${ano}-${tipo}-${trimestre}`;
            try {
                const r = await fetch(`/api/comparativo_receitas_v2/${periodo}?_t=${Date.now()}`, { cache: 'no-store' });
                const d = await r.json();
                if (d.erro) return;
                const at = d.atual;
                const an = d.anterior;
                const varReceita = an.realizado_total > 0 ? ((at.realizado_total - an.realizado_total) / an.realizado_total) * 100 : 0;
                const varExec = at.percentual_total - an.percentual_total;
                const fmt = (v) => v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                document.getElementById('resumo-realizado').innerText = 'R$ ' + fmt(at.realizado_total);
                document.getElementById('resumo-realizado-anterior').innerText = 'Anterior: R$ ' + fmt(an.realizado_total);
                document.getElementById('resumo-orcado').innerText = 'R$ ' + fmt(at.orcado_total);
                document.getElementById('resumo-orcado-anterior').innerText = 'Anterior: R$ ' + fmt(an.orcado_total);
                document.getElementById('resumo-execucao').innerText = fmt(at.percentual_total) + '%';
                const deltaEl = document.getElementById('resumo-execucao-delta');
                deltaEl.innerText = (varExec >= 0 ? '+' : '') + fmt(varExec) + ' p.p.';
                deltaEl.style.color = varExec >= 0 ? '#28a745' : '#dc3545';
            } catch (e) { console.error(e); }
        }

        function gerarPDF() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico para gerar o PDF.'); return; }
            const periodo = check.parentElement.querySelector('strong').innerText;
            window.open('/relatorio_comparativo_receitas_v2?periodo_atual=' + encodeURIComponent(periodo), '_blank');
        }
"""

# Adiciona o script no final do último <script>
if 'function carregarResumo' not in c:
    pos = c.rfind('</script>')
    if pos != -1:
        c = c[:pos] + script + "\n" + c[pos:]

# 3. Chama carregarResumo() ao verificar
c = c.replace(
    "dadosAtuais = d;\n                renderizarTabela(d);",
    "dadosAtuais = d;\n                renderizarTabela(d);\n                carregarResumo();"
)

# 4. Atualiza a função gerarPDF existente
c = c.replace(
    "window.open('/relatorio_comparativo_receitas?periodo_atual=' + encodeURIComponent(check.parentElement.querySelector('strong').innerText), '_blank');",
    "window.open('/relatorio_comparativo_receitas_v2?periodo_atual=' + encodeURIComponent(check.parentElement.querySelector('strong').innerText), '_blank');"
)

open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
print("[OK] Tela de Comparativo de Receitas atualizada com resumo e PDF!")
