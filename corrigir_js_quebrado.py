c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# 1. Remove o trecho quebrado do meio do try/catch
trecho_quebrado = """            
            // Se for Centro de Custos, redireciona para a tela de análise
            if (tipo === "Centro de Custos") {
                window.location.href = "/analise_centro_custos";
            }
            """
c = c.replace(trecho_quebrado, "")

# 2. Restaura a estrutura do catch
c = c.replace("} catch (e) {", "} catch (e) {")

# 3. Adiciona o redirecionamento no lugar certo: DEPOIS do bloco try/catch, antes do fechamento da função
# Encontra o fechamento do catch (o último "}" antes do fim da função)
# Como o script é grande, vamos usar um marcador específico: o final do bloco try/catch do upload
marcador_fim = "msgDiv.innerHTML = \"<span style='color: green;'>Upload concluído! Arquivo salvo com sucesso.</span>\";"

if marcador_fim in c:
    # Adiciona o redirecionamento logo após a mensagem de sucesso
    c = c.replace(
        marcador_fim,
        marcador_fim + """
        
        // Redirecionamento para Centro de Custos
        if (tipo === "Centro de Custos") {
            setTimeout(function() { window.location.href = "/analise_centro_custos"; }, 1000);
        }
        """
    )
    print("[OK] Redirecionamento inserido no lugar correto!")
else:
    print("[AVISO] Marcador não encontrado. Verifique manualmente.")

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] index.html corrigido!")
