#!/usr/bin/env bash
# wait-for.sh host:port -- command ...
set -e

hostport="$1"
shift

host="${hostport%:*}"
port="${hostport#*:}"

until nc -z "$host" "$port"; do
  echo "⏳ Esperando ${host}:${port}..."
  sleep 1
done

exec "$@"