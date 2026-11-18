# Where each number in the paper comes from
| Paper item | Source file (results/tables/) | Column / row |
|---|---|---|
| Table 1 AUROC/AP point estimates, controls, chance | main_metrics_seed42.csv | all rows |
| Table 1 CIs | bootstrap_ci.csv | AP_s*/AUROC_s*, AP_ctl_*/AUROC_ctl_* |
| Seed std (0.0045, 0.0022) and means (0.5955, 0.6293) | seed_summary.csv | AUROC_mean / AUROC_std |
| k=20 vs k=5 (+0.066, +0.038) | bootstrap_ci.csv | AUROC_diff_20_5, AP_diff_20_5 |
| Table 2 paired differences vs controls | bootstrap_ci.csv | AUROC_diff_{5,10,20}_vs_position, AUROC_diff_20_vs_length, AP_diff_20_vs_position |
| Severity pairwise AUROC/AP | severity_pairwise_k20.csv | all rows |
| Mean scores by label (4.712 / 4.844 / 4.988) | score_by_label_k20.csv | mean |
| Table 3 thresholds and flag rates | threshold_analysis.csv, thresholds.json | all |
| Position strata (0.739 / 0.643 / 0.566; prevalence) | strata_pos_bin.csv | AUROC_k20, n, prevalence |
| Error-case observations (mean position 5.3 / 4.0, lengths 103 / 81) | false_positives_top25.csv, false_negatives_top25.csv | computed from sentence_id and sentence text |
| Reproduction vs Colab (1e-16) | consistency_vs_colab.csv | max_abs_diff |
