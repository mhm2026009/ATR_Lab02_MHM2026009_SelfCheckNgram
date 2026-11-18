#!/usr/bin/env python
"""Regenerate every table from the raw sentence-level CSVs (no model, no network needed).

Usage: python scripts/evaluate.py [--n_boot 1000]
Outputs -> results/tables/*.csv
"""
import argparse, os, sys, json
import numpy as np, pandas as pd
from sklearn.metrics import roc_curve, confusion_matrix
from sklearn.model_selection import GroupKFold
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.metrics import load_main, to_wide, ap_auc, doc_bootstrap, ci, KS

ap = argparse.ArgumentParser()
ap.add_argument("--n_boot", type=int, default=1000)
args = ap.parse_args()
RAW, OUT = f"{ROOT}/results/raw", f"{ROOT}/results/tables"
os.makedirs(OUT, exist_ok=True)

df = load_main(f"{RAW}/selfcheck_results.csv")
wide = to_wide(df)
y = wide.actual.values
print(f"[check] sentences={len(wide)} docs={wide.doc_id.nunique()} positives={y.sum()} prevalence={y.mean():.4f}")
print("[check] label counts:", wide.human_label.value_counts().to_dict())

# 1) Main metrics, seed 42 (point estimates, all methods and controls)
rows = []
for col, name in [("s5","SelfCheck-NGram k=5"),("s10","SelfCheck-NGram k=10"),("s20","SelfCheck-NGram k=20"),
                  ("ctl_position","Control: sentence position"),("ctl_length","Control: sentence length"),
                  ("ctl_random","Control: random score")]:
    a, u = ap_auc(y, wide[col]); rows.append({"method": name, "AP": a, "AUROC": u})
    if col.startswith("ctl_") and col != "ctl_random":     # opposite orientation, reported for transparency
        a2, u2 = ap_auc(y, -wide[col]); rows.append({"method": name + " (reversed sign)", "AP": a2, "AUROC": u2})
rows.append({"method": "Chance (prevalence / 0.5)", "AP": y.mean(), "AUROC": 0.5})
main = pd.DataFrame(rows); main.to_csv(f"{OUT}/main_metrics_seed42.csv", index=False)
print(main.round(4).to_string(index=False))

# 2) Five-seed stability (k=5,10; k=20 uses all 20 samples so it is seed-invariant by construction)
add = pd.read_csv(f"{RAW}/selfcheck_additional_seeds.csv")
allseeds = pd.concat([df.assign(seed=42), add], ignore_index=True)
srows = []
for (seed, k), g in allseeds.groupby(["seed", "sample_count"]):
    a, u = ap_auc(g.actual, g.hallucination_score); srows.append({"seed": seed, "sample_count": k, "AP": a, "AUROC": u})
seed_metrics = pd.DataFrame(srows); seed_metrics.to_csv(f"{OUT}/seed_metrics.csv", index=False)
seed_summary = seed_metrics.groupby("sample_count")[["AP","AUROC"]].agg(["mean","std","min","max"])
seed_summary.columns = ["_".join(c) for c in seed_summary.columns]; seed_summary.reset_index().to_csv(f"{OUT}/seed_summary.csv", index=False)
print(seed_summary.round(4).to_string())

# 3) Biography-level bootstrap CIs incl. controls and paired differences
cols = ["s5","s10","s20","ctl_position","ctl_length","ctl_random"]
boot = doc_bootstrap(wide, cols, n_boot=args.n_boot, seed=42)
boot["AP_diff_20_5"]  = boot.AP_s20 - boot.AP_s5
boot["AUROC_diff_20_5"] = boot.AUROC_s20 - boot.AUROC_s5
boot["AUROC_diff_20_vs_position"] = boot.AUROC_s20 - boot.AUROC_ctl_position
boot["AUROC_diff_20_vs_length"]   = boot.AUROC_s20 - boot.AUROC_ctl_length
boot["AP_diff_20_vs_position"] = boot.AP_s20 - boot.AP_ctl_position
boot["AP_diff_20_vs_length"]   = boot.AP_s20 - boot.AP_ctl_length
for k in (5,10):
    boot[f"AUROC_diff_{k}_vs_position"] = boot[f"AUROC_s{k}"] - boot.AUROC_ctl_position
    boot[f"AP_diff_{k}_vs_position"] = boot[f"AP_s{k}"] - boot.AP_ctl_position
boot.to_csv(f"{OUT}/bootstrap_draws.csv", index=False)
crow = []
for c in boot.columns:
    m, lo, hi = ci(boot[c]); crow.append({"metric": c, "boot_mean": m, "ci95_low": lo, "ci95_high": hi, "ci_excludes_0": (lo > 0 or hi < 0) if "diff" in c else ""})
pd.DataFrame(crow).to_csv(f"{OUT}/bootstrap_ci.csv", index=False)
print(pd.DataFrame(crow).round(4).to_string(index=False))

# 4) Severity analysis at k=20 (pairwise AUROC/AP + score summary)
w = wide.copy(); prow = []
for pos, neg in [("major_inaccurate","accurate"),("minor_inaccurate","accurate"),("major_inaccurate","minor_inaccurate")]:
    sub = w[w.human_label.isin([pos, neg])]; yy = (sub.human_label == pos).astype(int)
    a, u = ap_auc(yy, sub.s20); prow.append({"comparison": f"{pos} vs {neg}", "n_pos": int(yy.sum()), "n_neg": int((1-yy).sum()), "AUROC": u, "AP": a})
pd.DataFrame(prow).to_csv(f"{OUT}/severity_pairwise_k20.csv", index=False)
w.groupby("human_label").s20.agg(["count","mean","std","min","median","max"]).to_csv(f"{OUT}/score_by_label_k20.csv")

# 5) Threshold analysis: in-sample Youden (exploratory, as in the Colab notebook) vs 5-fold doc-grouped CV
def youden_thr(yt, s):
    f, t, th = roc_curve(yt, s); return th[np.argmax(t - f)]
thr_in = youden_thr(y, wide.s20); pred_in = (wide.s20 >= thr_in).astype(int)
pred_cv = np.zeros(len(wide), dtype=int); fold_thr = []
for tr, te in GroupKFold(n_splits=5).split(wide, y, groups=wide.doc_id):
    th = youden_thr(y[tr], wide.s20.values[tr]); fold_thr.append(float(th)); pred_cv[te] = (wide.s20.values[te] >= th).astype(int)
trows = []
for name, pred in [("in-sample Youden (exploratory)", pred_in.values), ("5-fold grouped CV Youden", pred_cv)]:
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    r = {"protocol": name, "TP": tp, "FP": fp, "FN": fn, "TN": tn, "precision": tp/(tp+fp), "recall": tp/(tp+fn), "accuracy": (tp+tn)/len(y)}
    for lab in ["major_inaccurate","minor_inaccurate"]:
        m = (wide.human_label == lab).values; r[f"detect_rate_{lab}"] = pred[m].mean()
    r["detect_rate_accurate_FP_rate"] = pred[(wide.human_label=="accurate").values].mean()
    trows.append(r)
tdf = pd.DataFrame(trows); tdf.to_csv(f"{OUT}/threshold_analysis.csv", index=False)
json.dump({"in_sample_threshold": float(thr_in), "cv_fold_thresholds": fold_thr}, open(f"{OUT}/thresholds.json","w"))
print(tdf.round(4).to_string(index=False)); print("thresholds:", thr_in, fold_thr)

# 6) Error cases (CV-threshold predictions) for qualitative inspection
w["pred_cv"] = pred_cv; w["score"] = w.s20
w[(w.actual==0)&(w.pred_cv==1)].sort_values("score", ascending=False).head(25)[["doc_id","sentence_id","sentence","human_label","score"]].to_csv(f"{OUT}/false_positives_top25.csv", index=False)
w[(w.actual==1)&(w.pred_cv==0)].sort_values("score").head(25)[["doc_id","sentence_id","sentence","human_label","score"]].to_csv(f"{OUT}/false_negatives_top25.csv", index=False)
# length of sentence vs. error
w["len_bin"] = pd.qcut(w.sentence.str.len(), 4, labels=["Q1 short","Q2","Q3","Q4 long"])
w["pos_bin"] = pd.cut(w.sentence_id, [-1,1,4,100], labels=["pos 0-1","pos 2-4","pos 5+"])
for b in ["len_bin","pos_bin"]:
    g = w.groupby(b, observed=True).apply(lambda d: pd.Series({"n": len(d), "prevalence": d.actual.mean(), "AUROC_k20": ap_auc(d.actual, d.s20)[1], "AP_k20": ap_auc(d.actual, d.s20)[0]}), include_groups=False)
    g.to_csv(f"{OUT}/strata_{b}.csv"); print(g.round(4))

# 7) Consistency check against the numbers saved by the original Colab run
orig = pd.read_csv(f"{ROOT}/results/colab_originals/selfcheck_confidence_intervals.csv").set_index("Metric")
cmp = []
for key, col in [("AP_5","AP_s5"),("AP_10","AP_s10"),("AP_20","AP_s20"),("AUROC_5","AUROC_s5"),("AUROC_10","AUROC_s10"),("AUROC_20","AUROC_s20"),("AP_difference_20_5","AP_diff_20_5"),("AUROC_difference_20_5","AUROC_diff_20_5")]:
    m, lo, hi = ci(boot[col]); o = orig.loc[key]
    cmp.append({"metric": key, "colab_mean": o["Bootstrap mean"], "rerun_mean": m, "colab_lo": o["95% CI lower"], "rerun_lo": lo, "colab_hi": o["95% CI upper"], "rerun_hi": hi, "max_abs_diff": max(abs(o["Bootstrap mean"]-m), abs(o["95% CI lower"]-lo), abs(o["95% CI upper"]-hi))})
cmp = pd.DataFrame(cmp); cmp.to_csv(f"{OUT}/consistency_vs_colab.csv", index=False)
print(cmp.round(5).to_string(index=False)); print("MAX ABS DIFF vs Colab:", cmp.max_abs_diff.max())
