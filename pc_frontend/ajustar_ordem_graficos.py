import re

c = open('relatorio_comparativo_receitas.html', encoding='utf-8-sig').read()

# 1. Gráfico de Grupos: Colocar Período Atual (2026) primeiro, depois Anterior (2025)
trecho_antigo_grupos = """                new Chart(document.getElementById('grafico-grupos').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: labelsGrupos,
                        datasets: [
                            { label: 'Período Anterior', data: gruposAn.map(g => g.realizado / 1000000), backgroundColor: '#5b8fc9', borderRadius: 4 },
                            { label: 'Período Atual', data: gruposAt.map(g => g.realizado / 1000000), backgroundColor: '#0a1c3a', borderRadius: 4 }
                        ]
                    },"""

trecho_novo_grupos = """                new Chart(document.getElementById('grafico-grupos').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: labelsGrupos,
                        datasets: [
                            { label: 'Período Atual', data: gruposAt.map(g => g.realizado / 1000000), backgroundColor: '#0a1c3a', borderRadius: 4 },
                            { label: 'Período Anterior', data: gruposAn.map(g => g.realizado / 1000000), backgroundColor: '#5b8fc9', borderRadius: 4 }
                        ]
                    },"""

if trecho_antigo_grupos in c:
    c = c.replace(trecho_antigo_grupos, trecho_novo_grupos)
    print("[OK] Ordem do gráfico de grupos corrigida (Atual primeiro)!")
else:
    print("[AVISO] Trecho do gráfico de grupos não encontrado.")

# 2. Gráfico de Ranking: Colocar Período Atual (2026) primeiro, depois Anterior (2025)
trecho_antigo_ranking = """                new Chart(document.getElementById('grafico-ranking').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: labelsCores,
                        datasets: [
                            { label: 'Período Anterior', data: valoresAnterior, backgroundColor: '#5b8fc9', borderRadius: 4 },
                            { label: 'Período Atual', data: valoresAtual, backgroundColor: '#0a1c3a', borderRadius: 4 }
                        ]
                    },"""

trecho_novo_ranking = """                new Chart(document.getElementById('grafico-ranking').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: labelsCores,
                        datasets: [
                            { label: 'Período Atual', data: valoresAtual, backgroundColor: '#0a1c3a', borderRadius: 4 },
                            { label: 'Período Anterior', data: valoresAnterior, backgroundColor: '#5b8fc9', borderRadius: 4 }
                        ]
                    },"""

if trecho_antigo_ranking in c:
    c = c.replace(trecho_antigo_ranking, trecho_novo_ranking)
    print("[OK] Ordem do gráfico de ranking corrigida (Atual primeiro)!")
else:
    print("[AVISO] Trecho do gráfico de ranking não encontrado.")

open('relatorio_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
print("[OK] relatorio_comparativo_receitas.html atualizado!")
