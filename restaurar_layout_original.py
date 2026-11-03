import os, glob, shutil, re, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos_v2.html"

print("Buscando backups para restaurar o layout original...")

# Procura todos os backups do relatório e pega o mais antigo (original) ou o que tem 'calc'
backups = glob.glob(r"pc_frontend\relatorio_centro_custos_v2.html.bak_*")
backups.sort()

if not backups:
    print("[ERRO] Nenhum backup encontrado! Não será possível restaurar o original.")
    exit()

# Pega o backup que foi feito ANTES das minhas alterações de layout (geralmente o _calc_ ou _espião_)
backup_original = None
for b in backups:
    if "calc" in b or "espiao" in b:
        backup_original = b
        break
if not backup_original:
    backup_original = backups[-1] # Pega o último se não achar o específico

shutil.copy2(backup_original, arquivo)
print(f"[OK] Layout original restaurado a partir de: {backup_original}")

# Agora vamos ler o arquivo restaurado
c = open(arquivo, encoding='utf-8').read()

# 1. Limpa qualquer script de "espião" antigo que tenha ficado
c = re.sub(r'<script id="interceptar_historico">.*?</script>', '', c, flags=re.DOTALL)

# 2. Injeta o Espião Limpo (que calcula os dados corretamente)
novo_espiao = """
    <script id="interceptar_historico">
        (function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            
            if (historicoId) {
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    if (url.includes('/api/relatorio_v2/')) {
                        return originalFetch(`/historico_centro_custos/${historicoId}`, options)
                            .then(res => res.json())
                            .then(data => {
                                const dados = data.dados ? data.dados : data;
                                const centros = dados.centros || [];
                                const centrosAnt = dados.centros_anterior || [];

                                const totalAtual = centros.reduce((acc, c) => acc + c.valor, 0);
                                const totalAnterior = centrosAnt.reduce((acc, c) => acc + c.valor, 0);

                                const variacao = totalAtual - totalAnterior;
                                const variacao_pct = totalAnterior > 0 ? (variacao / totalAnterior) * 100 : 0;

                                let maiorCentro = { nome: "Nenhum", valor: 0 };
                                if (centros.length > 0) {
                                    maiorCentro = centros.reduce((max, c) => c.valor > max.valor ? c : max, centros[0]);
                                }

                                // Retorna o JSON no formato exato que o HTML original espera
                                const respostaFinal = {
                                    atual: {
                                        total: totalAtual,
                                        media_mensal: totalAtual / 9, // Considerando 9 meses no gráfico
                                        maior_centro: maiorCentro
                                    },
                                    anterior: {
                                        total: totalAnterior,
                                        media_mensal: totalAnterior / 9
                                    },
                                    variacao_pct: variacao_pct,
                                    centros: centros,
                                    centros_anterior: centrosAnt
                                };

                                return new Response(JSON.stringify(respostaFinal), { 
                                    headers: { 'Content-Type': 'application/json' } 
                                });
                            });
                    }
                    return originalFetch(url, options);
                };
            }
        })();
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', novo_espiao + '\n</body>', 1)
else:
    c += novo_espiao

# 3. Adiciona APENAS a regra para esconder os botões na impressão (sem quebrar o layout original)
css_botao = """
    <style>
        @media print {
            button, .btn, .no-print { display: none !important; }
            /* Remove aquele texto invisível que estava causando caracteres estranhos na tabela */
            .material-icons, .fas, .far { display: none !important; }
        }
    </style>
"""

if '</head>' in c:
    c = c.replace('</head>', css_botao + '\n</head>', 1)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Relatório restaurado com o layout original, espião de dados e sem o botão na impressão!")
