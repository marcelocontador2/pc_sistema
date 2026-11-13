import subprocess
import sys

print("🔧 Instalando xhtml2pdf...")
result = subprocess.run([sys.executable, "-m", "pip", "install", "xhtml2pdf"], capture_output=True, text=True)
print(result.stdout[-500:] if result.stdout else "Sem saída")
print(result.stderr[-500:] if result.stderr else "Sem erro")
print("\n✅ Instalação concluída. Agora vamos reescrever a função de PDF.")
