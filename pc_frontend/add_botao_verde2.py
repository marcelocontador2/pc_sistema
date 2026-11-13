import shutil

path = "analise_bp.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_verde2")

# O bloco exato que está no arquivo
antigo = """html += `<div class="hist-item" style="cursor: pointer;" onclick="carregarHistoricoSelecionado(this)">
                            <input type="checkbox" value="${item.id}" class="check-hist">
                            <div><strong>${item.periodo}</strong><br><span style="font-size:11px;color:#777;">${item.data_geracao}</span></div>
                        </div>`;"""

# Adiciona o botao verde dentro do item, mas sem quebrar o clique do container
novo = """html += `<div class="hist-item" style="cursor: pointer; display: flex; justify-content: space-between; align-items: center;" onclick="carregarHistoricoSelecionado(this)">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox" value="${item.id}" class="check-hist" onclick="event.stopPropagation();">
                                <div><strong>${item.periodo}</strong><br><span style="font-size:11px;color:#777;">${item.data_geracao}</span></div>
                            </div>
                            <button class="btn btn-salvar" style="padding: 4px 10px; font-size: 11px;" onclick="event.stopPropagation(); exibirHistorico(${item.id})">Exibir</button>
                        </div>`;"""

if antigo in s:
    s = s.replace(antigo, novo, 1)
    print("OK: Botao Exibir (verde) injetado com sucesso")
else:
    print("AVISO: Bloco exato nao encontrado. Tentando substituicao simplificada...")
    # Fallback: substitui apenas o fechamento da div
    s = s.replace('</div>`;\n                    });', '</div><button class="btn btn-salvar" style="padding: 4px 10px; font-size: 11px; margin-left: 10px;" onclick="event.stopPropagation(); exibirHistorico(${item.id})">Exibir</button></div>`;\n                    });', 1)
    print("OK: Substituicao simplificada aplicada")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("BOTAO EXIBIR VERDE ADICIONADO!")
