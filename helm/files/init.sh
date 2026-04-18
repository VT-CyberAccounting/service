#!/bin/sh
set -e
until mc alias set local http://s3/ minio "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1; do
  echo "waiting for s3..."
  sleep 2
done
mc mb --ignore-existing local/submissions
echo "submissions bucket ready"