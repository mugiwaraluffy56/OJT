#!/usr/bin/env python3
"""
Entry point for the GitHub Action.
Lightweight license detector: TF-IDF + fuzzy matching against SPDX templates.

Usage (action passes args):
    python entrypoint.py <repo_path> <spdx_templates_path> <fail_on_ambiguous>
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from rapidfuzz import fuzz
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# thresholds (tune on validation)
TFIDF_SIM_THRESHOLD = 0.58
FUZZY_THRESHOLD = 85

def sanitize_text(s: str) -> str:
    s = re.sub(r"/\*+|\*+/|//+|#\s?", " ", s)
    s = re.sub(r"\b(19|20)\d{2}\b", "YEAR", s)
    s = re.sub(r"\bCopyright\b.*", "COPYRIGHT", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def load_spdx_templates(folder: str) -> Dict[str,str]:
    templates = {}
    p = Path(folder)
    if not p.exists():
        return {}
    for f in p.glob("*.txt"):
        spdx = f.stem
        text = f.read_text(encoding="utf-8", errors="ignore")
        templates[spdx] = sanitize_text(text)
    return templates

def extract_candidates(repo_path: str) -> List[Tuple[str,str]]:
    candidates = []
    repo = Path(repo_path)
    # license files
    for name in ["LICENSE","LICENSE.txt","LICENSE.md","COPYING","UNLICENSE"]:
        p = repo / name
        if p.exists():
            candidates.append((str(p), sanitize_text(p.read_text(encoding="utf-8", errors="ignore"))))
    # top-of-file headers
    exts = ["*.py","*.js","*.ts","*.java","*.c","*.cpp","*.go","*.rs","*.rb","*.php"]
    for ext in exts:
        for f in repo.rglob(ext):
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            head = "\n".join(txt.splitlines()[:60])
            head_s = sanitize_text(head)
            if any(k in head_s for k in ["license", "permission is hereby", "redistribution", "gpl", "apache"]):
                candidates.append((str(f), head_s))
    # metadata files
    for f in repo.rglob("package.json"):
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        m = re.search(r'"license"\s*:\s*"([^"]+)"', txt)
        if m:
            candidates.append((str(f), sanitize_text(m.group(1))))
    return candidates

def match_candidates(candidates: List[Tuple[str,str]], templates: Dict[str,str]) -> List[Dict]:
    results = []
    if not templates:
        return results
    spdx_ids = list(templates.keys())
    template_texts = [templates[s] for s in spdx_ids]
    # TF-IDF vectorizer fit on templates + candidates for consistent vector space
    corpus = template_texts + [c for _, c in candidates]
    vectorizer = TfidfVectorizer(ngram_range=(1,3), min_df=1).fit(corpus)
    template_vecs = vectorizer.transform(template_texts)
    cand_vecs = vectorizer.transform([c for _, c in candidates]) if candidates else []
    for idx, (src, cand) in enumerate(candidates):
        rec = {"source": src, "candidate_text_sample": cand[:400]}
        # TF-IDF similarity
        if cand_vecs.shape[0] > 0:
            sims = cosine_similarity(cand_vecs[idx], template_vecs)[0]
            best_idx = int(np.argmax(sims))
            rec["best_spdx_by_tfidf"] = spdx_ids[best_idx]
            rec["tfidf_score"] = float(sims[best_idx])
        else:
            rec["best_spdx_by_tfidf"] = None
            rec["tfidf_score"] = 0.0
        # fuzzy
        fuzzy_scores = {s: fuzz.partial_ratio(cand, templates[s]) for s in spdx_ids}
        fuzzy_best_spdx, fuzzy_best_score = max(fuzzy_scores.items(), key=lambda kv: kv[1])
        rec["best_spdx_by_fuzzy"] = fuzzy_best_spdx
        rec["fuzzy_score"] = int(fuzzy_best_score)
        results.append(rec)
    return results

def aggregate(matches: List[Dict]) -> Dict:
    votes = {}
    for m in matches:
        if m.get("tfidf_score", 0) >= TFIDF_SIM_THRESHOLD:
            spdx = m["best_spdx_by_tfidf"]
            votes.setdefault(spdx, []).append(("tfidf", m["tfidf_score"]))
        if m.get("fuzzy_score", 0) >= FUZZY_THRESHOLD:
            spdx = m["best_spdx_by_fuzzy"]
            votes.setdefault(spdx, []).append(("fuzzy", m["fuzzy_score"]/100.0))
    agg = []
    for spdx, vlist in votes.items():
        score = sum([s for _, s in vlist]) / max(1, len(vlist))
        agg.append((spdx, score, vlist))
    agg = sorted(agg, key=lambda x: x[1], reverse=True)
    if not agg:
        return {"verdict": "NONE", "candidates": []}
    candidates = [{"spdx": a[0], "score": a[1], "signals": a[2]} for a in agg]
    top_score = candidates[0]["score"]
    if top_score > 0.75:
        verdict = "ACCEPT"
    elif top_score > 0.55:
        verdict = "POSSIBLE"
    else:
        verdict = "AMBIGUOUS"
    # detect likely dual-license: second candidate also high
    if len(candidates) > 1 and candidates[1]["score"] >= 0.6:
        verdict = "DUAL_MAYBE"
    return {"verdict": verdict, "candidates": candidates}

def main():
    if len(sys.argv) < 4:
        print("Usage: entrypoint.py <repo_path> <spdx_templates_path> <fail_on_ambiguous>")
        sys.exit(2)
    repo_path = sys.argv[1]
    spdx_path = sys.argv[2]
    fail_on_ambig = sys.argv[3].lower() in ("1","true","yes","y")

    templates = load_spdx_templates(spdx_path)
    if not templates:
        # try to create basic templates if folder absent: minimal builtins
        print("WARNING: No SPDX templates found at", spdx_path, "— action will use very limited heuristics.")
        # provide tiny builtins (not exhaustive)
        templates = {
            "mit": sanitize_text("Permission is hereby granted, free of charge, to any person obtaining a copy ..."),
            "apache-2.0": sanitize_text("Licensed under the Apache License, Version 2.0 (the \"License\");"),
            "gpl-3.0-only": sanitize_text("GNU GENERAL PUBLIC LICENSE Version 3"),
        }

    candidates = extract_candidates(repo_path)
    matches = match_candidates(candidates, templates)
    report = {"repo": str(repo_path), "templates_count": len(templates), "candidates_found": len(candidates), "matches": matches}
    result = aggregate(matches)
    report["result"] = result

    # Print report to stdout and to file
    out = json.dumps(report, indent=2)
    print(out)
    # also write to /github/workspace if available
    try:
        Path("/github/workspace/license-detection-report.json").write_text(out)
    except Exception:
        pass

    # Determine exit code according to verdict and fail_on_ambig
    if fail_on_ambig and result["verdict"] in ("AMBIGUOUS", "NONE", "POSSIBLE"):
        # treat POSSIBLE as cautionary fail for prototype
        print("Action configured to fail on ambiguous or none. Failing with verdict:", result["verdict"])
        sys.exit(1)
    # else success
    sys.exit(0)

if __name__ == "__main__":
    main()
