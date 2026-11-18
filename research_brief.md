# One-page research brief (Gate G1)

| Field | Content |
|---|---|
| Review topic and key papers | T20 "A Taxonomy of Hallucination Types in Large Language Models for Research Applications" (my Paper 1). Original papers to verify from the review: Manakul et al. 2023 (SelfCheckGPT) [metadata in `paper/references.bib` is written from memory: re-check against the original]; others [TO FILL from my review bibliography]. |
| Research gap | The review lists as open: calibrated abstention, claim-level provenance, standardized taxonomy, citation-grounding benchmarks, cross-domain/longitudinal testing, multimodal hallucination. Narrowed to the *detection signal* that abstention would need: how good is a cheap, zero-resource, sampling-based hallucination detector, and how does it depend on sample budget? [Review section/page numbers: TO VERIFY] |
| Research question | **RQ1** How do AP/AUROC of SelfCheck-NGram change with the number of sampled passages (k = 5, 10, 20)? **RQ2** Does it beat trivial non-semantic controls (sentence position, length, random)? **RQ3** Is it better at flagging major than minor inaccuracies, and how robust is a decision threshold? |
| Study pathway | B - controlled comparative study (with elements of A: a published method evaluated under a sample-budget condition). Novelty is not claimed. |
| Dataset / protocol | `potsawee/wiki_bio_gpt3_hallucination`, evaluation split, 238 biographies / 1,908 sentences, human labels (accurate / minor / major inaccurate), 20 GPT-3 samples each. Positive = any inaccurate (prevalence 0.7296). Biography-level bootstrap and grouped CV. License [TO VERIFY]. |
| Baseline / comparators | Official `selfcheckgpt` package (SelfCheck-NGram, n=1), verified by execution. Controls: sentence position, sentence length, random. A second *published* method is NOT included (see limitations). |
| Primary metric and control | AUROC (primary), AP (secondary; chance = 0.7296). Held constant: sentences, labels, 20-sample pool, scoring function. Varied: k. |
| Computing and risks | Colab runtime, ~19-20 min per seed for scoring; evaluation runs offline in about a minute. Risks: single dataset, single GPT-3 generator, 1-gram model is weak, one set of human labels. Fallback: raw scores already saved in `results/raw`. |
| First executable milestone | DONE: `scripts/check_env.py` and `scripts/evaluate.py` reproduce all Colab bootstrap CIs to within 1e-16. |
