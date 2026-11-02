c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Adiciona o redirecionamento após a mensagem de sucesso
if "redirecionar_centro_custos" not in c:
    trecho_antigo = '''            msgDiv.innerHTML = "<span style='color: green;'>Sucesso! " + (result.mensagem || "Arquivo enviado.") + " (" + (result.arquivo || "") + ")</span>";
            document.getElementById('form-upload').reset();
            document.getElementById('upload-ano').value = "2026";
            desativarOutrosPeriodos('');'''
    
    trecho_novo = '''            msgDiv.innerHTML = "<span style='color: green;'>Sucesso! " + (result.mensagem || "Arquivo enviado.") + " (" + (result.arquivo || "") + ")</span>";
            document.getElementById('form-upload').reset();
            document.getElementById('upload-ano').value = "2026";
            desativarOutrosPeriodos('');
            
            // Redirecionamento para Centro de Custos
            if (tipo && tipo.toUpperCase() === "CENTRO_CUSTOS") {
                setTimeout(function() {
                    window.location.href = "/analise_centro_custos";
                }, 1000);
            }'''
    
    if trecho_antigo in c:
        c = c.replace(trecho_antigo, trecho_novo)
        open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
        print("[OK] Redirecionamento adicionado ao JavaScript!")
    else:
        print("[AVISO] Trecho não encontrado. Verifique manualmente.")
else:
    print("[AVISO] Redirecionamento já existe.")
