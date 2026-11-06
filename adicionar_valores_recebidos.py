import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_valores_recebidos_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Localiza o bloco que gera os cards dos grupos
# Vou procurar o trecho exato e substituir
padrao_antigo = r"""let htmlGrupos = '';
gruposAt\.forEach\(function\(g\) \{
    const anterior = \(gruposAn\.find\(function\(x\) \{ return x\.nome === g\.nome; \}\) \|\| \{\}\)\.realizado \|\| 0;
    const variacao = \(g\.realizado \|\| 0\) - anterior;
    const pct = anterior > 0 \? \(variacao / anterior\) \* 100 : 0;
    const cor = variacao >= 0 \? '#10b981' : '#dc2626';
    const seta = variacao >= 0 \? '▲' : '▼';
    htmlGrupos \+= 
        '<div class="grupo-item" style="border-left-color: ' \+ cor \+ ';">' \+
            '<div class="grupo-nome">' \+ capitalizeNome\(g\.nome\) \+ '</div>' \+
            '<div class="grupo-valor" style="color: ' \+ cor \+ ';">' \+ seta \+ ' ' \+ fmtMi\(variacao\) \+ '</div>' \+
            '<div class="grupo-descricao">' \+ \(anterior > 0 \? fmtPct\(pct\) \+ ' em relacao ao anterior' : 'Sem dados anteriores'\) \+ '</div>' \+
        '</div>';
\}\);"""

novo_bloco = """let htmlGrupos = '';
gruposAt.forEach(function(g) {
    const valorAtual = g.realizado || 0;
    const anterior = (gruposAn.find(function(x) { return x.nome === g.nome; }) || {}).realizado || 0;
    const variacao = valorAtual - anterior;
    const pct = anterior > 0 ? (variacao / anterior) * 100 : 0;
    const cor = variacao >= 0 ? '#10b981' : '#dc2626';
    const seta = variacao >= 0 ? '▲' : '▼';
    
    // Valores formatados
    const txtAtual = fmtMi(valorAtual);
    const txtAnterior = anterior > 0 ? fmtMi(anterior) : '—';
    const txtVariacao = fmtMi(variacao);
    const txtPct = anterior > 0 ? fmtPct(pct) : 'Sem dados anteriores';
    
    htmlGrupos += 
        '<div class="grupo-item" style="border-left-color: ' + cor + ';">' +
            '<div class="grupo-nome">' + capitalizeNome(g.nome) + '</div>' +
            '<div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px; margin-bottom: 4px;">' +
                '<div style="font-size: 13px; color: #1e293b;">' +
                    '<strong>Recebido:</strong> ' + txtAtual +
                '</div>' +
                '<div style="font-size: 11px; color: #64748b;">' +
                    'Anterior: ' + txtAnterior +
                '</div>' +
            '</div>' +
            '<div style="font-size: 12px; color: ' + cor + '; font-weight: bold;">' +
                seta + ' ' + txtVariacao + ' (' + txtPct + ')' +
            '</div>' +
        '</div>';
});"""

if re.search(padrao_antigo, c, re.DOTALL):
    c = re.sub(padrao_antigo, novo_bloco, c, flags=re.DOTALL)
    print("[OK] Bloco de cards atualizado com os valores recebidos!")
else:
    print("[AVISO] Não encontrei o bloco exato. Tentando substituição mais flexível...")
    # Fallback: substitui apenas a linha que monta o html
    padrao_flex = r"htmlGrupos \+= \s*'<div class=\"grupo-item\".*?</div>';"
    novo_flex = """htmlGrupos += 
        '<div class="grupo-item" style="border-left-color: ' + cor + ';">' +
            '<div class="grupo-nome">' + capitalizeNome(g.nome) + '</div>' +
            '<div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px; margin-bottom: 4px;">' +
                '<div style="font-size: 13px; color: #1e293b;">' +
                    '<strong>Recebido:</strong> ' + fmtMi(g.realizado || 0) +
                '</div>' +
                '<div style="font-size: 11px; color: #64748b;">' +
                    'Anterior: ' + (anterior > 0 ? fmtMi(anterior) : '—') +
                '</div>' +
            '</div>' +
            '<div style="font-size: 12px; color: ' + cor + '; font-weight: bold;">' +
                seta + ' ' + fmtMi(variacao) + ' (' + (anterior > 0 ? fmtPct(pct) : 'Sem dados anteriores') + ')' +
            '</div>' +
        '</div>';"""
    if re.search(padrao_flex, c, re.DOTALL):
        c = re.sub(padrao_flex, novo_flex, c, flags=re.DOTALL)
        print("[OK] Substituição via fallback aplicada.")
    else:
        print("[ERRO] Não consegui localizar o bloco de geração dos cards.")

# Ajusta o CSS da classe .grupo-item para melhorar o espaçamento
c = c.replace(
    '.grupo-item {\n            display: block;\n            background: #f8fafc;\n            padding: 10px 15px;\n            margin-bottom: 8px;\n            border-left: 4px solid #ccc;\n            border-radius: 4px;\n        }',
    '.grupo-item {\n            display: block;\n            background: #f8fafc;\n            padding: 12px 15px;\n            margin-bottom: 10px;\n            border-left: 4px solid #ccc;\n            border-radius: 4px;\n            transition: background 0.15s;\n        }\n        .grupo-item:hover {\n            background: #f1f5f9;\n        }'
)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] CSS ajustado e arquivo salvo.")
