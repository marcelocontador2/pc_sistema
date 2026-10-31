c = open('../pc_frontend/custo_pessoal_pdf_completo.html', encoding='utf-8-sig').read()

# 1. Substituir as variáveis de cor para a paleta oficial COFEN
c = c.replace('--primary: #1a3b5c; /* Azul COFEN */', '--primary: #003366; /* Azul Institucional COFEN */')
c = c.replace('--secondary: #2c5282;', '--secondary: #00509e; /* Azul de Destaque COFEN */')
c = c.replace('--bg-light: #f8fafc;', '--bg-light: #eef4f9; /* Fundo azul acinzentado claro */')
c = c.replace('--text-main: #2d3748;', '--text-main: #1a202c; /* Texto escuro para melhor leitura */')
c = c.replace('--text-muted: #718096;', '--text-muted: #4a5568;')

# 2. Ajustar a cor do texto na tarja (para dar mais contraste)
# Nenhuma mudança necessária, o branco (#ffffff) já está correto.

# 3. Ajustar a cor de fundo do total-row (Azul bem clarinho)
c = c.replace('background-color: #ebf8ff; /* Azul bem claro */', 'background-color: #e6f0fa; /* Azul COFEN super claro */')

open('../pc_frontend/custo_pessoal_pdf_completo.html', 'w', encoding='utf-8').write(c)
print("[OK] Paleta de cores oficial do COFEN aplicada com sucesso!")
