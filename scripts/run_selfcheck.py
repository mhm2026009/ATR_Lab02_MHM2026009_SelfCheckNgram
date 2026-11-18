#!/usr/bin/env python
"""Re-generate the raw SelfCheck-NGram scores (the ~20 min/seed step run in Google Colab).

Logic is lifted from notebooks/ATR_final_assignment_colab_original.ipynb (cells 9 and 15), which were executed
in Colab. [TEST REQUIRED] as a standalone script: this file itself has NOT been executed outside the notebook.

Usage:  python scripts/run_selfcheck.py --seeds 42 43 44 45 46 --out results/raw_rerun
Needs network access to download the HF dataset (potsawee/wiki_bio_gpt3_hallucination) and `pip install selfcheckgpt datasets spacy`.
Seed s, biography d uses random.Random(s + d) to shuffle the 20 sampled passages; nested subsets of size 5/10/20 are taken.
"""
import argparse, os, random
import pandas as pd
from datasets import load_dataset
from selfcheckgpt.modeling_selfcheck import SelfCheckNgram

ap = argparse.ArgumentParser()
ap.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44, 45, 46])
ap.add_argument("--ks", type=int, nargs="+", default=[5, 10, 20])
ap.add_argument("--out", default="results/raw_rerun")
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)

ds = load_dataset("potsawee/wiki_bio_gpt3_hallucination")["evaluation"]
scorer = SelfCheckNgram(n=1)   # unigram variant, sentence score = avg_neg_logprob
for seed in a.seeds:
    rows = []
    for doc_id, row in enumerate(ds):
        sents, ann, samples = row["gpt3_sentences"], row["annotation"], row["gpt3_text_samples"]
        assert len(sents) == len(ann) and len(samples) >= 20
        idx = list(range(len(samples))); random.Random(seed + doc_id).shuffle(idx)
        for k in a.ks:
            out = scorer.predict(sentences=sents, passage=row["gpt3_text"], sampled_passages=[samples[i] for i in idx[:k]])
            sc = out["sent_level"]["avg_neg_logprob"]; assert len(sc) == len(sents)
            for sid, s in enumerate(sc):
                rows.append({"seed": seed, "doc_id": doc_id, "sentence_id": sid, "sentence": sents[sid], "human_label": ann[sid],
                             "actual": 0 if ann[sid] == "accurate" else 1, "sample_count": k, "hallucination_score": float(s)})
    pd.DataFrame(rows).to_csv(f"{a.out}/selfcheck_seed_{seed}.csv", index=False); print("seed", seed, "done", len(rows))
