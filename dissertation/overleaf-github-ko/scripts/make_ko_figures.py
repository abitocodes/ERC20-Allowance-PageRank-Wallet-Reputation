"""Korean-label versions of the five data figures used in the thesis.

The data and every computation are those of
wallet-reputation-experiments/scripts/generate_dissertation_figures.py;
only the visible text is translated. Output: overleaf-github-ko/Figures/generated/.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KO_ROOT = HERE.parent
EXP = KO_ROOT.parent / "wallet-reputation-experiments"
sys.path.insert(0, str(EXP / "scripts"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from scipy import stats

import generate_dissertation_figures as G  # reuse helpers (_common_block)
from pagerank_variants import AWP_ID, ENDORSERANK_ID
from project_paths import PROCESSED_DIR

OUT = KO_ROOT / "Figures" / "generated"


def setup():
    plt.rcParams.update({
        "font.family": "NanumMyeongjo",
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        "font.size": 10, "axes.labelsize": 11, "axes.titlesize": 11,
        "figure.dpi": 150, "savefig.dpi": 200, "savefig.bbox": "tight",
        "axes.grid": True, "grid.alpha": 0.3,
    })


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name)
    plt.close(fig)
    print("wrote", OUT / name)


def score_distributions(rankings):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4))
    for ax, col, panel in ((axes[0], f"{ENDORSERANK_ID}_score", "엔도스랭크"), (axes[1], f"{AWP_ID}_score", "AWP")):
        s = rankings[col].astype(float)
        s = s[s > 0]
        ax.hist(np.log10(s), bins=40, color="#5a4a7a", edgecolor="white", linewidth=0.3)
        ax.set_yscale("log")
        ax.set_xlabel(r"$\log_{10}$(점수)")
        ax.set_ylabel("지갑 수(로그 눈금)")
        ax.text(0.98, 0.95, panel, transform=ax.transAxes, va="top", ha="right", fontsize=10)
        if panel == "엔도스랭크":
            value, count = G._common_block(s)
            ax.annotate(f"지갑 {count:,}개가\n같은 점수 {value:.2e}", xy=(np.log10(value), count),
                        xytext=(0.45, 0.62), textcoords="axes fraction", fontsize=8,
                        arrowprops={"arrowstyle": "->", "linewidth": 0.7})
    fig.tight_layout()
    save(fig, "score-distributions.pdf")


def rank_scatter(rankings):
    er_score = rankings[f"{ENDORSERANK_ID}_score"].astype(float)
    awp_score = rankings[f"{AWP_ID}_score"].astype(float)
    n = len(rankings)
    x = pd.Series(n + 1 - stats.rankdata(er_score), index=rankings.index)
    y = pd.Series(n + 1 - stats.rankdata(awp_score), index=rankings.index)
    fig, ax = plt.subplots(figsize=(5.2, 5.0))
    rng = np.random.default_rng(42)
    idx = rng.choice(n, size=min(2000, n), replace=False)
    ax.scatter(x.iloc[idx], y.iloc[idx], s=6, alpha=0.35, color="#2c5f8a", edgecolors="none")
    ax.plot([1, n], [1, n], "k--", linewidth=0.8, label="두 순위가 같은 선")
    tau, _ = stats.kendalltau(er_score, awp_score)
    common, n_common = G._common_block(er_score)
    x_common = float(x[er_score == common].iloc[0])
    ax.text(x_common + 80, n * 0.30, f"지갑 {n_common:,}개 동점\n(점수 {common:.2e})", fontsize=7.5, va="center")
    n_zero = int((er_score == 0).sum())
    if n_zero:
        x_zero = float(x[er_score == 0].iloc[0])
        ax.text(x_zero - 80, n * 0.22, f"지갑 {n_zero:,}개 동점\n(점수 0)", fontsize=7.5, va="center", ha="right")
    ax.set_xlabel("엔도스랭크 순위(1 = 가장 높음, 동점은 평균 순위를 나눠 가짐)")
    ax.set_ylabel("AWP 순위(1 = 가장 높은 점수)")
    ax.legend(loc="upper left", frameon=False, title=rf"켄달 $\tau_b$ = {tau:.3f}")
    ax.set_xlim(-60, n + 60)
    ax.set_ylim(-60, n + 60)
    ax.set_aspect("equal", adjustable="box")
    save(fig, "rank-scatter.pdf")
    return tau, n_common, common, n_zero


def runtime_scaling(summary):
    rows = (summary.get("benchmark_tier2") or {}).get("rows") or []
    incohort_rows = (summary.get("benchmark_scaling") or {}).get("rows") or []
    fig, ax = plt.subplots(figsize=(5.8, 3.8))
    all_n = []
    if incohort_rows:
        n = [r["n_wallets"] for r in incohort_rows]
        ax.plot(n, [r[ENDORSERANK_ID]["runtime_sec_mean"] for r in incohort_rows], "o-", color="#2c5f8a", label="엔도스랭크(코호트 안)")
        ax.plot(n, [r[AWP_ID]["runtime_sec_mean"] for r in incohort_rows], "s-", color="#a03c3c", label="AWP(코호트 안)")
        all_n.extend(n)
    if rows:
        n2 = [r["n_wallets"] for r in rows]
        ax.plot(n2, [r[ENDORSERANK_ID]["runtime_sec_mean"] for r in rows], "o--", color="#5a8ab8", label="엔도스랭크(확장 풀)")
        ax.plot(n2, [r[AWP_ID]["runtime_sec_mean"] for r in rows], "s--", color="#c06060", label="AWP(확장 풀)")
        all_n.extend(n2)
    ax.set_xscale("log")
    ticks = sorted(set(all_n))
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.set_xlim(min(all_n) * 0.9, max(all_n) * 1.1)
    plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
    ax.set_xlabel("지갑 수 $n$(로그 눈금)")
    ax.set_ylabel("풀이 한 번에 걸린 실제 시간(초)")
    ax.legend(frameon=False, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2)
    save(fig, "runtime-scaling.pdf")


def damping_sensitivity(summary):
    rows = ((summary.get("robustness") or {}).get("damping_sweep") or {}).get("rows") or []
    d = [r["damping"] for r in rows]
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    ax.plot(d, [r["er_allowance_tau"] for r in rows], "o-", color="#2c5f8a", label="ER 허락")
    ax.plot(d, [r["awp_allowance_tau"] for r in rows], "s-", color="#a03c3c", label="AWP 허락")
    ax.plot(d, [r["er_transfer_tau"] for r in rows], "o--", color="#5a8ab8", label="ER 송금")
    ax.plot(d, [r["awp_transfer_tau"] for r in rows], "s--", color="#c06060", label="AWP 송금")
    ax.set_xlabel("페이지랭크 감쇠 계수 $d$")
    ax.set_ylabel(r"평균 켄달 $\tau$")
    ax.legend(frameon=False, fontsize=8, loc="center", bbox_to_anchor=(0.5, 0.3), ncol=2)
    ax.set_xticks(d)
    save(fig, "damping-sensitivity.pdf")
    return rows


def logistic_decay():
    k, t0 = 0.01, 180.0
    window_days = 182.0
    dt = np.linspace(0, 400, 400)
    sigma = 1.0 / (1.0 + np.exp(k * (dt - t0)))
    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    ax.axvspan(0, window_days, color="#c8d4e0", alpha=0.35, linewidth=0)
    ax.text(window_days / 2, 0.08, "관찰 기간 안에서\n나올 수 있는 나이", ha="center", fontsize=8)
    ax.plot(dt, sigma, color="#2c5f8a", linewidth=2)
    ax.axvline(t0, color="gray", linestyle="--", linewidth=0.8)
    ax.text(t0 + 5, 0.55, r"$t_0=180$일", fontsize=9)
    ax.set_xlabel(r"지난 날수 $\Delta t$(일)")
    ax.set_ylabel(r"감쇠 무게 $\sigma(\Delta t)$")
    ax.set_ylim(-0.02, 1.05)
    save(fig, "logistic-decay.pdf")


def main():
    setup()
    rankings = pd.read_parquet(PROCESSED_DIR / "wallet_rankings.parquet")
    summary = json.loads((PROCESSED_DIR / "eval_summary.json").read_text(encoding="utf-8"))
    score_distributions(rankings)
    print("rank scatter values:", rank_scatter(rankings))
    runtime_scaling(summary)
    print("damping rows:", damping_sensitivity(summary))
    logistic_decay()


if __name__ == "__main__":
    main()
