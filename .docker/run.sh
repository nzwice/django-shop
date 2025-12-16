#!/bin/bash
set -e;

dev_server() {
    __dev_common
    echo "Migrating schema..."
    time python manage.py migrate

    echo "Collecting static files..."
    time python manage.py collectstatic --no-input --clear

    echo "Compiling i18n..."
    time python manage.py compilemessages

    echo "Load db data..."
    time python manage.py loaddata /app/data/db.json

    echo "seed_products_suggestion..."
    time python manage.py seed_products_suggestion

    echo "Running server..."
    python manage.py runserver 0.0.0.0:8000
}

dev_stripe() {
    __dev_common
    __configure_stripe_webhook
    stripe listen --forward-to "host.docker.internal:${WEBHOOK_SERVER_PORT}/en/payment/webhook/" --api-key "${STRIPE_SECRET_KEY}"
}

dev_worker() {
    __dev_common
    echo "Watch workers..."
    watchmedo auto-restart --directory=/app --pattern=*.py --recursive -- celery -A django_shop worker -l INFO
}

dev_flower() {
    __dev_common
    celery -A django_shop flower -l INFO
}

__dev_common() {
    export DEBUG=true
}

__configure_stripe_webhook() {
    local webhook_secret=`stripe listen --api-key ${STRIPE_SECRET_KEY} --print-secret`
    dotenv -f .env set STRIPE_WEBHOOK_SECRET "$webhook_secret"
}

"$@"

