from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Substituir a funcao mudarEntidade por uma versao mais robusta
inicio = conteudo.find("function mudarEntidade(novaEntidade)")
if inicio == -1:
    print("ERRO: nao achei a funcao mudarEntidade")
    exit(1)

# Encontrar o fim da funcao (proximo function ou fim do script)
fim = conteudo.find("function ", inicio + 10)
if fim == -1:
    fim = conteudo.find("</script>", inicio)
if fim == -1:
    fim = len(conteudo)

nova_funcao = '''function mudarEntidade(novaEntidade) {
            console.log("[TOGGLE] mudarEntidade chamada com:", novaEntidade);
            
            // Atualizar visual dos botoes
            var btnCofen = document.getElementById('btn-cofen');
            var btnCoren = document.getElementById('btn-coren');
            if (btnCofen) btnCofen.classList.toggle('ativo', novaEntidade === 'COFEN');
            if (btnCoren) btnCoren.classList.toggle('ativo', novaEntidade === 'COREN');
            
            // Salvar no backend
            fetch('/api/configuracoes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tipo_entidade: novaEntidade})
            })
            .then(r => r.json())
            .then(d => {
                console.log("[TOGGLE] Config salva no backend:", d);
                // Recarregar a analise
                if (typeof carregar === 'function') {
                    console.log("[TOGGLE] Chamando carregar()...");
                    carregar();
                } else {
                    console.error("[TOGGLE] Funcao carregar() nao encontrada!");
                }
            })
            .catch(e => console.error('[TOGGLE] Erro ao salvar config:', e));
        }
        
        '''

conteudo = conteudo[:inicio] + nova_funcao + conteudo[fim:]
arquivo.write_text(conteudo, encoding="utf-8")
print("OK: Funcao mudarEntidade substituida por versao robusta!")
