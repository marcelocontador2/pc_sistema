c = open('panorama.html', encoding='utf-8-sig').read()

# Texto exato da função antiga (copiado do seu Select-String)
antiga = """        function exibirSelecionado() {
            const check = document.querySelector(".check-historico:checked");
            if (!check) { alert("Selecione um item no histórico."); return; }
            fetch('/historico_panorama/' + check.value).then(r => r.json()).then(data => { aplicarValores(data); });
        }"""

# Nova função que busca os dados completos da API
nova = """        function exibirSelecionado() {
            const check = document.querySelector(".check-historico:checked");
            if (!check) { alert("Selecione um item no histórico."); return; }
            const periodo = check.parentElement.querySelector('strong').innerText;
            fetch(`/api/panorama/${periodo}?_t=${Date.now()}`, { cache: 'no-store' })
                .then(r => r.json())
                .then(data => { aplicarValores(data); })
                .catch(e => { console.error(e); alert('Erro ao carregar dados.'); });
        }"""

if antiga in c:
    c = c.replace(antiga, nova)
    open('panorama.html', 'w', encoding='utf-8').write(c)
    print("[OK] Função exibirSelecionado substituída com sucesso!")
else:
    print("[AVISO] Texto exato não encontrado. Tentando regex mais flexível...")
    import re
    padrao = r'function exibirSelecionado\(\) \{.*?fetch\(.*?\)\.then\(.*?\);\s*\}'
    if re.search(padrao, c, re.DOTALL):
        c = re.sub(padrao, nova, c, flags=re.DOTALL)
        open('panorama.html', 'w', encoding='utf-8').write(c)
        print("[OK] Função substituída via regex!")
    else:
        print("[ERRO] Não foi possível encontrar a função.")
