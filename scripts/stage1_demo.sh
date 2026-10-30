#!/bin/sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

for config in examples/configs/*.yaml; do
    echo "=== $config"
    sh run.sh "$config"
    echo "код возврата: $?"
    echo
done

echo "=== конфигурационный файл не существует"
sh run.sh examples/configs/no_such_config.yaml
echo "код возврата: $?"
