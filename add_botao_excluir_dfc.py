import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_dfc.html"
shutil.copy2(arq, f"{arq}.bak_btn_excluir_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# 1. Adiciona o botao no top-bar, ao lado do Gerar PDF
antigo_topo = """        <button class="btn btn-voltar" onclick="window.location.href='/'">← Voltar</button>
        <button class="btn btn-salvar" id="btn-salvar" onclick="salvar()" style="display:none;">Confirmar e Salvar</button>
        <button class="btn btn-pdf" onclick="gerarPDF()">Gerar PDF</button>"""

novo_topo = """        <button class="btn btn-voltar" onclick="window.location.href='/'">← Voltar</button>
        <button class="btn btn-salvar" id="btn-salvar" onclick="salvar()" style="display:none;">Confirmar e Salvar</button>
        <button class="btn btn-excluir" style="background:#dc3545; color:white;" onclick="excluirSelecionado()">Excluir Selecionado</button>
        <button class="btn btn-pdf" onclick="gerarPDF()">Gerar PDF</button>"""

if antigo_topo in c:
    c = c.replace(antigo_topo, novo_topo, 1)
    print("[OK] Botao 'Excluir Selecionado' adicionado no topo.")
else:
    print("[AVISO] Nao encontrei o bloco do topo. Tentando variacao...")
    c = c.replace(
        '<button class="btn btn-pdf" onclick="gerarPDF()">Gerar PDF</button>',
        '<button class="btn btn-excluir" style="background:#dc3545; color:white;" onclick="excluirSelecionado()">Excluir Selecionado</button>\n        <button class="btn btn-pdf" onclick="gerarPDF()">Gerar PDF</button>'
    )

# 2. Adiciona a funcao 'excluirSelecionado' antes do fechamento do </script>
antigo_js = """        document.addEventListener('DOMContentLoaded', carregarHistorico);"""

novo_js = """        function excluirSelecionado() {
            const sel = document.querySelector(".check-hist:checked");
            if (!sel) {
                alert("Selecione um item no histórico para excluir.");
                return;
            }
            if (!confirm("Tem certeza que deseja excluir este histórico?")) return;

            fetch('/excluir_analise_dfc/' + sel.value, { method: 'DELETE' })
                .then(r => r.json())
                .then(data => {
                    if (data.ok) {
                        alert("Excluído com sucesso!");
                        carregarHistorico();
                    } else {
                        alert("Erro ao excluir.");
                    }
                })
                .catch(e => alert("Erro de conexao."));
        }

        document.addEventListener('DOMContentLoaded', carregarHistorico);"""

if antigo_js in c:
    c = c.replace(antigo_js, novo_js, 1)
    print("[OK] Funcao 'excluirSelecionado' adicionada.")
else:
    print("[AVISO] Nao encontrei o ponto do DOMContentLoaded para inserir a funcao.")

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Arquivo salvo.")
