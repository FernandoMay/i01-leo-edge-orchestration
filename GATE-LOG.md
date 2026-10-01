==============================================================================
i01 audit release gate
asserts: (1) falsifiers RED with working positive controls
         (2) findings are still recorded
         (3) NON-FINDINGS are still recorded AND still marked as such
==============================================================================

  --- instrument integrity ---
  [OK     ] I01-1 test_objective_correspondence.py  exit=1 FAIL=2 PASS=2
  [OK     ] I01-2 test_document_correspondence.py  exit=1 FAIL=3 PASS=1
  [OK     ] I01-3 test_provenance_reachability.py  exit=1 FAIL=1 PASS=1

  --- findings retained ---
  [OK     ] R2 objective comparability
  [OK     ] R3 wording and provenance
  [OK     ] zero R1 findings
  [OK     ] provenance unrecoverable in principle
  [OK     ] unseeded revisions counted
  [OK     ] conclusion contradicted by own table
  [OK     ] C4 queue serialisation omitted from pseudocode

  --- non-findings protected ---
  [OK     ] N1 pairing
  [OK     ] N2 wall-clock is not provenance evidence
  [OK     ] N3 the sampling test is underpowered, not evidence
  [OK     ] N4 the abstract's numbers are not contradicted
  [OK     ] N5 the prior report's byte-identical wording is wrong

  --- structural prohibitions ---
  [OK     ] no manuscript text edited on this branch
  [OK     ] abstract never labelled CONTRADICTED in the summary
  [OK     ] pairing never listed among R2 findings

==============================================================================
GATE PASSED
  3 falsifiers RED with working positive controls
  7 findings retained
  5 non-findings retained and still negated
  3 structural prohibitions stated

This asserts nothing about scientific merit or publishability. It says the
audit instruments are intact, the findings have not been quietly dropped,
and the non-findings have not been quietly promoted into findings.
An audit that cannot do both is a second source of unverified claims.

NO MANUSCRIPT TEXT HAS BEEN EDITED ON THIS BRANCH.

---

## Gate defects found while building the gate (all retained)

The gate reported three problems on first execution. **All three were the gate's
own**, and the adjudication document was correct in every case:

1. **Patterns could not see markdown line wrapping.** Two patterns spanned a line
   break — `objective comparability, not instance pairing` and `neither that the
   abstract came from another run nor that it matches this one`. Both sentences are
   present and correct in the document; markdown simply wraps prose. Whitespace is
   now collapsed before matching.
2. **A prohibition searched for upper-case text in a mixed-case document.** The
   document writes "No manuscript text has been edited."; the needle was
   `NO MANUSCRIPT TEXT HAS BEEN EDITED`. Prohibition patterns are now case-insensitive.

A gate that cannot read its own document's line wrapping manufactures false alarms,
and a false alarm costs credibility that a real finding then has to overcome. The
three failures were investigated rather than assumed, and none of them was suppressed
— they were fixed in the instrument.

## Why this gate also protects NON-FINDINGS

The first version of this gate checked only that findings survived. That is half the
job and the half that fails more visibly.

An audit is itself a source of claims. Left unchecked it becomes a second source of
unverified claims, and the failure mode is asymmetric:

- a **finding** silently dropped because it stopped being convenient;
- a **non-finding** silently promoted into a finding because it read like one.

The second is the more dangerous of the two, because it manufactures a result that
was never established. N3 in particular — the underpowered 25/60-sample containment
test — is exactly the kind of observation that reads like a result. If it were ever
cited as "the abstract matches an unseeded revision", the audit would have invented
that claim while appearing to be rigorous about it.

Each non-finding is therefore checked for BOTH its presence and its own negation. A
pattern for the positive half alone would pass if the adjudication had reversed
itself, which is the failure being guarded against.
