import re

c = open('../pc_frontend/analise_centro_custos.html', encoding='utf-8-sig').read()

# 1. Remove os dois botões de relatório e adiciona um único "Gerar Relatório"
c = c.replace(
    '<button class="btn btn-pdf" onclick="window.open(\'/relatorio_centro_custos\', \'_blank\')" style="background-color: #6f42c1; color: white; margin-right: 10px;">📄 Gerar Resumo</button>\n            <button class="btn btn-pdf" onclick="window.open(\'/relatorio_centro_custos_completo\', \'_blank\')" style="background-color: #17a2b8; color: white;">📊 Gerar Completo</button>',
    '<button class="btn btn-pdf" onclick="gerarRelatorio()" style="background-color: #6f42c1; color: white;">📄 Gerar Relatório</button>'
)

# 2. Adiciona a função gerarRelatorio() no JavaScript
if "function gerarRelatorio" not in c:
    script_gerar = """
        function gerarRelatorio() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) {
                alert('Selecione um item no histórico para gerar o relatório.');
                return;
            }
            const id = check.value;
            window.open('/relatorio_centro_custos?id=' + id, '_blank');
        }
"""
    pos = c.rfind("</script>")
    if pos != -1:
        c = c[:pos] + script_gerar + "\n" + c[pos:]
        print("[OK] Função gerarRelatorio() adicionada!")

open('../pc_frontend/analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Tela de análise ajustada: botão único 'Gerar Relatório'!")
