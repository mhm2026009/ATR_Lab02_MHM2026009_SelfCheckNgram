# Research decisions log (decision -> reason -> evidence -> next action)

**Retrospective-protocol disclosure.** The SelfCheck-NGram scoring runs (5 seeds, bootstrap, error analysis in the Colab notebook) were executed
*before* this log and `configs/experiment.yaml` were written. The control baselines and the grouped-CV threshold were added afterwards, but the
main scores were not changed or re-tuned. The protocol is therefore "frozen retrospectively", not pre-registered, and the paper says so.

| ID | Decision | Reason | Evidence label | Next action |
|---|---|---|---|---|
| D-01 | Stay in the T20 hallucination area; study the detection quality of a zero-resource detector | Detection signal is a prerequisite for the review gap "calibrated abstention" | Link INFERRED; method and data access VERIFIED (notebook cells 1-3 ran) | Fill review section refs in `gap_matrix.md` |
| D-02 | Pathway B: controlled comparison (k = 5/10/20 plus controls) | Smallest credible study with available compute | VERIFIED feasible (19-20 min per seed in Colab) | - |
| D-03 | Method: official `selfcheckgpt` SelfCheck-NGram n=1; sentence score = `avg_neg_logprob` | Open package; no API or large model needed | Runs: VERIFIED. Package version: UNKNOWN | Record `pip freeze` from Colab |
| D-04 | Dataset: `potsawee/wiki_bio_gpt3_hallucination`, evaluation split | Human sentence labels plus 20 samples per biography | VERIFIED loads (238 rows) | Check dataset license [TO VERIFY] |
| D-05 | Positive class = minor or major inaccurate (prevalence 0.7296); primary metric AUROC | AP chance level is high (0.73), so AP alone is easy to over-read | VERIFIED from data | - |
| D-06 | Nested random subsets of the 20 samples; seeds 42-46 | Fair comparison across k. k=20 uses every sample, so it is seed-invariant (std = 0 by construction) | VERIFIED | - |
| D-07 | Resampling unit = biography (bootstrap and CV grouped by `doc_id`) | Sentences within a biography are correlated | VERIFIED in code | - |
| D-08 | Add controls: sentence position, sentence length, random score | A detector should beat trivial heuristics | VERIFIED computed (`results/tables/`) | - |
| D-09 | Report the grouped-CV threshold; keep in-sample Youden J only as exploratory | The in-sample threshold (4.648) was chosen and evaluated on the same data | VERIFIED: small effect (accuracy 0.692 vs 0.680) | - |
| D-10 | No second published detector included | Needs a Colab rerun with network (about 20 min per variant); not possible offline | Effect UNKNOWN | Future work; see `baseline_validation.md` |
| D-11 | Do not reuse structure or numbers of peer repo MRA2026003 | Its result files are hard-coded in `run_experiments.py` and disagree with its own log | VERIFIED by reading the code | - |

Decisions D-08 to D-11 were made by the AI assistant on the student's instruction to "complete everything"; the student must confirm or change them. [USER TO CONFIRM]
