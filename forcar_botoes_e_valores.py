import re, shutil, datetime

arquivo = r"pc_frontend\panorama.html"
backup = f"pc_frontend\\panorama_backup_definitivo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adicionar IDs nos botões de forma robusta
def add_id_to_button(html, texto_botao, id_novo):
    # Procura qualquer <button ...> que contenha o texto
    padrao = re.compile(r'(<button[^>]*>)([^<]*' + texto_botao + r'[^<]*)(</button>)', re.IGNORECASE)
    
    def repl(m):
        tag_abertura = m.group(1)
        if 'id=' not in tag_abertura:
            tag_abertura = tag_abertura.replace('<button', f'<button id="{id_novo}"')
        return tag_abertura + m.group(2) + m.group(3)
    
    return padrao.sub(repl, html)

html = add_id_to_button(html, 'Verificar', 'btn-verificar')
html = add_id_to_button(html, 'Gerar PDF', 'btn-pdf')
html = add_id_to_button(html, 'Confirmar e Salvar', 'btn-salvar')
html = add_id_to_button(html, 'Exibir Selecionado', 'btn-exibir')
html = add_id_to_button(html, 'Excluir Selecionado', 'btn-excluir')

# 2. Substitui a função aplicarValores por uma versão que varre o DOM inteiro
old_aplicar_pattern = re.compile(r'function aplicarValores\(data\)\s*\{.*?\n\}', re.DOTALL)
if old_aplicar_pattern.search(html):
    nova_aplicar = """function aplicarValores(data) {
    const format = (val) => {
        if (val === undefined || val === null) return 'R$ 0,0 mi';
        let num = Math.abs(val) / 1000000;
        let prefix = val < 0 ? '-R$ ' : 'R$ ';
        return prefix + num.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mi';
    };

    const map = {
        'caixa e equivalente': data.caixa_bp,
        'ativo total': data.ativo_total,
        'passivo total': data.passivo_total,
        'patrimônio líquido': data.patrimonio_liquido,
        'patrimonio liquido': data.patrimonio_liquido,
        'receitas realizadas': data.receita_realizada,
        'despesas empenhadas': data.despesa_empenhada,
        'superávit orçamentário': data.superavit_orcamentario,
        'déficit orçamentário': data.superavit_orcamentario,
        'superávit patrimonial': data.superavit_patrimonial,
        'superávit financeiro': data.superavit_financeiro
    };

    // Varre todos os elementos (divs, spans, etc) da pagina
    document.querySelectorAll('div, span, p, h1, h2, h3, h4').forEach(el => {
        let txt = el.innerText ? el.innerText.toLowerCase().trim() : '';
        for (let key in map) {
            // Se o elemento tem o texto e começa com R$ ou 0,00
            if (txt.includes(key) && el.children.length === 0 && (txt.includes('r$') || txt.includes('0,0'))) {
                el.innerText = format(map[key]);
                break;
            }
            // Se for o título do card (ex: "Ativo Total")
            if (txt === key) {
                // Pega o próximo elemento irmão (o valor)
                let next = el.nextElementSibling;
                if (next && (next.innerText.includes('R$') || next.innerText.includes('0,0'))) {
                    next.innerText = format(map[key]);
                }
                // Ou o elemento pai tem o valor
                let parent = el.parentElement;
                if (parent) {
                    Array.from(parent.children).forEach(child => {
                        if (child !== el && (child.innerText.includes('R$') || child.innerText.includes('0,0'))) {
                            child.innerText = format(map[key]);
                        }
                    });
                }
            }
        }
    });
}"""
    html = old_aplicar_pattern.sub(nova_aplicar, html, count=1)

# 3. Adiciona os Event Listeners (quebra-galho final)
# Procuramos o bloco final </script> e injetamos antes dele
fix_events = """
// --- EVENTOS DOS BOTOES (Força Bruta) ---
document.addEventListener("DOMContentLoaded", function() {
    const btnV = document.getElementById('btn-verificar');
    if(btnV) btnV.onclick = function(e){ e.preventDefault(); carregarPanorama(); };
    
    const btnS = document.getElementById('btn-salvar');
    if(btnS) btnS.onclick = function(e){ e.preventDefault(); salvarPanorama(); };
    
    const btnP = document.getElementById('btn-pdf');
    if(btnP) btnP.onclick = function(e){ e.preventDefault(); gerarPDFPanorama(); };
    
    const btnE = document.getElementById('btn-exibir');
    if(btnE) btnE.onclick = function(e){ e.preventDefault(); exibirSelecionado(); };
    
    const btnX = document.getElementById('btn-excluir');
    if(btnX) btnX.onclick = function(e){ e.preventDefault(); excluirSelecionado(); };
});
"""
if "EVENTOS DOS BOTOES" not in html:
    # Injeta antes do fechamento do último <script>
    idx_script = html.rfind('</script>')
    if idx_script != -1:
        html = html[:idx_script] + fix_events + html[idx_script:]

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Botoes agora tem IDs fixos e cliques forcados via EventListener.")
print("[OK] Funcao aplicarValores agora varre a pagina inteira em busca de texto e valores.")
print("\n=== PROXIMO PASSO ===")
print("1. Va no navegador: http://127.0.0.1:9994/panorama")
print("2. Aperte Ctrl + Shift + R (MUITO IMPORTANTE).")
print("3. Clique em Verificar.")
