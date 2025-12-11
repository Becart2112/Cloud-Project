output "resource_group_name" {
  description = "Main resource group name"
  value       = azurerm_resource_group.main.name
}

output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.app_storage.name
}

output "storage_container_name" {
  description = "Documents container name"
  value       = azurerm_storage_container.documents.name
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