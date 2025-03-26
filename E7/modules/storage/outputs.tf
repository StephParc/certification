output "storage_account_name" {
  value = azurerm_storage_account.my_storage_account.name
}

output "datalake_name_dev" {
  value = azurerm_storage_data_lake_gen2_filesystem.datalake_dev.name
}

# output "blob_name" {
#   value = azurerm_storage_container.blob_container.name
# }