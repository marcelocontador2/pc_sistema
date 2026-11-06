import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_bp.html"
shutil.copy2(arq, f"{arq}.bak_fmt_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# 1. Ajusta o cabecalho da tabela (remove o "mi")
c = c.replace("Período Atual (R$ mi)", "Período Atual (R$)")
c = c.replace("Período Anterior (R$ mi)", "Período Anterior (R$)")
c = c.replace("Evolução das Principais Contas (R$ mi)", "Evolução das Principais Contas (R$)")

# 2. Ajusta a funcao fmtMil para mostrar o valor cheio (sem dividir por 1 milhao)
antigo_fmt = """function fmtMil(v) {
            return (v / 1000000).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }"""

novo_fmt = """function fmtMil(v) {
            // Mostra o valor cheio, sem dividir por 1 milhao
            return v.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }"""

if antigo_fmt in c:
    c = c.replace(antigo_fmt, novo_fmt)
    print("[OK] Funcao fmtMil ajustada para mostrar valor cheio.")

# 3. Ajusta o grafico para nao dividir por 1 milhao
c = c.replace("d.ativo_circulante.anterior / 1000000", "d.ativo_circulante.anterior")
c = c.replace("d.ativo_nao_circulante.anterior / 1000000", "d.ativo_nao_circulante.anterior")
c = c.replace("d.passivo_circulante.anterior / 1000000", "d.passivo_circulante.anterior")
c = c.replace("d.patrimonio_liquido.anterior / 1000000", "d.patrimonio_liquido.anterior")
c = c.replace("d.ativo_circulante.atual / 1000000", "d.ativo_circulante.atual")
c = c.replace("d.ativo_nao_circulante.atual / 1000000", "d.ativo_nao_circulante.atual")
c = c.replace("d.passivo_circulante.atual / 1000000", "d.passivo_circulante.atual")
c = c.replace("d.patrimonio_liquido.atual / 1000000", "d.patrimonio_liquido.atual")

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Frontend ajustado para mostrar valores cheios (sem cortar milhar).")
