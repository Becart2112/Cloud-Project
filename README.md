# Cloud-Project

### Objectif ###
Application sous azure permettant de stocker des fichiers sur le cloud d'azure, avec un site qui permet de faire des sous dossiers aussi.

### Prérequis ###
- Python 3.10+
- Azure Functions Core Tools
- Azure Storage Account existant (nom `maxprojcloudstorage`)
- Clé d’accès (qui m'a enlecé 1 milliard de commit du au secret de github que j'ai pas réussi à enlever hier) du Storage Account

### Configuration ###
1. configurer le local.settings.json avec sa propre clé d'azure (du coup ca dépend là, j'ai réussi à laisser la mienne)

2. Installer les dépendances :
   
   cd src/azure_function
   pip install -r requirements.txt

### Lancement ###

cd src/azure_function
func start

### Tests des endpoints (PowerShell) ###
SI vous voulez tester 

Invoke-RestMethod -Method Post -Uri "http://localhost:7071/api/create-folder" -ContentType 'application/json' -Body '{"name":"Mon dossier"}'
Invoke-RestMethod -Uri "http://localhost:7071/api/folders"

Créer un fichier de test puis uploader

Set-Content .\test.pdf 'hello'
curl.exe -X POST "http://localhost:7071/api/upload" -F "file=@test.pdf" -F "folderId=root"

Invoke-RestMethod -Uri "http://localhost:7071/api/documents"

si tout marche bien normalement c'est good !

### Ressources Cloud utilisées ###

- Azure Blob Storage (container `documents`, dossier logique `root/…`)
- Azure Table Storage (`documents`, `folders`)
- Azure Functions (runtime Python)
