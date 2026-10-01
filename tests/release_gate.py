#!/usr/bin/env python3
"""Release gate for the i01 audit branch.

What this gate asserts
----------------------
Every falsifier must be RED, and every falsifier must also print at least one PASS
that is a positive control. A falsifier that is red because nothing works is not
evidence; a falsifier that is red with a working positive control is.

This is not decoration. On first execution the Quantum gate rejected two of six
falsifiers, including a claim checker that had never agreed with anything and a
falsifier whose passing controls were invisible to the gate.

This gate does NOT assert that the package is in any particular scientific state. It
asserts that the audit instruments are intact and the recorded defects are present.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
PYTHON = os.environ.get("PYTHON", "python3")

FALSIFIERS = [
    ("I01-1", "test_objective_correspondence.py"),
    ("I01-2", "test_document_correspondence.py"),
    ("I01-3", "test_provenance_reachability.py"),
]

NOISE = re.compile(r"^Running |RuntimeWarning")


def run(script, timeout=900):
    try:
        proc = subprocess.run([PYTHON, os.path.join(HERE, script)],
                              capture_output=True, text=True, cwd=ROOT,
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"
    out = "\n".join(l for l in (proc.stdout + proc.stderr).split("\n")
                    if not NOISE.search(l))
    return proc.returncode, out


def main():
    print("=" * 78)
    print("i01 audit release gate")
    print("asserts: every falsifier is RED and every falsifier's positive control "
          "still PASSES")
    print("=" * 78)

    failures = []
    for tag, script in FALSIFIERS:
        rc, out = run(script)
        n_fail = len(re.findall(r"^\s*\[FAIL\]", out, re.M))
        n_pass = len(re.findall(r"^\s*\[PASS\]", out, re.M))

        problems = []
        if rc is None:
            problems.append("timed out")
        elif rc == 0:
            problems.append("exited 0 (GREEN) — the defect it detects may be gone")
        if n_fail == 0:
            problems.append("reported no FAIL — it is not detecting anything")
        if n_pass == 0:
            problems.append("no positive control PASSED — it cannot discriminate, so "
                            "its FAIL results are void")

        print(f"  [{'OK' if not problems else 'PROBLEM':7s}] {tag} {script}")
        print(f"            exit={rc}  FAIL={n_fail}  PASS={n_pass}")
        for p in problems:
            print(f"            - {p}")
            failures.append(f"{tag}: {p}")
        print()

    print("=" * 78)
    if failures:
        print(f"GATE FAILED — {len(failures)} problem(s):")
        for f in failures:
            print(f"  {f}")
        return 1

    print(f"GATE PASSED — {len(FALSIFIERS)} falsifiers, all RED, all with a working "
          f"positive control")
    print()
    print("This is not a statement about the package's scientific merit, and not a")
    print("statement about whether the manuscript is publishable. It says the audit")
    print("instruments are intact and the recorded defects are still present.")
    print()
    print("NO MANUSCRIPT TEXT HAS BEEN EDITED ON THIS BRANCH.")
    return 0


if __name__ == "__main__":
    sys.exit(main())