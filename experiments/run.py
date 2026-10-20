"""Roda um experimento do miniprojeto no MPE simple_spread.

Exemplos (na raiz do projeto, com o venv ativo):
    python experiments/run.py --algo mappo --share all --seed 0
    python experiments/run.py --algo ippo --share individual --seed 1 --steps 1000000

Cada execução grava em results/<algo>_<share>_s<seed>/ (progress.csv tem a curva de aprendizado).
"""
import argparse
import os

from marllib import marl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

p = argparse.ArgumentParser()
p.add_argument("--algo", required=True, choices=["ippo", "mappo", "vdppo"])
p.add_argument("--share", default="all", choices=["all", "individual"],
               help="all = todos os agentes compartilham a mesma rede; individual = uma rede por agente")
p.add_argument("--seed", type=int, default=0)
p.add_argument("--steps", type=int, default=1_000_000)
p.add_argument("--map", default="simple_spread")
p.add_argument("--out", default=None, help="pasta de saída (padrão: results/<algo>_<share>_s<seed>)")
args = p.parse_args()

out = args.out or os.path.join(ROOT, "results", f"{args.algo}_{args.share}_s{args.seed}")

env = marl.make_env(environment_name="mpe", map_name=args.map, force_coop=True)
algo = getattr(marl.algos, args.algo)(hyperparam_source="mpe")  # hiperparâmetros "finetuned" do artigo
model = marl.build_model(env, algo, {"core_arch": "mlp", "encode_layer": "128-256"})

algo.fit(
    env,
    model,
    stop={"timesteps_total": args.steps},
    local_mode=True,
    num_gpus=0,
    num_workers=1,
    share_policy=args.share,
    seed=args.seed,
    checkpoint_freq=50,
    checkpoint_end=True,
    local_dir=out,
)
print(f"OK {args.algo} {args.share} seed={args.seed} -> {out}")
