output "resource_group_name" {
  description = "Main resource group name"
  value       = azurerm_resource_group.main.name
}

output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.app_storage.name
}

output "cosmosdb_endpoint" {
  description = "Cosmos DB endpoint"
  value       = azurerm_cosmosdb_account.db.endpoint
}

output "cosmosdb_key" {
  description = "Cosmos DB primary key"
  value       = azurerm_cosmosdb_account.db.primary_key
  sensitive   = true
}

output "cosmosdb_database_name" {
  description = "Cosmos DB database name"
  value       = azurerm_cosmosdb_sql_database.db_sql.name
}

output "documents_container_name" {
  description = "Documents container name"
  value       = azurerm_cosmosdb_sql_container.db_container.name
}

output "folders_container_name" {
  description = "Folders container name"
  value       = azurerm_cosmosdb_sql_container.folders_container.name
}

output "function_app_name" {
  description = "Name of the Azure Function App"
  value       = azurerm_function_app.doc_processor.name
}

output "function_app_default_hostname" {
  description = "Default hostname of the Function App"
  value       = azurerm_function_app.doc_processor.default_hostname
}

output "function_app_id" {
  description = "ID of the Azure Function App"
  value       = azurerm_function_app.doc_processor.id
}

# COMMENTED OUT - Container Registry
# output "acr_login_server" {
#   value       = azurerm_container_registry.acr.login_server
# }
#
# output "acr_admin_username" {
#   value       = azurerm_container_registry.acr.admin_username
#   sensitive   = true
# }
#
# output "acr_admin_password" {
#   value       = azurerm_container_registry.acr.admin_password
#   sensitive   = true
# }

# COMMENTED OUT - Container App
# output "container_app_fqdn" {
#   value       = azurerm_container_app.frontend.ingress[0].fqdn
# }