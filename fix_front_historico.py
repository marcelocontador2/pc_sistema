p = 'pc_frontend/notas_explicativas.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

js_fix = '''
<script>
    // Função para carregar o histórico do MCASP na aba lateral
    async function carregarHistoricoMCASP() {
        try {
            const resp = await fetch('/api/notas_mcasp/historico');
            const itens = await resp.json();
            const container = document.getElementById('historico-salvo');
            if (!container) return;
            
            if (itens.length === 0) {
                container.innerHTML = '<p style="color:#999; font-size:12px;">Nenhum histórico MCASP.</p>';
                return;
            }
            let html = '';
            itens.forEach(item => {
                html += `
                <div class="historico-item" style="margin-bottom: 10px; padding: 10px; background: #f8f9fa; border-left: 3px solid #003366; border-radius: 4px; cursor: pointer;">
                    <div style="font-weight: bold; font-size: 13px; color: #333;">Período: ${item.periodo}</div>
                    <div style="font-size: 11px; color: #666;">${item.data_geracao}</div>
                    <div style="margin-top: 5px; display: flex; gap: 5px;">
                        <button onclick="window.open('/gerar_pdf_mcasp/${item.id}', '_blank')" style="background: #003366; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 11px;">Gerar PDF</button>
                    </div>
                </div>`;
            });
            container.innerHTML = html;
        } catch(e) { console.error(e); }
    }

    // Sobrescreve a função de alternar abas para carregar o histórico correto
    const originalMostrarMCASP = window.mostrarMCASP;
    window.mostrarMCASP = function() {
        if (typeof originalMostrarMCASP === 'function') originalMostrarMCASP();
        carregarHistoricoMCASP();
    };

    const originalMostrarTradicional = window.mostrarTradicional;
    window.mostrarTradicional = function() {
        if (typeof originalMostrarTradicional === 'function') originalMostrarTradicional();
        if (typeof carregarHistorico === 'function') carregarHistorico(); // Restaura o histórico antigo
    };
</script>
'''

if 'carregarHistoricoMCASP' not in s:
    # Substitui o conteúdo do botão Salvar para salvar no MCASP
    old_salvar = """                const resp = await fetch('/api/notas_mcasp/salvar_historico', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ periodo: periodo })
                });"""
    new_salvar = """                const resp = await fetch('/api/notas_mcasp/salvar_historico', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ periodo: periodo })
                });"""
    
    s = s.replace('</body>', js_fix + '\n</body>', 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)
    print('OK: Frontend atualizado com histórico separado do MCASP!')
else:
    print('AVISO: O código já foi atualizado.')
