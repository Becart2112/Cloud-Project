# main.tf

# Déclare le fournisseur azure
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  # Config backend
  backend "azurerm" {
    resource_group_name  = "backend_terraform"  
    storage_account_name = "tfstatecloudproject"       
    container_name       = "tfstate"               
    key                  = "doc_manager.tfstate"
  }
}

# config avec l'abonnement 
provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Groupe de Ressources
resource "azurerm_resource_group" "main" {
  name     = "${var.prefix}-rg"
  location = var.location  # ← UTILISE var.location
}

# le Compte de Stockage
resource "azurerm_storage_account" "app_storage" {
  name                     = "${var.prefix}appstorage"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Conteneur Blob pour les uploads des documents
resource "azurerm_storage_container" "input_container" {
  name                  = "input-documents"
  storage_account_name  = azurerm_storage_account.app_storage.name
  container_access_type = "private"
}

# 5. Azure Function App
resource "azurerm_service_plan" "function_plan" {
  name                = "${var.prefix}-func-plan"
  location            = var.location  # ← CHANGE eastus EN var.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "Y1"
}

resource "azurerm_function_app" "doc_processor" {
  name                       = "${var.prefix}-doc-processor"
  location                   = var.location  # ← CHANGE eastus EN var.location
  resource_group_name        = azurerm_resource_group.main.name
  app_service_plan_id        = azurerm_service_plan.function_plan.id
  storage_account_name       = azurerm_storage_account.app_storage.name
  storage_account_access_key = azurerm_storage_account.app_storage.primary_access_key
  version                    = "~4"
  https_only                 = true
  
  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME"    = "python"
    "AzureWebJobsStorage"         = azurerm_storage_account.app_storage.primary_connection_string
    "DOCUMENT_INPUT_CONTAINER"    = azurerm_storage_container.input_container.name
    "COSMOS_DB_ENDPOINT"          = azurerm_cosmosdb_account.db.endpoint
    "COSMOS_DB_MASTER_KEY"        = azurerm_cosmosdb_account.db.primary_key
    "COSMOS_DB_CONTAINER"         = azurerm_cosmosdb_sql_container.db_container.name
    "COSMOS_DB_FOLDERS_CONTAINER" = azurerm_cosmosdb_sql_container.folders_container.name
  }
}

# 6. Azure Container Registry - COMMENTED OUT
# resource "azurerm_container_registry" "acr" {
#   name                = "${var.prefix}acr"
#   resource_group_name = azurerm_resource_group.main.name
#   location            = azurerm_resource_group.main.location
#   sku                 = "Basic"
#   admin_enabled       = true 
# }

# 7. Container App Environment - COMMENTED OUT
# resource "azurerm_container_app_environment" "env" {
#   name                = "${var.prefix}-env"
#   location            = azurerm_resource_group.main.location
#   resource_group_name = azurerm_resource_group.main.name
# }

# 8. Container App (Frontend) - COMMENTED OUT
# resource "azurerm_container_app" "frontend" {
#   name                         = "${var.prefix}-frontend"
#   container_app_environment_id = azurerm_container_app_environment.env.id
#   resource_group_name          = azurerm_resource_group.main.name
#   revision_mode                = "Single"
#
#   template {
#     container {
#       name   = "frontend-app"
#       image  = "${azurerm_container_registry.acr.login_server}/frontend:latest"
#       cpu    = 0.25
#       memory = "0.5Gi"
#       
#       env {
#         name  = "FUNCTION_APP_URL"
#         value = "https://${azurerm_function_app.doc_processor.default_hostname}"
#       }
#     }
#   }
#
#   ingress {
#     external_enabled = true
#     target_port      = 5000
#     
#     traffic_weight {
#       latest_revision = true 
#       percentage      = 100
#     }
#   }
# }