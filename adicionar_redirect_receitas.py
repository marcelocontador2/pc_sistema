c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Adiciona redirecionamento para Comparativo de Receitas
if "COMPARATIVO_RECEITAS" in c and "analise_comparativo_receitas" not in c:
    # Procura o bloco onde o tipo é verificado para redirecionamento
    trecho_antigo = """            // Redirecionamento para Centro de Custos
            if (tipo && tipo.toUpperCase() === "CENTRO_CUSTOS") {
                setTimeout(function() {
                    window.location.href = "/analise_centro_custos";
                }, 1500);
            }"""
    trecho_novo = """            // Redirecionamento para Centro de Custos
            if (tipo && tipo.toUpperCase() === "CENTRO_CUSTOS") {
                setTimeout(function() {
                    window.location.href = "/analise_centro_custos";
                }, 1500);
            }
            // Redirecionamento para Comparativo de Receitas
            if (tipo && tipo.toUpperCase() === "COMPARATIVO_RECEITAS") {
                setTimeout(function() {
                    window.location.href = "/analise_comparativo_receitas";
                }, 1500);
            }"""
    
    if trecho_antigo in c:
        c = c.replace(trecho_antigo, trecho_novo)
        print("[OK] Redirecionamento para Comparativo de Receitas adicionado!")
    else:
        print("[AVISO] Trecho de redirecionamento não encontrado. Tentando abordagem alternativa...")
        # Se não encontrar, adiciona um novo bloco após o envio do formulário
        # (pode ser necessário ajustar manualmente)
    
    open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
else:
    print("[AVISO] Redirecionamento já existe ou tipo não encontrado.")
