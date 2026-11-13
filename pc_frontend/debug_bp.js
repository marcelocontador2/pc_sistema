// ===== 2. ANÁLISE BP =====
H += tit(2, 'Análise do Balanço Patrimonial');
H += '<div class="desc">DEBUG: Estrutura recebida do backend.</div>';

try {
    const bpRaw = unwrap(D.analise_bp) || D.balanco_patrimonial || D.bp || null;
    if (bpRaw) {
        H += '<div style="border: 2px solid red; padding: 10px; background: #fff; font-family: monospace; font-size: 11px; color: black;">';
        H += '<b>OBJETO ENCONTRADO! Chaves disponíveis:</b><br>';
        H += '<ul>';
        Object.keys(bpRaw).forEach(k => {
            let val = bpRaw[k];
            let tipo = typeof val;
            let amostra = tipo === 'object' && val !== null ? JSON.stringify(val).substring(0, 50) : String(val).substring(0, 50);
            H += `<li><b>${k}</b> (${tipo}): ${amostra}</li>`;
        });
        H += '</ul></div>';
    } else {
        H += '<p style="color:red;">O objeto D.analise_bp está vazio ou não foi encontrado.</p>';
    }
} catch (e) {
    H += '<p style="color:red;">Erro: ' + e.message + '</p>';
}
