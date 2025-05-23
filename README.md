# 📊 Coleta de Indicadores Econômicos e Dados Financeiros (B3 + Notícias)

Este projeto automatiza a coleta de:

- Indicadores econômicos do **Banco Central do Brasil (BACEN)** via SGS
- Notícias sobre economia e investimentos de sites como G1, CNN Brasil, InfoMoney e Exame
- Preços diários das **ações mais negociadas da B3** via API da Alpha Vantage

---

## ⚙️ Tecnologias Utilizadas

- Python 3.10+
- `pandas`
- `requests`
- `beautifulsoup4`
- `python-dotenv`

---

## 📁 Estrutura do Projeto

.
├── data/
│ ├── indicadores_economicos.csv
│ ├── noticias_economia.csv
│ └── top_10_acoes.csv
├── .env
├── requirements.txt
└── main.py


---

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com:

ALPHA_VANTAGE_API_KEY=coloque_sua_chave_aqui


> 🔑 Obtenha uma chave gratuita em: https://www.alphavantage.co/support/#api-key

---

## 🚀 Como Executar

1. **Crie o ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows

2. **Instale as dependências::**
   ```bash
   pip install -r requirements.txt

3. **Execute o script:**
   ```bash
   python main.py

## 📌 Funcionalidades

### 📈 Indicadores Econômicos
Busca os últimos dados de:

- IPCA  
- SELIC  
- PIB  
- Dólar  
- Commodities  
- IGP-M  

via API SGS do Banco Central.

---

### 📰 Coleta de Notícias
Extrai notícias relacionadas à economia com base em palavras-chave como:

`"ipca"`, `"inflação"`, `"juros"`, `"bolsa"`, `"ações"`, `"investimentos"`, `"selic"`, etc.

**Fontes utilizadas:**

- CNN Brasil  
- G1 Economia  
- InfoMoney  
- Exame  

---

### 💹 Cotações de Ações da B3
Coleta dados diários (**abertura, alta, baixa, fechamento, volume**) das 10 ações mais negociadas:

`PETR4, VALE3, ITUB4, BBDC4, ABEV3, BBAS3, B3SA3, WEGE3, RENT3, MGLU3`

---

## 📦 Saídas
Os resultados são salvos em arquivos CSV na pasta `data/`:

- `indicadores_economicos.csv`  
- `noticias_economia.csv`  
- `top_10_acoes.csv`

---

## ⚠️ Limites de API

- **Alpha Vantage (versão gratuita):**  
  Máx. **5 chamadas por minuto**.  
  O script aplica `sleep(15)` automaticamente entre as requisições.

- **BACEN e sites de notícias:**  
  Sem limite rígido, mas **sujeitos a mudanças de estrutura** nas páginas HTML.
