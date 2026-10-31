c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()

# 1. Corrige o limite (era d.limite, deve ser d.limite_atual)
c = c.replace(
    "const limite = d.limite || (rcl * 0.5);",
    "const limite = d.limite_atual || d.limite || (rcl * 0.5);"
)

# 2. Corrige a margem (era d.margem, deve ser d.margem_disponivel_atual)
c = c.replace(
    "const margem = d.margem || (limite - custo);",
    "const margem = d.margem_disponivel_atual || d.margem || (limite - custo);"
)

open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
print("[OK] JavaScript corrigido! Agora usa limite_atual e margem_disponivel_atual.")
