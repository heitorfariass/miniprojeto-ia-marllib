"""Aplica os patches do MARLlib no RLlib instalado, COPIANDO os arquivos.

Equivale a `python MARLlib/marllib/patch/add_patch.py -y`, mas o script original
cria hard links/junctions no Windows, o que é frágil com a pasta dentro do OneDrive.
"""
import os
import shutil

import ray

PATCH_ROOT = os.path.join(os.path.dirname(__file__), "..", "MARLlib", "marllib", "patch")
RAY_ROOT = os.path.dirname(ray.__file__)

FILES = [
    "rllib/execution/replay_buffer.py",
    "rllib/execution/train_ops.py",
    "rllib/models/preprocessors.py",
    "rllib/policy/rnn_sequencing.py",
    "rllib/policy/torch_policy.py",
    "rllib/utils/exploration/ornstein_uhlenbeck_noise.py",
]

for rel in FILES:
    src = os.path.abspath(os.path.join(PATCH_ROOT, rel))
    dst = os.path.join(RAY_ROOT, rel)
    shutil.copyfile(src, dst)
    print(f"patched {dst}")
print("patches aplicados")
