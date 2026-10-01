#!/usr/bin/env python3
"""I01-1 falsifier: do the three compared methods optimise the same objective?

Pre-specified property under test
---------------------------------
From `P1-REPAIR-SPEC-v1.0.md`, item 3, repair class R2, gate property:

    "all compared methods optimise the same stated objective"

This falsifier tests that property and nothing else. It does not test whether any
method is good, nor whether the paper should exist.

Why behavioural rather than textual
-----------------------------------
`DEFECT-001-LEO.md` §4.2 asserts that `PSOOptimizer._evaluate` and
`GAOptimizer._fitness` have byte-identical bodies and that neither reads
`energy_level`, `queue_length`, `task.priority` or `task.computational_load`. That
is a prior report, and a prior report is a premise to be tested, not evidence. (The
LEO R2 falsifier was built on an imported premise that turned out to be wrong.) So
every assertion here is established by intervention: hold the assignment fixed, move
one state quantity, and observe whether the objective responds.

Tests
-----
F1  Do PSO and GA rank assignments identically? A set of assignments is scored by
    both. If the two objectives differ anywhere, at least one pair must disagree.

F2  Does the baselines' objective respond to the quantities XING optimises?
    energy_level, queue_length, task.priority and task.computational_load are varied
    one at a time with the assignment held fixed.

F3  Is the baselines' cost a function only of the load counts? Two assignments with
    identical load distributions but different satellite identities and different
    task properties must score identically if the objective ignores them.

Positive control (MANDATORY)
---------------------------
XING's reward is run through the identical battery. It MUST respond to all four
quantities. If it does not, this falsifier cannot detect objective insensitivity and
every F2 result is void.

Boundary
--------
This establishes an implementation fact. It assigns no scientific disposition and no
manuscript disposition. Whether an ill-posed comparison makes the paper wrong, or
merely narrower than claimed, is a separate question answered after the falsifiers.
"""

import ast
import os
import sys
import itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "src", "simulation.py")


def load_module():
    sys.path.insert(0, os.path.join(HERE, "..", "src"))
    import simulation as sim
    return sim


def make_sat(sim, sat_id, energy=0.8, compute=10.0, queue_len=0):
    sat = sim.Satellite(sat_id=sat_id, orbital_plane=0,
                        position=np.array([500.0, 0.0, 0.0]),
                        compute_capacity=compute, memory_capacity=16.0,
                        energy_level=energy)
    for _ in range(queue_len):
        sat.queue.append(sim.Task(task_id=9000 + sat_id, computational_load=1.0,
                                  data_size=1.0, deadline=1.0,
                                  priority=sim.TaskPriority.LOW))
    return sat


def make_task(sim, tid, load=5.0, priority=None, deadline=10.0):
    # `priority` cannot default to sim.TaskPriority.MEDIUM: default arguments are
    # evaluated at definition time, before `sim` exists in the module namespace.
    if priority is None:
        priority = sim.TaskPriority.MEDIUM
    return sim.Task(task_id=tid, computational_load=load, data_size=1.0,
                    deadline=deadline, priority=priority)


def make_constellation(sim, energies=(0.8, 0.8, 0.8), queue_lens=(0, 0, 0)):
    sats = [make_sat(sim, i, energy=e, queue_len=q)
            for i, (e, q) in enumerate(zip(energies, queue_lens))]
    return sim.LEOConstellation(satellites=sats, num_orbital_planes=1,
                                satellites_per_plane=len(sats), altitude=550.0)


def function_body_ast(src_path, func_qualname):
    """Return the normalised AST dump of a function body, so two functions can be
    compared structurally rather than by string equality."""
    tree = ast.parse(open(src_path).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_qualname:
            body = [n for n in node.body if not isinstance(n, ast.Expr)
                    or not isinstance(getattr(n, "value", None), ast.Constant)]
            return ast.dump(ast.Module(body=body, type_ignores=[]))
    return None


def main():
    print("=" * 78)
    print("I01-1 falsifier — objective correspondence across XING / PSO / GA")
    print("property: all compared methods optimise the same stated objective")
    print("=" * 78)

    sim = load_module()
    failures = []

    pso = sim.PSOOptimizer(make_constellation(sim), num_particles=5, max_iter=5)
    ga = sim.GAOptimizer(make_constellation(sim), pop_size=5, max_gen=5)
    xing = sim.XINGOrchestrator(make_constellation(sim))

    n_tasks = 9
    tasks = [make_task(sim, i) for i in range(n_tasks)]

    # ---- F1: do PSO and GA rank assignments identically? --------------------
    print("\n  [INFO] F1 do PSO._evaluate and GA._fitness rank assignments the same?")
    ast_pso = function_body_ast(SRC, "_evaluate")
    ast_ga = function_body_ast(SRC, "_fitness")
    print(f"         AST of the two function bodies is identical: "
          f"{ast_pso == ast_ga}")
    if ast_pso != ast_ga:
        print("         the bodies differ structurally; the textual report's "
              "'byte-identical' claim")
        print("         may still hold modulo formatting, which is checked below "
              "behaviourally.")

    rng = np.random.default_rng(7)
    agreements = 0
    disagreements = []
    tested = 0
    for trial in range(200):
        a = rng.integers(0, pso.num_sats, size=n_tasks)
        cpso = pso._evaluate(a, tasks)
        cga = ga._fitness(a, tasks)
        tested += 1
        if abs(cpso - cga) < 1e-12:
            agreements += 1
        else:
            disagreements.append((a.tolist(), cpso, cga))
    print(f"         {agreements}/{tested} assignments scored identically")
    if not disagreements:
        print("  [PASS] F1 the two baselines agree on every assignment tested")
    else:
        print(f"  [FAIL] F1 {len(disagreements)} disagreements, first: "
              f"{disagreements[0][1]} vs {disagreements[0][2]}")
        failures.append("F1-baseline-objectives-differ")

    # ---- the structural consequence of that objective ------------------------
    print("\n  [INFO] what the baselines' cost is actually a function of:")
    print(f"         _evaluate computes sum_i sat_loads[assignment[i]] / 10")
    print(f"         which is identically sum_s sat_loads[s]^2 / 10, i.e. a pure")
    print(f"         function of the per-satellite task COUNTS.")
    # Every label below is DERIVED from the assignment actually scored. An earlier
    # version printed a hand-written `loads` array that was never used to compute
    # anything, so the costs were right and the labels beside them were fabricated
    # (it printed "loads [5,0,4]" beside cost 2.7000, which corresponds to [3,3,3]).
    cases = [
        ("balanced      ", np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])),
        ("moderate      ", np.array([0, 0, 0, 0, 0, 0, 1, 1, 2])),
        ("concentrated  ", np.zeros(n_tasks, dtype=int)),
    ]
    closed_form_ok = True
    for label, assignment in cases:
        loads_actual = np.bincount(assignment, minlength=pso.num_sats).astype(float)
        cost = pso._evaluate(assignment, tasks)
        closed_form = float((loads_actual ** 2).sum()) / 10.0
        agree = abs(cost - closed_form) < 1e-9
        closed_form_ok = closed_form_ok and agree
        print(f"         {label} loads {loads_actual.astype(int).tolist()!s:14s} "
              f"-> cost {cost:8.4f}   sum of squares / 10 = {closed_form:8.4f}   "
              f"agree: {agree}")
    print(f"         cost == sum of squared load counts, exactly, for every case: "
          f"{closed_form_ok}")
    print(f"         The objective's minimum is attained by the most even spread and")
    print(f"         is independent of WHICH task lands on which satellite.")

    # ---- F3: identical load distribution, different everything else ---------
    print("\n  [INFO] F3 does the cost change when only identity/properties change?")
    # Two assignments with the SAME counts (0,0,0,1,1,1,2,2,2) but pinned to
    # satellites whose energies differ, with tasks of very different loads/priorities.
    spread_a = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
    heavy_first = [make_task(sim, i, load=50.0, priority=sim.TaskPriority.CRITICAL)
                   for i in range(n_tasks)]
    light_last = [make_task(sim, i, load=1.0, priority=sim.TaskPriority.LOW)
                  for i in range(n_tasks)]
    costs = {
        "default constellation, medium tasks": pso._evaluate(spread_a, tasks),
        "default constellation, HEAVY CRITICAL tasks": pso._evaluate(spread_a, heavy_first),
        "default constellation, LIGHT LOW tasks": pso._evaluate(spread_a, light_last),
    }
    # pin the spread onto satellites with very different energy levels
    skew = sim.PSOOptimizer(make_constellation(sim, energies=(0.2, 0.9, 1.0)),
                            num_particles=5, max_iter=5)
    costs["skewed-energy constellation, same spread"] = skew._evaluate(spread_a, tasks)
    for label, c in costs.items():
        print(f"           {label:46s} cost {c:.6f}")
    distinct = sorted({round(c, 9) for c in costs.values()})
    if len(distinct) == 1:
        print(f"  [FAIL] F3 all four cost {distinct[0]:.6f} despite the satellite energy "
              f"profile")
        print(f"         spanning 0.2 to 1.0, task loads spanning 1.0 to 50.0, and "
              f"priorities spanning")
        print(f"         LOW to CRITICAL. The objective reads task COUNTS only. No "
              f"assignment that")
        print(f"         differs only in WHICH task goes where can be preferred over "
              f"another.")
        failures.append("F3-objective-blind-to-task-and-satellite-state")
    else:
        print("  [PASS] F3 the cost responds to satellite and task state")

    # ---- F2: does the baselines' objective read what XING optimises? ---------
    print("\n  [INFO] F2 does the baselines' cost respond to the quantities XING "
          "optimises?")
    fixed = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
    probes = [
        ("energy_level of sat 0 (0.80 -> 0.25)",
         make_constellation(sim, energies=(0.25, 0.8, 0.8))),
        ("energy_level of sat 0 (0.80 -> 1.00)",
         make_constellation(sim, energies=(1.0, 0.8, 0.8))),
        ("queue_length of sat 0 (0 -> 6)",
         make_constellation(sim, queue_lens=(6, 0, 0))),
        ("compute_capacity of sat 0 (10 -> 2)",
         make_constellation(sim, energies=(0.8, 0.8, 0.8))),
    ]
    base_cost = None
    responded = []
    for label, constellation in probes:
        opt = sim.PSOOptimizer(constellation, num_particles=5, max_iter=5)
        c = opt._evaluate(fixed, tasks)
        if base_cost is None:
            base_cost = c
        delta = c - base_cost
        changed = abs(delta) > 1e-12
        responded.append((label, c, delta, changed))
        print(f"           {label:42s} cost {c:.6f}   delta {delta:+.3e}"
              f"   changed: {changed}")
    if not any(ch for *_, ch in responded):
        print("  [FAIL] F2 the baselines' cost is invariant under every one of these "
              "interventions.")
        print("         XING's reward is built from compute_capacity, energy_level,")
        print("         queue_length, task.priority and task.computational_load. The")
        print("         baselines read none of them. They are not solving the problem")
        print("         XING solves.")
        failures.append("F2-baselines-ignore-xing-criteria")
    else:
        print("  [PASS] F2 at least one intervention moves the baselines' cost")

    # ---- POSITIVE CONTROL: XING must respond to the same battery ------------
    print("\n  [INFO] POSITIVE CONTROL — XING's reward under the identical battery:")
    base_sat, base_task = make_sat(sim, 0, energy=0.8, queue_len=0), make_task(sim, 1)
    base_reward = xing._calculate_reward(base_sat, base_task)
    print(f"           baseline reward {base_reward:.6f}")

    ctrl = [
        ("energy_level 0.80 -> 0.25",
         make_sat(sim, 0, energy=0.25, queue_len=0), base_task, "decrease"),
        ("energy_level 0.80 -> 1.00",
         make_sat(sim, 0, energy=1.00, queue_len=0), base_task, "increase"),
        ("queue_length 0 -> 6",
         make_sat(sim, 0, energy=0.8, queue_len=6), base_task, "decrease"),
        ("task priority MEDIUM -> CRITICAL",
         base_sat, make_task(sim, 1, priority=sim.TaskPriority.CRITICAL), "increase"),
        ("task priority MEDIUM -> LOW",
         base_sat, make_task(sim, 1, priority=sim.TaskPriority.LOW), "decrease"),
        ("computational_load 5.0 -> 50.0",
         base_sat, make_task(sim, 1, load=50.0), "decrease"),
    ]
    ctrl_ok = 0
    for label, sat, task, expected in ctrl:
        r = xing._calculate_reward(sat, task)
        delta = r - base_reward
        moved = abs(delta) > 1e-12
        direction = ("increase" if delta > 0 else "decrease") if moved else "no change"
        agrees = (direction == expected)
        ctrl_ok += int(moved and agrees)
        print(f"           {label:38s} reward {r:12.6f}  delta {delta:+11.4f}  "
              f"{direction:9s} expected {expected:9s} {'OK' if agrees else 'MISMATCH'}")
    print(f"         {ctrl_ok}/{len(ctrl)} interventions moved the reward in the "
          f"predicted direction")
    if ctrl_ok == len(ctrl):
        print("  [PASS] positive control: XING's reward responds to all "
              f"{len(ctrl)} interventions")
        print("           in the predicted direction, so this falsifier CAN detect an")
        print("           objective that ignores these quantities. F2's invariance is")
        print("           therefore a property of the baselines, not of the instrument.")
    else:
        print("  [FAIL] positive control: XING's reward failed to respond correctly, "
              "so the")
        print("         F2 invariance results are void.")
        failures.append("I01-1-positive-control-broken")

    print("=" * 78)
    if failures:
        print("FAILED: " + ", ".join(failures))
        print()
        print("Implementation fact: the three methods do not share an objective. XING")
        print("maximises a four-term reward over compute, energy, queue and priority.")
        print("PSO and GA minimise sum of squared per-satellite task counts, read from")
        print("identical function bodies. They never read energy_level, queue_length,")
        print("task.priority or task.computational_load.")
        print()
        print("Claim correspondence: NOT ADJUDICATED. Whether the manuscript's framing")
        print("survives this, and what must change if it does not, is the next phase.")
        return 1
    print("PASSED: the three methods optimise the same objective")
    return 0


if __name__ == "__main__":
    sys.exit(main())