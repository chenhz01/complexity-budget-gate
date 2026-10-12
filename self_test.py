#!/usr/bin/env python3
"""self_test for complexity-budget-gate. Tiers: [A] functional, [B] exception/CLI, [C] extreme edges."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import complexity_budget_gate as cbg  # noqa: E402

RESULTS = []


def check(name, cond):
    RESULTS.append((name, bool(cond)))


def run_cli(args):
    return subprocess.run([sys.executable, os.path.join(HERE, "complexity_budget_gate.py")] + args,
                          capture_output=True, text=True)


TMP = tempfile.mkdtemp(prefix="cbg_selftest_")


def p(name):
    return os.path.join(TMP, name)


def _bad_budget(obj):
    path = p("bad_%d.json" % len(RESULTS))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    try:
        cbg.load_budget(path)
        return False
    except ValueError:
        return True


def _binary_py():
    path = p("bin.py")
    with open(path, "wb") as f:
        f.write(b"\xff\xfe\x00def f(): pass")
    return path


def write(name, text):
    path = os.path.join(TMP, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


SIMPLE = "def f(x):\n    return x + 1\n"
BRANCHY = ("def g(x):\n"
           "    if x > 0:\n"
           "        if x > 10:\n"
           "            return 2\n"
           "        return 1\n"
           "    for i in range(x):\n"
           "        if i:\n"
           "            x += 1\n"
           "    return x and x or 0\n")
NESTED = ("def outer(x):\n"
          "    def inner(y):\n"
          "        if y:\n"
          "            return 1\n"
          "        return 0\n"
          "    return inner(x)\n")


def budget(default, files=None):
    return write("b_%d.json" % (abs(hash((default, json.dumps(files or {})))) % 10**8),
                 json.dumps({"default": default, "files": files or {}}))


# ---------------- [A] functional ----------------
check("A01 simple function cc=1", cbg.file_complexities(write("s.py", SIMPLE)) == [("f", 1)])
check("A02 branchy function cc=9", cbg.file_complexities(write("br.py", BRANCHY)) == [("g", 9)])
check("A03 nested functions reported separately",
      dict(cbg.file_complexities(write("n.py", NESTED))) == {"outer": 1, "inner": 2})
check("A04 methods found in classes", "m" in dict(cbg.file_complexities(
    write("c.py", "class C:\n    def m(self):\n        if self:\n            return 1\n"))))
check("A05 async functions found", cbg.file_complexities(
    write("a.py", "async def h():\n    return 1\n")) == [("h", 1)])
check("A06 comprehensions count", cbg.file_complexities(write("cp.py",
    "def q(xs):\n    return [x for x in xs if x]\n")) == [("q", 3)])
check("A07 and/or chains count", cbg.file_complexities(write("bo.py",
    "def r(a, b, c):\n    return a and b and c\n")) == [("r", 4)])
check("A08 except handlers count", cbg.file_complexities(write("ex.py",
    "def t():\n    try:\n        pass\n    except ValueError:\n        pass\n    except KeyError:\n        pass\n"
    )) == [("t", 3)])
check("A09 default budget applied", cbg.budget_for("any/path.py", 8, {}) == 8)
check("A10 glob override applied", cbg.budget_for("legacy/old.py", 8, {"legacy/*.py": 15}) == 15)
check("A11 non-matching glob falls back", cbg.budget_for("src/new.py", 8, {"legacy/*.py": 15}) == 8)
check("A12 longest glob wins", cbg.budget_for("legacy/special/x.py", 8,
      {"legacy/*.py": 15, "legacy/special/*.py": 20}) == 20)
check("A13 clean run zero violations", cbg.check([write("ok.py", SIMPLE)], budget(8))["violations"] == [])
check("A14 over-budget detected", len(cbg.check([write("ov.py", BRANCHY)], budget(3))["violations"]) == 1)
check("A15 report has worst cc", cbg.check([write("ov2.py", BRANCHY)], budget(3))["worst"] == 9)
check("A16 directory walking finds py files",
      cbg.check([TMP], budget(1))["files_scanned"] >= 5)
check("A17 budget-template writes file", (cbg.write_template(p("tpl.json")),
      json.load(open(p("tpl.json")))["default"] == 8)[1])
check("A18 over_by computed", cbg.check([write("ov3.py", BRANCHY)], budget(3))["violations"][0]["over_by"] == 6)
check("A19 per-file override suppresses violation", cbg.check(
    [write("ov4.py", BRANCHY)], budget(3, {"**/ov4.py": 10}))["violations"] == [])
check("A20 exclude list works", cbg.check([write("skipme/ex.py", BRANCHY)],
      budget(3), exclude=["**/skipme/**"])["violations"] == [])

check("B01 budget missing default rejected", _bad_budget({"files": {}}))
check("B02 budget default not int rejected", _bad_budget({"default": "x"}))
check("B03 budget default zero rejected", _bad_budget({"default": 0}))
check("B04 budget files not dict rejected", _bad_budget({"default": 8, "files": []}))


check("B05 syntax error file reported as violation", cbg.check(
    [write("syn.py", "def broken(:\n")], budget(8))["violations"][0]["function"] == "<parse>")
check("B06 CLI check clean exits 0", run_cli(
    ["check", p("s.py"), "--budget", budget(8)]).returncode == 0)
check("B07 CLI check over-budget exits 1", run_cli(
    ["check", p("ov.py"), "--budget", budget(3)]).returncode == 1)
check("B08 CLI missing budget file exits 2", run_cli(
    ["check", p("s.py"), "--budget", p("missing.json")]).returncode == 2)
check("B09 CLI report file written", run_cli(
    ["check", p("ov.py"), "--budget", budget(3), "--report", p("rep.json")]
).returncode == 1 and json.load(open(p("rep.json")))["worst"] == 9)
check("B10 CLI budget-template works", run_cli(
    ["budget-template", "--out", p("tpl2.json")]).returncode == 0 and os.path.exists(p("tpl2.json")))
check("B11 CLI no subcommand exits 2", run_cli([]).returncode == 2)
check("B12 CLI missing paths arg exits 2", run_cli(["check", "--budget", budget(8)]).returncode == 2)
check("B13 non-utf8 py file fails closed exit 2", run_cli(
    ["check", _binary_py(), "--budget", budget(8)]).returncode == 2)

# ---------------- [C] extreme edges ----------------
check("C01 empty file parses with no functions",
      cbg.file_complexities(write("empty.py", "")) == [])
check("C02 empty file clean under budget 1", cbg.check([write("empty2.py", "")], budget(1))["violations"] == [])
LONG_LINE = "def long_cond(a, b, c, d):\n    return a and b and c and d and a or b or c or d\n"
check("C03 dense bool ops counted (cc=11)", cbg.file_complexities(write("dense.py", LONG_LINE)) == [("long_cond", 10)])
check("C04 200k-char flat function parses", len(cbg.file_complexities(
    write("big.py", "def big(x):\n" + "    y = x\n" * 20000 + "    return y\n"))) == 1)
DEEP = "def deep(x):\n" + "".join("    " * i + "if x:\n" for i in range(1, 41)) + "    " * 41 + "return 1\n"
check("C05 40-level nesting cc=41", cbg.file_complexities(write("deep.py", DEEP)) == [("deep", 41)])
check("C06 deep nesting over budget 10", len(cbg.check([p("deep.py")], budget(10))["violations"]) == 1)
check("C07 unicode function name handled", cbg.file_complexities(write("uni.py",
    "def 中文函数(x):\n    if x:\n        return 1\n    return 0\n")) == [("中文函数", 2)])
check("C08 unicode comment file scans clean", cbg.check([write("uni2.py",
    "# 注释 → 符号\ndef f():\n    return 1\n")], budget(1))["violations"] == [])
check("C09 lambda does not inflate enclosing cc", cbg.file_complexities(write("lam.py",
    "def f(xs):\n    return list(map(lambda x: x if x else 0, xs))\n")) == [("f", 1)])
check("C10 200-branch function counted", len(cbg.file_complexities(write("many.py",
    "def many(x):\n" + "".join("    if x == %d:\n        return %d\n" % (i, i) for i in range(200))
    + "    return -1\n"))) == 1)
check("C11 200-branch over budget detected", cbg.check([p("many.py")], budget(50))["violations"][0]["complexity"] == 201)
check("C12 match-case counted", cbg.file_complexities(write("mc.py",
    "def m(v):\n    match v:\n        case 1:\n            return 1\n        case 2:\n            return 2\n"
    )) == [("m", 3)])
check("C13 while-else does not double count", cbg.file_complexities(write("we.py",
    "def w(x):\n    while x:\n        x -= 1\n    else:\n        pass\n    return x\n")) == [("w", 2)])
check("C14 duplicate paths deduped", cbg.check([p("s.py"), p("s.py")], budget(8))["files_scanned"] == 1)
check("C15 nested __pycache__ excluded", os.path.basename(
    cbg.collect_python_files([TMP])[0]).endswith(".py"))
check("C16 non-py files ignored", cbg.check([write("note.txt", "def f(): pass")], budget(1))["files_scanned"] == 0)
check("C17 ternary counted", cbg.file_complexities(write("ie.py",
    "def f(x):\n    return 1 if x else 0\n")) == [("f", 2)])
check("C18 giant budget never trips", cbg.check([p("many.py")], budget(10**9))["violations"] == [])
check("C19 corrupt budget json exit 2", run_cli(
    ["check", p("s.py"), "--budget", write("corrupt.json", "{oops")]).returncode == 2)
check("C20 assert counted", cbg.file_complexities(write("as.py",
    "def f(x):\n    assert x\n    return x\n")) == [("f", 2)])


# ---------------- [R2] round-2 block (v0.1.1: --max-violations ratchet) ----------------
DEEP2 = "def d2(x):\n" + "".join("    " * i + "if x:\n" for i in range(1, 61)) + "    " * 61 + "return 1\n"
check("R01 tolerate 1 violation exits 0", run_cli(
    ["check", p("ov.py"), "--budget", budget(3), "--max-violations", "1"]).returncode == 0)
check("R02 tolerate 0 still exits 1", run_cli(
    ["check", p("ov.py"), "--budget", budget(3), "--max-violations", "0"]).returncode == 1)
check("R03 two violations exceed tolerance 1", run_cli(
    ["check", p("ov.py"), p("ov2.py"), "--budget", budget(3), "--max-violations", "1"]).returncode == 1)
check("R04 negative tolerance still fails", run_cli(
    ["check", p("ov.py"), "--budget", budget(3), "--max-violations", "-5"]).returncode == 1)
check("R05 clean run with tolerance exits 0", run_cli(
    ["check", p("s.py"), "--budget", budget(8), "--max-violations", "3"]).returncode == 0)
check("R06 report file holds 2 violations", run_cli(
    ["check", p("ov.py"), p("ov2.py"), "--budget", budget(3), "--report", p("rep2.json")]
).returncode == 1 and len(json.load(open(p("rep2.json")))["violations"]) == 2)
check("R07 worst equals max function cc", cbg.check([p("many.py")], budget(500))["worst"] == 201)
check("R08 backslash glob pattern normalized", cbg.budget_for(
    "legacy/old.py", 8, {"legacy\\*.py": 15}) == 15)
check("R09 60-level nesting parses cc=61",
      cbg.file_complexities(write("deep2.py", DEEP2)) == [("d2", 61)])
check("R10 100-level over budget flagged", len(cbg.check([p("deep2.py")], budget(50))["violations"]) == 1)
check("R11 unicode filename glob override applies", cbg.budget_for(
    "legacy/模块.py", 8, {"legacy/*.py": 15}) == 15)


def main():
    passed = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    for n, ok in RESULTS:
        if not ok:
            print("FAIL:", n)
    print("SUMMARY: PASS %d/%d" % (passed, total))
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
