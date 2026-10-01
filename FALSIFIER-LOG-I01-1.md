==============================================================================
I01-1 falsifier — objective correspondence across XING / PSO / GA
property: all compared methods optimise the same stated objective
==============================================================================

  [INFO] F1 do PSO._evaluate and GA._fitness rank assignments the same?
         AST of the two function bodies is identical: False
         the bodies differ structurally; the textual report's 'byte-identical' claim
         may still hold modulo formatting, which is checked below behaviourally.
         200/200 assignments scored identically
  [PASS] F1 the two baselines agree on every assignment tested

  [INFO] what the baselines' cost is actually a function of:
         _evaluate computes sum_i sat_loads[assignment[i]] / 10
         which is identically sum_s sat_loads[s]^2 / 10, i.e. a pure
         function of the per-satellite task COUNTS.
         balanced       loads [3, 3, 3]      -> cost   2.7000   sum of squares / 10 =   2.7000   agree: True
         moderate       loads [6, 2, 1]      -> cost   4.1000   sum of squares / 10 =   4.1000   agree: True
         concentrated   loads [9, 0, 0]      -> cost   8.1000   sum of squares / 10 =   8.1000   agree: True
         cost == sum of squared load counts, exactly, for every case: True
         The objective's minimum is attained by the most even spread and
         is independent of WHICH task lands on which satellite.

  [INFO] F3 does the cost change when only identity/properties change?
           default constellation, medium tasks            cost 2.700000
           default constellation, HEAVY CRITICAL tasks    cost 2.700000
           default constellation, LIGHT LOW tasks         cost 2.700000
           skewed-energy constellation, same spread       cost 2.700000
  [FAIL] F3 all four cost 2.700000 despite the satellite energy profile
         spanning 0.2 to 1.0, task loads spanning 1.0 to 50.0, and priorities spanning
         LOW to CRITICAL. The objective reads task COUNTS only. No assignment that
         differs only in WHICH task goes where can be preferred over another.

  [INFO] F2 does the baselines' cost respond to the quantities XING optimises?
           energy_level of sat 0 (0.80 -> 0.25)       cost 2.700000   delta +0.000e+00   changed: False
           energy_level of sat 0 (0.80 -> 1.00)       cost 2.700000   delta +0.000e+00   changed: False
           queue_length of sat 0 (0 -> 6)             cost 2.700000   delta +0.000e+00   changed: False
           compute_capacity of sat 0 (10 -> 2)        cost 2.700000   delta +0.000e+00   changed: False
  [FAIL] F2 the baselines' cost is invariant under every one of these interventions.
         XING's reward is built from compute_capacity, energy_level,
         queue_length, task.priority and task.computational_load. The
         baselines read none of them. They are not solving the problem
         XING solves.

  [INFO] POSITIVE CONTROL — XING's reward under the identical battery:
           baseline reward 1.340000
           energy_level 0.80 -> 0.25              reward     0.625000  delta     -0.7150  decrease  expected decrease  OK
           energy_level 0.80 -> 1.00              reward     1.600000  delta     +0.2600  increase  expected increase  OK
           queue_length 0 -> 6                    reward     0.440000  delta     -0.9000  decrease  expected decrease  OK
           task priority MEDIUM -> CRITICAL       reward     1.940000  delta     +0.6000  increase  expected increase  OK
           task priority MEDIUM -> LOW            reward     1.040000  delta     -0.3000  decrease  expected decrease  OK
           computational_load 5.0 -> 50.0         reward     0.620000  delta     -0.7200  decrease  expected decrease  OK
         6/6 interventions moved the reward in the predicted direction
  [PASS] positive control: XING's reward responds to all 6 interventions
           in the predicted direction, so this falsifier CAN detect an
           objective that ignores these quantities. F2's invariance is
           therefore a property of the baselines, not of the instrument.
==============================================================================
FAILED: F3-objective-blind-to-task-and-satellite-state, F2-baselines-ignore-xing-criteria

Implementation fact: the three methods do not share an objective. XING
maximises a four-term reward over compute, energy, queue and priority.
PSO and GA minimise sum of squared per-satellite task counts, read from
identical function bodies. They never read energy_level, queue_length,
task.priority or task.computational_load.

Claim correspondence: NOT ADJUDICATED. Whether the manuscript's framing
survives this, and what must change if it does not, is the next phase.

## Correction to the prior report's premise

`DEFECT-001-LEO.md` §4.2 states that `PSOOptimizer._evaluate` and
`GAOptimizer._fitness` have **byte-identical bodies**. That is wrong in detail, and
the correction matters because the report's wording invites a reader to check the
text rather than the behaviour.

`_evaluate` binds `sat_id = int(assignment[i])` to a local before indexing.
`_fitness` inlines `int(assignment[i])` at each use. An AST comparison of the two
function bodies reports them as **structurally different**. They are *behaviourally*
identical — 200 of 200 randomly generated assignments scored identically — but they
are not textually identical.

This is a correction to the audit instrument, not to the finding. The defect report's
substantive claim, that the baselines share one objective and it is not XING's,
survives and is now established behaviourally rather than asserted textually.

## Falsifier defects found while building I01-1 (all retained)

1. **Fabricated labels beside correct numbers.** The first version printed a
   hand-written `loads = np.array([5, 0, 4])` that was never used to compute
   anything, and labelled the printed costs with it. The costs were correct; the
   labels were invented. It printed "loads [5,0,4]" beside a cost of 2.7000, which
   corresponds to loads [3,3,3], and printed a "sum sq / 10" that disagreed with the
   cost on the same line — so the line contradicted itself. Every label is now
   derived from the assignment actually scored, and the closed form is asserted
   against the same derived array.

   This is recorded prominently because it is the one failure mode this entire
   programme exists to catch, committed by its own newest instrument: a number that
   was never computed appearing next to a number that was.

2. **Default argument bound before the module existed.** `make_task(sim, tid,
   priority=sim.TaskPriority.MEDIUM)` raised `NameError` because default arguments
   are evaluated at definition time and `sim` is a parameter, not a global.

## What F2 and F3 establish, and what they do not

The baselines' objective is, exactly,

    cost(assignment) = sum over satellites of (task count on that satellite)^2 / 10

verified to 1e-9 against the code for three assignments of different concentration.
It is a pure load-balancing penalty. It does not read `compute_capacity`,
`energy_level`, `queue_length`, `task.priority`, `task.computational_load`,
`deadline` or `data_size`. Every one of four interventions on the satellites and
three task-property substitutions moved it by exactly 0.

XING's reward, run through the identical battery, moved in the predicted direction
on **6 of 6** interventions. The falsifier can therefore detect an objective that
ignores these quantities, and the baselines' invariance is a property of the
baselines rather than an artefact of the instrument.

**Consequence for the equivalence class.** Because cost depends only on the count
vector, every assignment sharing a count vector has identical cost. An assignment
that places a CRITICAL, 50-GFLOPS task on an energy-0.2 satellite is scored exactly
the same as one that spreads three LIGHT LOW tasks evenly. The baselines' search has
no gradient to follow toward task-aware placement, because there is none in their
objective.

**What this does not establish.** It does not establish that the paper's conclusion
is wrong, only that the table cannot bear the reading of it as a comparison. The
70x latency difference is a fact about two programs solving two different problems;
whether the manuscript's framing survives that is the adjudication phase.
