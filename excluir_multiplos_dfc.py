import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_dfc.html"
shutil.copy2(arq, f"{arq}.bak_excluir_multi_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Funcao antiga: exclui apenas 1 item
antigo = """        function excluirSelecionado() {
            const sel = document.querySelector(".check-hist:checked");
            if (!sel) {
                alert("Selecione um item no historico para excluir.");
                return;
            }
            if (!confirm("Tem certeza que deseja excluir este historico?")) return;

            fetch('/excluir_analise_dfc/' + sel.value, { method: 'DELETE' })
                .then(r => r.json())
                .then(data => {
                    if (data.ok) {
                        alert("Excluido com sucesso!");
                        carregarHistorico();
                    } else {
                        alert("Erro ao excluir.");
                    }
                })
                .catch(e => alert("Erro de conexao."));
        }"""

# Nova funcao: exclui TODOS os itens marcados
novo = """        function excluirSelecionado() {
            const selecionados = document.querySelectorAll(".check-hist:checked");
            if (selecionados.length === 0) {
                alert("Selecione pelo menos um item no historico para excluir.");
                return;
            }
            
            const msg = selecionados.length === 1 
                ? "Tem certeza que deseja excluir este historico?" 
                : "Tem certeza que deseja excluir os " + selecionados.length + " historicos selecionados?";
            
            if (!confirm(msg)) return;

            // Coleta todos os IDs
            const ids = Array.from(selecionados).map(s => s.value);
            let excluidos = 0;
            let erros = 0;

            // Cria uma promise para cada ID e espera todas terminarem
            const promessas = ids.map(id => 
                fetch('/excluir_analise_dfc/' + id, { method: 'DELETE' })
                    .then(r => r.json())
                    .then(data => {
                        if (data.ok) excluidos++;
                        else erros++;
                    })
                    .catch(e => { erros++; })
            );

            Promise.all(promessas).then(() => {
                if (erros > 0) {
                    alert("Concluido: " + excluidos + " excluidos, " + erros + " com erro.");
                } else {
                    alert(excluidos + " item(ns) excluido(s) com sucesso!");
                }
                carregarHistorico();
            });
        }"""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Funcao excluirSelecionado atualizada para excluir MULTIPLOS itens.")
else:
    print("[ERRO] Funcao excluirSelecionado nao encontrada. O HTML pode ter sido modificado.")
