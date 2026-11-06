import re

arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

padrao = re.compile(r"(// ===== 2\. ANÁLISE BP =====.*?)(?=// ===== 3\. ANÁLISE BO =====)", re.DOTALL)
m = padrao.search(html)

if not m:
    print("[ERRO] Bloco da Seção 2 não encontrado.")
    raise SystemExit

bloco_atual = m.group(1)

if 'SUPERÁVIT FINANCEIRO' in bloco_atual:
    print("[AVISO] Superávit Financeiro já está no bloco.")
    raise SystemExit

alvo = "H += tab(['Conta','Período Atual (R$)','Período Anterior (R$)', 'Var. (%)'], rows);"

if alvo not in bloco_atual:
    print("[ERRO] Não encontrei a linha exata do tab() no bloco da Seção 2.")
    raise SystemExit

codigo_superavit = """// Calcular Superávit Financeiro (Ativo Circulante - Passivo Circulante)
    const itemAtivoCirc = encontrados.find(e => e.chave.toLowerCase().includes('ativo_circulante'));
    const itemPassivoCirc = encontrados.find(e => e.chave.toLowerCase().includes('passivo_circulante'));
    if (itemAtivoCirc && itemPassivoCirc) {
        const sfAt = parseFloat(itemAtivoCirc.atual) - parseFloat(itemPassivoCirc.atual);
        const sfAn = parseFloat(itemAtivoCirc.anterior) - parseFloat(itemPassivoCirc.anterior);
        let sfVar = '-';
        if (sfAn && sfAn !== 0) {
            const varP = ((sfAt - sfAn) / Math.abs(sfAn)) * 100;
            sfVar = (varP > 0 ? '+' : '') + varP.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
        }
        rows.push(['SUPERÁVIT FINANCEIRO', 'R$ ' + sfAt.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}), 'R$ ' + sfAn.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}), sfVar]);
    }

    """

novo_bloco = bloco_atual.replace(alvo, codigo_superavit + alvo)

html = html.replace(bloco_atual, novo_bloco)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Linha de Superávit Financeiro adicionada com cálculo automático!")
