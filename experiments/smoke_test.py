"""Teste rápido do ambiente: MAPPO no MPE simple_spread por poucos passos (CPU).

Uso (na raiz do projeto, com o venv ativo):
    python experiments/smoke_test.py
"""
import os

from marllib import marl

STOP_TIMESTEPS = int(os.environ.get("SMOKE_TIMESTEPS", "6400"))

env = marl.make_env(environment_name="mpe", map_name="simple_spread", force_coop=True)
mappo = marl.algos.mappo(hyperparam_source="mpe")
model = marl.build_model(env, mappo, {"core_arch": "mlp", "encode_layer": "128-256"})

mappo.fit(
    env,
    model,
    stop={"timesteps_total": STOP_TIMESTEPS},
    local_mode=True,
    num_gpus=0,
    num_workers=1,
    share_policy="all",
    checkpoint_freq=0,
    local_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results")),
)
print("SMOKE TEST OK")
