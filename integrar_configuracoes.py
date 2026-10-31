from pathlib import Path

# ============ 1. ADICIONAR BOTAO CONFIGURACOES NA TELA DE CUSTO PESSOAL ============
arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Adicionar botao "Configuracoes" ao lado do "Voltar"
if "btn-configuracoes" not in conteudo:
    trecho_voltar = '<button class="btn btn-voltar" id="btn-voltar">← Voltar</button>'
    btn_config = '''<button class="btn btn-voltar" id="btn-voltar">← Voltar</button>
            <a href="/configuracoes" class="btn btn-ciano" style="text-decoration:none; display:inline-block; padding:10px 20px; margin-left:5px;">⚙️ Configurações</a>'''
    if trecho_voltar in conteudo:
        conteudo = conteudo.replace(trecho_voltar, btn_config, 1)
        print("OK: Botao 'Configuracoes' adicionado!")
    else:
        print("AVISO: nao achei o botao 'Voltar'")

# Garantir que a tela recarrega ao voltar do cache (pageshow)
if "window.addEventListener('pageshow'" not in conteudo:
    trecho_carregar = "window.onload = carregar;"
    if trecho_carregar not in conteudo:
        trecho_carregar = "window.onload = function() {"
    
    # Adicionar o listener de pageshow
    js_pageshow = '''
        window.addEventListener('pageshow', function(event) {
            // Se a pagina veio do cache (voltou da tela de configuracoes)
            if (event.persisted || (performance && performance.navigation && performance.navigation.type === 2)) {
                console.log("[PAGESHOW] Recarregando dados...");
                if (typeof carregar === 'function') carregar();
            }
        });
        
        '''
    if trecho_carregar in conteudo:
        conteudo = conteudo.replace(trecho_carregar, js_pageshow + trecho_carregar, 1)
        print("OK: Listener 'pageshow' adicionado!")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: custo_pessoal.html atualizado!")
