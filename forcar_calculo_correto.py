from pathlib import Path
import re

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Encontrar a funcao carregar() e garantir que ela chame preencherTabela com os dados da API
# (sem usar dados em cache ou variaveis antigas)
padrao_carregar = r"function carregar\(\) \{.*?\n        \}"
nova_carregar = '''function carregar() {
            var periodo = encodeURIComponent(document.getElementById('periodo-select').value);
            console.log("[CARREGAR] Buscando dados para periodo:", periodo);
            
            fetch('/api/custo_pessoal/' + periodo + '?t=' + Date.now())
                .then(r => r.json())
                .then(function(d) {
                    console.log("[CARREGAR] Dados recebidos:", d);
                    if (d.erro) { alert('Erro na API: ' + d.erro); return; }
                    preencherTabela(d);
                })
                .catch(function(e) { 
                    console.error("[CARREGAR] Erro:", e); 
                    alert('Erro de conexao.'); 
                });
        }'''

match = re.search(padrao_carregar, conteudo, re.DOTALL)
if match:
    conteudo = conteudo.replace(match.group(0), nova_carregar, 1)
    print("OK: Funcao carregar() substituida (sempre busca dados frescos)")
else:
    print("AVISO: nao achei a funcao carregar()")

# 2. Encontrar a funcao preencherTabela e garantir que ela use d.limite_atual e d.limite_pct
padrao_preencher = r"function preencherTabela\(d\) \{.*?\n        \}"
nova_preencher = '''function preencherTabela(d) {
            console.log("[PREENCHER] Dados recebidos:", d);
            
            var rcl = parseFloat(d.rcl_atual || d.rcl_total || 0);
            var custo = parseFloat(d.custo_atual || d.custo_total || 0);
            var limite = parseFloat(d.limite_atual || (rcl * (d.limite_pct || 0.5)));
            var margem = parseFloat(d.margem_disponivel_atual || (limite - custo));
            var limite_pct = d.limite_pct || 0.5;
            
            console.log("[PREENCHER] limite_pct:", limite_pct, "| limite:", limite, "| margem:", margem);
            
            var fmt = function(v) { return (v || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}); };
            var pct = function(parte, total) { return total ? ((parte/total)*100).toFixed(2) + '%' : '0,00%'; };
            
            var el = function(id) { return document.getElementById(id); };
            
            if (el('comp-rcl')) el('comp-rcl').textContent = fmt(rcl);
            if (el('comp-custo')) el('comp-custo').textContent = fmt(custo);
            if (el('comp-limite')) el('comp-limite').textContent = fmt(limite);
            if (el('comp-limite-pct')) el('comp-limite-pct').textContent = (limite_pct * 100).toFixed(2) + '%';
            if (el('comp-margem')) el('comp-margem').innerHTML = '<b>' + fmt(margem) + '</b>';
            if (el('comp-pct-custo')) el('comp-pct-custo').textContent = pct(custo, rcl);
            if (el('comp-pct-margem')) el('comp-pct-margem').innerHTML = '<b>' + pct(margem, rcl) + '</b>';
            
            // Corrigir o texto do limite (remover o "50%" fixo)
            var limiteLabel = document.querySelector('td:contains("Limite")');
            if (el('comp-limite-pct')) {
                var labelEl = el('comp-limite-pct').parentElement;
                if (labelEl) {
                    labelEl.innerHTML = (limite_pct * 100).toFixed(2) + '%';
                }
            }
        }'''

match = re.search(padrao_preencher, conteudo, re.DOTALL)
if match:
    conteudo = conteudo.replace(match.group(0), nova_preencher, 1)
    print("OK: Funcao preencherTabela() substituida (usa limite_atual)")
else:
    print("AVISO: nao achei a funcao preencherTabela()")

# 3. Corrigir o label do HTML que mostra "Limite LRF"
conteudo = conteudo.replace(
    "Limite LRF",
    "Limite Resolução Cofen 814/2026"
)
# Adicionar ID no <td> do percentual do limite (se nao tiver)
conteudo = re.sub(
    r'<tr><td>Limite Resolução Cofen 814/2026</td><td id="comp-limite"([^>]*)>([^<]*)</td><td([^>]*)>50,00%</td></tr>',
    '<tr><td>Limite Resolução Cofen 814/2026</td><td id="comp-limite"\\1>\\2</td><td id="comp-limite-pct"\\3>50,00%</td></tr>',
    conteudo
)

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML atualizado!")
