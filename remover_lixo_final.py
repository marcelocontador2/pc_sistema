import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Remove o fechamento duplicado no final: </ul> </li> </ul>
    # Procura o padrao "  </ul>\n    </li>\n  </ul>\n" e substitui por "  </ul>\n"
    padrao_lixo = re.compile(r'(\s*</ul>)\s*</li>\s*</ul>\s*', re.IGNORECASE)
    c = padrao_lixo.sub(r'\1', c)

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_fechamento_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        alterados += 1
        print(f"[OK] {arq} - Fechamento duplicado removido.")

print(f"\n[OK] {alterados} arquivos alterados.")
