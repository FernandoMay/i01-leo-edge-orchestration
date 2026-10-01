==============================================================================
I01-2 falsifier — document correspondence and provenance
properties: the conclusion's directions match its own table; every stated
            number is internally consistent and corresponds to a run; the
            repository records what produced the abstract's numbers
==============================================================================

  [INFO] positive control — extractor against a document with known values:
           known values ['941', '28.07', '39.5'] recovered from a synthetic document: True
           full extraction: ['941', '28.07', '39.5']
  [PASS] positive control: the extractor recovers known values, so its
           silence elsewhere is informative.

  [INFO] reproducing the comparison (this audit's own numbers):
           two consecutive runs agree on every non-timing metric: True

  [INFO] wall-clock variance across 5 runs of identical code and seed:
           XING exec  min 0.0398  max 0.0490  span 0.0092
           PSO exec   min 0.4191  max 0.5695  span 0.1504
           GA exec    min 1.9228  max 1.9888  span 0.0660
           the abstract states 0.037 s and the table 0.047 s for XING's assignment
           runtime. Observed wall-clock span over 5 runs: 0.0398 to 0.0490
             the abstract's 0.037 s lies INSIDE  the observed span: False
             the table's    0.047 s lies INSIDE  the observed span: True

           => THIS INVOCATION: the table's figure lies inside the span and the abstract's does not, so exec time favours neither run in particular and cannot support a provenance claim.
              Observed XING exec span: 0.0398-0.0490 s. The span is
              load-dependent and moved substantially between invocations of
              this same script, which is the reason no branch of it is
              treated as a finding.
           => The table's execution-time column is machine-dependent and
              not portable. That is a separate R3 observation about the
              table, not about the abstract's provenance.

           => Assignment runtime is wall-clock and is EXCLUDED from the
              provenance finding below, in BOTH directions: it does not
              show the abstract came from another run, and it does not show
              the abstract matches this run.
           => This corrects DEFECT-001 §4.4, which listed the assignment
              phase 0.037 / 0.047 / 0.0627 in the provenance table without
              separating a wall-clock quantity from a deterministic one.
           task count: [941.0, 941.0, 941.0]
           method     avg latency  deadline met   exec time
           XING           28.0745        39.53%      0.0472
           PSO             0.4024        98.72%      0.7154
           GA              0.4025        98.72%      2.2423

  [INFO] sections located, with their line spans:
           abstract           lines 23-24
           comparison table   lines 161-175
           discussion         lines 161-178
           conclusion         lines 191-195

  [INFO] P1 does the conclusion's direction match the paper's own table?
           rows parsed from the COMPARISON table: {'XING': {'latency': 28.07, 'deadline': 39.5, 'exec': 0.047}, 'PSO': {'latency': 0.4, 'deadline': 98.7, 'exec': 0.415}, 'GA': {'latency': 0.4, 'deadline': 98.7, 'exec': 1.815}}
           table says XING wins on latency                 : False
           table says XING wins on deadline compliance     : False
           table says XING wins on execution efficiency    : True
  [FAIL] P1 the conclusion claims 'significant improvements over classical optimization
         methods' in latency, deadline compliance and execution efficiency, but its
         own table shows XING LOSING on: latency, deadline compliance.
         Concretely: latency 28.07 vs 0.4/0.4; deadline 39.5% vs 98.7%/98.7%.
         XING wins on assignment runtime only.
           the discussion states the narrow honest reading: True
           the abstract states a trade-off rather than an advantage: True
           Three framings coexist: abstract (trade-off, superseded
           numbers), discussion (narrow claim), conclusion (significant
           improvements, contradicted by the table it cites).

  [INFO] P2 stated values per section, against a fresh run:
           task count       run   941.0000   abstract=does NOT state it   comparison table=states 941
           XING latency     run    28.0745   abstract=does NOT state it   comparison table=states 28.07
           XING deadline %  run    39.5324   abstract=does NOT state it   comparison table=states 39.5
           PSO latency      run     0.4024   abstract=does NOT state it   comparison table=states 0.40
           GA latency       run     0.4025   abstract=does NOT state it   comparison table=states 0.40
           PSO deadline %   run    98.7248   abstract=does NOT state it   comparison table=states 98.7
           GA deadline %    run    98.7248   abstract=does NOT state it   comparison table=states 98.7

           XING assignment runtime:
             abstract   states [0.037, 0.41, 0.42, 31.24, 37.2, 98.1, 98.2]
             table      states 0.047
             discussion states [0.037, 0.047, 0.4, 0.415, 1.815, 28.07, 39.5, 98.7]
             current run  0.0472
  [FAIL] P2 (document consistency only, NOT provenance) the discussion states
         XING's assignment runtime as 0.037 s while the table on the same page
         states 0.047 s. The discussion carries the ABSTRACT's figure into a
         section that otherwise reads the table correctly. Both figures are
         wall-clock measurements, so this is an internal document inconsistency
         and NOT evidence that the abstract came from another run.

           task count: abstract 955.0   table caption 941.0   current run 941.0
  [FAIL] P2 the abstract and the table state different task counts, and the
         current run reproduces only the table's (941.0).

  [INFO] P3 provenance of the abstract's numbers
           Absence protocol: each search below reports its coverage.
           commits in this repository's full history: 5
           commits listed by git log --all: 5
             65aec3f test(i01): objective correspondence falsifier — the three methods do not share an objective
             ad697bc refactor: strengthen manuscript and reproducibility package
             9ccbcc5 docs: add compiled PDF
             a458ef3 fix: update LaTeX with real simulation results
             9c7f212 feat: I-01-LEO-EDGE-ORCHESTRATION - research paper with simulation, tests, and LaTeX

           searching EVERY commit's full tree for the abstract's numbers:
             955 tasks            needle 955       commits searched 5/5 (complete: True)  hits: ['65aec3f', 'ad697bc', '9ccbcc5', 'a458ef3']
             31.24 s latency      needle 31.24     commits searched 5/5 (complete: True)  hits: ['65aec3f', 'ad697bc', '9ccbcc5', 'a458ef3']
             37.2% deadline       needle 37.2      commits searched 5/5 (complete: True)  hits: ['65aec3f', 'ad697bc', '9ccbcc5', 'a458ef3']

           every seed literal found in every commit: [('65aec3f', '20260909'), ('ad697bc', '20260909')]
           data artifacts in HEAD matching data/results/metrics/output: NONE
           total files tracked in HEAD: 11
             .gitignore
             CITATION.cff
             Dockerfile
             FALSIFIER-LOG-I01-1.md
             README.md
             latex/paper.pdf
             latex/paper.tex
             requirements.txt
             src/simulation.py
             tests/test_objective_correspondence.py
             tests/test_simulation.py

           FINDING: the abstract's numbers are not produced by the code
           at any commit in this repository's history, and no tracked file
           records a run, a configuration, or a commit that produced them.
           Candidate explanations — a different seed, dataset, configuration,
           lost commit, or manual run — are PLAUSIBLE AND UNVERIFIED. None
           is selected. The finding is the missing provenance.
==============================================================================
FAILED: I01-2-exec-time-is-wall-clock-not-provenance, P1-conclusion-contradicts-own-table, P2-discussion-exec-figure-differs-from-table, P2-abstract-task-count-unreconciled, P3-abstract-provenance-absent

Implementation fact: the run is deterministic and the table reproduces it.
Document fact: the abstract's numbers correspond to nothing in the
repository; the discussion quotes one superseded value while reading the
table correctly elsewhere; the conclusion asserts a direction its own
table contradicts.

NO CAUSE IS SELECTED for the abstract's provenance, and NO MANUSCRIPT TEXT
HAS BEEN EDITED.

---

## Falsifier defects found while building I01-2 (all retained)

1. **The table lookup grabbed the wrong table.** `doc.section(r"\begin{table}", ...)`
   returns the FIRST table in the document, which is *Simulation Parameters*, not
   *Performance Comparison*. P1 therefore reported "could not parse the comparison
   table" against an empty dict and the strongest finding in the document went
   unexamined. The locator now searches for the table by its caption.

2. **A per-quantity scan that counted every numeral in the file.** The first P2
   walked all 204 lines collecting every number with no regard for context, so it
   reported "69 occurrences" for the deadline ratio — 69 being the total count of
   numerals in `paper.tex`. Each quantity's line-number list was meaningless. This is
   the same failure as I01-1's fabricated load vectors: a number printed beside a
   label that does not describe it. Every lookup is now scoped to a named section and
   names that section.

3. **A bad section locator produced a false negative about the document.** The check
   for the discussion's honest reading looked for `\subsection{Discussion}`, which
   does not exist in this paper, so the span came back empty and the output said
   "the discussion states the narrow honest reading: False". The paper's honest
   passage is at line 177, inside *Performance Comparison*. A wrong locator makes a
   document look worse than it is, which is as damaging as one that flatters it.

4. **An `or` where the sentence needed an `and`.** The wall-clock containment check
   printed "BOTH figures fall inside the observed span" when only one was, because
   the branch condition was `abstract_in or table_in`. The narrative around it then
   asserted which figure the machine could not reproduce, hardcoded from an earlier
   observation. The claim was false and it inverted the interpretation.

5. **A branch gap that announced the opposite of what was measured.** The corrected
   version had three branches for four combinations, so "table reproducible,
   abstract not" fell through to a branch stating NEITHER was reproducible while the
   table's figure was demonstrably inside the observed span.

6. **Hardcoded narrative around a load-dependent measurement.** Even after the branch
   fix the surrounding prose described a specific outcome. Re-running the same
   script produced spans of 0.0367–0.0382, 0.0368–0.0711 and 0.0430–0.0507 across
   three invocations, and the verdict flipped between branches. The narrative is now
   derived from the measurement and states the load-dependence as the reason no
   branch is treated as a finding.

## Correction to DEFECT-001 §4.4: the assignment runtime is not provenance evidence

The prior report's provenance table lists, among others:

| quantity | abstract | table | this run |
|---|---|---|---|
| assignment phase | 0.037 s | 0.047 s | 0.0627 s |

`execution_time` is measured with `time.time()` around the assignment call. It is
wall-clock. Across repeated invocations of identical code at an identical seed, the
observed XING assignment span on this machine has been 0.0367–0.0382 s,
0.0368–0.0711 s, 0.0430–0.0507 s and 0.0368–0.0921 s. **Both the abstract's 0.037 and
the table's 0.047 fall inside spans observed on this machine.**

Therefore the assignment-runtime column:
- does **not** show the abstract came from a different run;
- does **not** show the abstract matches this run;
- is machine-dependent and is not portable.

The prior report listed it as provenance evidence without separating a wall-clock
quantity from a deterministic one. It is excluded here in both directions.

The provenance finding rests only on deterministic quantities: task count
(abstract 955, table 941, run 941), average latency (31.24 / 28.07 / 28.0745) and
deadline ratio (37.2% / 39.5% / 39.5324).

Separately, the table's own execution-time column is an R3 observation: it is a
wall-clock figure presented as a result, with no machine, load or timing method
recorded.

## What I01-2 establishes

P1 FAILS. The conclusion claims "significant improvements over classical optimization
methods in latency, deadline compliance, and execution efficiency". Its own table
gives XING 28.07 s against 0.40 s for both baselines, and 39.5% against 98.7%. XING
wins on assignment runtime only. The abstract states a trade-off, the discussion
states a narrow claim, and the conclusion states a universal advantage. Three
framings coexist in one document.

P2 FAILS on two counts. The abstract states 955 tasks where the table caption states
941 and the run produces 941. And the discussion states XING's assignment runtime as
0.037 s where the table on the same page states 0.047 s — flagged explicitly as a
document inconsistency and **not** as run-mismatch evidence, because both are
wall-clock figures.

The run is deterministic across repeats on every non-timing metric, and the table
reproduces it at the table's own display precision.

P3 establishes absence with coverage. 5 of 5 commits searched for each of the three
deterministic values; every hit is manuscript prose in `latex/paper.tex`; no code,
data file or artifact in any commit carries them; the only seed literal anywhere in
the history is 20260909. Eleven files are tracked in HEAD.

**No cause is selected.** A different seed, dataset, configuration, lost commit or
manual run are all plausible; none is established. I01-3 tests the one candidate that
can be tested.

---

## Post-adjudication check: §Execution Time Analysis ratios

While adjudicating, the ratios at `:181` were checked arithmetically. Both ratios in
one sentence must share a single XING denominator, because `run_comparison` measures
XING's assignment time **once** per run (`:414-416`), before PSO and before GA.

| stated | implied XING exec |
|---|---|
| 12.3× faster than PSO | 0.415 / 12.3 = **0.03374 s** |
| 49.1× faster than GA | 1.815 / 49.1 = **0.03697 s** |

They differ by 0.00323 s, so the two ratios cannot both come from one run.

Cross-checked against the document's own bases:

| basis | PSO ratio | GA ratio |
|---|---|---|
| the table (XING 0.047) | 8.83× | 38.62× |
| the abstract (XING 0.037) | 11.22× | **49.05×** |
| as stated | 12.30× | 49.10× |

The GA ratio traces to the **abstract's** superseded figures. The PSO ratio traces to
neither. Recorded as **C12/C13, R3**.

**Wall-clock caveat, stated explicitly.** `execution_time` is wall-clock, so the
ratios cannot be reproduced and their mutual inconsistency is consistent with the
measurements having come from different sessions. The finding is therefore a
document-provenance finding, not a determinism finding: the paper presents ratios
derived from at least two different XING measurements, names no run, and records no
timing method. It is NOT evidence about which run produced the abstract.
