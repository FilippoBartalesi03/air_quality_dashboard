from flask import Flask, jsonify, redirect
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
import logging
import os

app = Flask(__name__)
CORS(app)  # Abilita CORS per le richieste dal frontend

# Configurazione logging
logging.basicConfig(level=logging.INFO)

# URL base dell'API upstream
API_BASE_URL = "https://api.zeroc.green/v1"

def calculate_weighted_average(data_points):
    """
    Calcola la media ponderata per gli ultimi 7 giorni disponibili (dei 10 forniti dall'API).
    Esclude i giorni con sample_size = 0.
    
    weighted_average = Σ(average * sample_size) / Σ(sample_size)
    """
    if not data_points:
        return None
    
    # Ordina per data decrescente (più recente prima) e prendi i primi 10
    try:
        sorted_points = sorted(data_points, key=lambda x: x.get('date', ''), reverse=True)[:10]
    except:
        sorted_points = data_points[:10]
    
    # Filtra solo quelli con sample_size > 0 e prendi i primi 7
    valid_points = [point for point in sorted_points if point.get('sample_size', 0) > 0][:7]
    
    if not valid_points:
        return None
    
    total_weighted_sum = sum(point['average'] * point['sample_size'] for point in valid_points)
    total_sample_size = sum(point['sample_size'] for point in valid_points)
    
    if total_sample_size == 0:
        return None
    
    return round(total_weighted_sum / total_sample_size, 6)

def add_weighted_averages(station_data):
    """
    Aggiunge le medie ponderate per ogni metrica ai dati della stazione.
    L'API restituisce metrics come array di oggetti: [{name, data_points, ...}, ...]
    """
    if 'metrics' not in station_data or not isinstance(station_data['metrics'], list):
        return station_data
    
    # Aggiungi campo weighted_averages
    station_data['weighted_averages'] = {}
    
    for metric in station_data['metrics']:
        metric_name = metric.get('name')
        data_points = metric.get('data_points', [])
        
        if metric_name and data_points:
            weighted_avg = calculate_weighted_average(data_points)
            station_data['weighted_averages'][metric_name] = weighted_avg
    
    return station_data

# ---------- Route root - Redirect to stations ----------
@app.route("/")
def home():
    return redirect("/api/stations")

# ---------- Lista di tutte le stazioni ----------
@app.route("/api/stations")
def get_stations():
    try:
        # L'API richiede trailing slash
        response = requests.get(f"{API_BASE_URL}/stations/", timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        logging.error(f"Errore nel recupero delle stazioni: {e}")
        return jsonify({"error": "Impossibile recuperare le stazioni", "details": str(e)}), 502

# ---------- Dati di una singola stazione ----------
@app.route("/api/stations/<station_id>")
def get_station(station_id):
    try:
        # L'API NON richiede trailing slash per l'ID
        response = requests.get(f"{API_BASE_URL}/stations/{station_id}", timeout=10)
        response.raise_for_status()
        station_data = response.json()
        
        # Aggiungi le medie ponderate
        station_data = add_weighted_averages(station_data)
        
        logging.info(f"Weighted averages for station {station_id}: {station_data.get('weighted_averages')}")
        
        return jsonify(station_data)
    except requests.exceptions.RequestException as e:
        logging.error(f"Errore nel recupero della stazione {station_id}: {e}")
        return jsonify({"error": "Impossibile recuperare i dati della stazione", "details": str(e)}), 502

# ---------- Avvio server ----------
if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 5001))  # Porta 5001 di default
    logging.info("Starting Flask backend on port %d", port)
    app.run(debug=True, host="127.0.0.1", port=port)