c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

# 1. Remove o gradiente lateral da capa
c = c.replace(
    "background: linear-gradient(to right, #fff 60%, var(--primary) 60%);",
    "background: #fff; position: relative;"
)

# 2. Adiciona uma tarja horizontal no topo da capa (usando ::before)
c = c.replace(
    ".cover h1 { font-size: 48px; color: var(--primary); margin: 0; line-height: 1.1; }",
    ".cover::before {\n                content: '';\n                position: absolute;\n                top: 0;\n                left: 0;\n                width: 100%;\n                height: 80px;\n                background: var(--primary);\n            }\n            .cover h1 { font-size: 48px; color: var(--primary); margin: 120px 0 0 0; line-height: 1.1; }"
)

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Capa ajustada com tarja horizontal no topo!")
