#!/bin/sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

for config in examples/stage2/*.yaml; do
    echo "=== $config"
    sh run.sh "$config"
    echo "код возврата: $?"
    echo
done
