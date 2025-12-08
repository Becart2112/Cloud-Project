# main.tf

# Bloc Terraform : Déclare le fournisseur Azure et le backend distant.
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  # --- CONFIGURATION DU BACKEND DISTANT (VOS VALEURS AZURE) ---
  backend "azurerm" {
    resource_group_name  = "backend_terraform"  
    storage_account_name = "tfstatecloudproject"       
    container_name       = "tfstate"               
    key                  = "doc_manager.tfstate"
  }
}

# Bloc Provider : Configure la connexion à votre abonnement Azure
provider "azurerm" {
  features {}
}

# 1. Création du Groupe de Ressources principal pour l'application
resource "azurerm_resource_group" "main" {
  name     = "${var.prefix}-rg"
  location = var.location
}

# 2. Création du Compte de Stockage principal (Blob Storage) pour l'application et la Function
resource "azurerm_storage_account" "app_storage" {
  name                     = "${var.prefix}appstorage" # Doit être unique globalement
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS" 
}

# 3. Conteneur Blob pour les uploads de documents bruts (Input)
resource "azurerm_storage_container" "input_container" {
  name                  = "input-documents"
  storage_account_name  = azurerm_storage_account.app_storage.name
  container_access_type = "private"
}

# 4. Base de données Cosmos DB (BDD)
resource "azurerm_cosmosdb_account" "db" {
  name                = "${var.prefix}-cosmosdb"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB" 

  consistency_policy {
    consistency_level = "Session"
  }
  
  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }
}

# 4.1. Conteneur dans Cosmos DB pour les métadonnées
resource "azurerm_cosmosdb_sql_database" "db_sql" {
  name                = "DocumentDB"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.db.name
}

resource "azurerm_cosmosdb_sql_container" "db_container" {
  name                  = "Documents"
  resource_group_name   = azurerm_resource_group.main.name
  account_name          = azurerm_cosmosdb_account.db.name
  database_name         = azurerm_cosmosdb_sql_database.db_sql.name
  # CORRECTION : partition_key_path est déprécié, utiliser partition_key_paths (liste)
  partition_key_paths   = ["/documentId"] 
  throughput            = 400
}

# 5. Azure Function App (Compute Serverless pour le Traitement)
resource "azurerm_service_plan" "function_plan" {
  name                = "${var.prefix}-func-plan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  os_type = "Linux" 

  sku_name            = "Y1"
}

resource "azurerm_function_app" "doc_processor" {
  name                       = "${var.prefix}-doc-processor" 
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  app_service_plan_id        = azurerm_service_plan.function_plan.id
  storage_account_name       = azurerm_storage_account.app_storage.name
  storage_account_access_key = azurerm_storage_account.app_storage.primary_access_key
  version                    = "~4" 
  
  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME"    = "python" 
    "AzureWebJobsStorage"         = azurerm_storage_account.app_storage.primary_connection_string
    "DOCUMENT_INPUT_CONTAINER"    = azurerm_storage_container.input_container.name
    "COSMOS_DB_ENDPOINT"          = azurerm_cosmosdb_account.db.endpoint
    "COSMOS_DB_MASTER_KEY"        = azurerm_cosmosdb_account.db.primary_key
    "COSMOS_DB_CONTAINER"         = azurerm_cosmosdb_sql_container.db_container.name
  }
}

# 6. Azure Container Registry (ACR) et Azure Container App (Frontend)
resource "azurerm_container_registry" "acr" {
  name                = "${var.prefix}acr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true 
}

resource "azurerm_container_app_environment" "env" {
  name                = "${var.prefix}-env"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_container_app" "frontend" {
  name                         = "${var.prefix}-frontend"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.main.name

  revision_mode = "Single" 

  template {
    container {
      name   = "frontend-app"
      image  = "${azurerm_container_registry.acr.login_server}/frontend:latest" 
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 80
    
    traffic_weight {
      latest_revision = true 
      percentage      = 100
    }
  }
}