---
name: tenant-setup
description: Create and configure new tenants with defaults. Use when user asks to "set up a tenant", "add a company", "create a new client", or "onboard a business".
---

# Tenant Setup

When this skill is active:
1. Validate tenant name and admin email are provided
2. Run `bash scripts/create_tenant.sh "Company Name" admin@company.com`
3. Confirm schema creation, migrations, and default data seeding
4. Remind about DNS and SSL if custom domain is used

Schema names are lowercase and URL-safe. Data is isolated per tenant.
