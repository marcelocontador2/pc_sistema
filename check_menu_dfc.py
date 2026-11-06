c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()
idx = c.find("analise_financeira_bf")
if idx != -1:
    print("Trecho ao redor do BF e DFC:")
    print(c[max(0, idx-100):idx+500])
