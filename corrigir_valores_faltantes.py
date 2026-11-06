import re, shutil, datetime

arquivo = r"pc_frontend\panorama.html"
backup = f"pc_frontend\\panorama_backup_valores_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Função blindada para achar e substituir qualquer texto de valor
nova_funcao = """function aplicarValores(data) {
    const format = (val) => {
        if (val === undefined || val === null) return 'R$ 0,0 mi';
        let num = Math.abs(val) / 1000000;
        let prefix = val < 0 ? '-R$ ' : 'R$ ';
        return prefix + num.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mi';
    };

    const map = [
        { keys: ['caixa e equivalente', 'caixa'], val: data.caixa_bp },
        { keys: ['ativo total'], val: data.ativo_total },
        { keys: ['passivo total'], val: data.passivo_total },
        { keys: ['patrimônio líquido', 'patrimonio liquido'], val: data.patrimonio_liquido },
        { keys: ['receitas realizadas', 'receita realizada'], val: data.receita_realizada },
        { keys: ['despesas empenhadas', 'despesa empenhada'], val: data.despesa_empenhada },
        { keys: ['superávit orçamentário', 'superavit orcamentario', 'déficit orçamentário', 'deficit orcamentario'], val: data.superavit_orcamentario },
        { keys: ['superávit patrimonial', 'superavit patrimonial'], val: data.superavit_patrimonial },
        { keys: ['superávit financeiro', 'superavit financeiro'], val: data.superavit_financeiro }
    ];

    // Passa por cada elemento que não tem filhos (textos soltos)
    document.querySelectorAll('*').forEach(el => {
        if (el.children.length > 0) return;
        let txt = el.innerText ? el.innerText.toLowerCase().trim() : '';

        for (let item of map) {
            if (item.keys.some(k => txt.includes(k))) {
                // Achou o titulo. Agora vai no elemento pai (o quadro do card)
                let card = el.parentElement;
                if (!card) continue;

                let atualizado = false;
                // Varre o card inteiro procurando qualquer coisa que pareça um valor em R$ ou 0,0
                Array.from(card.querySelectorAll('*')).forEach(child => {
                    if (atualizado || child === el || child.children.length > 0) return;
                    let cTxt = child.innerText.trim();
                    
                    if (cTxt.includes('R$') || cTxt.includes('0,0') || cTxt.includes('0,00')) {
                        child.innerText = format(item.val);
                        atualizado = true;
                    }
                });

                // Se não achou no quadro (talvez esteja do lado de fora), tenta o próximo irmão
                if (!atualizado && el.nextElementSibling) {
                    let next = el.nextElementSibling;
                    if (next.innerText.includes('R$') || next.innerText.includes('0,0')) {
                        next.innerText = format(item.val);
                    }
                }
            }
        }
    });
}"""

# Substitui a função antiga no arquivo
padrao = re.compile(r'function aplicarValores\(data\)\s*\{.*?\n\}', re.DOTALL)
if padrao.search(html):
    html = padrao.sub(nova_funcao, html, count=1)
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Funcao aplicarValores substituida com sucesso.")
    print("[OK] Agora ela varre o card inteiro e preenche os valores que faltavam.")
else:
    print("[ERRO] Nao foi possivel encontrar a funcao aplicarValores no arquivo.")

print("\n=== PROXIMO PASSO ===")
print("1. Va no navegador: http://127.0.0.1:9994/panorama")
print("2. Aperte Ctrl + Shift + R (MUITO IMPORTANTE).")
print("3. Clique em Verificar.")
