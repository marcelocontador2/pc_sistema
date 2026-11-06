import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_bp.html"
shutil.copy2(arq, f"{arq}.bak_grafico_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Corrige a ordem dos dados no grafico (Atual primeiro, Anterior depois)
antigo = """datasets: [
                        {
                            label: 'Anterior',
                            data: [
                                d.ativo_circulante.anterior,
                                d.ativo_nao_circulante.anterior,
                                d.passivo_circulante.anterior,
                                d.patrimonio_liquido.anterior
                            ],
                            backgroundColor: '#5b9bd5',
                            borderRadius: 4
                        },
                        {
                            label: 'Atual',
                            data: [
                                d.ativo_circulante.atual,
                                d.ativo_nao_circulante.atual,
                                d.passivo_circulante.atual,
                                d.patrimonio_liquido.atual
                            ],
                            backgroundColor: '#1f4e79',
                            borderRadius: 4
                        }
                    ]"""

novo = """datasets: [
                        {
                            label: 'Atual',
                            data: [
                                d.ativo_circulante.atual,
                                d.ativo_nao_circulante.atual,
                                d.passivo_circulante.atual,
                                d.patrimonio_liquido.atual
                            ],
                            backgroundColor: '#1f4e79',
                            borderRadius: 4
                        },
                        {
                            label: 'Anterior',
                            data: [
                                d.ativo_circulante.anterior,
                                d.ativo_nao_circulante.anterior,
                                d.passivo_circulante.anterior,
                                d.patrimonio_liquido.anterior
                            ],
                            backgroundColor: '#5b9bd5',
                            borderRadius: 4
                        }
                    ]"""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Grafico corrigido: 'Atual' primeiro, 'Anterior' depois.")
else:
    print("[AVISO] Trecho do grafico nao encontrado. Tentando variacao...")
    # Tenta trocar os labels e as cores
    c = c.replace("label: 'Anterior'", "label: 'ATUAL_TEMP'")
    c = c.replace("label: 'Atual'", "label: 'Anterior'")
    c = c.replace("label: 'ATUAL_TEMP'", "label: 'Atual'")
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Grafico ajustado (variacao).")
