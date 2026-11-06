import shutil, datetime, sys

arquivo = r"pc_frontend\panorama.html"
backup = f"pc_frontend\\panorama_backup_final_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Função segura para substituir blocos inteiros de funções JS
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

# 1. Nova função aplicarValores (à prova de falhas)
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

    document.querySelectorAll('.card, .kpi-card, .card-panorama').forEach(card => {
        let textoCard = card.innerText.toLowerCase();
        for (let key in map) {
            if (textoCard.includes(key)) {
                let elementos = card.querySelectorAll('*');
                for (let el of elementos) {
                    if (el.children.length === 0 && el.innerText.includes('R$')) {
                        el.innerText = format(map[key]);
                        break;
                    }
                }
                break;
            }
        }
    });
}"""

# 2. Nova função carregarHistorico (com catch para não travar no "Carregando...")
novo_historico = """function carregarHistorico() {
    fetch('/historico_panorama')
        .then(r => r.json())
        .then(data => {
            let html = '';
            if (!data || data.length === 0) {
                html = '<li>Nenhum histórico.</li>';
            } else {
                data.forEach(item => {
                    html += `<li style="margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <input type="checkbox" class="check-historico" value="${item.id}" style="width: 16px; height: 16px; cursor: pointer;">
                            <div><div style="font-weight: bold; color: #0056b3;">${item.periodo}</div><div style="font-size: 12px; color: #888;">Gerado em: ${item.data_geracao}</div></div>
                        </div></li>`;
                });
            }
            document.getElementById('lista-historico').innerHTML = html;
        })
        .catch(e => {
            console.error("Erro no historico", e);
            document.getElementById('lista-historico').innerHTML = '<li>Erro ao carregar.</li>';
        });
}"""

html = substituir_funcao(html, "aplicarValores", nova_aplicar)
html = substituir_funcao(html, "carregarHistorico", novo_historico)

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] aplicarValores blindada (vai ler os valores da API e preencher os cards).")
print("[OK] carregarHistorico blindada (nao vai mais travar em 'Carregando...').")
print("\n=== PROXIMO PASSO ===")
print("1. O servidor NAO precisa ser reiniciado.")
print("2. Va no navegador: http://127.0.0.1:9994/panorama")
print("3. Aperte Ctrl + Shift + R (MUITO IMPORTANTE para limpar o cache).")
print("4. Clique em Verificar. Os valores devem aparecer!")
