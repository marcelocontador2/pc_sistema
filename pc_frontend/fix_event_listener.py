import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_event_listener")

# 1. Remove o onclick do botao Exibir
s = re.sub(r'<button([^>]*)onclick="exibirSelecionado\(\)"([^>]*)>', r'<button\1 id="btn-exibir-composicao"\2>', s)

# 2. Adiciona um event listener no final do script
event_listener = """
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const btn = document.getElementById('btn-exibir-composicao');
        if (btn) {
            btn.addEventListener('click', function() {
                if (typeof exibirSelecionado === 'function') {
                    exibirSelecionado();
                } else {
                    console.error('Funcao exibirSelecionado nao encontrada!');
                }
            });
            console.log('Event listener do botao Exibir configurado.');
        } else {
            console.error('Botao Exibir nao encontrado para configurar o listener.');
        }
    });
</script>
"""

if 'btn-exibir-composicao' not in s:
    s = s.replace('</body>', event_listener + '\n</body>')
    print("OK: Event listener adicionado ao botao Exibir.")
else:
    print("AVISO: Botao ja tem ID. Verifique o HTML.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
