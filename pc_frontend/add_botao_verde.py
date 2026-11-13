import shutil

path = "analise_bp.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_botao_verde")

# 1) Adiciona o botao "Exibir" verde dentro do item do historico
antigo = """<div class="hist-item">
                            <input type="checkbox" value="${item.id}" class="check-hist">
                            <div><strong>${item.periodo}</strong><br><span style="font-size:11px;color:#777;">${item.data_geracao}</span></div>
                        </div>"""

novo = """<div class="hist-item" style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <input type="checkbox" value="${item.id}" class="check-hist">
                                <div><strong>${item.periodo}</strong><br><span style="font-size:11px;color:#777;">${item.data_geracao}</span></div>
                            </div>
                            <button class="btn btn-salvar" style="padding: 4px 10px; font-size: 11px;" onclick="exibirHistorico(${item.id})">Exibir</button>
                        </div>"""

if antigo in s:
    s = s.replace(antigo, novo, 1)
    print("OK: Botao Exibir (verde) injetado no HTML")
else:
    print("AVISO: Bloco do historico nao encontrado")

# 2) Adiciona a funcao exibirHistorico() que chama o carregamento real
ancora_func = "function excluirSelecionado() {"
nova_func = """async function exibirHistorico(id) {
            try {
                const r = await fetch('/historico_analise_bp/' + id);
                if (!r.ok) throw new Error("HTTP " + r.status);
                const dados = await r.json();
                const d = dados.dados?.dados || dados.dados || dados;
                render(d);
                
                // Marca o checkbox visualmente
                document.querySelectorAll('.check-hist').forEach(cb => cb.checked = false);
                const cb = document.querySelector(`.check-hist[value="${id}"]`);
                if(cb) cb.checked = true;
                
            } catch (e) {
                alert("Erro ao carregar o historico.");
                console.error(e);
            }
        }

        function excluirSelecionado() {"""

if ancora_func in s:
    s = s.replace(ancora_func, nova_func, 1)
    print("OK: Funcao exibirHistorico() criada")
else:
    print("AVISO: Funcao excluirSelecionado nao encontrada")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("BOTAO EXIBIR VERDE ADICIONADO COM SUCESSO!")
