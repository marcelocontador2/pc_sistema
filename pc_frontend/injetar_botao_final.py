c = open('relatorio_centro_custos_v2.html', encoding='utf-8-sig').read()

# 1. Remove qualquer botão antigo (se existir)
import re
c = re.sub(r'<div style="padding: 20px 40px; text-align: right;">.*?</div>', '', c, flags=re.DOTALL)

# 2. Insere o botão antes do fechamento do </body>
if 'Salvar Relatório' not in c:
    c = c.replace(
        '</body>',
        '''    <div style="padding: 20px 40px; text-align: right;">
        <button onclick="salvarRelatorio()" style="padding: 12px 24px; background: #0a1c3a; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold;">💾 Salvar Relatório</button>
    </div>
</body>'''
    )
    print("[OK] Botão inserido!")

# 3. Adiciona a função salvarRelatorio no final do último <script>
if 'function salvarRelatorio' not in c:
    script = """
        function salvarRelatorio() {
            const params = new URLSearchParams(window.location.search);
            const periodo = params.get('periodo_atual') || '2026-TRIMESTRE-3';
            
            const textoTotal = document.getElementById('conclusao-total') ? document.getElementById('conclusao-total').innerHTML : '';
            const textoConcentracao = document.getElementById('conclusao-concentracao') ? document.getElementById('conclusao-concentracao').innerHTML : '';
            const textoAlertas = document.getElementById('conclusao-alertas') ? document.getElementById('conclusao-alertas').innerHTML : '';
            const textoRecomendacoes = document.getElementById('conclusao-recomendacoes') ? document.getElementById('conclusao-recomendacoes').innerHTML : '';
            
            fetch('/salvar_relatorio_v2', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    periodo: periodo,
                    texto_total: textoTotal,
                    texto_concentracao: textoConcentracao,
                    texto_alertas: textoAlertas,
                    texto_recomendacoes: textoRecomendacoes
                })
            })
            .then(r => r.json())
            .then(res => {
                if (res.ok) {
                    alert('Relatório salvo com sucesso no banco de dados!');
                    // Gera o download do HTML
                    const blob = new Blob([document.documentElement.outerHTML], { type: 'text/html' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'relatorio_centro_custos_' + periodo + '.html';
                    a.click();
                    URL.revokeObjectURL(url);
                } else {
                    alert('Erro ao salvar: ' + (res.mensagem || 'Falha desconhecida'));
                }
            })
            .catch(e => {
                console.error(e);
                alert('Erro ao salvar no servidor.');
            });
        }
    """
    # Adiciona antes do último </script>
    pos = c.rfind('</script>')
    if pos != -1:
        c = c[:pos] + script + "\n" + c[pos:]
        print("[OK] Função salvarRelatorio inserida!")

open('relatorio_centro_custos_v2.html', 'w', encoding='utf-8').write(c)
print("[OK] HTML atualizado!")
