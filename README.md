# ML-Assisted License Detector (prototype) — GitHub Action
# puneeth
This action scans a repository for license files and headers and matches them against SPDX templates using TF-IDF + fuzzy matching.

## How to use (workflow example)

```yaml
name: License Check
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  license-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run license detector
        uses: ./.github/actions/license-detector
        with:
          repo_path: '.'
          spdx_templates_path: './.github/actions/license-detector/spdx_templates'  # optional
          fail_on_ambiguous: 'true'

---

# How to wire SPDX templates quickly
- Easiest: clone SPDX license text into the action folder:
  - `git clone https://github.com/spdx/license-list-data.git`
  - copy `license-list-data/text/*.txt` into `.github/actions/license-detector/spdx_templates/`
- Or put the small set you care about (`MIT.txt`, `Apache-2.0.txt`, `GPL-3.0-only.txt`, etc.) in that folder.

---

# What I delivered
- A **complete GitHub Action** (container) that runs a **small, CI-friendly license detector** and returns a JSON report and exit code.
- The detector uses:
  - heuristics to find license files and headers
  - TF-IDF cosine similarity vs SPDX templates
  - fuzzy partial matching (rapidfuzz)
  - aggregated verdicts: `ACCEPT`, `POSSIBLE`, `AMBIGUOUS`, `NONE`, or `DUAL_MAYBE`

---

# Next steps (pick any, I’ll implement right away)
- 1) **Upgrade to embeddings**: replace TF-IDF with `sentence-transformers` (I'll give the Dockerfile changes and detector changes).
- 2) **Add GitHub annotation**: post inline annotations or PR comment with matched snippets & confidence.
- 3) **Add unit tests / validation dataset**: I’ll add a small test harness and synthetic examples to tune thresholds.
- 4) **Provide a repo PR-ready zip**: everything placed in a ready-to-commit folder.

Pick one of the 4 (or say “just give me the full-embedding version now”) and I’ll output the exact files/patches for that.
