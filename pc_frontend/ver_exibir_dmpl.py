import re
import shutil

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_exibir_dmpl")

# Vamos ver o que a funcao exibirSelecionado faz atualmente
match = re.search(r'function\s+exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    print("=== FUNCAO EXIBIR SELECIONADO ATUAL ===")
    print(match.group(0)[:1500])
    
    # Vamos ver tambem a funcao carregarHistorico para saber onde os dados sao guardados
    print("\n=== FUNCAO CARREGAR HISTORICO (PARA VER ONDE SALVA OS DADOS) ===")
    match2 = re.search(r'function\s+carregarHistorico\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
    if match2:
        print(match2.group(0)[:1500])
else:
    print("Funcao exibirSelecionado nao encontrada.")
