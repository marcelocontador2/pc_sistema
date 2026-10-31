from pathlib import Path
import re

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Adicionar as funcoes dos botoes antes do </script>
funcoes_js = '''
        // === FUNCOES DOS BOTOES ===
        function salvarCusto() {
            var periodo = document.getElementById('periodo-select').value;
            fetch('/salvar_custo_pessoal/' + periodo, {method: 'POST'})
                .then(r => r.json())
                .then(d => { alert('Custo salvo com sucesso!'); carregarHistorico(); })
                .catch(e => alert('Erro ao salvar: ' + e.message));
        }
        
        function exibirSelecionado() {
            var check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no historico.'); return; }
            fetch('/historico_custo_pessoal/' + check.value)
                .then(r => r.json())
                .then(d => {
                    if (d.dados) {
                        document.getElementById('periodo-select').value = d.periodo || '2026-TRIMESTRE-3';
                        carregar();
                    }
                })
                .catch(e => alert('Erro ao carregar historico: ' + e.message));
        }
        
        function excluirSelecionado() {
            var checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) { alert('Selecione pelo menos um item.'); return; }
            var promessas = [];
            checks.forEach(c => {
                promessas.push(fetch('/excluir_custo_pessoal/' + c.value, {method: 'DELETE'}).then(r => r.ok).catch(() => false));
            });
            Promise.all(promessas).then(results => {
                if (results.some(r => r === true)) { alert('Excluido!'); carregarHistorico(); }
            });
        }
        
        function gerarPDF() {
            var periodo = document.getElementById('periodo-select').value;
            window.open('/gerar_pdf_custo_pessoal?periodo=' + periodo, '_blank');
        }
        
        function gerarPDFCompleto() {
            var periodo = document.getElementById('periodo-select').value;
            window.open('/gerar_pdf_completo_custo_pessoal?periodo=' + periodo, '_blank');
        }
        
        function carregarHistorico() {
            fetch('/historico_custo_pessoal')
                .then(r => r.json())
                .then(data => {
                    var div = document.getElementById('historico');
                    if (!div) return;
                    if (!data || data.length === 0) {
                        div.innerHTML = '<p style="color:#666;">Nenhum historico salvo.</p>';
                        return;
                    }
                    var html = '';
                    data.forEach(item => {
                        html += '<div style="padding:10px; border-bottom:1px solid #eee; display:flex; align-items:center; gap:8px;">';
                        html += '<input type="checkbox" class="check-historico" value="' + item.id + '" style="cursor:pointer;">';
                        html += '<div>';
                        html += '<b>' + item.periodo + '</b><br>';
                        html += '<small style="color:#666;">' + (item.data_geracao || '') + '</small>';
                        html += '</div></div>';
                    });
                    div.innerHTML = html;
                })
                .catch(e => console.error('Erro ao carregar historico:', e));
        }
'''

# Inserir antes do </script>
trecho_script = "</script>"
if trecho_script in conteudo:
    # Verificar se ja tem as funcoes
    if "function salvarCusto" not in conteudo:
        conteudo = conteudo.replace(trecho_script, funcoes_js + trecho_script, 1)
        print("OK: Funcoes dos botoes adicionadas!")

# 2. Adicionar onclick nos botoes (se nao tiverem)
botoes = {
    'btn-salvar': 'salvarCusto()',
    'btn-exibir': 'exibirSelecionado()',
    'btn-excluir': 'excluirSelecionado()',
    'btn-pdf': 'gerarPDF()',
    'btn-pdf-completo': 'gerarPDFCompleto()'
}

for btn_id, funcao in botoes.items():
    padrao = rf'(<button[^>]*id="{btn_id}")([^>]*)(>)'
    match = re.search(padrao, conteudo)
    if match:
        if 'onclick=' not in match.group(0):
            novo_btn = match.group(1) + f' onclick="{funcao}"' + match.group(2) + match.group(3)
            conteudo = conteudo.replace(match.group(0), novo_btn, 1)
            print(f"OK: onclick adicionado no {btn_id}")

# 3. Adicionar carregarHistorico no window.onload
if "carregarHistorico()" not in conteudo:
    # Encontrar a linha "carregar();" no onload
    match = re.search(r"window\.onload\s*=\s*function\s*\(\)\s*\{[^}]*carregar\(\);", conteudo)
    if match:
        trecho = match.group(0)
        novo_trecho = trecho.replace("carregar();", "carregar(); carregarHistorico();")
        conteudo = conteudo.replace(trecho, novo_trecho, 1)
        print("OK: carregarHistorico adicionado no onload!")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML atualizado!")
