#!/bin/sh

print_help() {
    echo 'Please specify the execution mode:'
    echo '  -f, --fastapi\t Run gunicorn/fastapi server'
    echo '  -c, --celery\t Run celery service'
    exit 1
}

case "$1" in
    '-f'|'--fastapi') gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 ;;
    '-c'|'--celery') poetry run celery --app=unipi.services.workers.celery worker --loglevel=info ;;
    *) print_help ;;
esac
