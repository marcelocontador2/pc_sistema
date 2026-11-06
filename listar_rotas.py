import requests, json

try:
    r = requests.get("http://127.0.0.1:9994/openapi.json", timeout=10)
    data = r.json()
    print("=== ROTAS QUE CONTÊM 'liquidez' ===")
    for path in sorted(data.get("paths", {}).keys()):
        if "liquidez" in path.lower() or "liquidity" in path.lower():
            methods = ", ".join(m.upper() for m in data["paths"][path].keys())
            print(f"  [{methods}] {path}")
    print()
    print("=== TODAS AS ROTAS (para conferência) ===")
    for path in sorted(data.get("paths", {}).keys()):
        methods = ", ".join(m.upper() for m in data["paths"][path].keys())
        print(f"  [{methods}] {path}")
except Exception as e:
    print("Erro:", e)
