from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Adicionar anti-cache no fetch do carregar()
trecho_antigo = "fetch('/api/custo_pessoal/' + periodo).then(lerJSON).then(function (d) {"
trecho_novo = "fetch('/api/custo_pessoal/' + periodo + '?t=' + Date.now()).then(lerJSON).then(function (d) {"

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: Anti-cache adicionado no fetch do carregar()!")
else:
    print("AVISO: nao achei o fetch do carregar()")

# 2. Adicionar uma pequena espera no mudarEntidade
trecho_antigo2 = '''            .then(d => {
                console.log("[TOGGLE] Config salva no backend:", d);
                // Recarregar a analise
                if (typeof carregar === 'function') {
                    console.log("[TOGGLE] Chamando carregar()...");
                    carregar();
                } else {
                    console.error("[TOGGLE] Funcao carregar() nao encontrada!");
                }
            })'''

trecho_novo2 = '''            .then(d => {
                console.log("[TOGGLE] Config salva no backend:", d);
                setTimeout(function() {
                    if (typeof carregar === 'function') {
                        console.log("[TOGGLE] Chamando carregar()...");
                        carregar();
                    } else {
                        console.error("[TOGGLE] Funcao carregar() nao encontrada!");
                    }
                }, 300);
            })'''

if trecho_antigo2 in conteudo:
    conteudo = conteudo.replace(trecho_antigo2, trecho_novo2, 1)
    print("OK: Delay de 300ms adicionado no mudarEntidade!")
else:
    print("AVISO: nao achei o trecho do setTimeout")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML atualizado!")
