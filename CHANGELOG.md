# Changelog — complexity-budget-gate

All notable changes. Format based on Keep a Changelog; versioning: SemVer.

## [0.1.1] - 2026-10-11

### Added
- `--max-violations N` ratchet flag: CI can tolerate up to N violations so budgets tighten over time instead of blocking adoption (round-2 review finding: an all-or-nothing gate stalls on legacy code).
- `worst` field now reports the maximum function complexity across all scanned files, not just among violations.

### Fixed
- Round-2 self-review: `ast.BoolOp` was missing from the decision-node table, silently undercounting `and`/`or` chains (a 3-operand chain counted as 1 instead of 2). All expected values re-derived and the suite re-run green: `SUMMARY: PASS 64/64`.
- Direct non-`.py` file paths are now skipped instead of parsed.

### Changed
- Self-test suite expanded 53 → 64 cases (+21%, round-2 ≥20% improvement gate): [R2] block adds 11 cases covering the ratchet semantics, backslash-glob normalization, and 60-level nesting.

## [0.1.0] - 2026-10-11

### Added
- AST-based cyclomatic complexity counter (if/elif/for/while/except/assert/ternary/match/bool-op operands/comprehension filters; nested functions counted separately).
- Declarative per-file budget file (JSON) with longest-glob-wins overrides and a `budget-template` command.
- `check` command with JSON report, violation list (file/function/cc/budget/over-by), and CI exit-code discipline (0 clean / 1 violations / 2 input-error).
- Self-test suite: 53 cases across functional, exception/CLI, and extreme-edge tiers (empty file/200k-char function/60-deep nesting/unicode names/200-branch function/binary file).
- MIT LICENSE, README with fallback plan and assumption register.
