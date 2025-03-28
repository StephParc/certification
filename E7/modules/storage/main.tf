# Création du compte de stockage
resource "azurerm_storage_account" "my_storage_account" {
  name                     = var.storage_account_name
  location                 = var.location
  resource_group_name      = var.resource_group_name
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = "true"

  depends_on = [var.resource_group_dependency]
}

# Création du datalake de dev
resource "azurerm_storage_data_lake_gen2_filesystem" "datalake_dev" {
  name               = var.datalake_name_dev
  storage_account_id = azurerm_storage_account.my_storage_account.id

  depends_on = [azurerm_storage_account.my_storage_account]
}

# Mise à plat des chemins arborescence datalake
locals {
  all_paths = [
    for path_list in var.directories : join("/", path_list)
  ]
}

# Crétaion de l'arborescence
resource "azurerm_storage_data_lake_gen2_path" "directories" {
  for_each           = toset(local.all_paths)
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.datalake_dev.name
  storage_account_id = azurerm_storage_account.my_storage_account.id
  path               = each.value
  resource           = "directory"
}

# ## Deuxième environnement
# # Création du datalake de qat
# resource "azurerm_storage_data_lake_gen2_filesystem" "datalake_qat" {
#   name               = var.datalake_name_qat
#   storage_account_id = azurerm_storage_account.my_storage_account.id

#   depends_on = [azurerm_storage_account.my_storage_account]
# }

# # Créer les répertoires principaux et leurs sous-répertoires
# resource "azurerm_storage_data_lake_gen2_path" "directories" {
#   for_each           = toset(local.all_paths)
#   filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.datalake_qat.name
#   storage_account_id = azurerm_storage_account.my_storage_account.id
#   path               = each.value
#   resource           = "directory"
# }

## Troisième environnement
# # Création du datalake de prd
# resource "azurerm_storage_data_lake_gen2_filesystem" "datalake_prd" {
#   name               = var.datalake_name_prd
#   storage_account_id = azurerm_storage_account.my_storage_account.id

#   depends_on = [azurerm_storage_account.my_storage_account]
# }

# # Créer les répertoires principaux et leurs sous-répertoires
# resource "azurerm_storage_data_lake_gen2_path" "directories" {
#   for_each           = toset(local.all_paths)
#   filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.datalake_prd.name
#   storage_account_id = azurerm_storage_account.my_storage_account.id
#   path               = each.value
#   resource           = "directory"
# }
