import pandas as pd
import folium
from folium.plugins import MarkerCluster, LocateControl
import logging
import os
from math import radians, sin, cos, sqrt, atan2
import json

# Configura logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define o caminho absoluto para o CSV baseado no local do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "..", "data", "butecos.csv")

def haversine(lat1, lon1, lat2, lon2):
    """Calcula a distância (em km) entre dois pontos usando a fórmula de Haversine."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def adicionar_pin(mapa, boteco, is_within_radius=False):
    """Adiciona um pin ao mapa com um popup elegante."""
    if "lat" in boteco and "lon" in boteco and boteco["lat"] is not None and boteco["lon"] is not None:
        html = f"""
        <div style="font-family: 'Arial', sans-serif; width: 250px; padding: 15px; background: linear-gradient(135deg, #f5f7fa, #c3cfe2); border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
            <h3 style="margin: 0 0 10px; font-size: 18px; color: #2c3e50; text-align: center; text-shadow: 1px 1px 1px rgba(255,255,255,0.5);">{boteco['nome']}</h3>
            <p style="margin: 0 0 10px; font-size: 14px; color: #34495e; line-height: 1.4;"><i class="fa fa-map-marker" style="margin-right: 5px;"></i>{boteco['endereco']}</p>
            <img src="{boteco['imagem']}" style="width: 100%; height: auto; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" onerror="this.src='https://via.placeholder.com/200x150';">
            <div style="display: flex; justify-content: space-between;">
                <a href="{boteco['detalhes_url']}" target="_blank" style="text-decoration: none; background: #e74c3c; color: white; padding: 8px 12px; border-radius: 5px; font-size: 13px; transition: background 0.3s;">Detalhes</a>
                <a href="{boteco['mapa_url']}" target="_blank" style="text-decoration: none; background: #3498db; color: white; padding: 8px 12px; border-radius: 5px; font-size: 13px; transition: background 0.3s;">Como Chegar</a>
            </div>
        </div>
        """
        icon_color = "green" if is_within_radius else "orange"
        folium.Marker(
            location=[boteco["lat"], boteco["lon"]],
            popup=folium.Popup(html, max_width=300),
            icon=folium.Icon(color=icon_color, icon="utensils", prefix="fa")
        ).add_to(mapa)
    else:
        logging.warning(f"Não foi possível adicionar o pin para o buteco '{boteco['nome']}' - coordenadas inválidas.")

def criar_mapa(csv_path=CSV_PATH, output_file="index.html"):
    """Cria um mapa interativo com pins dos butecos, localização do usuário, raio ajustável e busca."""
    logging.info("Iniciando a criação do mapa...")
    
    # Inicializa o mapa centrado em Belo Horizonte
    mapa = folium.Map(
        location=[-19.9208, -43.9378],
        zoom_start=12,
        tiles="OpenStreetMap",
        control_scale=True
    )
    
    marker_cluster = MarkerCluster().add_to(mapa)
    
    try:
        logging.info(f"Tentando carregar o arquivo: {csv_path}")
        df = pd.read_csv(csv_path)
        logging.info(f"Carregado {len(df)} butecos do arquivo {csv_path}")
        
        # Valida e limpa dados do CSV
        df = df[["nome", "endereco", "lat", "lon", "imagem", "detalhes_url", "mapa_url"]].fillna("")
        for _, boteco in df.iterrows():
            adicionar_pin(marker_cluster, boteco.to_dict(), is_within_radius=False)
        
        LocateControl(
            auto_start=True,
            strings={"title": "Encontrar minha localização", "popup": "Você está aqui"}
        ).add_to(mapa)
        
        mapa.save(output_file)
        logging.info(f"Mapa criado com sucesso! O arquivo foi salvo como '{output_file}'.")
    
    except FileNotFoundError:
        logging.error(f"Arquivo {csv_path} não encontrado. Verifique o caminho.")
        raise
    except Exception as e:
        logging.error(f"Erro ao criar o mapa: {e}")
        raise

if __name__ == "__main__":
    logging.info("Iniciando o processo...")
    criar_mapa()