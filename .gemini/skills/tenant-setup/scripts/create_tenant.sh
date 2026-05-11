#!/bin/bash
set -e
TENANT_NAME="$1"
ADMIN_EMAIL="$2"
DOMAIN="${3:-}"

[ -z "$TENANT_NAME" ] || [ -z "$ADMIN_EMAIL" ] && {
    echo "Usage: $0 <tenant_name> <admin_email> [domain]"
    exit 1
}

SCHEMA=$(echo "$TENANT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -cd '[:alnum:]_')

echo "Creating tenant: $TENANT_NAME (schema: $SCHEMA)"

python manage.py create_tenant \
    --name "$TENANT_NAME" \
    --admin-email "$ADMIN_EMAIL" \
    --schema-name "$SCHEMA" \
    ${DOMAIN:+--domain "$DOMAIN"}

python manage.py migrate_schemas --schema="$SCHEMA"
echo "Tenant $TENANT_NAME created successfully"
