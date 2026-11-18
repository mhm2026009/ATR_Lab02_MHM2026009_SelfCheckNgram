#!/usr/bin/env python
"""Build all paper figures from results/tables (run scripts/evaluate.py first)."""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.metrics import load_main, to_wide
T, F = f"{ROOT}/results/tables", f"{ROOT}/results/figures"
os.makedirs(F, exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150})
ci = pd.read_csv(f"{T}/bootstrap_ci.csv").set_index("metric")
seeds = pd.read_csv(f"{T}/seed_metrics.csv")

# Fig 1: AP and AUROC vs k with 95% bootstrap CI and seed points; chance/controls as reference lines
fig, ax = plt.subplots(1, 2, figsize=(8, 3.3))
for a, m, chance, lab in [(ax[0], "AP", 0.7296, "AP"), (ax[1], "AUROC", 0.5, "AUROC")]:
    ks = [5, 10, 20]
    mean = [ci.loc[f"{m}_s{k}", "boot_mean"] for k in ks]
    lo = [ci.loc[f"{m}_s{k}", "ci95_low"] for k in ks]; hi = [ci.loc[f"{m}_s{k}", "ci95_high"] for k in ks]
    a.errorbar(ks, mean, yerr=[np.array(mean)-lo, np.array(hi)-mean], fmt="o-", capsize=4, label="SelfCheck-NGram (bootstrap mean, 95% CI)")
    for k in ks:
        v = seeds[(seeds.sample_count == k)][m]; a.scatter([k]*len(v), v, s=10, c="k", alpha=.5, zorder=3, label="Individual seeds (5)" if k == 5 else None)
    a.axhline(ci.loc[f"{m}_ctl_position", "boot_mean"], ls="--", c="tab:red", label="Control: sentence position")
    a.axhline(chance, ls=":", c="gray", label="Chance")
    a.set_xticks(ks); a.set_xlabel("Number of sampled passages (k)"); a.set_ylabel(lab + " (higher = better)")
ax[0].legend(fontsize=6.5, loc="lower right"); fig.tight_layout(); fig.savefig(f"{F}/fig1_metric_vs_k.png"); plt.close(fig)

# Fig 2: AUROC of method vs controls with CI
names = [("AUROC_s20", "SelfCheck\nk=20"), ("AUROC_s10", "SelfCheck\nk=10"), ("AUROC_s5", "SelfCheck\nk=5"),
         ("AUROC_ctl_position", "Control:\nposition"), ("AUROC_ctl_length", "Control:\nlength"), ("AUROC_ctl_random", "Control:\nrandom")]
fig, ax = plt.subplots(figsize=(6.2, 3.2))
m = [ci.loc[n, "boot_mean"] for n, _ in names]; lo = [ci.loc[n, "ci95_low"] for n, _ in names]; hi = [ci.loc[n, "ci95_high"] for n, _ in names]
cols = ["tab:blue"]*3 + ["tab:red"]*3
ax.bar(range(6), m, yerr=[np.array(m)-lo, np.array(hi)-m], color=cols, capsize=4, alpha=.85)
ax.axhline(.5, ls=":", c="gray"); ax.set_xticks(range(6)); ax.set_xticklabels([l for _, l in names], fontsize=8)
ax.set_ylim(.4, .72); ax.set_ylabel("AUROC (95% bootstrap CI)"); fig.tight_layout(); fig.savefig(f"{F}/fig2_method_vs_controls.png"); plt.close(fig)

# Fig 3: score distribution by human label (k=20)
w = to_wide(load_main(f"{ROOT}/results/raw/selfcheck_results.csv"))
order = ["accurate", "minor_inaccurate", "major_inaccurate"]
fig, ax = plt.subplots(figsize=(5.5, 3.2))
ax.boxplot([w[w.human_label == l].s20 for l in order], tick_labels=["accurate\n(n=516)", "minor\n(n=631)", "major\n(n=761)"], showfliers=False)
ax.set_ylabel("Hallucination score, k=20\n(higher = more suspect)"); fig.tight_layout(); fig.savefig(f"{F}/fig3_score_by_label.png"); plt.close(fig)

# Fig 4: AUROC by sentence-position stratum (method vs overall) -> shows position confound
st = pd.read_csv(f"{T}/strata_pos_bin.csv")
fig, ax = plt.subplots(figsize=(5, 3.2))
ax.bar(st.pos_bin, st.AUROC_k20, color="tab:blue", alpha=.85); ax.axhline(.5, ls=":", c="gray")
for i, (v, n) in enumerate(zip(st.AUROC_k20, st.n)): ax.text(i, v+.01, f"{v:.3f}\n(n={int(n)})", ha="center", fontsize=8)
ax.set_ylim(.4, .85); ax.set_ylabel("AUROC, SelfCheck k=20"); ax.set_xlabel("Sentence position within biography"); fig.tight_layout(); fig.savefig(f"{F}/fig4_auroc_by_position.png"); plt.close(fig)

# Fig 5: detection rate by severity, in-sample vs grouped-CV threshold
th = pd.read_csv(f"{T}/threshold_analysis.csv")
fig, ax = plt.subplots(figsize=(5.5, 3.2)); x = np.arange(3); wd = .36
for i, (_, r) in enumerate(th.iterrows()):
    vals = [r.detect_rate_major_inaccurate, r.detect_rate_minor_inaccurate, r.detect_rate_accurate_FP_rate]
    ax.bar(x + (i-.5)*wd, vals, wd, label=r.protocol)
ax.set_xticks(x); ax.set_xticklabels(["major\n(detected)", "minor\n(detected)", "accurate\n(false alarm)"]); ax.set_ylabel("Fraction flagged"); ax.set_ylim(0, 1)
ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(f"{F}/fig5_detection_by_severity.png"); plt.close(fig)

# Fig 6: pipeline diagram
fig, ax = plt.subplots(figsize=(8, 2.2)); ax.axis("off")
boxes = ["wiki_bio_gpt3_\nhallucination\n(238 bios, 1,908 sent.)", "Sample k of 20\npassages\n(k=5,10,20; seeds)", "SelfCheck-NGram\n(unigram)\nscore per sentence", "AP / AUROC\n+ biography-level\nbootstrap", "Controls:\nposition, length,\nrandom", "Severity, threshold\n(CV), strata,\nerror cases"]
xs = np.linspace(0.02, 0.98-0.15, 6)
for x0, t in zip(xs, boxes):
    ax.add_patch(FancyBboxPatch((x0, .15), .15, .7, boxstyle="round,pad=.01", fc="#e8f0fe" if "Control" not in t else "#fde8e8", ec="k", lw=.8, transform=ax.transAxes))
    ax.text(x0+.075, .5, t, ha="center", va="center", fontsize=7, transform=ax.transAxes)
for a, b in zip(xs[:-1], xs[1:]): ax.annotate("", xy=(b, .5), xytext=(a+.15, .5), xycoords="axes fraction", arrowprops=dict(arrowstyle="->"))
fig.savefig(f"{F}/fig6_pipeline.png", bbox_inches="tight"); plt.close(fig)
print("figures written:", sorted(os.listdir(F)))
