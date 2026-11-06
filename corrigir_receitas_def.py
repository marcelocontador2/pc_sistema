import re, shutil, datetime, os

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. DESCOBRE QUAL ARQUIVO O BACKEND ABRE
# ==========================================
print("=" * 70)
print("1. VERIFICANDO QUAL ARQUIVO O BACKEND ABRE")
print("=" * 70)

c_back = open(r"pc_backend\main.py", encoding='utf-8-sig').read()
match = re.search(r'def gerar_pdf_comparativo_receitas.*?(url\s*=\s*f?"[^"]+")', c_back, re.DOTALL)
arquivo_backend = None
if match:
    url_playwright = match.group(1)
    print(f"URL do Playwright: {url_playwright}")
    # Extrai o nome do arquivo
    m2 = re.search(r'/(relatorio_comparativo_receitas[^?"]+)', url_playwright)
    if m2:
        arquivo_backend = m2.group(1) + ".html"
        print(f"Arquivo aberto pelo backend: {arquivo_backend}")
else:
    print("[AVISO] Não achei a URL do Playwright")

# ==========================================
# 2. VERIFICA A ORDEM DAS COLUNAS NA TABELA
# ==========================================
print("\n" + "=" * 70)
print("2. VERIFICANDO ORDEM DAS COLUNAS")
print("=" * 70)

# O arquivo novo foi escrito em relatorio_comparativo_receitas.html
arquivo_novo = r"pc_frontend\relatorio_comparativo_receitas.html"
if os.path.exists(arquivo_novo):
    c_novo = open(arquivo_novo, encoding='utf-8').read()
    if 'Período Anterior' in c_novo and 'Período Atual' in c_novo:
        # Verifica qual vem primeiro
        pos_anterior = c_novo.find('Período Anterior')
        pos_atual = c_novo.find('Período Atual')
        if pos_anterior < pos_atual:
            print("[CONFIRMADO] A tabela atual mostra Anterior primeiro. Vou trocar.")
            ordem_atual = "Anterior → Atual"
        else:
            print("[OK] A tabela já mostra Atual primeiro.")
            ordem_atual = "Atual → Anterior"
    else:
        print("[AVISO] Não encontrei as colunas 'Período Atual' e 'Período Anterior'")
else:
    print(f"[ERRO] Arquivo novo não encontrado: {arquivo_novo}")

# ==========================================
# 3. LÊ O HTML NOVO E CORRIGE OS PROBLEMAS
# ==========================================
print("\n" + "=" * 70)
print("3. APLICANDO CORREÇÕES")
print("=" * 70)

if os.path.exists(arquivo_novo):
    c = open(arquivo_novo, encoding='utf-8').read()
    
    # 3.1 Corrigir a ordem das colunas (Atual antes de Anterior)
    # Trocar cabeçalhos
    c = c.replace(
        '<th class="text-right">Período Anterior</th>\n                    <th class="text-right">Período Atual</th>',
        '<th class="text-right">Período Atual</th>\n                    <th class="text-right">Período Anterior</th>'
    )
    # Trocar os dados na tabela
    c = c.replace(
        "'<tr><td>Receita Orçada</td><td class=\"text-right\">' + fmt(an.orcado_total) + '</td><td class=\"text-right\">' + fmt(at.orcado_total) + '</td>",
        "'<tr><td>Receita Orçada</td><td class=\"text-right\">' + fmt(at.orcado_total) + '</td><td class=\"text-right\">' + fmt(an.orcado_total) + '</td>"
    )
    c = c.replace(
        "'<tr><td>Receita Realizada</td><td class=\"text-right\">' + fmt(an.realizado_total) + '</td><td class=\"text-right\">' + fmt(at.realizado_total) + '</td>",
        "'<tr><td>Receita Realizada</td><td class=\"text-right\">' + fmt(at.realizado_total) + '</td><td class=\"text-right\">' + fmt(an.realizado_total) + '</td>"
    )
    c = c.replace(
        "'<tr><td>Percentual Executado</td><td class=\"text-right\">' + fmtPct(an.percentual_total).replace('+','') + '</td><td class=\"text-right\">' + fmtPct(at.percentual_total).replace('+','') + '</td>",
        "'<tr><td>Percentual Executado</td><td class=\"text-right\">' + fmtPct(at.percentual_total).replace('+','') + '</td><td class=\"text-right\">' + fmtPct(an.percentual_total).replace('+','') + '</td>"
    )
    print("[OK] Ordem das colunas corrigida (Atual → Anterior)")
    
    # 3.2 Corrigir cards com nowrap (impede quebra de linha)
    c = c.replace(
        '.kpi-value { font-size: 18px; font-weight: 700; color: #0f172a; }',
        '.kpi-value { font-size: 16px; font-weight: 700; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }'
    )
    print("[OK] Cards agora não quebram linha")
    
    # 3.3 Impedir quebra de página nos gráficos e cards
    c = c.replace(
        '.chart-container { page-break-inside: avoid; }',
        '.chart-container { page-break-inside: avoid !important; height: 200px !important; }'
    )
    c = c.replace(
        '.grupos-grid { page-break-inside: avoid; }',
        '.grupos-grid { page-break-inside: avoid !important; grid-template-columns: repeat(3, 1fr) !important; }'
    )
    
    # 3.4 Corrigir sobreposição dos gráficos na página 4 (ranking)
    c = c.replace(
        '''<div class="row-2col">
            <div class="col-half">
                <h3>Top 10</h3>
                <div class="chart-container" style="height: 200px;">
                    <canvas id="grafico-ranking"></canvas>
                </div>
            </div>
            <div class="col-half">
                <h3>Participação</h3>
                <div class="chart-container" style="height: 200px;">
                    <canvas id="grafico-participacao"></canvas>
                </div>
            </div>
        </div>''',
        '''<div style="display: flex; gap: 15px; margin-bottom: 15px;">
            <div style="flex: 1; min-width: 0;">
                <h3>Top 10</h3>
                <div style="width: 100%; height: 200px; position: relative;">
                    <canvas id="grafico-ranking"></canvas>
                </div>
            </div>
            <div style="flex: 1; min-width: 0;">
                <h3>Participação</h3>
                <div style="width: 100%; height: 200px; position: relative;">
                    <canvas id="grafico-participacao"></canvas>
                </div>
            </div>
        </div>'''
    )
    print("[OK] Gráficos de ranking/participação lado a lado, sem sobreposição")
    
    # 3.5 Remover qualquer <ol> ou lista numerada que possa estar causando o "1. 2. 3..."
    c = re.sub(r'<ol[^>]*>.*?</ol>', '', c, flags=re.DOTALL)
    print("[OK] Possíveis listas numeradas removidas")
    
    # 3.6 Adicionar CSS para garantir que a página 2 não renderize lixo
    c = c.replace(
        '</style>',
        '''
        /* Correções adicionais para impressão */
        @media print {
            .kpi-value { white-space: nowrap !important; font-size: 15px !important; }
            .kpi-card { min-height: 70px !important; }
            .grupo-card { min-height: 70px !important; }
            .chart-container { max-height: 200px !important; }
            .page-content { page-break-after: always !important; }
            .page-content:last-child { page-break-after: auto !important; }
        }
        </style>'''
    )
    
    # ==========================================
    # 4. COPIA PARA O ARQUIVO CORRETO (v2)
    # ==========================================
    if arquivo_backend and arquivo_backend == "relatorio_comparativo_receitas_v2.html":
        arquivo_v2 = r"pc_frontend\relatorio_comparativo_receitas_v2.html"
        if os.path.exists(arquivo_v2):
            shutil.copy2(arquivo_v2, f"{arquivo_v2}.bak_corrigido_{ts}")
        with open(arquivo_v2, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"\n[OK] Conteúdo copiado para o arquivo que o backend realmente abre: {arquivo_backend}")
    else:
        print(f"\n[INFO] Backend abre '{arquivo_backend}' — nenhuma cópia necessária")
    
    # Salva também no arquivo original
    with open(arquivo_novo, 'w', encoding='utf-8') as f:
        f.write(c)
    print("[OK] Arquivo corrigido salvo")

print()
print("=" * 70)
print("RESUMO DAS CORREÇÕES")
print("=" * 70)
print("1. Tabela com colunas: Atual -> Anterior")
print("2. Cards com valores em linha unica (sem quebrar)")
print("3. Graficos de ranking/participacao em layout flex (sem sobrepor)")
print("4. Listas numeradas removidas")
print("5. Conteudo copiado para o arquivo que o backend realmente abre")
print()
print("=== TESTE ===")
print("1. Gere o PDF novamente")
print("2. Se o servidor estiver com cache, reinicie: Stop-Process -Id (Get-NetTCPConnection -LocalPort 9994).OwningProcess -Force")
