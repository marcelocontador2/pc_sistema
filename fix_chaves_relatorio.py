import shutil
import re

caminho_html = "pc_frontend/relatorio_consolidado.html"
shutil.copy(caminho_html, caminho_html + ".bak_fix_chaves_desbalanceadas")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# Localiza o último bloco <script>
idx_script = html.rfind("<script")
if idx_script == -1:
    print("❌ Nenhum <script> encontrado.")
else:
    # Pega o bloco de script
    idx_fim = html.find("</script>", idx_script)
    if idx_fim == -1:
        print("❌ </script> não encontrado.")
    else:
        bloco = html[idx_script:idx_fim]
        
        # Conta as chaves
        abre = bloco.count("{")
        fecha = bloco.count("}")
        print(f"📊 Chaves abertas: {abre} | Chaves fechadas: {fecha}")
        
        if fecha > abre:
            print(f"⚠️ Há {fecha - abre} chave(s) '}}' sobrando(s). Tentando remover...")
            
            # Estratégia: remover chaves '}' que estão em linhas isoladas no final do bloco
            linhas_bloco = bloco.split("\n")
            chaves_removidas = 0
            
            # Percorre de baixo para cima, removendo linhas que são só "}" no final do bloco (antes do </script>)
            for i in range(len(linhas_bloco) - 1, -1, -1):
                if chaves_removidas >= (fecha - abre):
                    break
                linha = linhas_bloco[i].strip()
                if linha == "}" and i > 0:
                    linhas_bloco[i] = ""
                    chaves_removidas += 1
            
            bloco_corrigido = "\n".join(linhas_bloco)
            html = html[:idx_script] + bloco_corrigido + html[idx_fim:]
            
            print(f"✅ {chaves_removidas} chave(s) removida(s).")
            
            # Verifica novamente
            bloco_novo = html[idx_script:html.find("</script>", idx_script)]
            abre_novo = bloco_novo.count("{")
            fecha_novo = bloco_novo.count("}")
            print(f"📊 Após correção: {abre_novo} abertas | {fecha_novo} fechadas")
            
            if abre_novo == fecha_novo:
                print("✅ Chaves balanceadas com sucesso!")
                with open(caminho_html, "w", encoding="utf-8") as f:
                    f.write(html)
            else:
                print("⚠️ Ainda desbalanceadas. Vou mostrar o final do bloco para você ver.")
                print("\n📌 Últimas 15 linhas do bloco:")
                for linha in bloco_corrigido.split("\n")[-15:]:
                    print(f"   {linha}")
