html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Comparativo de Despesas</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Inter', sans-serif; margin: 0; padding: 40px; }
        h1 { color: #0a1c3a; }
        .card { background: #eef4f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>Relatório Comparativo de Despesas</h1>
    <p>Período: <span id="periodo"></span></p>
    <div class="card">
        <h2>Resumo</h2>
        <p>Despesa Realizada: <strong id="resumo-realizado"></strong></p>
        <p>Despesa Empenhada: <strong id="resumo-empenhado"></strong></p>
    </div>
    <script>
        const params = new URLSearchParams(window.location.search);
        const periodo = params.get('periodo_atual') || '2026-TRIMESTRE-3';
        document.getElementById('periodo').innerText = periodo;
        fetch(`/api/comparativo_despesas_v2/${periodo}?_t=${Date.now()}`, { cache: 'no-store' })
            .then(r => r.json())
            .then(d => {
                if (d.erro) return;
                document.getElementById('resumo-realizado').innerText = 'R$ ' + d.atual.realizado_total.toLocaleString('pt-BR');
                document.getElementById('resumo-empenhado').innerText = 'R$ ' + d.atual.empenhado_total.toLocaleString('pt-BR');
            });
    </script>
</body>
</html>
"""

with open('relatorio_comparativo_despesas.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("[OK] Relatório de Despesas criado!")
