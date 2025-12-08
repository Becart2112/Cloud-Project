variable "prefix" {
  description = "Préfixe unique pour nommer les ressources Azure (ex: 'maxcloudapp'). Doit être unique et en minuscules."
  type        = string
}

variable "location" {
  description = "Région Azure où les services seront déployés."
  type        = string
  default     = "eastus"
}