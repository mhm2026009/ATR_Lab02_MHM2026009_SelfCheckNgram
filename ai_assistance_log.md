# AI assistance log

Tool for the entries below: Claude (Anthropic chat interface), session of 2026-11-18. Only things that really happened in that session are logged.

## Not recorded (student must fill in)
The earlier Colab notebook (`notebooks/ATR_final_assignment_colab_original.ipynb`) and the earlier staged prompts (Prompts 01-02, then up to 04, then 11) were
done in other sessions. I have no record of those prompts, so none are invented here. [USER TO FILL: tool, prompt text or summary, what you changed]

## Session 2026-11-18 entries

| # | Task | Prompt / request (summary) | AI proposal | Human decision | Verification method | Change / outcome |
|---|---|---|---|---|---|---|
| 1 | Assess pending work | "How much of my work is pending; check my friend's zip and repo" | Compared the assignment PDF with the notebook, CSVs and the peer's zip | Student asked the AI to complete everything | Read files directly; opened notebook cells | Pending list produced |
| 2 | Audit of a peer's submission | (same request) | Found that the peer's `run_experiments.py` hard-codes results in a dictionary and that his tables disagree with his own CSV log | Peer's numbers and structure NOT reused (D-11) | Read the script; recomputed his group means and a Wilcoxon test from his log | Peer's table says p = 0.03; recomputation from his log gave p of about 0.004 |
| 3 | Evaluation code | "Complete everything" | `src/metrics.py`, `scripts/evaluate.py` rebuilding all tables from raw CSVs | [USER TO CONFIRM: reviewed and understood] | Re-ran the Colab bootstrap with the same RNG pattern; compared with the saved CIs | Matches to 7e-17 (`consistency_vs_colab.csv`) |
| 4 | **AI caught a methodological issue** | (same) | Threshold 4.648 (notebook cell 25) was fit by Youden's J and scored on the same data | [USER TO CONFIRM] Report grouped-CV threshold as primary | 5-fold GroupKFold by biography | In-sample accuracy 0.692 vs CV 0.680: small effect, reported anyway |
| 5 | Added controls | (same) | Sentence position, length and random controls | [USER TO CONFIRM] keep controls | Computed with paired biography-level bootstrap | Position control is not distinguishable from SelfCheck k=5 (AUROC diff +0.007, 95% CI -0.036 to 0.047); reported as a limitation |
| 6 | **AI/tool error (real)** | Skeleton directory creation | First shell command used brace expansion under `/bin/sh`; it created a literal folder named `{src,scripts,...` and failed to copy files | - | Noticed missing files and the stray folder | Deleted the folder and redid it with `bash` |
| 7 | **AI/tool error (real)** | Writing the docs | One heredoc broke on an apostrophe in the text and wrote four partial files | - | `ls` showed files of the wrong size | Deleted them and recreated with the file tool |
| 8 | Paper draft | Write LaTeX paper from measured tables | Draft in `paper/main.tex` with numbers copied from `results/tables` | [USER TO CONFIRM] | Cross-check each number against CSV (see `paper/README_numbers.md`) | - |
| 9 | Bibliography | Create `.bib` | Entries written from the AI's memory, not from a source the student supplied | Must be verified by the student | NOT verified | Marked `[VERIFY]` in `references.bib` |

## What I should be able to explain in the viva
1. Why AP looks good (0.82) while AUROC is only 0.65: the positive class is 73% of sentences, so AP chance level is already 0.73.
2. Why k=20 has zero seed variance (all 20 samples are always used).
3. Why bootstrap and CV are grouped by biography.
4. Why the sentence-position control matters and what Fig. 4 shows.
5. What the experiment cannot show: it is one detector (unigram), one dataset, one generator (GPT-3), one labelling.

## Risks that remain
* Student has not personally reviewed the AI-written scripts and paper. The assignment requires ownership: read and run every script before submitting.
* Bibliography and review-section references are unverified.
* No second published method; no comparison with the original paper's numbers.
