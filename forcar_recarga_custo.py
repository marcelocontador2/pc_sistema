from pathlib import Path
import re

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Substituir o window.onload por uma versao que sempre recarrega
if "window.onload = function()" in conteudo:
    # Encontrar o bloco do onload
    match = re.search(r"window\.onload\s*=\s*function\s*\(\)\s*\{.*?\};", conteudo, re.DOTALL)
    if match:
        novo_onload = '''window.onload = function() {
            // Sempre recarrega os dados ao carregar a pagina
            // (garante que a configuracao mais recente seja aplicada)
            carregar();
            carregarHistorico();
        };'''
        conteudo = conteudo.replace(match.group(0), novo_onload, 1)
        print("OK: window.onload substituido!")
    else:
        print("AVISO: nao achei o bloco do window.onload")

# 2. Adicionar o listener de pageshow (para quando voltar do cache)
if "pageshow" not in conteudo:
    trecho_js = "window.onload = function() {"
    js_pageshow = '''
        window.addEventListener('pageshow', function(event) {
            console.log("[PAGESHOW] Pagina carregada (persisted=" + event.persisted + ")");
            // Sempre recarrega os dados (a API ja le a configuracao do banco)
            if (typeof carregar === 'function') carregar();
            if (typeof carregarHistorico === 'function') carregarHistorico();
        });
        
        '''
    conteudo = conteudo.replace(trecho_js, js_pageshow + trecho_js, 1)
    print("OK: Listener 'pageshow' adicionado!")

# 3. Garantir que o anti-cache esta no fetch do carregar
if "?t=" not in conteudo:
    conteudo = conteudo.replace(
        "fetch('/api/custo_pessoal/' + periodo)",
        "fetch('/api/custo_pessoal/' + periodo + '?t=' + Date.now())"
    )
    print("OK: Anti-cache adicionado no fetch!")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML atualizado!")
