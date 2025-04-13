# Crawler Comida di Buteco

Este projeto coleta informações sobre butecos participantes do Comida di Buteco em Belo Horizonte.

## Configuração
1. Clone o repositório.
2. Crie um ambiente virtual: `python -m venv venv`
3. Ative o ambiente: `source venv/bin/activate` (Linux/Mac) ou `venv\Scripts\activate` (Windows)
4. Instale as dependências: `pip install -r requirements.txt`
5. Crie um arquivo `.env` com a chave da API do Google Maps:
6. Execute o notebook em `notebooks/crawler.ipynb` ou o script em `src/crawler.py`.

## Estrutura
- `data/`: Armazena os CSVs gerados.
- `src/`: Contém o código do crawler.
- `notebooks/`: Contém os notebooks para exploração.