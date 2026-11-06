import subprocess, os, shutil

# 1. Salva uma cópia do main.py atual
shutil.copy2(r"pc_backend\main.py", r"pc_backend\main_backup_antes_reset.py")
print("[OK] Backup do main.py atual salvo em main_backup_antes_reset.py")

# 2. Mostra o log dos últimos commits (para confirmar o hash)
result = subprocess.run(
    ["git", "log", "--oneline", "-5"],
    capture_output=True, text=True
)
print("\n=== ÚLTIMOS COMMITS ===")
print(result.stdout)

# 3. Restaura o main.py do commit 15c3af0 (o que tinha o PDF funcional)
result = subprocess.run(
    ["git", "checkout", "15c3af0", "--", "pc_backend/main.py"],
    capture_output=True, text=True
)

if result.returncode == 0:
    print("[OK] main.py restaurado do commit 15c3af0.")
else:
    print(f"[ERRO] Falha ao restaurar: {result.stderr}")
    exit()

# 4. Valida a sintaxe
with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

try:
    compile(codigo, "main.py", "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

print("\n[OK] Estado restaurado. O main.py está no estado do último commit funcional.")
print("[INFO] Agora reinicie o servidor e teste o PDF consolidado.")
