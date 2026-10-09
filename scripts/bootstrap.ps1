$ErrorActionPreference = 'Stop'
Write-Host 'SafeScroll bootstrap' -ForegroundColor Cyan
corepack enable
corepack prepare pnpm@10.14.0 --activate
if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env' }
pnpm install
if (Get-Command docker -ErrorAction SilentlyContinue) {
  docker compose -f infra/docker-compose.yml up -d postgres redis
}
if (Get-Command uv -ErrorAction SilentlyContinue) {
  Push-Location apps/api
  uv sync --dev
  Pop-Location
}
Write-Host ''
Write-Host 'Next:' -ForegroundColor Green
Write-Host '  pnpm dev:web'
Write-Host '  cd apps/api; uv run uvicorn app.main:app --reload --port 8000'
Write-Host '  ollama pull qwen3:1.7b'
