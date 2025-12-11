import azure.functions as func
import json
from datetime import datetime
import mimetypes
import os
import uuid
from azure.data.tables import TableServiceClient, TableEntity
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

# Configuration
STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = "documents"
DOCUMENTS_TABLE = "documents"
FOLDERS_TABLE = "folders"

def get_table_client(table_name):
    """Get Azure Table Storage client"""
    table_service = TableServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    table_client = table_service.get_table_client(table_name)
    
    # Create table if not exists
    try:
        table_service.create_table(table_name)
    except:
        pass
    
    return table_client

def get_blob_client():
    """Get Azure Blob Storage client"""
    blob_service = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    
    # Create container if not exists
    try:
        blob_service.create_container(BLOB_CONTAINER_NAME)
    except:
        pass
    
    return blob_service.get_container_client(BLOB_CONTAINER_NAME)

def add_cors_headers(response):
    """Add CORS headers"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.function_name("HealthCheck")
@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    try:
        # Test storage connection
        table_client = get_table_client(DOCUMENTS_TABLE)
        blob_client = get_blob_client()
        
        return add_cors_headers(func.HttpResponse(
            json.dumps({
                "status": "healthy",
                "storage": "azure",
                "database": "table_storage",
                "blob": "connected"
            }),
            status_code=200,
            mimetype="application/json"
        ))
    except Exception as e:
        return add_cors_headers(func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        ))

@app.function_name("UploadDocument")
@app.route(route="upload", methods=["POST", "OPTIONS"])
def upload_document(req: func.HttpRequest) -> func.HttpResponse:
    """Upload document"""
    if req.method == "OPTIONS":
        return add_cors_headers(func.HttpResponse("OK", status_code=200))
    
    try:
        file = req.files.get('file')
        folder_id = req.form.get('folderId', 'root')
        
        if not file:
            return add_cors_headers(func.HttpResponse(
                json.dumps({"error": "No file provided"}),
                status_code=400,
                mimetype="application/json"
            ))
        
        filename = file.filename
        file_content = file.read()
        doc_id = str(uuid.uuid4())
        
        # Upload to Blob Storage
        blob_client = get_blob_client()
        blob_name = f"{folder_id}/{doc_id}-{filename}"
        blob_client.upload_blob(blob_name, file_content, overwrite=True)
        blob_url = f"https://maxprojcloudstorage.blob.core.windows.net/{BLOB_CONTAINER_NAME}/{blob_name}"
        
        # Save metadata to Table Storage
        table_client = get_table_client(DOCUMENTS_TABLE)
        entity = TableEntity()
        entity['PartitionKey'] = folder_id
        entity['RowKey'] = doc_id
        entity['originalName'] = filename
        entity['uploadDate'] = datetime.utcnow().isoformat()
        entity['fileSize'] = len(file_content)
        entity['mimeType'] = mimetypes.guess_type(filename)[0] or "unknown"
        entity['blobUrl'] = blob_url
        entity['status'] = "processed"
        
        table_client.create_entity(entity)
        
        return add_cors_headers(func.HttpResponse(
            json.dumps({
                "message": "Document uploaded successfully",
                "id": doc_id,
                "blobUrl": blob_url
            }),
            status_code=200,
            mimetype="application/json"
        ))
        
    except Exception as e:
        return add_cors_headers(func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        ))

@app.function_name("ListDocuments")
@app.route(route="documents", methods=["GET", "OPTIONS"])
def list_documents(req: func.HttpRequest) -> func.HttpResponse:
    """List documents"""
    if req.method == "OPTIONS":
        return add_cors_headers(func.HttpResponse("OK", status_code=200))
    
    try:
        folder_id = req.params.get('folderId', 'root')
        table_client = get_table_client(DOCUMENTS_TABLE)
        
        # Query documents by folder
        entities = table_client.query_entities(f"PartitionKey eq '{folder_id}'")
        
        documents = []
        for entity in entities:
            documents.append({
                "id": entity['RowKey'],
                "originalName": entity.get('originalName'),
                "uploadDate": entity.get('uploadDate'),
                "fileSize": entity.get('fileSize'),
                "mimeType": entity.get('mimeType'),
                "blobUrl": entity.get('blobUrl'),
                "status": entity.get('status'),
                "folderId": entity['PartitionKey']
            })
        
        return add_cors_headers(func.HttpResponse(
            json.dumps(documents),
            status_code=200,
            mimetype="application/json"
        ))
        
    except Exception as e:
        return add_cors_headers(func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        ))

@app.function_name("ListFolders")
@app.route(route="folders", methods=["GET", "OPTIONS"])
def list_folders(req: func.HttpRequest) -> func.HttpResponse:
    """List folders"""
    if req.method == "OPTIONS":
        return add_cors_headers(func.HttpResponse("OK", status_code=200))
    
    try:
        table_client = get_table_client(FOLDERS_TABLE)
        entities = table_client.list_entities()
        
        folders = []
        for entity in entities:
            folders.append({
                "id": entity['RowKey'],
                "name": entity.get('name'),
                "createdAt": entity.get('createdAt')
            })
        
        return add_cors_headers(func.HttpResponse(
            json.dumps(folders),
            status_code=200,
            mimetype="application/json"
        ))
        
    except Exception as e:
        return add_cors_headers(func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        ))

@app.function_name("CreateFolder")
@app.route(route="create-folder", methods=["POST", "OPTIONS"])
def create_folder(req: func.HttpRequest) -> func.HttpResponse:
    """Create folder"""
    if req.method == "OPTIONS":
        return add_cors_headers(func.HttpResponse("OK", status_code=200))
    
    try:
        req_body = req.get_json()
        name = req_body.get('name')
        
        if not name:
            return add_cors_headers(func.HttpResponse(
                json.dumps({"error": "Folder name required"}),
                status_code=400,
                mimetype="application/json"
            ))
        
        folder_id = str(uuid.uuid4())
        table_client = get_table_client(FOLDERS_TABLE)
        
        entity = TableEntity()
        entity['PartitionKey'] = 'folders'
        entity['RowKey'] = folder_id
        entity['name'] = name
        entity['createdAt'] = datetime.utcnow().isoformat()
        
        table_client.create_entity(entity)
        
        return add_cors_headers(func.HttpResponse(
            json.dumps({
                "id": folder_id,
                "name": name,
                "createdAt": entity['createdAt']
            }),
            status_code=201,
            mimetype="application/json"
        ))
        
    except Exception as e:
        return add_cors_headers(func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        ))

@app.function_name("DeleteFolder")
@app.route(route="folders/{folder_id}", methods=["DELETE", "OPTIONS"])
def delete_folder(req: func.HttpRequest) -> func.HttpResponse:
    """Delete folder"""
    if req.method == "OPTIONS":
        return add_cors_headers(func.HttpResponse("OK", status_code=200))
    
    try:
        folder_id = req.route_params.get('folder_id')
        table_client = get_table_client(FOLDERS_TABLE)
        
        table_client.delete_entity('folders', folder_id)
        
        return add_cors_headers(func.HttpResponse(
            json.dumps({"message": "Folder deleted"}),
            status_code=200,
            mimetype="application/json"
        ))
        
    except Exception as e:
        return add_cors_headers(func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        ))