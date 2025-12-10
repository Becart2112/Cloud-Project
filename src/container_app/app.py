from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

#url du site
FUNCTION_URL = os.environ.get("FUNCTION_APP_URL", "http://localhost:7071")

@app.route("/")
def index():
    return render_template("index.html")

# pour upload les docs

@app.route("/api/upload", methods=["POST"])
def upload():
    """Proxy vers la Function App - Upload document"""
    try:
        file = request.files.get('file')
        folder_id = request.form.get('folderId', None)
        
        if not file:
            return jsonify({"error": "No file"}), 400
        
        files = {'file': (file.filename, file.stream, file.content_type)}
        data = {}
        if folder_id:
            data['folderId'] = folder_id
        
        resp = requests.post(f"{FUNCTION_URL}/api/upload", files=files, data=data)
        return resp.json(), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/documents", methods=["GET"])
def get_documents():
    """Récupérer liste des documents (tous ou par dossier)"""
    try:
        folder_id = request.args.get('folderId')
        
        params = {}
        if folder_id:
            params['folderId'] = folder_id
        
        resp = requests.get(f"{FUNCTION_URL}/api/documents", params=params)
        return resp.json(), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# pour faire un osus fichiers (dossier?s)

@app.route("/api/folders", methods=["GET"])
def get_folders():
    """Lister tous les dossiers"""
    try:
        resp = requests.get(f"{FUNCTION_URL}/api/folders")
        return resp.json(), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/folders", methods=["POST"])
def create_folder():
    """Créer un nouveau dossier"""
    try:
        data = request.json
        name = data.get('name')
        
        if not name:
            return jsonify({"error": "Folder name required"}), 400
        
        resp = requests.post(
            f"{FUNCTION_URL}/api/create-folder",
            json={"name": name},
            headers={"Content-Type": "application/json"}
        )
        return resp.json(), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/folders/<folder_id>", methods=["DELETE"])
def delete_folder(folder_id):
    """Supprimer un dossier"""
    try:
        resp = requests.delete(f"{FUNCTION_URL}/api/folders/{folder_id}")
        return resp.json(), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)