import re
import shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_fix_exibir_comp")

# 1. Encontra o bloco do DOMContentLoaded para adicionar o event listener do botao Exibir
# Procura o final do bloco DOMContentLoaded (onde tem carregarHistorico();)
padrao_dom = re.compile(r'(document\.addEventListener\(\'DOMContentLoaded\',\s*function\(\)\s*\{.*?carregarHistorico\(\);)(.*?)(\}\);)', re.DOTALL)

def adicionar_listener(match):
    inicio = match.group(1)
    resto = match.group(2)
    fim = match.group(3)
    
    # Adiciona o listener do botao Exibir
    listener = '''
  // --- CORRECAO: Vincula o botao Exibir a funcao exibirSelecionado ---
  const btnExibir = document.getElementById('btn-exibir-composicao');
  if (btnExibir) {
      btnExibir.addEventListener('click', exibirSelecionado);
  }
'''
    return inicio + listener + resto + fim

nova_s, n = padrao_dom.subn(adicionar_listener, s)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Event listener do botao Exibir adicionado com sucesso!")
else:
    print("AVISO: Nao foi possivel encontrar o DOMContentLoaded para injetar o listener.")
    # Tenta uma abordagem mais simples: insere antes do </body>
    if 'btn-exibir-composicao' in s and 'btnExibir.addEventListener' not in s:
        s = s.replace('</body>', '''
<script>
document.addEventListener('DOMContentLoaded', function() {
    const btnExibir = document.getElementById('btn-exibir-composicao');
    if (btnExibir) {
        btnExibir.addEventListener('click', exibirSelecionado);
    }
});
</script>
</body>''')
        with open(path, "w", encoding="utf-8") as f:
            f.write(s)
        print("OK: Event listener adicionado via script extra no final do body.")
