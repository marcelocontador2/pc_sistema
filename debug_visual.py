from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Adicionar um bloco de debug visivel na tela
if 'id="debug-info"' not in conteudo:
    # Adicionar o bloco de debug antes do fechamento do body
    trecho_body = "</body>"
    debug_div = '''
    <div id="debug-info" style="margin: 20px; padding: 15px; background: #f0f0f0; border-radius: 8px; font-family: monospace; font-size: 12px; display: none;">
        <b>Debug:</b> <span id="debug-text">Aguardando...</span>
    </div>
    <script>
        // Funcao de debug visivel
        function mostrarDebug(msg) {
            var el = document.getElementById('debug-info');
            var txt = document.getElementById('debug-text');
            if (el && txt) {
                el.style.display = 'block';
                txt.innerText = msg;
            }
        }
        
        // Interceptar erros
        window.onerror = function(msg, url, line) {
            mostrarDebug('ERRO: ' + msg + ' (linha ' + line + ')');
            return false;
        };
    </script>
    </body>'''
    conteudo = conteudo.replace(trecho_body, debug_div, 1)
    print("OK: Bloco de debug adicionado!")

# Adicionar logs no carregar()
conteudo = conteudo.replace(
    "console.log(\"[CARREGAR] Buscando dados para periodo:\", periodo);",
    "console.log(\"[CARREGAR] Buscando dados para periodo:\", periodo); mostrarDebug('Buscando dados...');"
)

# Adicionar logs no preencherTabela()
conteudo = conteudo.replace(
    "console.log(\"[PREENCHER] Dados recebidos:\", d);",
    "console.log(\"[PREENCHER] Dados recebidos:\", d); mostrarDebug('Dados: limite_pct=' + d.limite_pct + ', limite=' + d.limite_atual + ', margem=' + d.margem_disponivel_atual);"
)

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML atualizado com debug visual!")
