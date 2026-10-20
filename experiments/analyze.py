"""Junta os progress.csv de results/<algo>_<share>_s<seed>/ e gera tabela + gráfico.

Uso: python experiments/analyze.py            -> results/resumo.csv, results/resumo.md, results/curvas.png
     python experiments/analyze.py results/piloto
"""
import glob
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "results")

# Valores da Tabela 4 do artigo (MPE simple_spread, compartilhamento padrão)
PAPER = {"ippo": -65.74, "mappo": -66.26, "vdppo": -213.99}

runs = []
for csv in glob.glob(os.path.join(RES, "*", "*", "*", "progress.csv")):
    run_dir = os.path.relpath(csv, RES).split(os.sep)[0]
    m = re.match(r"(ippo|mappo|vdppo)_(all|individual)(?:_s(\d+))?$", run_dir)
    if not m:
        continue
    df = pd.read_csv(csv)
    if df.empty:
        continue
    algo, share, seed = m.group(1), m.group(2), int(m.group(3) or 0)
    tail = df.tail(max(1, len(df) // 10))  # últimos 10% das iterações
    runs.append({
        "algo": algo, "share": share, "seed": seed,
        "timesteps": int(df["timesteps_total"].iloc[-1]),
        "final_reward": tail["episode_reward_mean"].mean(),
        "train_min": df["time_total_s"].iloc[-1] / 60,
        "curve": df[["timesteps_total", "episode_reward_mean"]],
        "curve_full": df[["training_iteration", "timesteps_total", "time_total_s", "episode_reward_mean",
                          "episode_reward_min", "episode_reward_max"]],
    })

if not runs:
    sys.exit(f"nenhum progress.csv encontrado em {RES}")

os.makedirs(os.path.join(RES, "curvas_dados"), exist_ok=True)
for r in runs:  # curva compacta por execução (os diretórios brutos do Ray não vão para o git)
    r["curve_full"].to_csv(os.path.join(RES, "curvas_dados", f"{r['algo']}_{r['share']}_s{r['seed']}.csv"), index=False)

per_run = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("curve")} for r in runs])
per_run.sort_values(["algo", "share", "seed"]).to_csv(os.path.join(RES, "resumo_por_execucao.csv"), index=False)

agg = per_run.groupby(["algo", "share"]).agg(
    seeds=("seed", "count"),
    recompensa_media=("final_reward", "mean"),
    desvio=("final_reward", "std"),
    tempo_min=("train_min", "mean"),
    passos=("timesteps", "mean"),
).reset_index()
agg["artigo"] = agg["algo"].map(PAPER).where(agg["share"] == "all")
agg.to_csv(os.path.join(RES, "resumo.csv"), index=False)
with open(os.path.join(RES, "resumo.md"), "w", encoding="utf-8") as f:
    f.write(agg.round(2).to_markdown(index=False) if hasattr(agg, "to_markdown") else agg.round(2).to_string(index=False))
print(agg.round(2).to_string(index=False))

fig, ax = plt.subplots(figsize=(8, 5))
for (algo, share), grp in per_run.groupby(["algo", "share"]):
    curves = [r["curve"].set_index("timesteps_total")["episode_reward_mean"]
              for r in runs if r["algo"] == algo and r["share"] == share]
    joined = pd.concat(curves, axis=1).sort_index().interpolate(limit_area="inside")
    mean, std = joined.mean(axis=1), joined.std(axis=1).fillna(0)
    line, = ax.plot(mean.index, mean.values, label=f"{algo.upper()} ({share})")
    ax.fill_between(mean.index, mean - std, mean + std, alpha=0.2, color=line.get_color())
ax.set_xlabel("passos de interação (timesteps)")
ax.set_ylabel("recompensa média por episódio")
ax.set_title("MPE simple_spread — média ± desvio entre sementes")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(RES, "curvas.png"), dpi=150)
print("gráfico:", os.path.join(RES, "curvas.png"))
