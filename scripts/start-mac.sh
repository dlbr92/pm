#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="pm-mvp"
CONTAINER_NAME="pm-mvp"

if [[ "${1:-}" != "--no-build" ]]; then
  docker build -t "${IMAGE_NAME}" .
fi

docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
docker run -d --name "${CONTAINER_NAME}" -p 8000:8000 --env-file .env "${IMAGE_NAME}" >/dev/null

echo "Container started: ${CONTAINER_NAME}"
echo "App URL: http://localhost:8000"
