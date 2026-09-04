"""
XING Cognitive Edge Orchestration for LEO Satellite Networks
Stochastic Queueing Model + Adaptive Scheduling

Paper: Cognitive Edge Orchestration for LEO Satellite Networks
       under Stochastic Resource Constraints
Venue: CCIOT 2026
Authors: Fernando May et al.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import random
import time
from enum import Enum


class TaskPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Task:
    task_id: int
    computational_load: float  # GFLOPS required
    data_size: float  # MB
    deadline: float  # seconds
    priority: TaskPriority
    arrival_time: float = 0.0
    assigned_satellite: int = -1
    completion_time: float = -1.0

    @property
    def is_urgent(self) -> bool:
        return self.priority in (TaskPriority.HIGH, TaskPriority.CRITICAL)


@dataclass
class Satellite:
    sat_id: int
    orbital_plane: int
    position: np.ndarray  # [x, y, z] in km
    compute_capacity: float  # GFLOPS
    memory_capacity: float  # GB
    energy_level: float  # 0-1 normalized
    queue: List[Task] = field(default_factory=list)
    active_tasks: int = 0

    @property
    def available_compute(self) -> float:
        utilization = min(1.0, self.active_tasks / 10.0)
        return self.compute_capacity * (1.0 - utilization) * self.energy_level

    @property
    def queue_length(self) -> int:
        return len(self.queue)

    def can_accept_task(self, task: Task) -> bool:
        return (self.available_compute >= task.computational_load * 0.1 and
                self.energy_level > 0.2)


@dataclass
class LEOConstellation:
    satellites: List[Satellite]
    num_orbital_planes: int
    satellites_per_plane: int
    altitude: float  # km

    @classmethod
    def create(cls, num_planes: int = 6, sats_per_plane: int = 12,
               altitude: float = 550.0) -> 'LEOConstellation':
        satellites = []
        sat_id = 0
        for plane in range(num_planes):
            plane_inclination = np.radians(53.0 + plane * 5)
            for sat in range(sats_per_plane):
                angle = 2 * np.pi * sat / sats_per_plane
                x = altitude * np.cos(angle) * np.cos(plane_inclination)
                y = altitude * np.sin(angle)
                z = altitude * np.cos(angle) * np.sin(plane_inclination)
                position = np.array([x, y, z])
                compute = np.random.uniform(5.0, 15.0)  # GFLOPS
                memory = np.random.uniform(8.0, 32.0)  # GB
                energy = np.random.uniform(0.7, 1.0)
                satellites.append(Satellite(
                    sat_id=sat_id, orbital_plane=plane,
                    position=position, compute_capacity=compute,
                    memory_capacity=memory, energy_level=energy
                ))
                sat_id += 1
        return cls(satellites=satellites, num_orbital_planes=num_planes,
                   satellites_per_plane=sats_per_plane, altitude=altitude)

    def get_distance(self, sat1_id: int, sat2_id: int) -> float:
        return np.linalg.norm(
            self.satellites[sat1_id].position -
            self.satellites[sat2_id].position
        )

    def get_nearest_satellites(self, position: np.ndarray,
                                k: int = 5) -> List[int]:
        distances = []
        for sat in self.satellites:
            dist = np.linalg.norm(sat.position - position)
            distances.append((sat.sat_id, dist))
        distances.sort(key=lambda x: x[1])
        return [d[0] for d in distances[:k]]


class StochasticQueueModel:
    """M/G/c queueing model for task arrivals in LEO edge computing."""

    def __init__(self, arrival_rate: float = 10.0,
                 service_rate: float = 15.0,
                 num_servers: int = 1):
        self.arrival_rate = arrival_rate  # tasks/sec
        self.service_rate = service_rate  # tasks/sec per server
        self.num_servers = num_servers

    def generate_tasks(self, duration: float,
                       num_tasks: int = None) -> List[Task]:
        if num_tasks is None:
            num_tasks = int(self.arrival_rate * duration)

        tasks = []
        inter_arrivals = np.random.exponential(
            1.0 / self.arrival_rate, num_tasks
        )
        arrival_times = np.cumsum(inter_arrivals)

        for i, arrival_time in enumerate(arrival_times):
            if arrival_time > duration:
                break

            comp_load = np.random.lognormal(mean=1.0, sigma=0.5)
            data_size = np.random.lognormal(mean=2.0, sigma=1.0)
            deadline = np.random.uniform(0.5, 5.0)
            priority = random.choice(list(TaskPriority))

            tasks.append(Task(
                task_id=i,
                computational_load=comp_load,
                data_size=data_size,
                deadline=deadline,
                priority=priority,
                arrival_time=arrival_time
            ))

        return tasks

    def calculate_metrics(self, completed_tasks: List[Task]) -> Dict:
        if not completed_tasks:
            return {"avg_latency": float('inf'), "throughput": 0,
                    "deadline_met_ratio": 0, "avg_energy": 0}

        latencies = [t.completion_time - t.arrival_time
                     for t in completed_tasks]
        deadlines_met = sum(1 for t in completed_tasks
                          if (t.completion_time - t.arrival_time) <= t.deadline)

        return {
            "avg_latency": np.mean(latencies),
            "p95_latency": np.percentile(latencies, 95),
            "throughput": len(completed_tasks) / max(latencies),
            "deadline_met_ratio": deadlines_met / len(completed_tasks),
            "total_tasks": len(completed_tasks)
        }


class XINGOrchestrator:
    """XING Cognitive Edge Orchestrator for LEO satellite networks."""

    def __init__(self, constellation: LEOConstellation,
                 learning_rate: float = 0.01):
        self.constellation = constellation
        self.learning_rate = learning_rate
        self.assignment_history: List[Tuple[int, int, float]] = []
        self.reward_history: List[float] = []

    def _calculate_reward(self, satellite: Satellite,
                          task: Task) -> float:
        effective_compute = satellite.compute_capacity * satellite.energy_level
        compute_score = effective_compute / max(
            task.computational_load, 0.1
        )
        energy_score = satellite.energy_level
        queue_penalty = satellite.queue_length * 0.15
        priority_bonus = task.priority.value * 0.3

        reward = (compute_score * 0.5 + energy_score * 0.3 -
                  queue_penalty + priority_bonus)
        return reward

    def _select_satellite(self, task: Task) -> int:
        best_sat = -1
        best_reward = -float('inf')

        for sat in self.constellation.satellites:
            if sat.can_accept_task(task):
                reward = self._calculate_reward(sat, task)
                if reward > best_reward:
                    best_reward = reward
                    best_sat = sat.sat_id

        if best_sat == -1:
            best_sat = min(self.constellation.satellites,
                          key=lambda s: s.queue_length).sat_id

        return best_sat

    def assign_tasks(self, tasks: List[Task]) -> List[Task]:
        for task in tasks:
            sat_id = self._select_satellite(task)
            task.assigned_satellite = sat_id
            self.constellation.satellites[sat_id].queue.append(task)

        completed = []
        for sat in self.constellation.satellites:
            sat_queue = sorted(sat.queue,
                             key=lambda t: (-t.priority.value, t.arrival_time))
            current_time = 0.0
            for task in sat_queue:
                service_time = task.computational_load / max(
                    sat.compute_capacity * sat.energy_level, 0.1
                )
                start_time = max(current_time, task.arrival_time)
                task.completion_time = start_time + service_time
                current_time = start_time + service_time
                completed.append(task)
            sat.queue.clear()

        return completed


class PSOOptimizer:
    """Particle Swarm Optimization for task assignment."""

    def __init__(self, constellation: LEOConstellation,
                 num_particles: int = 20, max_iter: int = 50):
        self.constellation = constellation
        self.num_particles = num_particles
        self.num_sats = len(constellation.satellites)
        self.max_iter = max_iter
        self.w = 0.7  # inertia
        self.c1 = 1.5  # cognitive
        self.c2 = 1.5  # social

    def optimize(self, tasks: List[Task]) -> List[Task]:
        n_tasks = len(tasks)
        positions = np.random.randint(
            0, self.num_sats, (self.num_particles, n_tasks)
        ).astype(float)
        velocities = np.zeros_like(positions)
        p_best = positions.copy()
        p_best_scores = np.full(self.num_particles, float('inf'))
        g_best = positions[0].copy()
        g_best_score = float('inf')

        for iteration in range(self.max_iter):
            for i in range(self.num_particles):
                score = self._evaluate(positions[i], tasks)
                if score < p_best_scores[i]:
                    p_best_scores[i] = score
                    p_best[i] = positions[i].copy()
                if score < g_best_score:
                    g_best_score = score
                    g_best = positions[i].copy()

            r1 = np.random.random((self.num_particles, n_tasks))
            r2 = np.random.random((self.num_particles, n_tasks))
            velocities = (self.w * velocities +
                         self.c1 * r1 * (p_best - positions) +
                         self.c2 * r2 * (g_best - positions))
            positions = np.clip(positions + velocities, 0,
                               self.num_sats - 1).round().astype(float)

        for i, task in enumerate(tasks):
            task.assigned_satellite = int(g_best[i])

        completed = []
        for sat in self.constellation.satellites:
            sat_queue = sorted(
                [t for t in tasks if t.assigned_satellite == sat.sat_id],
                key=lambda t: t.arrival_time
            )
            current_time = 0.0
            for task in sat_queue:
                effective_compute = sat.compute_capacity * sat.energy_level
                service_time = task.computational_load / max(
                    effective_compute, 0.1
                )
                start_time = max(current_time, task.arrival_time)
                task.completion_time = start_time + service_time
                current_time = start_time + service_time
                completed.append(task)

        return completed

    def _evaluate(self, assignment: np.ndarray,
                  tasks: List[Task]) -> float:
        total_cost = 0
        sat_loads = np.zeros(self.num_sats)

        for i, task in enumerate(tasks):
            sat_id = int(assignment[i])
            sat_loads[sat_id] += 1

        for i, task in enumerate(tasks):
            sat_id = int(assignment[i])
            load_factor = sat_loads[sat_id] / 10.0
            total_cost += load_factor

        return total_cost


class GAOptimizer:
    """Genetic Algorithm for task assignment."""

    def __init__(self, constellation: LEOConstellation,
                 pop_size: int = 50, max_gen: int = 100,
                 mutation_rate: float = 0.1):
        self.constellation = constellation
        self.pop_size = pop_size
        self.num_sats = len(constellation.satellites)
        self.max_gen = max_gen
        self.mutation_rate = mutation_rate

    def optimize(self, tasks: List[Task]) -> List[Task]:
        n_tasks = len(tasks)
        population = np.random.randint(
            0, self.num_sats, (self.pop_size, n_tasks)
        )

        for gen in range(self.max_gen):
            fitness = np.array([self._fitness(ind, tasks)
                               for ind in population])
            elite_idx = np.argsort(fitness)[:10]
            new_pop = [population[i] for i in elite_idx]

            while len(new_pop) < self.pop_size:
                p1, p2 = random.sample(range(self.pop_size), 2)
                cut = random.randint(1, n_tasks - 1)
                child = np.concatenate([
                    population[p1, :cut], population[p2, cut:]
                ])
                if random.random() < self.mutation_rate:
                    mut_pos = random.randint(0, n_tasks - 1)
                    child[mut_pos] = random.randint(0, self.num_sats - 1)
                new_pop.append(child)

            population = np.array(new_pop[:self.pop_size])

        best_idx = np.argmin([self._fitness(ind, tasks)
                             for ind in population])
        best = population[best_idx]

        for i, task in enumerate(tasks):
            task.assigned_satellite = int(best[i])

        completed = []
        for sat in self.constellation.satellites:
            sat_queue = sorted(
                [t for t in tasks if t.assigned_satellite == sat.sat_id],
                key=lambda t: t.arrival_time
            )
            current_time = 0.0
            for task in sat_queue:
                service_time = task.computational_load / max(
                    sat.compute_capacity * sat.energy_level, 0.1
                )
                start_time = max(current_time, task.arrival_time)
                task.completion_time = start_time + service_time
                current_time = start_time + service_time
                completed.append(task)

        return completed

    def _fitness(self, assignment: np.ndarray,
                 tasks: List[Task]) -> float:
        total_cost = 0
        sat_loads = np.zeros(self.num_sats)
        for i, task in enumerate(tasks):
            sat_loads[int(assignment[i])] += 1
        for i, task in enumerate(tasks):
            load_factor = sat_loads[int(assignment[i])] / 10.0
            total_cost += load_factor
        return total_cost


class SimulationRunner:
    """Main simulation runner for comparing orchestration methods."""

    def __init__(self, num_planes: int = 6, sats_per_plane: int = 12,
                 duration: float = 100.0, arrival_rate: float = 10.0):
        self.constellation = LEOConstellation.create(
            num_planes, sats_per_plane
        )
        self.queue_model = StochasticQueueModel(arrival_rate=arrival_rate)
        self.duration = duration

    def run_comparison(self) -> Dict:
        results = {}

        tasks = self.queue_model.generate_tasks(self.duration)

        print("Running XING Orchestrator...")
        constellation_copy = self._copy_constellation()
        orchestrator = XINGOrchestrator(constellation_copy)
        start = time.time()
        completed_xing = orchestrator.assign_tasks([self._copy_task(t) for t in tasks])
        xing_time = time.time() - start
        results["XING"] = {
            **self.queue_model.calculate_metrics(completed_xing),
            "execution_time": xing_time
        }

        print("Running PSO Optimizer...")
        constellation_copy = self._copy_constellation()
        pso = PSOOptimizer(constellation_copy)
        start = time.time()
        completed_pso = pso.optimize([self._copy_task(t) for t in tasks])
        pso_time = time.time() - start
        results["PSO"] = {
            **self.queue_model.calculate_metrics(completed_pso),
            "execution_time": pso_time
        }

        print("Running GA Optimizer...")
        constellation_copy = self._copy_constellation()
        ga = GAOptimizer(constellation_copy)
        start = time.time()
        completed_ga = ga.optimize([self._copy_task(t) for t in tasks])
        ga_time = time.time() - start
        results["GA"] = {
            **self.queue_model.calculate_metrics(completed_ga),
            "execution_time": ga_time
        }

        return results

    def _copy_constellation(self) -> LEOConstellation:
        new_sats = []
        for sat in self.constellation.satellites:
            new_sat = Satellite(
                sat_id=sat.sat_id,
                orbital_plane=sat.orbital_plane,
                position=sat.position.copy(),
                compute_capacity=sat.compute_capacity,
                memory_capacity=sat.memory_capacity,
                energy_level=sat.energy_level
            )
            new_sats.append(new_sat)
        return LEOConstellation(
            satellites=new_sats,
            num_orbital_planes=self.constellation.num_orbital_planes,
            satellites_per_plane=self.constellation.satellites_per_plane,
            altitude=self.constellation.altitude
        )

    def _copy_task(self, task: Task) -> Task:
        return Task(
            task_id=task.task_id,
            computational_load=task.computational_load,
            data_size=task.data_size,
            deadline=task.deadline,
            priority=task.priority,
            arrival_time=task.arrival_time
        )

    def run_scaling_experiment(self) -> Dict:
        scales = [1, 2, 4, 8, 12]
        results = {}

        for num_planes in scales:
            sats = num_planes * 12
            print(f"\nScaling to {sats} satellites...")
            self.constellation = LEOConstellation.create(
                num_planes, 12
            )
            scale_results = self.run_comparison()
            results[sats] = scale_results

        return results


if __name__ == "__main__":
    print("=" * 60)
    print("XING Cognitive Edge Orchestration for LEO Networks")
    print("CCIOT 2026 — Simulation Runner")
    print("=" * 60)

    runner = SimulationRunner(
        num_planes=6, sats_per_plane=12,
        duration=100.0, arrival_rate=10.0
    )

    results = runner.run_comparison()

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    for method, metrics in results.items():
        print(f"\n{method}:")
        print(f"  Avg Latency:       {metrics['avg_latency']:.4f} s")
        print(f"  P95 Latency:       {metrics['p95_latency']:.4f} s")
        print(f"  Throughput:        {metrics['throughput']:.2f} tasks/s")
        print(f"  Deadline Met:      {metrics['deadline_met_ratio']:.2%}")
        print(f"  Execution Time:    {metrics['execution_time']:.4f} s")
        print(f"  Total Tasks:       {metrics['total_tasks']}")
