c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Encontra o trecho atual onde a mensagem de sucesso é exibida
trecho_antigo = 'msgDiv.innerHTML = "<span style=\'color: green;\'>Sucesso! " + (result.mensagem || "Arquivo enviado.") + " (" + (result.arquivo || "") + ")</span>";'

# Cria um novo trecho mais robusto, com o nome do arquivo e a mensagem do backend
trecho_novo = '''msgDiv.innerHTML = "<div style='background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin-top: 15px;'><strong>✅ Upload realizado com sucesso!</strong><br><strong>Arquivo:</strong> " + (result.arquivo || arquivo.name) + "<br><strong>Tipo:</strong> " + (tipo || "Não informado") + "<br><strong>Detalhe:</strong> " + (result.mensagem || "Processado com sucesso.") + "</div>";'''

if trecho_antigo in c:
    c = c.replace(trecho_antigo, trecho_novo)
    open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
    print("[OK] Mensagem de sucesso padronizada inserida!")
else:
    print("[AVISO] Trecho antigo não encontrado. Tentando abordagem alternativa...")
    # Fallback: procura qualquer msgDiv.innerHTML com "Sucesso"
    import re
    padrao = r'msgDiv\.innerHTML = "<span style=\'color: green;\'>Sucesso!.*?</span>";'
    if re.search(padrao, c):
        c = re.sub(padrao, trecho_novo, c, flags=re.DOTALL)
        open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
        print("[OK] Mensagem de sucesso substituída via regex!")
    else:
        print("[ERRO] Não foi possível encontrar a mensagem de sucesso no HTML.")
