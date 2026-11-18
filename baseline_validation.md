# Baseline validation report

Baseline = official `selfcheckgpt` SelfCheck-NGram (n=1). It was not re-implemented, so this report covers (a) the data and protocol and (b) whether
the evaluation code reproduces what the Colab run produced. It does **not** yet verify agreement with the original paper.

## VERIFIED (executed code; logs in `logs/`)
* Dataset loaded in Colab: 238 biographies, each with 20 sampled passages and equal-length sentence/annotation lists (asserted in the scoring loop; notebook cells 1 and 9).
* `src/metrics.py::load_main`: no missing values; `actual` consistent with `human_label` on all 5,724 rows; the three k-conditions cover identical (doc, sentence) rows; counts accurate 516 / minor 631 / major 761 = 1,908.
* `scripts/evaluate.py` reproduces every bootstrap mean and 95% CI saved by the Colab run (`results/tables/consistency_vs_colab.csv`, max absolute difference 6.9e-17).
* Seed stability: across 5 seeds, AP/AUROC at k=5 and k=10 vary by a std of at most 0.0045; k=20 is identical by construction (all 20 samples used).
* Sanity: the random-score control gives AUROC 0.499 and AP 0.728 (prevalence 0.7296), as expected.

## UNCERTAIN
* **Agreement with the original SelfCheckGPT paper.** Not checked; no number from the paper is quoted here. To compare: score variant (average vs maximum negative log-probability), number of samples, positive class (non-factual vs factual), and which AUC-PR the paper reports. A mismatch in any of these makes a direct comparison invalid.
* Versions of `selfcheckgpt`, `datasets`, `spacy` used in Colab were not recorded.
* Whether the dataset card's license permits redistributing the sentence table in `results/raw/`.

## NEEDS CORRECTION (already handled in this repo)
* Notebook cell 25: the Youden threshold (4.648) was chosen and evaluated on the same data. Now also reported with 5-fold grouped CV (`results/tables/threshold_analysis.csv`).
* Notebook cell 32: detection and miss rates were typed in by hand. `scripts/make_figures.py` now reads them from CSV.
* Notebook cells 18-19: files were recovered after a runtime reset. Documented here; all later outputs came from the saved CSVs.

## Additional checks still required (need Colab and network)
1. Run `python scripts/run_selfcheck.py --seeds 42` and compare with `results/raw/selfcheck_results.csv` (scores should be identical). [TEST REQUIRED]
2. Compare with the original paper's reported unigram results under a matching protocol. [TO VERIFY]
3. Optionally run one more published SelfCheck variant to add a second *method* comparator. [TEST REQUIRED]
