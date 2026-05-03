#!/bin/bash
set -e
CMD="${1:-help}"
SVC="${2:-}"

case "$CMD" in
    setup)
        docker-compose build
        docker-compose run --rm web poetry install
        docker-compose run --rm web python manage.py migrate_schemas
        echo "Setup complete. Run: $0 start"
        ;;
    start)
        docker-compose up -d
        echo "Frontend: http://localhost:3000 | API: http://localhost:8000"
        ;;
    stop)
        docker-compose down
        ;;
    restart)
        docker-compose restart
        ;;
    logs)
        docker-compose logs -f ${SVC:-}
        ;;
    shell)
        docker-compose exec web /bin/bash
        ;;
    status)
        docker-compose ps
        ;;
    migrate)
        docker-compose exec web python manage.py migrate_schemas
        ;;
    test)
        docker-compose exec web pytest "${@:2}"
        ;;
    clean)
        docker-compose down -v --rmi all --remove-orphans
        ;;
    *)
        echo "Usage: $0 {setup|start|stop|restart|logs|shell|status|migrate|test|clean} [service]"
        exit 1
        ;;
esac
