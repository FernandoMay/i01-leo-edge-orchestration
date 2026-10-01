# Claim Adjudication — i01 LEO Edge Orchestration

**Status:** adjudication complete. **No manuscript text has been edited.**
**Branch:** `fix/i01-audit-sweep`. **Baseline:** `ad697bc`.
**Evidence:** `FALSIFIER-LOG-I01-1.md`, `I01-2.md`, `I01-3.md`, `GATE-LOG.md`.

---

## 0. What changed after reading the manuscript in full

The first pass at this adjudication was going to classify i01 as badly
overclaimed. Reading §§Baseline Methods, Execution Time Analysis, Scalability and
**Limitations and Threats to Validity** in full does not support that.

The paper is honest in four places that matter:

- `:189` — "PSO and GA are implemented as **lightweight baselines rather than tuned
  state-of-the-art solvers**. Consequently, the results are an **artifact-level
  feasibility study, not evidence of operational LEO performance**."
- `:181` — "This **does not establish end-to-end real-time suitability** because the
  simulator omits propagation delay, link contention, and orbital mobility."
- `:185` — "Scaling results **should be reported after repeated seeded trials**
  rather than inferred from a single execution."
- `:177` — "The experiment therefore supports a **narrow claim**."

Three of these are *more* conservative than the evidence requires. They are recorded
as RETAIN so they are not averaged away by the defects below — the same discipline
applied in Quantum (C18) and CRL.

**The overclaim is concentrated in exactly one sentence**, the conclusion at `:193`.
That is a materially different situation from Quantum (15 of 17 claims contradicted)
and from LEO (1 of 21 surviving). It should be reported as such.

---

## 1. Disposition vocabulary

| Disposition | Meaning |
|---|---|
| **RETAIN** | Accurate as written. |
| **REWRITE** | The measurement may be sound; the sentence does not describe it. |
| **REMOVE** | Contradicted, and no edit makes the sentence true. |
| **LIMITED** | True only under a narrower statement than the one made. |
| **NOT MADE** | The manuscript does not assert this. Recorded to prevent a fabricated claim from entering the matrix. |
| **NOT VERIFIED** | Not contradicted; the evidence cannot decide it. |
| **NOT REPRODUCIBLE** | Machine-dependent by construction; cannot be reproduced on any machine but the one that made it. |

---

## 2. Adjudication matrix

| ID | Claim | Source | Evidence | Verdict | Disposition | Class |
|---|---|---|---|---|---|---|
| C1 | PSO inertia weight 0.7 | `:155` | `simulation.py:249` `self.w = 0.7` | **SUPPORTED** | RETAIN | — |
| C2 | GA with elitism and 10% mutation | `:156` | `:326` `mutation_rate=0.1`; `:342-343` elite preservation | **SUPPORTED** | RETAIN | — |
| C3 | Reward function eq. (2) with α, β, γ, δ | `:99-102` | `:187-196` coefficients 0.5 / 0.3 / 0.15 / 0.3 | **SUPPORTED** | RETAIN | — |
| C4 | Algorithm 1 completion model `t_completion = t_arrival + t_service` | `:118-120` | `:226-233` accumulates `current_time` and takes `max(current_time, arrival)` | **CONTRADICTED** | **REWRITE** | **R3** |
| C5 | PSO/GA optimise energy, queue, load or priority | — | no such claim in the manuscript | **NOT MADE** | — | — |
| C6 | PSO/GA optimise load balancing | `:155-156` "lightweight baselines"; `:189` | I01-1: cost is exactly `Σ_s tasks_s²/10` | **SUPPORTED** | RETAIN | — |
| C7 | PSO and GA optimise the same function as each other | — | I01-1 F1: 200/200 assignments identical | **SUPPORTED** | RETAIN | — |
| C8 | PSO/GA optimise the same multi-criteria objective as XING | implied by "comparison" framing | I01-1 F2/F3: 4 satellite and 3 task interventions moved cost by **exactly 0** | **CONTRADICTED** as an implication | **REWRITE the framing** | **R2** |
| C9 | Arms evaluated on identical instances | `:150`? not stated; true in fact | `run_comparison:409` generates tasks once, passes copies | **SUPPORTED** | RETAIN | — |
| C10 | XING is faster | `:177` "fastest assignment runtime" | table: exec 0.047 vs 0.415 / 1.815; latency 28.07 vs 0.40 | **LIMITED** — faster to *assign*, ~70× slower to *complete* | qualify wording | **R2** |
| C11 | Assignment runtime is 0.037 s | `:24`, `:177` | table says 0.047; both wall-clock | **DOCUMENT INCONSISTENT** | **REWRITE** | **R3** |
| C12 | Assignment phase is 12.3× faster than PSO and 49.1× than GA | `:181` | implies XING = 0.03374 s and 0.03697 s — **two different denominators in one sentence** | **CONTRADICTED** | **REMOVE or recompute** | **R3** |
| C13 | Ratios do not derive from the table | `:181` | table basis gives 8.83× and 38.62×; abstract basis gives 11.22× and 49.05× | **CONTRADICTED** | as C12 | **R3** |
| C14 | End-to-end real-time suitability is not established | `:181` | accurate scoping | **SUPPORTED** | RETAIN | — |
| C15 | Scaling deferred pending repeated seeded trials | `:185` | accurate self-limitation | **SUPPORTED** | RETAIN | — |
| C16 | PSO/GA are lightweight, untuned baselines | `:189` | accurate, and it discloses the weakness | **SUPPORTED** | RETAIN | — |
| C17 | Results are artifact-level feasibility, not operational evidence | `:189` | accurate and correctly scoped | **SUPPORTED** | RETAIN | — |
| C18 | Abstract: 955 tasks, 31.24 s, 37.2% | `:24` | no seeded revision produces them; 3 of 5 revisions unseeded | **NOT VERIFIED** | regenerate from a recorded run | **R3** |
| C19 | Conclusion: "significant improvements ... in latency, deadline compliance, and execution efficiency" | `:193` | own table: XING loses latency 28.07 vs 0.40 and deadline 39.5% vs 98.7% | **CONTRADICTED** | **REWRITE** | **R3** |
| C20 | Table's Exec Time column | `:170-172` | wall-clock; no machine, load or timing method recorded | **NOT REPRODUCIBLE** | label as machine-dependent | **R3** |

**Counts:** SUPPORTED 9 · CONTRADICTED 4 · LIMITED 1 · NOT VERIFIED 1 ·
NOT REPRODUCIBLE 1 · DOCUMENT INCONSISTENT 1 · NOT MADE 1.
**Repair classes:** R3 = 8 · R2 = 2 · R1 = **0**.

---

## 3. Repair classes, held strictly

### R3 — valid numbers, invalid document. No code change. (8 items)
C4, C11, C12, C13, C18, C19, C20, and the framing half of C8.
Every one of these is a document or provenance fix. The measurements stand; the
sentences and the lineage do not describe them.

### R2 — the experiment cannot answer the question asked. (2 items)
C8 (framing) and C10 (what "faster" means). **The R2 defect in i01 is objective
comparability, not instance pairing.** `run_comparison` generates the task set once
and hands copies to all three methods, so the arms *are* paired. Nothing here
licenses "the experimental comparison is invalid"; what is invalid is reading a
70× latency gap as evidence about optimisation quality, because the two sides are
optimising different quantities.

### R1 — mechanism not implemented. (0 items)
**There are none.** XING's four-term reward exists (C3). The baselines' optimiser
exists (C6, C7). The queue model exists. Every mechanism the manuscript describes is
present in the code. This is the first package in the sweep with an empty R1 column,
and that is a finding about the package, not an absence of audit.

---

## 4. C4 in detail — the one implementation/document mismatch that is not wall-clock

Algorithm 1 at `:118-120` states, for each task in a satellite's queue:

```
t_service   <- w_j / c_i^avail
t_completion <- t_arrival + t_service
```

The code at `:226-233` states:

```python
current_time = 0.0
for task in sat_queue:
    service_time = task.computational_load / max(sat.compute_capacity * sat.energy_level, 0.1)
    start_time = max(current_time, task.arrival_time)
    task.completion_time = start_time + service_time
    current_time = start_time + service_time
```

The code **serialises the queue**. Tasks in the same satellite's queue wait for one
another. The pseudocode does not, and uses a different divisor
(`c_i^avail` includes a utilisation factor that the code's `compute_capacity *
energy_level` does not).

This matters more than a documentation nit: **the queue serialisation is the
mechanism that produces XING's 28.07 s latency.** Under the pseudocode's model
XING's latency would be far lower and the comparison would look different. The
document omits the very mechanism that explains its most important result.

---

## 5. Provenance disposition, held conservative

```
seeded current revision  →  reproducible, exactly (941 / 28.0745 / 39.5324)
seeded ad697bc           →  reproduces the table, not the abstract
3 of 5 revisions         →  NO seed literal; any value they produced is
                           unrecoverable IN PRINCIPLE, not merely unrecovered
abstract's 3 values      →  NOT VERIFIED — provenance gap
```

**The abstract's numbers are NOT marked CONTRADICTED.** The evidence supports a
narrower and more precise statement: no seeded revision produces them; three
historical revisions could have produced them but cannot be re-run to a fixed value;
and no commit carries them outside manuscript prose. Lineage is **unrecoverable**,
which is not the same as refuted.

---

## 6. Non-findings — explicitly protected

These are recorded so the audit cannot become a second source of unverified claims.
The gate asserts each one is still present and still marked as a non-finding.

**N1 — Pairing is NOT a defect.** `run_comparison:409` generates the task set once
and passes copies to all three methods. The arms share every instance. Any
adjudication asserting an unpaired comparison in i01 would be wrong, and must not be
inherited from the Quantum or ISAC pattern.

**N2 — Wall-clock time is NOT provenance evidence, in either direction.**
`execution_time` spans observed across repeated invocations: 0.0367–0.0382,
0.0368–0.0711, 0.0430–0.0507, 0.0368–0.0921 s. Both the abstract's 0.037 and the
table's 0.047 fall inside observed spans. Exec time shows neither that the abstract
came from another run nor that it matches this one.

**N3 — The 25/60-sample containment test is a POWER ASSESSMENT, not evidence.** It
returns true at 60 samples of `a458ef3` and false at 25 samples of `9ccbcc5`. The
test is underpowered. It is not reported as a finding in either direction and must
not be cited as one.

**N4 — The abstract's numbers are NOT CONTRADICTED.** They are unreconciled. A
finding that says "contradicted" overstates the evidence and must not enter the
matrix.

**N5 — Defect-001's "byte-identical bodies" is wrong in detail.** `_evaluate` binds
`sat_id` to a local; `_fitness` inlines `int(assignment[i])`. The AST reports them
structurally different. They are behaviourally identical. The substantive finding
stands; the wording must not be inherited.

---

## 7. What would have to be true for the comparison to become meaningful

Not a repair proposal — a statement of the gate property, from
`P1-REPAIR-SPEC-v1.0.md` item 3:

> all compared methods optimise the same stated objective

Two mutually exclusive resolutions, and choosing between them is a scientific
decision, not an editorial one:

- **Make the objectives comparable.** Give the baselines a cost that reads the same
  quantities XING's reward reads. Then the table compares like with like, and
  whatever wins, wins on a stated objective.
- **Stop calling it a comparison.** Reframe as a two-policy demonstration — a
  task-aware greedy policy versus a load-balancing baseline — with the objective
  difference stated up front as the point rather than hidden as a fair fight.

The paper currently does neither, and its conclusion assumes the first.

---

## 8. Summary

| | |
|---|---|
| Claims adjudicated | 20 |
| SUPPORTED / RETAIN | 9 |
| CONTRADICTED | 4 |
| LIMITED | 1 |
| NOT VERIFIED | 1 |
| NOT REPRODUCIBLE | 1 |
| NOT MADE | 1 |
| **R1 findings** | **0** |
| **R2 findings** | **2** |
| **R3 findings** | **8** |
| Non-findings protected | 5 |
| Falsifier defects retained | 7 |

Three falsifiers, all RED, all with working positive controls, gate passing. No
manuscript text edited. The overclaim is one sentence, not fifteen claims.