#!/usr/bin/env bash
# Instala o ambiente do miniprojeto no Linux (x86_64).  Uso: bash setup.sh
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v uv >/dev/null; then
  echo ">> Instalando uv (gerenciador de Python)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

[ -f MARLlib/requirements.txt ] || git submodule update --init

uv python install 3.8
uv venv .venv --python 3.8 --seed --clear
PY=.venv/bin/python

echo ">> Dependências (leva ~10-15 min na primeira vez; baixa ~1 GB)"
$PY -m pip install -q "pip==21" "setuptools==65.5.0" "wheel==0.38.0"
$PY -m pip install -q --no-build-isolation -r MARLlib/requirements.txt
$PY -m pip install -q "pillow==9.5.0"
$PY -m pip install -q --no-deps -e MARLlib
$PY experiments/apply_patch.py

echo
echo "Pronto. Ative com:  source .venv/bin/activate"
echo "Depois rode:        python experiments/smoke_test.py"
