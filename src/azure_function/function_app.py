import azure.functions as func
import json
from datetime import datetime
import mimetypes

app = func.FunctionApp()

# Mock storage (en mémoire pour tests locaux)
DOCUMENTS = []

def add_cors_headers(response):
    """Ajoute les headers CORS"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route(route="upload", methods=["POST", "OPTIONS"])
def upload_document(req: func.HttpRequest) -> func.HttpResponse:
    """Upload et traiter un document"""
    if req.method == "OPTIONS":
        return add_cors_headers(func.HttpResponse("OK", status_code=200))
    
    try:
        file = req.files.get('file')
        if not file:
            return add_cors_headers(func.HttpResponse("No file provided", status_code=400))
        
        filename = file.filename
        file_content = file.read()
        
        # Créer métadonnées
        doc_metadata = {
            "documentId": filename,
            "originalName": filename,
            "uploadDate": datetime.utcnow().isoformat(),
            "fileSize": len(file_content),
            "mimeType": mimetypes.guess_type(filename)[0] or "unknown",
            "status": "processed"
        }
        
        DOCUMENTS.append(doc_metadata)
        
        return add_cors_headers(func.HttpResponse(
            json.dumps({"message": "Document uploaded", "id": filename}),
            status_code=200,
            mimetype="application/json"
        ))
    except Exception as e:
        return add_cors_headers(func.HttpResponse(f"Error: {str(e)}", status_code=500))

@app.route(route="documents", methods=["GET", "OPTIONS"])
def list_documents(req: func.HttpRequest) -> func.HttpResponse:
    """Lister tous les documents"""
    if req.method == "OPTIONS":
        return add_cors_headers(func.HttpResponse("OK", status_code=200))
    
    try:
        return add_cors_headers(func.HttpResponse(
            json.dumps(DOCUMENTS),
            status_code=200,
            mimetype="application/json"
        ))
    except Exception as e:
        return add_cors_headers(func.HttpResponse(f"Error: {str(e)}", status_code=500))

@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check"""
    return add_cors_headers(func.HttpResponse("OK", status_code=200))