$ErrorActionPreference = "Stop"

$containerName = "pm-mvp"

$existingContainer = docker ps -aq --filter "name=^$containerName$"
if ($existingContainer) {
  docker rm -f $containerName | Out-Null
}

Write-Host "Container stopped (if it existed): $containerName"
