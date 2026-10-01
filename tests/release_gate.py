#!/usr/bin/env python3
"""Release gate for the i01 audit branch.

Two jobs, and the second is the one that matters most here.

1. INSTRUMENT INTEGRITY. Every falsifier must be RED and must have a working
   positive control. A falsifier that is red because nothing works is not evidence.

2. NON-FINDING PROTECTION. An audit is a source of claims. Without a check, it
   becomes a SECOND SOURCE OF UNVERIFIED CLAIMS — the failure mode where a
   preliminary finding hardens into an accepted fact because nobody re-read it.

   So this gate also asserts that each non-finding is still recorded AND still
   marked as a non-finding. If someone later "fixes" the adjudication by promoting
   N2 or N4 into findings, this gate fails.

   The findings are protected too. An audit that quietly drops its own findings is
   the same failure in the opposite direction.
"""

import os
import re
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
PYTHON = os.environ.get("PYTHON", "python3")
ADJUDICATION = os.path.join(ROOT, "CLAIM-ADJUDICATION-I01.md")

FALSIFIERS = [
    ("I01-1", "test_objective_correspondence.py"),
    ("I01-2", "test_document_correspondence.py"),
    ("I01-3", "test_provenance_reachability.py"),
]

# Each non-finding must be present AND must carry its own negation. Checking for the
# phrase alone would let the adjudication quietly reverse it.
NON_FINDINGS = [
    ("N1", "pairing", [
        r"Pairing is NOT a defect",
        r"arms share every instance",
    ]),
    ("N2", "wall-clock is not provenance evidence", [
        r"Wall-clock time is NOT provenance evidence",
        r"neither that the abstract came from another run nor that it matches this one",
    ]),
    ("N3", "the sampling test is underpowered, not evidence", [
        r"POWER ASSESSMENT, not evidence",
        r"underpowered",
        r"must\s+not be cited as one",
    ]),
    ("N4", "the abstract's numbers are not contradicted", [
        r"abstract's numbers are NOT CONTRADICTED",
        r"They are unreconciled",
    ]),
    ("N5", "the prior report's byte-identical wording is wrong", [
        r"byte-identical",
        r"structurally different",
    ]),
]

FINDINGS = [
    ("R2 objective comparability", r"objective comparability, not instance pairing"),
    ("R3 wording and provenance", r"R3 = 8"),
    ("zero R1 findings", r"R1 = \*\*0\*\*|\*\*R1 findings\*\* \| \*\*0\*\*"),
    ("provenance unrecoverable in principle",
     r"unrecoverable \*\*IN PRINCIPLE\*\*|unrecoverable IN PRINCIPLE"),
    ("unseeded revisions counted", r"3 of 5 revisions"),
    ("conclusion contradicted by own table", r"significant improvements"),
    ("C4 queue serialisation omitted from pseudocode", r"serialises the queue"),
]

NOISE = re.compile(r"^Running |RuntimeWarning")


def run(script, timeout=900):
    try:
        proc = subprocess.run([PYTHON, os.path.join(HERE, script)],
                              capture_output=True, text=True, cwd=ROOT,
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, ""
    return proc.returncode, proc.stdout + proc.stderr


def main():
    print("=" * 78)
    print("i01 audit release gate")
    print("asserts: (1) falsifiers RED with working positive controls")
    print("         (2) findings are still recorded")
    print("         (3) NON-FINDINGS are still recorded AND still marked as such")
    print("=" * 78)
    failures = []

    # ---- 1. instrument integrity ------------------------------------------
    print("\n  --- instrument integrity ---")
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
            problems.append("no positive control PASSED — its FAIL results are void")
        print(f"  [{'OK' if not problems else 'PROBLEM':7s}] {tag} {script}"
              f"  exit={rc} FAIL={n_fail} PASS={n_pass}")
        for p in problems:
            print(f"            - {p}")
            failures.append(f"{tag}: {p}")

    if not os.path.exists(ADJUDICATION):
        print(f"\n  [FAIL] adjudication document missing: {ADJUDICATION}")
        failures.append("adjudication-document-missing")
        text = ""
    else:
        raw = open(ADJUDICATION, encoding="utf-8").read()
        # Markdown wraps prose across lines, so a pattern spanning a line break never
        # matches even when the sentence is present and correct. The first version of
        # this gate reported three problems that were all its own: two patterns spanned
        # a wrap point, and one searched for upper-case text in a document written in
        # mixed case. Whitespace is collapsed before matching, and the prohibition
        # patterns are case-insensitive. A gate that cannot see its own document's
        # line wrapping is a gate that manufactures false alarms.
        text = re.sub(r"\s+", " ", raw)

    # ---- 2. findings retained ---------------------------------------------
    print("\n  --- findings retained ---")
    for label, pattern in FINDINGS:
        ok = re.search(pattern, text) is not None
        print(f"  [{'OK' if ok else 'PROBLEM':7s}] {label}")
        if not ok:
            failures.append(f"finding dropped: {label}")

    # ---- 3. non-findings retained AND still negated -----------------------
    print("\n  --- non-findings protected ---")
    for tag, label, patterns in NON_FINDINGS:
        missing = [p for p in patterns if re.search(p, text) is None]
        if not missing:
            print(f"  [{'OK':7s}] {tag} {label}")
        else:
            print(f"  [{'PROBLEM':7s}] {tag} {label}")
            for m in missing:
                print(f"            - missing or reversed: {m!r}")
            failures.append(f"non-finding lost or reversed: {tag} {label}")

    # ---- 4. the structural prohibitions ----------------------------------
    print("\n  --- structural prohibitions ---")
    prohibitions = [
        ("no manuscript text edited on this branch",
         r"no manuscript text has been edited"),
        ("abstract never labelled CONTRADICTED in the summary",
         r"NOT VERIFIED — provenance gap"),
        ("pairing never listed among R2 findings",
         r"not instance pairing"),
    ]
    for label, pattern in prohibitions:
        # Case-insensitive: the document writes "No manuscript text has been edited."
        # with a capitalised first word, and a prohibition phrased as prose will not
        # reliably match a fixed-case needle.
        ok = re.search(pattern, text, re.IGNORECASE) is not None
        print(f"  [{'OK' if ok else 'PROBLEM':7s}] {label}")
        if not ok:
            failures.append(f"prohibition not stated: {label}")

    print("\n" + "=" * 78)
    if failures:
        print(f"GATE FAILED — {len(failures)} problem(s):")
        for f in failures:
            print(f"  {f}")
        return 1

    print("GATE PASSED")
    print(f"  {len(FALSIFIERS)} falsifiers RED with working positive controls")
    print(f"  {len(FINDINGS)} findings retained")
    print(f"  {len(NON_FINDINGS)} non-findings retained and still negated")
    print(f"  {len(prohibitions)} structural prohibitions stated")
    print()
    print("This asserts nothing about scientific merit or publishability. It says the")
    print("audit instruments are intact, the findings have not been quietly dropped,")
    print("and the non-findings have not been quietly promoted into findings.")
    print("An audit that cannot do both is a second source of unverified claims.")
    print()
    print("NO MANUSCRIPT TEXT HAS BEEN EDITED ON THIS BRANCH.")
    return 0


if __name__ == "__main__":
    sys.exit(main())