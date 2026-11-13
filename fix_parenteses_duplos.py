import shutil

caminho = "pc_frontend/integridade.html"
shutil.copy(caminho, caminho + ".bak_fix_parenteses_conf")

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

# Localiza a função normalizarMatriz
idx_inicio = html.find("function normalizarMatriz(")
if idx_inicio != -1:
    i = html.find("{", idx_inicio)
    c = 1
    i += 1
    while i < len(html) and c > 0:
        if html[i] == "{": c += 1
        elif html[i] == "}": c -= 1
        i += 1
    
    # Substitui a função com a lógica de limpar parênteses duplicados
    nova_funcao = '''function normalizarMatriz(matriz) {
        if (!matriz || matriz.length === 0) return [];
        
        return matriz.map(m => {
            // Limpa a string de conf para evitar parênteses duplicados
            let conf = m.conf;
            if (conf && typeof conf === 'string') {
                // Remove todos os parênteses existentes
                let limpo = conf.replace(/[()]/g, '');
                // Se for um número, coloca apenas um par de parênteses
                if (!isNaN(parseInt(limpo)) && limpo !== "0" && limpo !== "") {
                    conf = `(${limpo})`;
                } else {
                    conf = limpo; // Se for "OK" ou outra coisa, deixa sem parênteses
                }
            }

            // Converte o formato novo para o antigo, se necessário
            return {
                item: m.item || m.descricao || m.nomenclatura || '',
                balancete: m.balancete || m.valor_balancete || m.valor || '-',
                bp: m.bp || m.valor_bp || '-',
                bf: m.bf || m.valor_bf || '-',
                bo: m.bo || m.valor_bo || '-',
                dfc: m.dfc || m.valor_dfc || '-',
                dvp: m.dvp || m.valor_dvp || '-',
                dmpl: m.dmpl || m.valor_dmpl || '-',
                conf: conf || 'OK'
            };
        });
    }'''
    
    html = html[:idx_inicio] + nova_funcao + html[i:]
    
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Função 'normalizarMatriz' ajustada para limpar parênteses duplicados!")
else:
    print("❌ Função 'normalizarMatriz' não encontrada no arquivo.")
