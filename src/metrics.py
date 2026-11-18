"""Core evaluation helpers for the SelfCheck-NGram sentence-level study.

Positive class (actual == 1): sentence annotated major_inaccurate or minor_inaccurate.
Higher hallucination_score => predicted more likely to be non-factual.
AP (average precision) and AUROC: higher is better.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

KS = (5, 10, 20)
LABELS = ("accurate", "minor_inaccurate", "major_inaccurate")


def load_main(path):
    """Load seed-42 sentence-level results and run integrity checks."""
    df = pd.read_csv(path)
    need = {"doc_id", "sentence_id", "sentence", "human_label", "actual",
            "sample_count", "hallucination_score"}
    assert need <= set(df.columns), f"missing columns: {need - set(df.columns)}"
    assert not df[sorted(need)].isna().any().any(), "missing values found"
    assert set(df.sample_count.unique()) == set(KS)
    assert set(df.human_label.unique()) <= set(LABELS)
    assert ((df.human_label != "accurate").astype(int) == df.actual).all(), "label/actual mismatch"
    keys = {k: df[df.sample_count == k][["doc_id", "sentence_id"]].values for k in KS}
    assert all((keys[k] == keys[KS[0]]).all() for k in KS), "k-conditions are not row-aligned"
    return df


def to_wide(df):
    """One row per sentence: s5/s10/s20 scores plus trivial controls."""
    base = df[df.sample_count == 20].sort_values(["doc_id", "sentence_id"]).reset_index(drop=True)
    wide = base[["doc_id", "sentence_id", "sentence", "human_label", "actual"]].copy()
    for k in KS:
        part = df[df.sample_count == k].sort_values(["doc_id", "sentence_id"]).reset_index(drop=True)
        assert (part[["doc_id", "sentence_id"]].values == wide[["doc_id", "sentence_id"]].values).all()
        wide[f"s{k}"] = part.hallucination_score.values
    wide["ctl_position"] = wide.sentence_id.astype(float)       # later sentence => riskier
    wide["ctl_length"] = wide.sentence.str.len().astype(float)  # longer sentence => riskier
    rng = np.random.default_rng(0)
    wide["ctl_random"] = rng.random(len(wide))                  # fixed random scorer
    return wide


def ap_auc(y, s):
    return average_precision_score(y, s), roc_auc_score(y, s)


def doc_bootstrap(wide, cols, n_boot=1000, seed=42):
    """Biography-level bootstrap. Same RNG call pattern as the original Colab notebook."""
    rng = np.random.default_rng(seed)
    doc_ids = sorted(wide.doc_id.unique())
    idx_by_doc = {d: np.where(wide.doc_id.values == d)[0] for d in doc_ids}
    y = wide.actual.values
    mats = {c: wide[c].values for c in cols}
    rows = []
    for _ in range(n_boot):
        sel = rng.choice(doc_ids, size=len(doc_ids), replace=True)
        idx = np.concatenate([idx_by_doc[d] for d in sel])
        row = {}
        for c in cols:
            ap, au = ap_auc(y[idx], mats[c][idx])
            row[f"AP_{c}"], row[f"AUROC_{c}"] = ap, au
        rows.append(row)
    return pd.DataFrame(rows)


def ci(series, lo=2.5, hi=97.5):
    return float(series.mean()), float(np.percentile(series, lo)), float(np.percentile(series, hi))
