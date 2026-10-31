from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Adicionar o toggle Cofen/Coren ao lado do periodo
trecho_antigo = '<select id="periodo-select"><option value="2026-TRIMESTRE-3">2026 - 3º Trimestre</option></select>'
trecho_novo = '''<select id="periodo-select"><option value="2026-TRIMESTRE-3">2026 - 3º Trimestre</option></select>
            <div style="display: inline-flex; margin-left: 15px; border: 1px solid #ccc; border-radius: 5px; overflow: hidden;">
                <button id="btn-cofen" class="btn-entidade ativo" onclick="mudarEntidade('COFEN')" style="padding: 10px 20px; border: none; cursor: pointer; font-weight: bold; background: #003366; color: #fff;">COFEN (50%)</button>
                <button id="btn-coren" class="btn-entidade" onclick="mudarEntidade('COREN')" style="padding: 10px 20px; border: none; cursor: pointer; font-weight: bold; background: #f0f0f0; color: #333;">COREN (60%)</button>
            </div>'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: Toggle Cofen/Coren adicionado!")
else:
    print("AVISO: nao achei o select do periodo")

# 2. Adicionar o CSS do toggle
if ".btn-entidade" not in conteudo:
    trecho_css = "</style>"
    css_novo = '''
        .btn-entidade { transition: all 0.2s; }
        .btn-entidade.ativo { background: #003366 !important; color: #fff !important; }
        .btn-entidade:not(.ativo) { background: #f0f0f0 !important; color: #333 !important; }
        .btn-entidade:hover { opacity: 0.9; }
    </style>'''
    conteudo = conteudo.replace(trecho_css, css_novo, 1)
    print("OK: CSS do toggle adicionado!")

# 3. Adicionar a funcao mudarEntidade no JS
if "function mudarEntidade" not in conteudo:
    # Procurar a funcao carregar (que carrega a analise)
    trecho_js = "function carregar() {"
    if trecho_js in conteudo:
        funcao_nova = '''function mudarEntidade(novaEntidade) {
            // Atualizar visual dos botoes
            document.getElementById('btn-cofen').classList.toggle('ativo', novaEntidade === 'COFEN');
            document.getElementById('btn-coren').classList.toggle('ativo', novaEntidade === 'COREN');
            
            // Salvar no backend
            fetch('/api/configuracoes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tipo_entidade: novaEntidade})
            }).then(r => r.json()).then(d => {
                console.log('Config salva:', d);
                // Recarregar a analise
                if (typeof carregar === 'function') carregar();
            }).catch(e => console.error('Erro ao salvar config:', e));
        }
        
        ''' + trecho_js
        conteudo = conteudo.replace(trecho_js, funcao_nova, 1)
        print("OK: Funcao mudarEntidade adicionada!")

# 4. Inicializar o toggle com a config atual (ao carregar a pagina)
if "carregarConfigInicial" not in conteudo:
    # Adicionar ao window.onload existente
    trecho_onload = "window.onload"
    if trecho_onload in conteudo:
        # Procurar o = depois do onload
        import re
        match = re.search(r"window\.onload\s*=\s*([^;]+);", conteudo)
        if match:
            funcao_original = match.group(1)
            funcao_init = '''(function() {
                fetch('/api/configuracoes').then(r => r.json()).then(d => {
                    var ent = d.tipo_entidade || 'COFEN';
                    var btnCofen = document.getElementById('btn-cofen');
                    var btnCoren = document.getElementById('btn-coren');
                    if (btnCofen) btnCofen.classList.toggle('ativo', ent === 'COFEN');
                    if (btnCoren) btnCoren.classList.toggle('ativo', ent === 'COREN');
                }).catch(e => console.error('Erro ao carregar config:', e));
                ''' + funcao_original + '''
            })();'''
            conteudo = conteudo.replace(match.group(0), "window.onload = " + funcao_init)
            print("OK: Inicializacao do toggle adicionada!")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: Frontend atualizado!")
