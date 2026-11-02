import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# 1. Substitui o botão de salvar por botão de imprimir
c = c.replace(
    '<button class="btn-salvar" onclick="salvarRelatorio()">💾 Salvar Relatório</button>',
    '<button class="btn-salvar" onclick="imprimirRelatorio()">📄 Imprimir / Salvar PDF</button>'
)

# 2. Substitui a função salvarRelatorio por imprimirRelatorio
antigo = '''        function salvarRelatorio() {
            const periodo = new URLSearchParams(window.location.search).get('periodo_atual') || '2026-TRIMESTRE-3';
            fetch('/salvar_relatorio_v2', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    periodo: periodo,
                    texto_total: document.getElementById('conclusao-total').innerHTML,
                    texto_concentracao: document.getElementById('conclusao-concentracao').innerHTML,
                    texto_alertas: document.getElementById('conclusao-alertas').innerHTML,
                    texto_recomendacoes: document.getElementById('conclusao-recomendacoes').innerHTML
                })
            })
            .then(r => r.json())
            .then(res => {
                if (res.ok) {
                    alert('Relatório salvo no banco!');
                    const blob = new Blob([document.documentElement.outerHTML], { type: 'text/html' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'relatorio_' + periodo + '.html';
                    a.click();
                    URL.revokeObjectURL(url);
                } else { alert('Erro ao salvar.'); }
            })
            .catch(e => { console.error(e); alert('Erro de conexão.'); });
        }'''

novo = '''        function imprimirRelatorio() {
            // Esconde o botão e os elementos de interface antes de imprimir
            const btn = document.querySelector('.btn-salvar');
            if (btn) btn.style.display = 'none';
            
            // Chama a janela de impressão (que permite salvar como PDF)
            window.print();
            
            // Restaura o botão após a impressão
            setTimeout(() => {
                if (btn) btn.style.display = 'block';
            }, 500);
        }'''

if antigo in c:
    c = c.replace(antigo, novo)
    print("[OK] Função imprimirRelatorio adicionada!")
else:
    print("[AVISO] Função antiga não encontrada. Tentando regex...")
    c = re.sub(r'function salvarRelatorio\(\) \{.*?\n        \}', novo, c, flags=re.DOTALL)
    print("[OK] Função substituída via regex!")

# 3. Adiciona o CSS @media print para formatar o PDF
css_print = """
        @media print {
            .page {
                page-break-after: always;
                height: auto;
                min-height: 100vh;
                padding: 20px;
            }
            .page:last-child {
                page-break-after: auto;
            }
            .btn-salvar {
                display: none !important;
            }
            body {
                margin: 0;
                padding: 0;
            }
            /* Esconde a barra de rolagem e outros elementos de UI */
            ::-webkit-scrollbar {
                display: none;
            }
        }
"""

# Adiciona o CSS dentro da tag <style>
if '@media print' not in c:
    c = c.replace('</style>', css_print + '</style>')
    print("[OK] CSS @media print adicionado!")

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] relatorio_final.html atualizado!")
