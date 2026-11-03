import re, shutil, datetime

html_path = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_frontend\importar.html"

# Backup
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(html_path, html_path + f".bak_{ts}")
print(f"[OK] Backup: importar.html.bak_{ts}")

h = open(html_path, encoding="utf-8-sig").read()

# Se já tem a opção, não duplica
if 'value="COMPARATIVO_DESPESAS"' in h or "value='COMPARATIVO_DESPESAS'" in h:
    print("[!] Opcao COMPARATIVO_DESPESAS ja existe. Nada a fazer.")
else:
    # Insere logo depois da option do BALANCETE (primeira opcao do select)
    padrao = r'(<option\s+value="BALANCETE"[^>]*>[^<]*</option>)'
    nova = r'\1\n            <option value="COMPARATIVO_DESPESAS">Comparativo de Despesas</option>'
    h2, n = re.subn(padrao, nova, h, count=1)
    if n == 1:
        open(html_path, "w", encoding="utf-8").write(h2)
        print("[OK] Opcao 'Comparativo de Despesas' adicionada ao select!")
    else:
        # Fallback: insere antes do </select>
        h2, n = re.subn(r'(</select>)', r'\n            <option value="COMPARATIVO_DESPESAS">Comparativo de Despesas</option>\n\1', h, count=1)
        if n == 1:
            open(html_path, "w", encoding="utf-8").write(h2)
            print("[OK] Opcao adicionada (fallback antes de </select>)!")
        else:
            print("[ERRO] Nao consegui encontrar o select. Verifique manualmente.")
