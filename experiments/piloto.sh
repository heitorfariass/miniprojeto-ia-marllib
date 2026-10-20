#!/usr/bin/env bash
# Piloto: 4 configurações x 32 mil passos, uma de cada vez, para medir tempo e checar que tudo roda.
# (Em paralelo no Windows os clusters do Ray colidem na inicialização.)
cd "$(dirname "$0")/.."
V=${PYTHON:-python}  # rode com o venv ativo
OUT="$(pwd -W 2>/dev/null || pwd)/results/piloto"
rm -rf results/piloto && mkdir -p results/piloto
for c in "ippo all" "mappo all" "vdppo all" "mappo individual"; do
  set -- $c
  s=$(date +%s)
  $V experiments/run.py --algo $1 --share $2 --seed 0 --steps 32000 --out "$OUT/$1_$2" > "results/piloto/$1_$2.log" 2>&1
  echo "$1 $2 exit=$? $(( $(date +%s)-s ))s"
done
