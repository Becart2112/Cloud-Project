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

output "acr_login_server" {
  description = "ACR login server URL"
  value       = azurerm_container_registry.acr.login_server
}

output "acr_admin_username" {
  description = "ACR admin username"
  value       = azurerm_container_registry.acr.admin_username
}

output "cosmosdb_endpoint" {
  description = "Cosmos DB endpoint"
  value       = azurerm_cosmosdb_account.db.endpoint
}

output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.app_storage.name
}

output "resource_group_name" {
  description = "Main resource group name"
  value       = azurerm_resource_group.main.name
}

output "container_app_fqdn" {
  description = "Container App FQDN"
  value       = azurerm_container_app.frontend.ingress[0].fqdn
}