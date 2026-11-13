import shutil

caminho = "pc_frontend/integridade.html"
shutil.copy(caminho, caminho + ".bak_fix_parenteses_v2")

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Ajustar a função normalizarMatriz para limpar TUDO e colocar 1 parêntese
idx_norm = html.find("function normalizarMatriz(")
if idx_norm != -1:
    i = html.find("{", idx_norm)
    c = 1
    i += 1
    while i < len(html) and c > 0:
        if html[i] == "{": c += 1
        elif html[i] == "}": c -= 1
        i += 1
    
    nova_norm = '''function normalizarMatriz(matriz) {
        if (!matriz || matriz.length === 0) return [];
        
        return matriz.map(m => {
            // Limpa a string de conf
            let conf = m.conf || "OK";
            if (typeof conf === 'string') {
                // Remove TODOS os parênteses e espaços
                let limpo = conf.replace(/[()\\s]/g, '');
                // Se for um número, coloca apenas UM par de parênteses
                if (limpo && !isNaN(parseInt(limpo))) {
                    conf = `(${limpo})`;
                } else {
                    conf = limpo || "OK";
                }
            }

            return {
                item: m.item || m.descricao || m.nomenclatura || '',
                balancete: m.balancete || m.valor_balancete || m.valor || '-',
                bp: m.bp || m.valor_bp || '-',
                bf: m.bf || m.valor_bf || '-',
                bo: m.bo || m.valor_bo || '-',
                dfc: m.dfc || m.valor_dfc || '-',
                dvp: m.dvp || m.valor_dvp || '-',
                dmpl: m.dmpl || m.valor_dmpl || '-',
                conf: conf
            };
        });
    }'''
    html = html[:idx_norm] + nova_norm + html[i:]
    print("✅ normalizarMatriz atualizada (remove todos e poe 1).")

# 2. Ajustar a função renderizarMatriz para colorir corretamente
idx_render = html.find("function renderizarMatriz(")
if idx_render != -1:
    i = html.find("{", idx_render)
    c = 1
    i += 1
    while i < len(html) and c > 0:
        if html[i] == "{": c += 1
        elif html[i] == "}": c -= 1
        i += 1
    
    nova_render = '''function renderizarMatriz(data, container) {
        if (!container) return;
        
        let matriz = data.matriz || [];
        matriz = normalizarMatriz(matriz);

        if (matriz.length === 0) {
            container.innerHTML = '<div class="loading">Nenhum dado encontrado.</div>';
            return;
        }

        let periodoExibicao = data.periodo;
        if (!periodoExibicao) {
            const ano = document.getElementById('ano')?.value || '';
            const tipo = document.getElementById('tipo_periodo')?.value || '';
            const trimestre = document.getElementById('trimestre')?.value || '';
            periodoExibicao = `${ano}-${tipo}-${trimestre}`;
        }

        let html = `
        <div style="background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="text-align: center; color: #003366; font-size: 24px; margin-bottom: 5px;">Matriz de Integridade - ${periodoExibicao}</h3>
            <p style="text-align: center; color: #666; font-size: 14px; margin-bottom: 20px; font-style: italic;">Gerado em: ${new Date().toLocaleString('pt-BR')}</p>
            
            <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 13px;">
                <thead>
                    <tr style="background-color: #004b8d; color: white; text-align: center;">
                        <th style="padding: 10px; border: 1px solid #ccc;">NOMENCLATURA</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">BALANCETE</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">BP</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">BF</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">BO</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">DFC</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">DVP</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">DMPL</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">CONF.</th>
                    </tr>
                </thead>
                <tbody>
        `;

        matriz.forEach(m => {
            let confFormatado = m.conf;
            let corConf = '#006400'; // Verde
            
            // Se a conf for um número entre parênteses, pinta de vermelho
            if (confFormatado && confFormatado.startsWith('(') && confFormatado.endsWith(')')) {
                corConf = '#cc0000'; // Vermelho
            } else if (confFormatado && confFormatado !== 'OK' && confFormatado !== '-') {
                // Se for número solto ou outra coisa, pinta de vermelho
                corConf = '#cc0000';
            }

            html += `
                <tr style="text-align: center; border-bottom: 1px solid #eee;">
                    <td style="padding: 8px; border: 1px solid #ccc; text-align: left; font-weight: bold; color: #333;">${m.item || ''}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.balancete)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.bp)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.bf)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.bo)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.dfc)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.dvp)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.dmpl)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc; font-weight: bold; color: ${corConf};">${confFormatado}</td>
                </tr>
            `;
        });

        html += `</tbody></table></div>`;
        container.innerHTML = html;
    }'''
    html = html[:idx_render] + nova_render + html[i:]
    print("✅ renderizarMatriz atualizada (colore corretamente).")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Correções aplicadas!")
