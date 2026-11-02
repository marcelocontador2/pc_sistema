c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# 1. Garantir que o tipo_relatorio seja enviado no FormData (já existe na linha 447, mas vamos confirmar)
if 'formData.append("tipo_relatorio", tipo);' not in c:
    # Se não existir, adiciona (improvável, mas por segurança)
    c = c.replace(
        'formData.append("file", arquivo);',
        'formData.append("file", arquivo);\n    formData.append("tipo_relatorio", document.getElementById("tipo_relatorio").value);'
    )

# 2. Após o upload, se for Centro de Custos, redirecionar para a tela de análise
if "processar_redirecionamento_centro_custos" not in c:
    # Adiciona a lógica no final do script de upload (após a resposta)
    c = c.replace(
        "msgDiv.innerHTML = \"<span style='color: green;'>Upload concluído! ",
        "msgDiv.innerHTML = \"<span style='color: green;'>Upload concluído! "
    )
    # Vamos adicionar uma verificação após o try/catch do upload
    # Primeiro, encontramos o fechamento do try/catch
    pos_fim = c.find("} catch (e) {", c.find("const response = await fetch('/upload'"))
    if pos_fim != -1:
        # Encontra o fechamento do catch
        pos_fim_catch = c.find("}", pos_fim) + 1
        if pos_fim_catch != -1:
            script_novo = """
            
            // Se for Centro de Custos, redireciona para a tela de análise
            if (tipo === "Centro de Custos") {
                window.location.href = "/analise_centro_custos";
            }
            """
            c = c[:pos_fim_catch] + script_novo + c[pos_fim_catch:]
            print("[OK] Redirecionamento para Centro de Custos adicionado!")
    else:
        print("[AVISO] Não foi possível encontrar o local exato do catch.")

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] JavaScript atualizado!")
