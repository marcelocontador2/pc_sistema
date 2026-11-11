p = 'pc_frontend/notas_explicativas.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# Função que intercepta o clique do botão Salvar da tela antiga
js_intercept = '''
<script>
    // Intercepta o salvamento. Se estiver na aba MCASP, salva no historico MCASP.
    const originalSalvar = window.salvarNotas; // Guarda a funcao original se ela existir
    window.salvarNotas = async function() {
        const telaMCASP = document.getElementById('tela-mcasp');
        if (telaMCASP && telaMCASP.style.display === 'block') {
            // Estamos na aba MCASP
            try {
                const periodo = document.getElementById('periodo').value || '2026-TRIMESTRE-3';
                const resp = await fetch('/api/notas_mcasp/salvar_historico', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ periodo: periodo })
                });
                const r = await resp.json();
                if (r.ok) {
                    alert('Histórico MCASP salvo com sucesso!');
                    if (typeof carregarHistorico === 'function') carregarHistorico();
                } else {
                    alert('Erro: ' + r.mensagem);
                }
            } catch(e) { alert('Erro de conexão.'); }
        } else {
            // Estamos na aba Tradicional
            if (typeof originalSalvar === 'function') {
                return originalSalvar();
            } else {
                alert('Salvando modelo tradicional...');
            }
        }
    };
</script>
'''

# Insere o interceptador antes do </body>
if 'window.salvarNotas = async function()' not in s:
    s = s.replace('</body>', js_intercept + '\n</body>', 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)
    print('OK: Interceptador do botao Salvar injetado!')
else:
    print('AVISO: Interceptador ja existe.')
