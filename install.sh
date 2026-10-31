#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

env_file="FinaceManager/.env"
env_example="FinaceManager/.env.example"

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker not found. Install Docker Desktop for Mac and try again." >&2
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Docker Compose is unavailable. Update or reinstall Docker Desktop." >&2
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "Docker is not running. Start Docker Desktop and try again." >&2
    exit 1
fi

if [[ ! -f "$env_file" ]]; then
    if [[ ! -f "$env_example" ]]; then
        echo "Configuration template not found: $env_example" >&2
        exit 1
    fi

    if ! command -v openssl >/dev/null 2>&1; then
        echo "OpenSSL is required to generate application secrets." >&2
        exit 1
    fi

    echo "No $env_file found - generating one with random secrets..."
    umask 077
    cp "$env_example" "$env_file"
    secret_key="$(openssl rand -hex 32)"
    database_password="$(openssl rand -hex 16)"
    database_root_password="$(openssl rand -hex 16)"
    sed -i '' \
        -e "s/^SECRET_KEY=.*/SECRET_KEY=$secret_key/" \
        -e "s/^DATABASE_PASSWORD=.*/DATABASE_PASSWORD=$database_password/" \
        -e "s/^DATABASE_ROOT_PASSWORD=.*/DATABASE_ROOT_PASSWORD=$database_root_password/" \
        "$env_file"
fi

echo "Building images and starting the stack (first run can take a few minutes)..."
docker compose --env-file "$env_file" up -d --build

port="$(sed -n 's/^HOST_PORT=//p' "$env_file" | head -n 1)"
if [[ ! "$port" =~ ^[0-9]+$ ]]; then
    echo "HOST_PORT is missing or invalid in $env_file." >&2
    exit 1
fi

echo "Waiting for the app to come online..."
for _ in {1..120}; do
    if curl --fail --silent --output /dev/null --max-time 3 "http://localhost:$port/"; then
        echo "Ready: http://localhost:$port (restarts automatically with Docker Desktop)"
        exit 0
    fi
    sleep 1
done

echo "The app did not respond within 120s. Check logs with: docker compose --env-file $env_file logs" >&2
exit 1
