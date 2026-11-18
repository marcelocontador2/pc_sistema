from pathlib import Path
import glob

print("=== ROUTERS (app/routers/) ===")
for arquivo in sorted(glob.glob("pc_backend/app/routers/*.py")):
    nome = Path(arquivo).name
    linhas = len(Path(arquivo).read_text(encoding="utf-8").split("\n"))
    print(f"  {nome:<35} {linhas:>4} linhas")

print()
print("=== INGESTORS (app/ingestion/) ===")
for arquivo in sorted(glob.glob("pc_backend/app/ingestion/*.py")):
    nome = Path(arquivo).name
    linhas = len(Path(arquivo).read_text(encoding="utf-8").split("\n"))
    print(f"  {nome:<35} {linhas:>4} linhas")

print()
print("=== ANALYTICS (app/analytics/) ===")
for arquivo in sorted(glob.glob("pc_backend/app/analytics/*.py")):
    nome = Path(arquivo).name
    linhas = len(Path(arquivo).read_text(encoding="utf-8").split("\n"))
    print(f"  {nome:<35} {linhas:>4} linhas")

print()
print("=== FRONTEND (pc_frontend/*.html) ===")
for arquivo in sorted(glob.glob("pc_frontend/*.html")):
    nome = Path(arquivo).name
    if any(x in nome for x in [".bak", "BROKEN", "_v2", "teste", "debug"]):
        continue
    linhas = len(Path(arquivo).read_text(encoding="utf-8", errors="ignore").split("\n"))
    print(f"  {nome:<40} {linhas:>4} linhas")
