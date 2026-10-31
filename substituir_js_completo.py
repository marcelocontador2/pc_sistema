from pathlib import Path
import re

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Encontrar o bloco <script> ... </script>
match = re.search(r'<script>(.*?)</script>', conteudo, re.DOTALL)
if not match:
    print("ERRO: nao achei o bloco <script>")
    exit(1)

# Novo JavaScript limpo
novo_js = '''
        function fmt(v) { return (v || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}); }
        function pct(parte, total) { return total ? ((parte/total)*100).toFixed(2) + '%' : '0,00%'; }
        function num(v) { return parseFloat(v) || 0; }
        function el(id) { return document.getElementById(id); }
        function lerJSON(r) { return r.json(); }

        function preencherTabela(d) {
            var rcl = num(d.rcl_atual || d.rcl_total || 0);
            var custo = num(d.custo_atual || d.custo_total || 0);
            var limite = num(d.limite_atual || (rcl * 0.5));
            var margem = num(d.margem_disponivel_atual || (limite - custo));
            var limite_pct = d.limite_pct || 0.5;

            el('comp-rcl').textContent = fmt(rcl);
            el('comp-custo').textContent = fmt(custo);
            el('comp-limite').textContent = fmt(limite);
            var pctEl = el('comp-limite-pct');
            if (pctEl) pctEl.textContent = (limite_pct * 100).toFixed(2) + '%';
            el('comp-margem').innerHTML = '<b>' + fmt(margem) + '</b>';
            el('comp-pct-custo').textContent = pct(custo, rcl);
            el('comp-pct-margem').innerHTML = '<b>' + pct(margem, rcl) + '</b>';
        }

        function carregar() {
            var periodo = encodeURIComponent(el('periodo-select').value);
            fetch('/api/custo_pessoal/' + periodo + '?t=' + Date.now())
                .then(lerJSON)
                .then(function(d) {
                    if (d.erro) { alert('Erro na API: ' + d.erro); return; }
                    preencherTabela(d);
                })
                .catch(function(e) { console.error(e); alert('Erro de conexao.'); });
        }

        function mudarEntidade(novaEntidade) {
            console.log("[TOGGLE] Mudando para:", novaEntidade);

            // Atualizar visual
            var btnCofen = el('btn-cofen');
            var btnCoren = el('btn-coren');
            if (btnCofen) {
                btnCofen.style.background = (novaEntidade === 'COFEN') ? '#003366' : '#f0f0f0';
                btnCofen.style.color = (novaEntidade === 'COFEN') ? '#fff' : '#333';
            }
            if (btnCoren) {
                btnCoren.style.background = (novaEntidade === 'COREN') ? '#003366' : '#f0f0f0';
                btnCoren.style.color = (novaEntidade === 'COREN') ? '#fff' : '#333';
            }

            // Salvar no backend
            fetch('/api/configuracoes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tipo_entidade: novaEntidade})
            })
            .then(r => r.json())
            .then(function(d) {
                console.log("[TOGGLE] Salvo:", d);
                setTimeout(carregar, 300);
            })
            .catch(function(e) { console.error("[TOGGLE] Erro:", e); });
        }

        window.onload = function() {
            carregar();
            fetch('/api/configuracoes').then(r => r.json()).then(function(d) {
                var ent = d.tipo_entidade || 'COFEN';
                var btnCofen = el('btn-cofen');
                var btnCoren = el('btn-coren');
                if (btnCofen) {
                    btnCofen.style.background = (ent === 'COFEN') ? '#003366' : '#f0f0f0';
                    btnCofen.style.color = (ent === 'COFEN') ? '#fff' : '#333';
                }
                if (btnCoren) {
                    btnCoren.style.background = (ent === 'COREN') ? '#003366' : '#f0f0f0';
                    btnCoren.style.color = (ent === 'COREN') ? '#fff' : '#333';
                }
            }).catch(function(e) { console.error(e); });
        };
'''

# Substituir o bloco
conteudo = conteudo[:match.start(1)] + novo_js + conteudo[match.end(1):]
arquivo.write_text(conteudo, encoding="utf-8")
print("OK: JavaScript substituido por versao limpa!")
