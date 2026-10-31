from pathlib import Path
import re

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Encontrar o bloco <script> principal
match = re.search(r'<script>(.*?)</script>', conteudo, re.DOTALL)
if not match:
    print("ERRO: nao achei o bloco <script>")
    exit(1)

# Novo JavaScript SIMPLES e FUNCIONAL
novo_js = '''
        function carregar() {
            console.log("[CARREGAR] Iniciando...");
            var periodo = document.getElementById('periodo-select').value;
            var url = '/api/custo_pessoal/' + periodo + '?t=' + Date.now();
            
            fetch(url)
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    console.log("[CARREGAR] Dados:", d);
                    
                    // Atualizar a tabela
                    var rcl = parseFloat(d.rcl_total || 0);
                    var custo = parseFloat(d.custo_total || 0);
                    var limite = parseFloat(d.limite_atual || (rcl * 0.5));
                    var margem = parseFloat(d.margem_disponivel_atual || (limite - custo));
                    var limite_pct = d.limite_pct || 0.5;
                    
                    var fmt = function(v) { return (v || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}); };
                    var pct = function(parte, total) { return total ? ((parte/total)*100).toFixed(2) + '%' : '0,00%'; };
                    
                    document.getElementById('comp-rcl').textContent = fmt(rcl);
                    document.getElementById('comp-custo').textContent = fmt(custo);
                    document.getElementById('comp-limite').textContent = fmt(limite);
                    document.getElementById('comp-margem').innerHTML = '<b>' + fmt(margem) + '</b>';
                    document.getElementById('comp-pct-custo').textContent = pct(custo, rcl);
                    document.getElementById('comp-pct-margem').innerHTML = '<b>' + pct(margem, rcl) + '</b>';
                    
                    // Atualizar o percentual do limite
                    var pctEl = document.getElementById('comp-limite-pct');
                    if (pctEl) pctEl.textContent = (limite_pct * 100).toFixed(2) + '%';
                    
                    console.log("[CARREGAR] Tabela atualizada!");
                })
                .catch(function(e) {
                    console.error("[CARREGAR] Erro:", e);
                    alert('Erro: ' + e.message);
                });
        }

        window.onload = function() {
            console.log("[ONLOAD] Pagina carregada");
            carregar();
        };
'''

# Substituir o bloco
conteudo = conteudo[:match.start(1)] + novo_js + conteudo[match.end(1):]
arquivo.write_text(conteudo, encoding="utf-8")
print("OK: JavaScript substituido por versao SIMPLES!")
