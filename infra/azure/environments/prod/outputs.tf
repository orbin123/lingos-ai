output "vm_principal_id" {
  description = "System-assigned runtime identity for reviewed data-plane grants."
  value       = module.vm.principal_id
}

output "postgres_fqdn" {
  description = "Passwordless PostgreSQL endpoint; no connection secret is emitted."
  value       = module.postgres.fqdn
}

output "blob_account_urls" {
  description = "Credential-free account endpoints for application configuration."
  value = {
    public  = module.storage.public_account_url
    private = module.storage.private_account_url
  }
}

output "key_vault_uri" {
  description = "Vault endpoint; this configuration creates no secrets."
  value       = module.key_vault.vault_uri
}
