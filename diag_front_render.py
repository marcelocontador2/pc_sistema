c = open("pc_frontend/conferencia.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) FUNCAO QUE RENDERIZA OS CARTOES (renderizarCartoes)")
print("=" * 70)
idx = c.find("function renderizarCartoes")
if idx != -1:
    fim = c.find("\n        function ", idx + 10)
    if fim == -1:
        fim = c.find("\n    </script>", idx)
    if fim == -1:
        fim = idx + 2000
    print(c[idx:fim])
else:
    print("[ERRO] Funcao renderizarCartoes nao encontrada.")

print("\n" + "=" * 70)
print("2) FUNCAO QUE CARREGA OS DADOS (fetch da API)")
print("=" * 70)
# Procura o fetch que chama a API de conferencia
idx = c.find("fetch('/api/conferencia/'")
if idx == -1:
    idx = c.find('fetch("/api/conferencia/"')
if idx != -1:
    fim = c.find("});", idx) + 3
    if fim == -1:
        fim = idx + 1000
    print(c[idx:fim])
else:
    print("[ERRO] Fetch da API nao encontrado.")
