import re

arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

padrao = re.compile(
    r"(// ===== 1\. INTEGRIDADE =====.*?H \+= tab\(\['Item','Balancete','BP','BF','BO','DFC','DVP','DMPL','Conf\.'\], rows\);)",
    re.DOTALL
)

# Usa aspas simples na string Python para não conflitar com as aspas do JS
nova_secao = '''// ===== 1. INTEGRIDADE =====
H += tit(1, 'Integridade entre Demonstrações');
H += '<div class="desc">Matriz de integridade com o cruzamento de todas as demonstrações.</div>';
const integ = unwrap(D.integridade);
if (integ && integ.matriz) {
    // Remove o "R$" dos valores (integridade usa formato numérico puro)
    function limpaRS(v) {
        if (v === null || v === undefined) return '-';
        let s = String(v);
        s = s.replace(/R\\$\\s*/g, '');
        return s.trim() || '-';
    }
    const rows = integ.matriz.map(m => [
        m.item || m.NOMENCLATURA || '-',
        limpaRS(m.balancete || m.BALANCETE),
        limpaRS(m.bp || m.BP),
        limpaRS(m.bf || m.BF),
        limpaRS(m.bo || m.BO),
        limpaRS(m.dfc || m.DFC),
        limpaRS(m.dvp || m.DVP),
        limpaRS(m.dmpl || m.DMPL),
        m.conf || m.CONFERENCIA || '-'
    ]);
    H += tab(['Item','Balancete','BP','BF','BO','DFC','DVP','DMPL','Conf.'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }'''

if padrao.search(html):
    # Usa lambda como replacement para evitar interpretação de escapes
    html = padrao.sub(lambda m: nova_secao, html)
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Seção de Integridade atualizada (sem R$).")
else:
    print("[ERRO] Não encontrei o bloco da Integridade no template.")
