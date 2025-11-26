from flask import Flask, jsonify, redirect # Flask per creare l'app web
from flask_cors import CORS  # CORS per permettere richieste da frontend 
import requests  # Per fare chiamate HTTP verso l'API esterna (upstream)
from datetime import datetime, timedelta # Per gestire date (usato per selezionare ultimi giorni)
import logging # Per stampare messaggi di log (debug, errori, info)
import os # Per leggere variabili d'ambiente (es. porta)

# Creazione dell'app Flask
app = Flask(__name__)
# Abilitazione del CORS (Cross-Origin Resource Sharing)
# Serve per permettere al frontend (ad esempio React o Vue) di comunicare con questo backend
CORS(app)  # CORS per le richieste dal frontend

# Configurazione logging
logging.basicConfig(level=logging.INFO)

# URL base dell'API esterna da cui recuperiamo i dati
API_BASE_URL = "https://api.zeroc.green/v1"

# FUNZIONE: calcolo della media ponderata per gli ultimi 7 giorni

def calculate_weighted_average(data_points):
    """
    Calcola la media ponderata per gli ultimi 7 giorni disponibili (dei 10 forniti dall'API).
    Esclude i giorni con sample_size = 0.
    
    weighted_average = Σ(average * sample_size) / Σ(sample_size)
    """
    # Se non ci sono dati, restituisci None
    if not data_points:
        return None
    
    # Ordina per data decrescente (più recente prima) e prendi i primi 10
    try:
        sorted_points = sorted(data_points, key=lambda x: x.get('date', ''), reverse=True)[:10]
    except:
        sorted_points = data_points[:10]
    
    # Filtra solo i punti che hanno sample_size > 0 (cioè con dati validi)
    # e tieni i primi 7 (ultimi 7 giorni utili)
    valid_points = [point for point in sorted_points if point.get('sample_size', 0) > 0][:7]
    
    # Se dopo il filtro non rimane nulla, restituisci None
    if not valid_points:
        return None
    
    # Calcola il numeratore della formula: somma di (average × sample_size)
    total_weighted_sum = sum(point['average'] * point['sample_size'] for point in valid_points)
    # Calcola il denominatore: somma di tutti i sample_size
    total_sample_size = sum(point['sample_size'] for point in valid_points)
    
    # Se la somma dei pesi è zero, non si può dividere → ritorna None
    if total_sample_size == 0:
        return None
    
    # Applica la formula della media ponderata e arrotonda a 6 decimali
    return round(total_weighted_sum / total_sample_size, 6)

# FUNZIONE: aggiunge la media ponderata ai dati di una stazione
def add_weighted_averages(station_data):
    """
    Aggiunge le medie ponderate per ogni metrica ai dati della stazione.
    L'API restituisce metrics come array di oggetti: [{name, data_points, ...}, ...]
    """
    # Controlla che esista il campo 'metrics' e che sia una lista
    if 'metrics' not in station_data or not isinstance(station_data['metrics'], list):
        return station_data
    
    # Crea un nuovo campo "weighted_averages" nel dizionario dei dati
    station_data['weighted_averages'] = {}
    
    # Scorri tutte le metriche della stazione (es. temperatura, umidità, CO₂)
    for metric in station_data['metrics']:
        metric_name = metric.get('name')
        data_points = metric.get('data_points', [])
        
         # Se la metrica ha un nome e dati validi, calcola la media ponderata
        if metric_name and data_points:
            weighted_avg = calculate_weighted_average(data_points)
            station_data['weighted_averages'][metric_name] = weighted_avg

    # Restituisce i dati completi con le medie ponderate aggiunte
    return station_data

# ---------- Route root - reindirizza a tutte le rotte ----------
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
        return jsonify(response.json()) # Ritorna i dati in formato JSON al frontend
    except requests.exceptions.RequestException as e: # Se c’è un errore (connessione, timeout, ecc.), log e messaggio di errore
        logging.error(f"Errore nel recupero delle stazioni: {e}")
        return jsonify({"error": "Impossibile recuperare le stazioni", "details": str(e)}), 502

# ---------- Dati di una singola stazione ----------
@app.route("/api/stations/<station_id>")
def get_station(station_id):
    try:
        # L'API NON richiede trailing slash per l'ID
        response = requests.get(f"{API_BASE_URL}/stations/{station_id}", timeout=10)
        response.raise_for_status()
        station_data = response.json() # Converte la risposta JSON in dizionario Python
        
        # Aggiungi le medie ponderate
        station_data = add_weighted_averages(station_data) # Calcola e aggiunge le medie ponderate per ogni metrica
        
        logging.info(f"Weighted averages for station {station_id}: {station_data.get('weighted_averages')}") # Log delle medie calcolate (utile per debug)
        
        return jsonify(station_data) # Ritorna i dati completi (originali + medie ponderate)
    except requests.exceptions.RequestException as e:
        logging.error(f"Errore nel recupero della stazione {station_id}: {e}") # Gestione errori di rete o API
        return jsonify({"error": "Impossibile recuperare i dati della stazione", "details": str(e)}), 502

# ---------- Avvio server ----------
if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 5001)) # Legge la porta da variabile d'ambiente (se non c’è, usa 5001 di default)
    logging.info("Starting Flask backend on port %d", port) # Messaggio di log quando il server parte
    app.run(debug=True, host="127.0.0.1", port=port) # Avvia l'app Flask in modalità debug (solo locale)