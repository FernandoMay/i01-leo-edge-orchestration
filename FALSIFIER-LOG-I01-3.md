==============================================================================
I01-3 falsifier — provenance of the abstract's numbers
property: the history reproduces the abstract's numbers, or records why not
==============================================================================

  [INFO] full history: 5 commits
           9c7f212  seeds=NONE — UNSEEDED   feat: I-01-LEO-EDGE-ORCHESTRATION - rese
           a458ef3  seeds=NONE — UNSEEDED   fix: update LaTeX with real simulation r
           9ccbcc5  seeds=NONE — UNSEEDED   docs: add compiled PDF
           ad697bc  seeds=['20260909', '20260909']   refactor: strengthen manuscript and repr
           65aec3f  seeds=['20260909', '20260909']   test(i01): objective correspondence fals

           seeded revisions:   2 (['ad697bc', '65aec3f'])
           UNSEEDED revisions: 3 (['9c7f212', 'a458ef3', '9ccbcc5'])
           A revision with no seed cannot reproduce a value, and a value
           it produces cannot be reproduced later. This is the structural
           reason the abstract is unreconcilable, and it is a VERIFIED
           property of the code history, not an inference about intent.

  [INFO] searching every commit's full tree for the abstract's values:
           task count         955      commits searched 5/5  complete: True
             present in: ['a458ef3', '9ccbcc5', 'ad697bc', '65aec3f']
             (all hits are manuscript prose in latex/paper.tex; no code,
              data file or artifact carries any of these values)
           XING avg latency   31.24    commits searched 5/5  complete: True
             present in: ['a458ef3', '9ccbcc5', 'ad697bc', '65aec3f']
             (all hits are manuscript prose in latex/paper.tex; no code,
              data file or artifact carries any of these values)
           XING deadline %    37.2     commits searched 5/5  complete: True
             present in: ['a458ef3', '9ccbcc5', 'ad697bc', '65aec3f']
             (all hits are manuscript prose in latex/paper.tex; no code,
              data file or artifact carries any of these values)

  [INFO] POSITIVE CONTROL — does the current revision reproduce its table?
           task count         table      941  run   941.0000   reproduced: True
           XING avg latency   table    28.07  run    28.0745   reproduced: True
           XING deadline %    table     39.5  run    39.5324   reproduced: True
  [PASS] positive control: the current revision reproduces every
           table value at the table's own display precision. This
           harness CAN detect reproduction, so a failure to reproduce
           the abstract's values below is informative.

  [INFO] can any SEEDED revision produce the abstract's values?
           ad697bc seeds=['20260909', '20260909'] -> {'task count': 941, 'XING avg latency': np.float64(28.0745), 'XING deadline %': 39.5324}  matches abstract: False
           65aec3f seeds=['20260909', '20260909'] -> {'task count': 941, 'XING avg latency': np.float64(28.0745), 'XING deadline %': 39.5324}  matches abstract: False
  [FAIL] no seeded revision in this repository's history produces the abstract's
         values. Only the UNSEEDED revisions could, and they cannot be re-run
         to a fixed value.

  [INFO] sampling the UNSEEDED revision 9ccbcc5 25 times, no seed set:
           quantity                 min       max  distinct   abstract   in range?
           task count           955.000  1000.000         7        955   True
           XING avg latency      27.058    31.015        25      31.24   False
           XING deadline %       35.347    41.300        23       37.2   True
           all three inside the observed range: False

           Method note: containment, not exact hit, is the correct test.
           These distributions are wide and take many distinct values, so a
           finite sample misses most specific values.

           POWER ASSESSMENT — and this is why the containment result
           cannot be reported as a finding:
             XING avg latency: the abstract's 31.24 lies 0.225 BEYOND the observed edge
             but a 60-sample probe of a different unseeded revision
             (a458ef3) reached latency max 31.892, which CONTAINS the
             abstract's 31.24. The same test therefore returns True at
             60 samples and False at 25.

             => THIS TEST IS UNDERPOWERED. Its outcome flips with sample
                size and with which unseeded revision is sampled. It is
                NOT reported as a finding in either direction.

           WHAT THE EVIDENCE DOES SUPPORT, regardless of sample size:
             1. No seeded revision in this history produces the abstract's
                values. Both seeded revisions reproduce the TABLE exactly.
             2. Three of five historical revisions carry no seed, so any
                value they produced is unrecoverable in principle — not
                merely unrecovered.
             3. No commit contains these values in code, data or an
                artifact; they appear only as manuscript prose.
           Compatibility with an unseeded revision is neither established
           nor excluded, and the sampling that might decide it is
           underpowered. NO CAUSE IS SELECTED.
==============================================================================
FAILED: I01-3-abstract-not-reproduced-by-any-seeded-revision, I01-3-containment-test-underpowered

Implementation fact: the current revision is seeded and reproduces its
table exactly. Three of five historical revisions carry no seed at all.
Document fact: the abstract's deterministic values are not produced by
any seeded revision and are compatible with an unseeded one.

NO CAUSE IS SELECTED. NO MANUSCRIPT TEXT HAS BEEN EDITED.

## Falsifier defects found while building I01-3 (all retained)

1. **The harness ignored the package's own seeding, and the positive control caught
   it.** The seeds live inside `if __name__ == "__main__":` at `simulation.py:491-493`.
   The first harness imported the module and called `run_comparison()` directly,
   which runs **unseeded**. The positive control then reported 1000 tasks where the
   table says 941, and correctly declared every downstream result void — including
   the claim that no seeded revision reproduces the abstract.

   This is the discipline working as intended: the control did not merely report a
   failure, it invalidated the conclusions that depended on it, and the fix was to
   the harness rather than to the finding. A control that passes only when the code
   under test happens to cooperate is not a control.

2. **A test whose outcome flips with sample size was about to become a finding.** The
   containment test on the unseeded revision returned "all three inside the range"
   at 60 samples of `a458ef3` and "latency outside the range" at 25 samples of
   `9ccbcc5`. The abstract's 31.24 sits 0.225 beyond the 25-sample maximum and well
   inside the 60-sample one.

   The verdict is now stated as a **power assessment**: the test is underpowered, its
   outcome depends on sample size and on which revision is sampled, and it is
   therefore not reported in either direction. Reporting the 60-sample containment as
   a finding would have been a coin flip presented as evidence.

3. **Exact matching was the wrong instrument for a wide distribution.** The first
   probe tested whether a 60-run sample contained the abstract's exact figure and
   reported it as absent, then corrected itself to range containment. Task count took
   26 distinct values across 60 runs spanning 938–1000, so any specific value has
   roughly a 1-in-26 chance per draw and most values are missed. Missing one is
   unremarkable. Recorded because "we ran it and did not find it" is exactly the
   inference DEFECT-001 §5 warns against.

## What I01-3 establishes, and what it explicitly does not

**Established:**

1. Both seeded revisions (`ad697bc`, `65aec3f`) reproduce the table exactly:
   941 tasks, 28.0745 s, 39.5324%. The table corresponds to a run.
2. **No seeded revision produces the abstract's values.** Both produce the table's.
3. **Three of five historical revisions (`9c7f212`, `a458ef3`, `9ccbcc5`) contain no
   seed literal at all.** Any value such a revision produced is unrecoverable *in
   principle* — not merely unrecovered. This is a verified property of the code
   history, not an inference about what the authors did.
4. Across all five commits, the abstract's three deterministic values appear only as
   manuscript prose. No code, data file or artifact carries them. The only seed
   literal anywhere in the history is 20260909.

**Not established, and not claimed:**

- That the abstract came from an unseeded revision. The sampling that might support
  it is underpowered, and its result is unstable.
- Any particular cause. A different seed, dataset, configuration, lost commit or
  manual run remain equally plausible and equally unverified.

**The finding is the unrecoverable provenance.** The repository does not merely fail
to record what produced the abstract; it contains code revisions that, by
construction, could not have recorded it. That is a stronger and more precise
statement than "provenance is missing", and it is the one the evidence supports.

## Relationship to DEFECT-001 §4.4 and §7

The prior report listed the abstract's provenance under "Not verified" and declined
to select a cause. That discipline was correct and is preserved. This falsifier adds
two verified facts the prior report did not have:

- the three earliest revisions are unseeded, which is a mechanism for the
  irrecoverability rather than a mere absence of a record;
- the assignment-runtime column is wall-clock and must be excluded from provenance
  reasoning in both directions.

It does not overturn the prior report's substantive conclusion. It sharpens what kind
of conclusion is available.
