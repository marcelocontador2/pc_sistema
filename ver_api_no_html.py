c = open("pc_frontend/analise_dfc.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("QUAL API O HTML ESTA CHAMANDO?")
print("=" * 70)
if '/api/analise_dfc/' in c:
    print("[OK] O HTML chama /api/analise_dfc/ (correto!)")
elif '/api/analise_financeira_bf/' in c:
    print("[ERRO] O HTML chama /api/analise_financeira_bf/ (errado!)")
else:
    print("[AVISO] Nao encontrei a chamada da API no HTML.")

# Mostra o trecho do fetch
idx = c.find('fetch(')
if idx != -1:
    print("\nTrecho do fetch:")
    print(c[idx:idx+300])
