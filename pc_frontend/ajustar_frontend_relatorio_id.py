c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

# Ajusta a inicialização do fetch para ler o ID da URL
c = c.replace(
    """        const params = new URLSearchParams(window.location.search);
        const periodoAtual = params.get('periodo_atual') || '2026-TRIMESTRE-3';
        const periodoAnterior = params.get('periodo_anterior') || '2025-TRIMESTRE-3';

        fetch(`/api/relatorio_centro_custos?periodo_atual=${periodoAtual}&periodo_anterior=${periodoAnterior}&_t=${Date.now()}`, { cache: 'no-store' })""",
    """        const params = new URLSearchParams(window.location.search);
        const id = params.get('id');
        const periodoAtual = params.get('periodo_atual') || '2026-TRIMESTRE-3';
        const periodoAnterior = params.get('periodo_anterior') || '2025-TRIMESTRE-3';

        // Se tiver ID, busca os dados do histórico específico; senão, busca por período
        let url;
        if (id) {
            url = `/api/relatorio_centro_custos?id=${id}&_t=${Date.now()}`;
        } else {
            url = `/api/relatorio_centro_custos?periodo_atual=${periodoAtual}&periodo_anterior=${periodoAnterior}&_t=${Date.now()}`;
        }

        fetch(url, { cache: 'no-store' })"""
)

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Frontend do relatório ajustado para buscar por ID!")
