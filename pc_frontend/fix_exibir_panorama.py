import re

path = "panorama.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Substitui a funcao exibirSelecionado para usar a classe correta 'check-historico'
padrao = re.compile(r'async function\s+exibirSelecionado\(\)\s*\{.*?\n\}', re.DOTALL)

nova_funcao = '''async function exibirSelecionado() {
    // A classe correta no HTML e 'check-historico' (nao 'check-hist')
    const check = document.querySelector('.check-historico:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    try {
        const r = await fetch('/historico_panorama/' + check.value);
        if (!r.ok) throw new Error("HTTP " + r.status);
        const dados = await r.json();
        preencherCards(dados);
    } catch (e) {
        alert("Erro ao carregar histórico: " + e.message);
    }
}'''

nova_s, n = padrao.subn(nova_funcao, s)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Funcao exibirSelecionado corrigida para usar a classe 'check-historico'!")
else:
    print("AVISO: Nao foi possivel encontrar a funcao exibirSelecionado.")
