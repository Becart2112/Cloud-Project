from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# URL de la Function App (récupérée depuis outputs Terraform)
FUNCTION_URL = os.environ.get("FUNCTION_APP_URL", "http://localhost:7071")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/upload", methods=["POST"])
def upload():
    """Proxy vers la Function App"""
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file"}), 400
    
    files = {'file': (file.filename, file.stream, file.content_type)}
    resp = requests.post(f"{FUNCTION_URL}/api/upload", files=files)
    return resp.json(), resp.status_code

@app.route("/api/documents", methods=["GET"])
def get_documents():
    """Récupérer liste des documents"""
    resp = requests.get(f"{FUNCTION_URL}/api/documents")
    return resp.json(), resp.status_code

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)