Param(
  [ValidateSet("up","down","migrate","seed","test","logs","psql")]
  [string]$Task = "up"
)

$ErrorActionPreference = "Stop"

function BackendDir {
  Set-Location -Path "backend"
}

function ComposeUp {
  BackendDir
  docker compose up -d --build
}

function ComposeDown {
  BackendDir
  docker compose down -v
}

function Migrate {
  BackendDir
  docker compose exec api alembic upgrade head
}

function Seed {
  BackendDir
  try {
    docker compose exec api python scripts/seed_pdf_demo.py
  } catch {
    Write-Warning "Seed falhou (scripts/seed_pdf_demo.py). Ajuste o caminho se necessário."
  }
}

function Tests {
  BackendDir
  docker compose exec api pytest -vv --maxfail=1
}

function Logs {
  BackendDir
  docker compose logs --tail 200
}

function Psql {
  # Abre um psql dentro do container do Postgres
  BackendDir
  docker compose exec db psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB
}

switch ($Task) {
  "up"      { ComposeUp }
  "down"    { ComposeDown }
  "migrate" { Migrate }
  "seed"    { Seed }
  "test"    { Tests }
  "logs"    { Logs }
  "psql"    { Psql }
  default   { ComposeUp }
}
