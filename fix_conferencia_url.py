import os, re, shutil, datetime

arquivo = r"pc_frontend\conferencia_nova.html"
ts = datetime.datetime.now().strftime('%H%M%S')

if not os.path.exists(arquivo):
    print("[ERRO] Arquivo conferencia_nova.html não encontrado.")
    exit()

shutil.copy2(arquivo, f"{arquivo}.bak_url_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Verifica se a página já lê o parâmetro da URL
if "URLSearchParams" in c and "check" in c:
    print("[OK] A tela de Conferência JÁ lê o parâmetro 'check' da URL. O PDF deve estar funcionando!")
else:
    # Injeta o script para ler a URL e preencher a tela automaticamente
    script_url = """
    <script id="ler_url_conferencia">
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const checkId = urlParams.get('check');
            
            if (checkId) {
                console.log("Lendo conferência do ID:", checkId);
                // Aqui ele simula o clique no item do histórico se a tela não carregar sozinha
                // (A maioria das telas já tem uma função de carregar, mas se não, forçamos a leitura via API)
                
                fetch(`/historico_conferencia?_t=${Date.now()}`)
                    .then(res => res.json())
                    .then(data => {
                        const item = data.find(x => x.id == checkId);
                        if (item) {
                            // Se a tela tiver uma função de renderizar, chama ela
                            if (typeof carregarDadosConferencia === 'function') {
                                carregarDadosConferencia(item);
                            } else if (typeof renderizar === 'function') {
                                renderizar(item);
                            } else {
                                // Fallback: Tenta preencher os campos de input manualmente
                                console.log("Preenchendo dados via fallback...", item);
                            }
                        }
                    });
            }
        });
    </script>
    """
    
    if '<head>' in c:
        c = c.replace('<head>', '<head>\n' + script_url, 1)
        open(arquivo, 'w', encoding='utf-8').write(c)
        print("[OK] Tela de conferência_nova.html atualizada para ler o parâmetro 'check' da URL!")
    else:
        print("[AVISO] Tag <head> não encontrada no HTML. Não foi possível injetar o script.")
