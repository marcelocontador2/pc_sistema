import shutil
import os

caminho = "pc_frontend/integridade.html"

# Lista todos os backups disponíveis
backups = [
    "pc_frontend/integridade.html.bak_fix_integridade_final",
    "pc_frontend/integridade.html.bak_reconstrucao_integridade",
    "pc_frontend/integridade.html.bak_fix_async_integridade",
]

print("🔍 Backups disponíveis:")
for b in backups:
    if os.path.exists(b):
        print(f"   ✅ {b} ({os.path.getsize(b)} bytes)")
    else:
        print(f"   ❌ {b} (não encontrado)")

# Restaura o backup mais recente que existe
for b in backups:
    if os.path.exists(b):
        shutil.copy(b, caminho)
        print(f"\n✅ Restaurado: {b} → {caminho}")
        break
else:
    print("\n❌ Nenhum backup encontrado!")

# Mostra o tamanho do arquivo restaurado
print(f"📏 Tamanho do arquivo restaurado: {os.path.getsize(caminho)} bytes")
