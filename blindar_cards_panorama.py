import re, shutil, datetime

arquivo = r"pc_frontend\panorama.html"
backup = f"pc_frontend\\panorama_backup_js_seguro_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

def substituir_funcao(html_original, nome_funcao, novo_codigo):
    idx = html_original.find(f"function {nome_funcao}(")
    if idx == -1:
        return html_original
    start_brace = html_original.find("{", idx)
    brace_count = 0
    for i in range(start_brace, len(html_original)):
        if html_original[i] == '{':
            brace_count += 1
        elif html_original[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                return html_original[:idx] + novo_codigo + html_original[i+1:]
    return html_original

# Nova função super blindada que injeta o HTML se os IDs não existirem
nova_aplicar = """function aplicarValores(data) {
    let d = data;
    if (d && d.dados) d = d.dados;
    if (typeof d === 'string') d = JSON.parse(d);
    if (d && d.dados) d = d.dados;

    const format = (val) => {
        if (val === undefined || val === null || isNaN(val)) return 'R$ 0,0 mi';
        let num = Math.abs(val) / 1000000;
        let prefix = val < 0 ? '-R$ ' : 'R$ ';
        return prefix + num.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mi';
    };

    // Procura a grade de cards. Se ela nao existir, cria do zero!
    let grid = document.querySelector('.cards-grid');
    if (!grid) {
        const main = document.querySelector('.main-content') || document.querySelector('main') || document.body;
        grid = document.createElement('div');
        grid.className = 'cards-grid';
        grid.style = 'display:grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px;';
        main.appendChild(grid);
    }

    // Redesenha todos os cards com os IDs certos
    grid.innerHTML = `
        <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Caixa e Equivalente de Caixa (BP)</div>
            <div id="val-caixa" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
        </div>
        <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Ativo Total</div>
            <div id="val-ativo" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
        </div>
        <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Passivo Total</div>
            <div id="val-passivo" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
        </div>
        <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Patrimônio Líquido</div>
            <div id="val-pl" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
        </div>
        <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Receitas Realizadas (BO)</div>
            <div id="val-receitas" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
        </div>
        <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Despesas Empenhadas (BO)</div>
            <div id="val-despesas" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
        </div>
        <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Superávit Orçamentário</div>
            <div id="val-superavit-orc" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
        </div>
        <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Superávit Patrimonial (DVP)</div>
            <div id="val-superavit-pat" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
        </div>
        <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Superávit Financeiro (BP)</div>
            <div id="val-superavit-fin" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
        </div>
    `;

    const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.innerText = format(val);
    };

    setVal('val-caixa', d.caixa_bp || d.caixa);
    setVal('val-ativo', d.ativo_total);
    setVal('val-passivo', d.passivo_total);
    setVal('val-pl', d.patrimonio_liquido);
    setVal('val-receitas', d.receita_realizada);
    setVal('val-despesas', d.despesa_empenhada);
    setVal('val-superavit-orc', d.superavit_orcamentario);
    setVal('val-superavit-pat', d.superavit_patrimonial);
    setVal('val-superavit-fin', d.superavit_financeiro);
}"""

html = substituir_funcao(html, "aplicarValores", nova_aplicar)

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] JavaScript atualizado. Agora os cards se auto-desenham na tela.")
print("\n=== PROXIMO PASSO ===")
print("1. Va no navegador: http://127.0.0.1:9994/panorama")
print("2. Aperte Ctrl + Shift + R (MUITO IMPORTANTE).")
print("3. Marque um item do historico e clique em Exibir.")
