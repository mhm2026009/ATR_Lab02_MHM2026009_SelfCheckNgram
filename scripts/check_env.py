#!/usr/bin/env python
"""Environment sanity check. Prints versions and verifies that the raw result files load and are consistent."""
import sys, os, platform, importlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
print("python", sys.version.split()[0], platform.platform())
for m in ["numpy", "pandas", "scipy", "sklearn", "matplotlib", "selfcheckgpt", "datasets", "torch"]:
    try: print(f"{m:14s}", getattr(importlib.import_module(m), "__version__", "installed (no __version__)"))
    except ImportError: print(f"{m:14s} NOT INSTALLED" + ("  (only needed for scripts/run_selfcheck.py)" if m in ("selfcheckgpt","datasets","torch") else ""))
from src.metrics import load_main
df = load_main(f"{ROOT}/results/raw/selfcheck_results.csv")
print("OK raw results:", len(df), "rows;", df.doc_id.nunique(), "biographies; k =", sorted(df.sample_count.unique()))
