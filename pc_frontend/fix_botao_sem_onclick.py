import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_botao_sem_onclick")

# 1. Substitui o botao Exibir por um novo botao sem onclick, com ID
# O botao atual tem: <button class="btn" style="background:#28a745" onclick="exibirSelecionado()">Exibir</button>
# ou similar
padrao_botao = re.compile(r'<button[^>]*>Exibir</button>', re.IGNORECASE)
match = padrao_botao.search(s)

if match:
    novo_botao = '<button id="btn-exibir-composicao" class="btn" style="background:#28a745">Exibir</button>'
    s = s[:match.start()] + novo_botao + s[match.end():]
    print("OK: Botao Exibir substituido por versao sem onclick.")
else:
    print("AVISO: Botao Exibir nao encontrado.")

# 2. Remove qualquer event listener antigo (se existir)
s = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\'.*?btn-exibir-composicao.*?</script>', '', s, flags=re.DOTALL)

# 3. Adiciona o event listener no final do body
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

if 'btn-exibir-composicao' in s and 'Event listener do botao Exibir' not in s:
    s = s.replace('</body>', event_listener + '\n</body>')
    print("OK: Event listener adicionado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
