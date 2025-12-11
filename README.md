# Tweet Mental Health Analyzer 🧠

Este projeto é uma ferramenta de **Processamento de Linguagem Natural (NLP)** focada em identificar sinais de sofrimento mental (como Ansiedade e Depressão) em tweets, utilizando técnicas de Machine Learning.

## 🚀 Funcionalidades
- Coleta de tweets via scraper (Twikit).
- Pré-processamento de texto (limpeza, tradução).
- Classificação de sentimentos/transtornos (Em desenvolvimento).
- Interface visual com Streamlit.

## 📂 Estrutura
- `src/`: Scripts de coleta e processamento.
- `models/`: Modelos de ML treinados.
- `app.py`: Dashboard interativo (Streamlit).
- `data/`: Datasets (Não incluídos no repousitório por privacidade).

## 🛠️ Instalação

1. Clone o repositório.
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## ⚠️ Nota sobre Cookies
Para usar o scraper, é necessário fornecer suas próprias credenciais/cookies do Twitter. O arquivo `cookies.json` **NÃO** está incluído por motivos de segurança.

