from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Substituir o trecho antigo do preencherTabela
trecho_antigo = '''        function preencherTabela(d) {
            var rcl = num(d.rcl_total), custo = num(d.custo_total);
            var limite = rcl * 0.5, margem = limite - custo;
            el('comp-rcl').textContent = fmt(rcl);
            el('comp-custo').textContent = fmt(custo);
            el('comp-limite').textContent = fmt(limite);
            el('comp-margem').innerHTML = '<b>' + fmt(margem) + '</b>';
            el('comp-pct-custo').textContent = pct(custo, rcl);
            el('comp-pct-margem').innerHTML = '<b>' + pct(margem, rcl) + '</b>';
        }'''

trecho_novo = '''        function preencherTabela(d) {
            var rcl = num(d.rcl_atual || d.rcl_total || 0);
            var custo = num(d.custo_atual || d.custo_total || 0);
            var limite = num(d.limite_atual || (rcl * 0.5));
            var margem = num(d.margem_disponivel_atual || (limite - custo));
            var limite_pct = d.limite_pct || 0.5;
            el('comp-rcl').textContent = fmt(rcl);
            el('comp-custo').textContent = fmt(custo);
            el('comp-limite').textContent = fmt(limite);
            if (el('comp-limite-pct')) el('comp-limite-pct').textContent = fmtPct(limite_pct * 100);
            el('comp-margem').innerHTML = '<b>' + fmt(margem) + '</b>';
            el('comp-pct-custo').textContent = pct(custo, rcl);
            el('comp-pct-margem').innerHTML = '<b>' + pct(margem, rcl) + '</b>';
        }'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: JS do preencherTabela atualizado!")
else:
    print("AVISO: nao achei o trecho exato. Tentando variacao...")
    # Tentar com indentacao diferente
    import re
    padrao = r"var limite = rcl \* 0\.5, margem = limite - custo;"
    if re.search(padrao, conteudo):
        conteudo = re.sub(
            padrao,
            "var limite = num(d.limite_atual || (rcl * 0.5));\n            var margem = num(d.margem_disponivel_atual || (limite - custo));\n            var limite_pct = d.limite_pct || 0.5;",
            conteudo
        )
        # Tambem atualizar o comp-limite-pct
        if "el('comp-limite-pct')" not in conteudo:
            conteudo = conteudo.replace(
                "el('comp-limite').textContent = fmt(limite);",
                "el('comp-limite').textContent = fmt(limite);\n            if (el('comp-limite-pct')) el('comp-limite-pct').textContent = fmtPct(limite_pct * 100);"
            )
        print("OK: JS atualizado via regex!")
    else:
        print("ERRO: nao achei o calculo do limite")

# Adicionar funcao fmtPct se nao existir
if "function fmtPct" not in conteudo:
    # Inserir depois da funcao fmt
    trecho_fmt = "function fmt(v) {"
    if trecho_fmt in conteudo:
        # Ja tem fmt, adicionar fmtPct ao lado
        conteudo = conteudo.replace(
            trecho_fmt,
            "function fmtPct(v) { return (v || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%'; }\n        function fmt(v) {",
            1
        )
        print("OK: Funcao fmtPct adicionada!")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML do Custo Pessoal corrigido!")
