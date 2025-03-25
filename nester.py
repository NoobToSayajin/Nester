from flask import Flask, request, jsonify, render_template
import sqlite3
import json
import os

app = Flask(__name__)

# Ajouter le filtre 'json' à l'environnement Jinja2
app.jinja_env.filters['json'] = json.dumps

# Configuration de la base de données
DATABASE = 'seahawks.db'

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
    """Reçoit les données du scan et les insère dans la base de données."""
    data = request.json

    # Log des données reçues
    print("Données reçues :", json.dumps(data, indent=4))  # Affiche les données dans la console Flask

    # Validation des données
    if not data:
        return jsonify({"status": "error", "message": "Aucune donnée reçue"}), 400

    # Vérification des champs obligatoires
    required_fields = ["franchise_id", "ip_address", "scan_data"]
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "error", "message": f"Champ manquant : {field}"}), 400

    # Vérification du type des champs
    if not isinstance(data["franchise_id"], str):
        return jsonify({"status": "error", "message": "franchise_id doit être une chaîne de caractères"}), 400

    if not isinstance(data["ip_address"], str):
        return jsonify({"status": "error", "message": "ip_address doit être une chaîne de caractères"}), 400

    if not isinstance(data["scan_data"], dict):
        return jsonify({"status": "error", "message": "scan_data doit être un dictionnaire"}), 400

    # Insertion des données dans la base de données
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scan_results (franchise_id, ip_address, connected_devices, latency, scan_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data.get("franchise_id"),
                data.get("ip_address"),
                data.get("connected_devices", 0),
                data.get("latency", 0),
                json.dumps(data.get("scan_data", {}))  # Convertir les données de scan en JSON
            ))
            conn.commit()
        return jsonify({"status": "success"}), 200
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Route pour afficher les données dans l'interface web
@app.route('/')
def index():
    """Affiche les résultats des scans dans l'interface web."""
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM scan_results ORDER BY timestamp DESC')
            results = cursor.fetchall()
            print("Résultats de la base de données :", results)  # Affiche les résultats dans la console Flask
            return render_template('index.html', results=results)
    except sqlite3.Error as e:
        return f"Erreur de base de données : {str(e)}", 500

# Création du fichier HTML pour l'interface web (à exécuter une seule fois)
def create_html_template():
    """Crée le fichier HTML pour l'interface web."""
    if not os.path.exists('templates'):
        os.makedirs('templates')

    html_content = '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Seahawks Nester</title>
        <style>
            .refresh-button {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .refresh-button:hover {
                background-color: #45a049;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                padding: 10px;
                text-align: left;
                border: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
            }
        </style>
    </head>
    <body>
        <h1>Résultats des scans</h1>
        <button class="refresh-button" onclick="refreshPage()">Actualiser</button>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Franchise ID</th>
                    <th>IP Address</th>
                    <th>Connected Devices</th>
                    <th>Latency</th>
                    <th>Scan Data</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                {% for row in results %}
                <tr>
                    <td>{{ row[0] }}</td>
                    <td>{{ row[1] }}</td>
                    <td>{{ row[2] }}</td>
                    <td>{{ row[3] }}</td>
                    <td>{{ row[4] }}</td>
                    <td>
                        <pre>
                            {% if row[5] %}
                                {{ row[5] | tojson(indent=4) }}
                            {% else %}
                                Aucune donnée de scan
                            {% endif %}
                        </pre>
                    </td>
                    <td>{{ row[6] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <script>
            function refreshPage() {
                window.location.reload();
            }
        </script>
    </body>
    </html>
    '''

    with open('templates/index.html', 'w') as f:
        f.write(html_content)

if __name__ == '__main__':
    # Initialisation de la base de données et création du template HTML
    init_db()
    create_html_template()

    # Démarrer l'application Flask
    app.run(host='192.168.40.131', port=5000, debug=True)  # Activez le mode debug pour plus de logs