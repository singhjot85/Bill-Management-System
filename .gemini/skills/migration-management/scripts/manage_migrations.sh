#!/bin/bash
set -e
CMD="${1:-check}"
TENANT="${2:-}"

case "$CMD" in
    check)
        python manage.py showmigrations --plan | grep -v "[X]"
        python manage.py migrate_schemas --plan
        ;;
    migrate-all)
        python manage.py migrate_schemas --schema=public
        python manage.py migrate_schemas
        ;;
    migrate-tenant)
        [ -z "$TENANT" ] && { echo "Usage: $0 migrate-tenant <schema>"; exit 1; }
        python manage.py migrate_schemas --schema="$TENANT"
        ;;
    makemigrations)
        python manage.py makemigrations
        ;;
    *)
        echo "Usage: $0 {check|migrate-all|migrate-tenant|makemigrations} [schema]"
        exit 1
        ;;
esac
