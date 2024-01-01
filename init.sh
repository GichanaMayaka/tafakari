#!/bin/sh

export ENV=prod
flask create-db
flask db upgrade
cp ./.env .. && cd ..
exec python -m gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    "tafakari:create_app()" ||
    echo "Gunicorn failed to start"
