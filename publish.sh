#!/bin/bash

cd "$(dirname "$0")" || exit 1

# run build
echo "=== Building site... ==="
if ! python scripts/build.py; then
    echo "Build failed!"
    exit 1
fi

# run deploy
echo "\n=== Deploying site... ==="
if ! python scripts/deploy.py; then
    echo "Deploy failed!"
    exit 1
fi

echo "\n=== Publication completed successfully ==="
exit 0
