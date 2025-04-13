import requests
from bs4 import BeautifulSoup
import googlemaps
import logging
import concurrent.futures
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Obter a chave da API do ambiente
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    logging.error("Chave da API do Google não encontrada. Verifique o arquivo .env.")
    raise ValueError("Chave da API do Google não encontrada.")

gmaps = googlemaps.Client(key=API_KEY)
def extrair_dados_item(item_div):
    """Extrai dados de um item do buteco."""
    try:
        # Extrai nome
        nome_tag = item_div.find("h2")
        nome = nome_tag.text.strip() if nome_tag else "Nome não encontrado"

        # Extrai endereço
        endereco_tag = item_div.find("p")
        endereco = endereco_tag.text.strip() if endereco_tag else "Endereço não encontrado"

        # Extrai imagem
        imagem_tag = item_div.find("img")
        imagem = imagem_tag["src"] if imagem_tag and imagem_tag.get("src") else None

        # Extrai URL de detalhes
        detalhes_tag = item_div.find("a", text="Detalhes")
        detalhes_url = detalhes_tag["href"] if detalhes_tag and detalhes_tag.get("href") else None

        # Extrai URL do mapa
        mapa_tag = item_div.find("a", class_="address")
        mapa_url = mapa_tag["href"] if mapa_tag and mapa_tag.get("href") else None

        dados = {
            "nome": nome,
            "endereco": endereco,
            "imagem": imagem,
            "detalhes_url": detalhes_url,
            "mapa_url": mapa_url
        }

        # Só retorna se pelo menos nome e endereço forem válidos
        if nome != "Nome não encontrado" and endereco != "Endereço não encontrado":
            return dados
        else:
            logging.warning("Item ignorado: nome ou endereço não encontrados")
            return None

    except Exception as e:
        logging.error(f"Erro ao extrair dados do item: {e}")
        return None

def geocode(endereco):
    """Geocodifica um endereço e retorna latitude e longitude."""
    try:
        geocode_result = gmaps.geocode(endereco)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            logging.info(f"Endereço geocodificado: {endereco} -> Lat: {location['lat']}, Lon: {location['lng']}")
            return location['lat'], location['lng']
        else:
            logging.warning(f"Não foi possível geocodificar o endereço: {endereco}")
            return None, None
    except Exception as e:
        logging.error(f"Erro ao geocodificar o endereço {endereco}: {e}")
        return None, None
    
    
def buscar_informacoes(url, timeout=10):
    """Busca informações de butecos em uma URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        logging.info(f"Buscando informações na URL: {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        butecos = []
        for item_div in soup.find_all("div", class_="item"):
            dados_boteco = extrair_dados_item(item_div)
            if dados_boteco:
                # Geocodifica o endereço
                lat, lon = geocode(dados_boteco["endereco"] + ", Belo Horizonte, MG")
                dados_boteco["lat"] = lat
                dados_boteco["lon"] = lon
                butecos.append(dados_boteco)
        logging.info(f"{len(butecos)} butecos encontrados na página {url}")
        return butecos
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao buscar informações na URL {url}: {e}")
        return []