variable "resource_group_name" {
  description = "Le nom du groupe de ressources"
  type        = string
}

variable "location" {
  description = "La localisation du groupe de ressources"
  type        = string
}

variable "storage_account_name" {
  description = "Le nom du compte de storage"
  type        = string
}

variable "datalake_name_dev" {
  description = "Le nom du conteneur datalake"
  type        = string
}

# variable "datalake_name_qat" {
#   description = "Le nom du conteneur datalake"
#   type        = string
# }

# variable "datalake_name_prd" {
#   description = "Le nom du conteneur datalake"
#   type        = string
# }

variable "directories" {
  type    = list(list(string))
}

# variable "directories" {
#   type    = map(list(string))
# }

variable "resource_group_dependency" {
  description = "Dépendance du groupe de ressources"
  type        = any
}