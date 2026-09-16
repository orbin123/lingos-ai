# Azure active-window billing runbook

This change removes the two resources that produced the September idle bill:

- Azure Container Registry is no longer used. The deployment workflow sends an
  exact public Git commit SHA to the VM. The VM downloads that commit, builds
  the backend image, and retains the immutable Docker image ID on its existing
  OS disk for wake and rollback.
- The Standard static public IPv4 exists only during an active window. Wake
  creates and attaches it and opens one exact-IP PostgreSQL firewall rule.
  Sleep removes the rule, detaches the address, and deletes the address.

The VM disk, PostgreSQL data, Blob data, and Key Vault remain persistent. Their
current meters are covered by the account allowances; this design does not
claim they can never become chargeable after those allowances expire.

## Why activation is gated

Deleting and recreating a Standard public IP changes the numeric address.
`api.lingosai.com` therefore cannot remain an A record. It must become a CNAME
to the stable Azure-managed label:

```text
api.lingosai.com CNAME lingosai-prod.centralindia.cloudapp.azure.com
```

`start.sh` checks this record and refuses to activate ephemeral billing until
the CNAME is visible. This prevents the first sleep from deleting an address
that production DNS still needs.

## Reviewed migration sequence

These are external and destructive production steps. They are not performed
by this PR and require the normal owner review gates.

1. Merge the PR with `AZURE_EPHEMERAL_BILLING_ENABLED` absent or `false`.
2. Wake the existing environment and run one protected backend deployment.
   Verify that the VM successfully builds the pinned commit locally, the API is
   healthy, and a local rollback image is recorded.
3. Review a saved Terraform plan. It must remove only the ACR, its `AcrPull`
   role assignment, the persistent public IP association/resource, and the
   Terraform-authored fixed PostgreSQL firewall rule. Apply only after the
   separately required approval.
4. Set the GitHub repository variable
   `AZURE_EPHEMERAL_BILLING_ENABLED=true`, then immediately run the protected
   **Azure wake** workflow. This creates the public IP through the reviewed
   lifecycle path while the bounded live window prevents the watchdog from
   deleting it. Confirm that
   `lingosai-prod.centralindia.cloudapp.azure.com` resolves to the new address.
5. During that same live window, change the existing `api.lingosai.com` A
   record to the CNAME above. DNS changes remain owner-operated and separately
   approved. If the cutover cannot be completed and verified in the window,
   set the variable back to `false` before recovery work.
6. Verify HTTPS, OAuth callback, WebSocket, and readiness through
   `https://api.lingosai.com`.
7. Run `./start.sh` and then `./scripts/azure-down.sh`. Confirm that the VM is
   deallocated, PostgreSQL is stopped, the public IP is absent, the exact-IP
   firewall rule is absent, and ACR remains absent.
8. Inspect Cost Management after its normal ingestion delay. The Container
   Registry and Standard IPv4 daily lines should stop growing while asleep.

Do not enable the repository variable before steps 2–3 are complete or outside
the approved DNS-cutover window.

## Daily use

```bash
./start.sh       # default six-hour window
./start.sh 2     # two-hour window
```

`start.sh` does four things:

1. verifies the safe DNS CNAME;
2. creates/attaches the public IP and exact PostgreSQL firewall rule;
3. starts PostgreSQL, the VM, and the existing local application image;
4. schedules a local exact-deadline shutdown fallback.

The GitHub watchdog checks every five minutes. It is the durable enforcement
path when the operator's computer sleeps or loses connectivity. Manual early
shutdown remains:

```bash
AZURE_EPHEMERAL_BILLING_ENABLED=true ./scripts/azure-down.sh
```

The operations are idempotent. A partial shutdown leaves the live-window tag
expired so the watchdog retries.

## Operational trade-offs

- A backend deployment builds on the small VM and is slower than ACR delivery.
  The existing bounded swap file prevents the dependency build from exhausting
  the 1 GiB host.
- ACR images are no longer remote rollback storage. The current and previous
  immutable image IDs remain on the persistent OS disk.
- The public IPv4 can change every wake. The Azure DNS label and application
  hostname do not.
- Scheduled GitHub workflows can be delayed. The local timer and manual sleep
  command are additional safeguards, not replacements for checking Azure Cost
  Management.
