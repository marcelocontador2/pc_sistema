# 🚀 REGRAS DE DESENVOLVIMENTO DO SISTEMA PC

Este documento define as diretrizes obrigatórias para qualquer alteração neste sistema, seja feita por um desenvolvedor humano ou por Inteligência Artificial.

## 📜 1. Limite de Código
- **NUNCA** envie ou gere códigos com mais de 500 linhas em um único bloco. 
- Se uma funcionalidade exigir muitas linhas, ela deve ser modularizada em arquivos menores (ex: criar um arquivo .py ou .js separado) e importada para o sistema principal.

## 🛡️ 2. Preservação do Sistema Existente
- **NÃO MEXER** e **NÃO EXCLUIR** nenhuma funcionalidade, rota ou código que já exista e esteja funcionando no sistema.
- Qualquer alteração deve ser apenas uma **adição** ou **refatoração cirúrgica** com backup prévio.

## 🧪 3. Ambiente de Testes (Sandbox)
- Toda nova funcionalidade ou alteração estrutural deve ser implementada primeiro em uma **base temporária** (arquivo separado ou ambiente de teste).
- A alteração só será efetivada no código principal (main.py ou index.html) após autorização expressa do gestor.

## ☁️ 4. Controle de Versão (GitHub)
- Antes de efetivar qualquer mudança no ambiente principal, envie sempre uma cópia do estado atual para o GitHub (Commit e Push).
- Isso garante que, se algo quebrar, possamos voltar para a versão anterior com segurança.

## 🛠️ 5. Tecnologias e Padrões
- **Backend:** Python + FastAPI.
- **Frontend:** HTML + JavaScript (Vanilla) + CSS.
- **Banco de Dados:** SQLite (para histórico e logs) e PostgreSQL (para dados principais).
- **Leitura de Arquivos:** Utilizar a biblioteca nativa csv do Python. Nunca tentar ler dados contábeis usando split() cego, para evitar erros de formatação (aspas, espaços e acentos do Windows).

## 📊 6. Normas Contábeis
- Todos os cálculos de integridade devem seguir rigorosamente:
  - **IPC 05:** DVP
  - **IPC 06:** Balanço Financeiro
  - **IPC 08:** DFC
  - **MCASP / NBC TSP:** Balanço Patrimonial
