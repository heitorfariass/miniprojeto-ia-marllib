#!/usr/bin/env bash
# Roda TODOS os experimentos do miniprojeto, um por vez (no Windows o Ray não aceita dois em paralelo).
# Pode ser interrompido e rodado de novo: execuções já concluídas são puladas.
#   bash experiments/run_all.sh            (padrão: 500 mil passos)
#   STEPS=300000 bash experiments/run_all.sh
cd "$(dirname "$0")/.."
V=${PYTHON:-python}  # rode com o venv ativo
STEPS=${STEPS:-500000}
mkdir -p results/logs
# 1º a comparação principal (rede compartilhada), depois a modificação (redes individuais)
for share in all individual; do
  for seed in 0 1 2; do
    for algo in ippo mappo; do
      name="${algo}_${share}_s${seed}"
      log="results/logs/$name.log"
      if grep -q "^OK " "$log" 2>/dev/null; then echo "pulando $name (já concluído)"; continue; fi
      rm -rf "results/$name"
      s=$(date +%s)
      $V experiments/run.py --algo $algo --share $share --seed $seed --steps $STEPS > "$log" 2>&1
      echo "$(date '+%H:%M') $name exit=$? $(( ($(date +%s)-s)/60 )) min"
    done
  done
done
$V experiments/analyze.py
