import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_frontend/relatorio_consolidado.html")
texto = arquivo.read_text(encoding="utf-8")

# O bloco JavaScript de correção (usa apenas ASCII e strings seguras)
js_fix = '''
// --- INICIO DA CORRECAO DO FRONTEND ---
document.addEventListener("DOMContentLoaded", function() {
    if (typeof carregarHistorico === "function") {
        carregarHistorico();
    }

    var marcarTodos = document.getElementById('selecionar-todos');
    if (marcarTodos) {
        marcarTodos.addEventListener('change', function() {
            var checkboxes = document.querySelectorAll('#lista-historico input[type="checkbox"]');
            for (var i = 0; i < checkboxes.length; i++) {
                checkboxes[i].checked = this.checked;
            }
            atualizarBotao();
        });
    }

    var btnExcluir = document.getElementById('btn-excluir-todos');
    if (btnExcluir) {
        btnExcluir.addEventListener('click', function() {
            var checkboxes = document.querySelectorAll('#lista-historico input[type="checkbox"]:checked');
            var ids = [];
            for (var i = 0; i < checkboxes.length; i++) {
                ids.push(checkboxes[i].value);
            }
            
            if (ids.length === 0) {
                alert("Nenhum item selecionado.");
                return;
            }
            
            if (!confirm("Excluir " + ids.length + " item(ns) selecionado(s)?")) return;
            
            fetch('/excluir_multiplos_relatorio_consolidado', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ids: ids})
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.ok) {
                    alert("Excluido com sucesso!");
                    location.reload();
                } else {
                    alert("Erro: " + (data.mensagem || data.erro));
                }
            })
            .catch(function(e) { alert("Erro na requisicao: " + e); });
        });
    }
});

function atualizarBotao() {
    var btn = document.getElementById('btn-excluir-todos');
    if (!btn) return;
    var checkboxes = document.querySelectorAll('#lista-historico input[type="checkbox"]:checked');
    btn.disabled = (checkboxes.length === 0);
}
// --- FIM DA CORRECAO DO FRONTEND ---
'''

# Remove qualquer tentativa anterior de injetar esse bloco (para evitar duplicacao)
if "// --- INICIO DA CORRECAO DO FRONTEND ---" in texto:
    inicio = texto.find("// --- INICIO DA CORRECAO DO FRONTEND ---")
    fim = texto.find("// --- FIM DA CORRECAO DO FRONTEND ---") + len("// --- FIM DA CORRECAO DO FRONTEND ---")
    texto = texto[:inicio] + texto[fim:]
    print("[INFO] Bloco antigo de correcao removido.")

# Insere o novo bloco antes do </script> final
pos = texto.rfind('</script>')
if pos != -1:
    texto = texto[:pos] + "\n" + js_fix + "\n" + texto[pos:]
    print("[OK] Novo bloco JavaScript injetado com sucesso.")
else:
    print("[ERRO] Nao encontrei a tag </script> no HTML.")
    sys.exit(1)

# Salva o arquivo
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo HTML atualizado e salvo.")
