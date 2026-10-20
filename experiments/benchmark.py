"""Teste de tempo em outro hardware: IPPO com rede compartilhada x uma rede por agente.

Roda as duas configurações com o mesmo orçamento (padrão 100 mil passos, ~10 min no PC de referência),
e grava results/benchmark/<nome>.md com a máquina, os tempos e a comparação com o PC de referência.

Uso (venv ativo, na raiz do repositório):
    python experiments/benchmark.py --nome joao
    python experiments/benchmark.py --nome joao --steps 200000
"""
import argparse
import datetime
import glob
import os
import platform
import subprocess
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Medido no PC de referência (Heitor): Windows 11, CPU 6 núcleos, sem GPU, 102.400 passos, semente 0
REF = {"all": 3.49, "individual": 5.81}

p = argparse.ArgumentParser()
p.add_argument("--nome", required=True, help="seu nome (vira o nome do arquivo de resultado)")
p.add_argument("--steps", type=int, default=100_000)
p.add_argument("--seed", type=int, default=0)
args = p.parse_args()

out_root = os.path.join(ROOT, "results", "benchmark", args.nome)
os.makedirs(out_root, exist_ok=True)


def cpu_name():
    try:
        if platform.system() == "Windows":
            return subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"],
                text=True).strip()
        if platform.system() == "Linux":
            for line in open("/proc/cpuinfo"):
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return platform.processor() or "desconhecido"


def ram_gb():
    try:
        import psutil
        return round(psutil.virtual_memory().total / 2**30, 1)
    except Exception:
        return "?"


rows = []
for share in ("all", "individual"):
    out = os.path.join(out_root, f"ippo_{share}")
    print(f"\n=== IPPO, rede {share}, {args.steps} passos — aguarde ===", flush=True)
    log = open(os.path.join(out_root, f"ippo_{share}.log"), "w", encoding="utf-8")
    rc = subprocess.call([sys.executable, os.path.join(ROOT, "experiments", "run.py"),
                          "--algo", "ippo", "--share", share, "--seed", str(args.seed),
                          "--steps", str(args.steps), "--out", out], stdout=log, stderr=subprocess.STDOUT)
    log.close()
    csvs = glob.glob(os.path.join(out, "*", "*", "progress.csv"))
    if rc != 0 or not csvs:
        sys.exit(f"falhou (código {rc}); veja {log.name}")
    df = pd.read_csv(csvs[0])
    tail = df.tail(max(1, len(df) // 10))
    rows.append({"rede": share, "passos": int(df.timesteps_total.iloc[-1]),
                 "tempo_min": round(df.time_total_s.iloc[-1] / 60, 2),
                 "recompensa_final": round(tail.episode_reward_mean.mean(), 1)})
    print(rows[-1], flush=True)

t_all, t_ind = rows[0]["tempo_min"], rows[1]["tempo_min"]
ganho = 100 * (1 - t_all / t_ind)
ganho_ref = 100 * (1 - REF["all"] / REF["individual"])

md = f"""# Benchmark de tempo — {args.nome}

Data: {datetime.datetime.now():%d/%m/%Y %H:%M}

| Máquina | |
|---|---|
| Sistema | {platform.system()} {platform.release()} |
| CPU | {cpu_name()} |
| Núcleos lógicos | {os.cpu_count()} |
| RAM | {ram_gb()} GB |
| Python | {platform.python_version()} |

| Rede | Passos | Tempo (min) | Recompensa final | Tempo no PC de referência (min) |
|---|---|---|---|---|
| compartilhada | {rows[0]['passos']} | {t_all} | {rows[0]['recompensa_final']} | {REF['all']} |
| uma por agente | {rows[1]['passos']} | {t_ind} | {rows[1]['recompensa_final']} | {REF['individual']} |

**Ganho de tempo da rede compartilhada nesta máquina: {ganho:.0f}%** (no PC de referência: {ganho_ref:.0f}%).
"""
if args.steps != 100_000:
    md += "\nObs.: orçamento diferente de 100 mil passos; a coluna de referência vale para ~100 mil.\n"

path = os.path.join(ROOT, "results", "benchmark", f"{args.nome}.md")
open(path, "w", encoding="utf-8").write(md)
print("\n" + md + f"\nResultado salvo em {path}")
