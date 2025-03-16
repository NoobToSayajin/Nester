import os
import json
import sqlite3
import requests
import customtkinter as ctk
from flask import Flask, request, jsonify, render_template
from threading import Thread
from tkinter import ttk

# Configuration
DATABASE = 'seahawks.db'
NESTER_URL = "http://localhost:5000/api/data"
app = Flask(__name__)

def init_db():
    """Initialise la base de données."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                franchise_id TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                connected_devices INTEGER,
                latency INTEGER,
                scan_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Route API pour recevoir les données du Harvester
@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scan_results (franchise_id, ip_address, connected_devices, latency, scan_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (data.get('franchise_id'), data.get('ip_address'), data.get('connected_devices'),
              data.get('latency'), json.dumps(data.get('scan_data'))))
        conn.commit()
    return jsonify({"status": "success"}), 200

# Route pour afficher les données dans l'interface web
@app.route('/')
def index():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scan_results ORDER BY timestamp DESC')
        results = cursor.fetchall()
    return render_template('index.html', results=results)

def fetch_data():
    """Récupère les données de la base de données."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scan_results ORDER BY timestamp DESC')
        return cursor.fetchall()

def update_table():
    """Met à jour le tableau de l'interface graphique."""
    for row in table.get_children():
        table.delete(row)
    for row in fetch_data():
        table.insert('', 'end', values=row)

def send_to_nester(data):
    """Envoie les données au serveur Nester."""
    try:
        response = requests.post(NESTER_URL, json=data)
        print(f"Réponse du serveur: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'envoi des données: {e}")

def start_flask():
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

# Lancer le serveur Flask dans un thread séparé
flask_thread = Thread(target=start_flask, daemon=True)
flask_thread.start()

# Interface graphique avec CustomTkinter
root = ctk.CTk()
root.title("Seahawks Nester")
root.geometry("1000x600")

columns = ("ID", "Franchise ID", "IP Address", "Connected Devices", "Latency", "Scan Data", "Timestamp")
table = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    table.heading(col, text=col)
table.pack(expand=True, fill="both", padx=10, pady=10)

refresh_button = ctk.CTkButton(root, text="Actualiser", command=update_table)
refresh_button.pack(pady=10)

update_table()
root.mainloop()
