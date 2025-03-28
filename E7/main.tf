module "resource_group" {
  source              = "./modules/resource_group"
  resource_group_name = var.resource_group_name
  location            = var.location
}

module "storage" {
  source                    = "./modules/storage"
  storage_account_name      = var.storage_account_name
  location                  = var.location
  resource_group_name       = var.resource_group_name
  datalake_name_dev         = var.datalake_name_dev
  directories               = var.directories

  resource_group_dependency = module.resource_group
}


