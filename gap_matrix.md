# Gap matrix (Prompt 02): source evidence -> candidate question -> possible experiment

Labels: VERIFIED = checked from original source or executed code; INFERRED = my interpretation; UNKNOWN = missing evidence.

**Important:** the text of my T20 review PDF was not available when this file was written. The gap names below are the ones listed for the review.
Every "source passage" cell must be filled in and checked against the review PDF before submission. [TO FILL]

| # | Gap named in review | Source passage in review | Reported in original paper, or my inference? | Candidate question | Experiment that would test it | Feasibility |
|---|---|---|---|---|---|---|
| 1 | Calibrated abstention | [TO FILL: section/page] | INFERRED link to detection quality | Can a cheap detector give a usable risk score for flag/abstain decisions? | Detection AUROC/AP plus threshold analysis on human-labelled sentences (**selected**) | High: data and scores exist |
| 2 | Citation-grounding benchmarks | [TO FILL] | INFERRED | Do detectors work on citations, not just biography facts? | Needs a citation-level labelled set | Medium-low |
| 3 | Claim-level provenance | [TO FILL] | INFERRED | Can flagged sentences be traced to claims and evidence? | Needs claim extraction plus evidence retrieval | Low |
| 4 | Standardized scholarly taxonomy | [TO FILL] | INFERRED | Do detector errors differ by hallucination type? | Partial: major vs minor severity (**included as RQ3**) | Medium |
| 5 | Cross-domain / longitudinal testing | [TO FILL] | INFERRED | Does performance hold on other domains and generators? | Second dataset | Medium (future work) |
| 6 | Multimodal hallucination | [TO FILL] | INFERRED | - | Out of scope | Low |

Ranking by significance, resources and feasibility: (1) detection signal for abstention, (4) severity breakdown, (5) cross-domain follow-up.

Novelty: NOT claimed. A separate literature search for prior sample-budget curves of SelfCheckGPT has not been done. [UNKNOWN]
