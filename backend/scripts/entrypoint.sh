#!/usr/bin/env bash
set -e

: "${APP_ENV:=development}"
: "${APP_HOST:=0.0.0.0}"
: "${APP_PORT:=8000}"

if [ "$APP_ENV" = "development" ]; then
  echo ">>> Starting API in DEV (reload ON) at http://${APP_HOST}:${APP_PORT}"
  exec uvicorn app.main:app \
    --host "$APP_HOST" \
    --port "$APP_PORT" \
    --reload \
    --reload-dir /app
else
  echo ">>> Starting API in PROD (reload OFF) at http://${APP_HOST}:${APP_PORT}"
  exec uvicorn app.main:app \
    --host "$APP_HOST" \
    --port "$APP_PORT"
fi