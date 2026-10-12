# Alignment Audit (Rules 85-100 / 16 items) — complexity-budget-gate v0.1.1

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Safety/Ethics section | N/A | Code-quality gate; no dual-use surface. Fails closed (exit 2) on unreadable/corrupt inputs; syntax errors surfaced as report rows |
| 2 | Privacy/dezero | PASS | No secrets/tokens/real names; contact uses hcac4735@agent.qq.com only; `grep -rEn "(sk-\|ghp_\|api[_-]?key\s*=\s*['\"][A-Za-z0-9])" .` → 0 hits |
| 3 | Copyright boundary | PASS | radon/mccabe/lizard comparisons are structural restatements of public knowledge, no >50-char copied text; MIT LICENSE present, "zhengming contributors" |
| 4 | Fact-check annotation | PASS | "64 cases, ~15 s" marked [Measured] with repro `python self_test.py`; "≈1 s for ~100 files" marked [estimated]; ±1 discrepancy claim is qualitative |
| 5 | Confidence grading | PASS | Opener: [High ≥80%] counting + exit codes, [Medium] per-function budget model; repeated in [Core Assumptions] (≥2 explicit labels) |
| 6 | PLAN B built-in | PASS | "Minimal Fallback (PLAN B)" section: one-grep elif trend line, zero tooling |
| 7 | Timeout preset | PASS | Quickstart states "~2 min total" with per-step instant / ≈1 s markers |
| 8 | Rule-conflict arbitration | PASS | "Design Trade-offs" opens with priority order: correctness of counting > determinism > CI ergonomics > language-feature coverage |
| 9 | Version changelog | PASS | CHANGELOG.md v0.1.0 + v0.1.1; v0.1.1 lists BoolOp counting fix, ratchet flag, and test delta |
| 10 | Exemption instruction | N/A | Session-level rule; static repo content not applicable |
| 11 | External-knowledge cutoff | PASS | Equivalence-absence claim dated "as of 2026-10-11"; no version-sensitive third-party claims |
| 12 | Assumption explicitness | PASS | "[Core Assumptions]" section with 3 labeled items |
| 13 | Logic-check trio | PASS | self_test.py tiers: [A] functional (20), [B] exception/CLI (13), [C] extreme edges (20: empty/200k-char/60-deep-nesting/unicode/200-branch/binary), [R2] round-2 (11). Final run: `python self_test.py` → `SUMMARY: PASS 64/64` |
| 14 | Socratic question | PASS | FAQ "When NOT to use this tool?" with 4 concrete anti-use-cases (greenfield culture, non-Python, flow-graph metrics, monorepo ranking) |
| 15 | Pareto improvement | PASS | v0.1.1: test count 53→64 (+21% ≥20% gate) + BoolOp undercount correctness fix + `--max-violations` ratchet feature; documented in CHANGELOG, suite re-run green |
| 16 | Ultimate fallback (≤60-word opener) | PASS | Opener = 59 words, includes what/who-needs-it/skip-judgment sentences |

Second-order effects (rule 16 bonus): PASS — "Limits & Second-order Effects" lists ratchet ossification, glob bargaining, and function-splitting metric gaming.

Scan evidence: `grep -rEn "(sk-|ghp_|api[_-]?key\s*=\s*['\"][A-Za-z0-9])" .` → 0 hits; `grep -c "hcac4735@agent.qq.com" README.md` → 1.
