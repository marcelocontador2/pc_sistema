import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_frontend/relatorio_consolidado.html")
texto = arquivo.read_text(encoding="utf-8")

# Substitui a funcao excluirSelecionados por uma versao com debug
antigo_js = """function excluirSelecionados() {
            const checkboxes = document.querySelectorAll('.checkbox-historico:checked');
            const ids = Array.from(checkboxes).map(cb => cb.value);
            
            if (ids.length === 0) {
                alert('Nenhum item selecionado.');
                return;
            }
            
            if (!confirm(`Excluir ${ids.length} item(ns)?`)) return;
            
            fetch('/excluir_multiplos_relatorio_consolidado', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ids: ids})
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    alert('Itens excluídos!');
                    location.reload();
                } else {
                    alert('Erro: ' + (data.mensagem || 'desconhecido'));
                }
            })
            .catch(e => alert('Erro: ' + e));
        }"""

novo_js = """function excluirSelecionados() {
            const checkboxes = document.querySelectorAll('.checkbox-historico:checked');
            const ids = Array.from(checkboxes).map(cb => cb.value);
            
            if (ids.length === 0) {
                alert('Nenhum item selecionado.');
                return;
            }
            
            if (!confirm(`Excluir ${ids.length} item(ns)?`)) return;
            
            fetch('/excluir_multiplos_relatorio_consolidado', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ids: ids})
            })
            .then(r => r.text())
            .then(text => {
                alert('Resposta do servidor: ' + text);
                try {
                    const data = JSON.parse(text);
                    if (data.ok) {
                        location.reload();
                    }
                } catch(e) {
                    alert('Erro ao parsear: ' + e);
                }
            })
            .catch(e => alert('Erro no fetch: ' + e));
        }"""

if antigo_js in texto:
    texto = texto.replace(antigo_js, novo_js, 1)
    print("[OK] Funcao excluirSelecionados substituida por versao com debug.")
else:
    # Tenta encontrar a funcao de forma mais tolerante
    import re
    padrao = re.compile(r'function excluirSelecionados\(\)\s*\{.*?\n\s*\}', re.DOTALL)
    if padrao.search(texto):
        texto = padrao.sub(novo_js, texto, count=1)
        print("[OK] Funcao excluirSelecionados substituida por versao com debug (fallback regex).")
    else:
        print("[ERRO] Nao encontrei a funcao excluirSelecionados.")
        sys.exit(1)

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
