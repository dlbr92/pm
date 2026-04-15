param(
  [switch]$NoBuild
)

$ErrorActionPreference = "Stop"

$imageName = "pm-mvp"
$containerName = "pm-mvp"

if (-not $NoBuild) {
  docker build -t $imageName .
}

$existingContainer = docker ps -aq --filter "name=^$containerName$"
if ($existingContainer) {
  docker rm -f $containerName | Out-Null
}

docker run -d --name $containerName -p 8000:8000 --env-file .env $imageName | Out-Null

Write-Host "Container started: $containerName"
Write-Host "App URL: http://localhost:8000"
