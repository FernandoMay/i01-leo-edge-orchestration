"""
Tests for XING LEO Edge Orchestration Simulation
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simulation import (
    Task, TaskPriority, Satellite, LEOConstellation,
    StochasticQueueModel, XINGOrchestrator, PSOOptimizer,
    GAOptimizer, SimulationRunner
)


class TestTask:
    def test_task_creation(self):
        task = Task(
            task_id=1,
            computational_load=5.0,
            data_size=100.0,
            deadline=2.0,
            priority=TaskPriority.HIGH
        )
        assert task.task_id == 1
        assert task.computational_load == 5.0
        assert task.is_urgent is True

    def test_task_priority_levels(self):
        for priority in TaskPriority:
            task = Task(
                task_id=1, computational_load=1.0,
                data_size=10.0, deadline=1.0, priority=priority
            )
            assert task.priority == priority

    def test_non_urgent_task(self):
        task = Task(
            task_id=1, computational_load=1.0,
            data_size=10.0, deadline=1.0, priority=TaskPriority.LOW
        )
        assert task.is_urgent is False


class TestSatellite:
    def test_satellite_creation(self):
        sat = Satellite(
            sat_id=0,
            orbital_plane=0,
            position=np.array([550.0, 0.0, 0.0]),
            compute_capacity=10.0,
            memory_capacity=16.0,
            energy_level=0.9
        )
        assert sat.sat_id == 0
        assert sat.compute_capacity == 10.0

    def test_available_compute(self):
        sat = Satellite(
            sat_id=0, orbital_plane=0,
            position=np.array([0, 0, 0]),
            compute_capacity=10.0,
            memory_capacity=16.0,
            energy_level=0.8
        )
        available = sat.available_compute
        assert available > 0
        assert available <= 10.0

    def test_can_accept_task(self):
        sat = Satellite(
            sat_id=0, orbital_plane=0,
            position=np.array([0, 0, 0]),
            compute_capacity=10.0,
            memory_capacity=16.0,
            energy_level=0.9
        )
        task = Task(
            task_id=1, computational_load=1.0,
            data_size=10.0, deadline=1.0, priority=TaskPriority.MEDIUM
        )
        assert sat.can_accept_task(task) is True

    def test_cannot_accept_low_energy(self):
        sat = Satellite(
            sat_id=0, orbital_plane=0,
            position=np.array([0, 0, 0]),
            compute_capacity=10.0,
            memory_capacity=16.0,
            energy_level=0.1
        )
        task = Task(
            task_id=1, computational_load=1.0,
            data_size=10.0, deadline=1.0, priority=TaskPriority.MEDIUM
        )
        assert sat.can_accept_task(task) is False


class TestLEOConstellation:
    def test_constellation_creation(self):
        constellation = LEOConstellation.create(
            num_planes=2, sats_per_plane=4
        )
        assert len(constellation.satellites) == 8
        assert constellation.num_orbital_planes == 2

    def test_distance_calculation(self):
        constellation = LEOConstellation.create(
            num_planes=1, sats_per_plane=4
        )
        dist = constellation.get_distance(0, 1)
        assert dist > 0

    def test_nearest_satellites(self):
        constellation = LEOConstellation.create(
            num_planes=2, sats_per_plane=6
        )
        position = np.array([550.0, 0.0, 0.0])
        nearest = constellation.get_nearest_satellites(position, k=3)
        assert len(nearest) == 3
        assert all(0 <= s < len(constellation.satellites) for s in nearest)


class TestStochasticQueueModel:
    def test_task_generation(self):
        model = StochasticQueueModel(arrival_rate=10.0)
        tasks = model.generate_tasks(duration=10.0)
        assert len(tasks) > 0
        assert all(isinstance(t, Task) for t in tasks)

    def test_task_arrival_times(self):
        model = StochasticQueueModel(arrival_rate=10.0)
        tasks = model.generate_tasks(duration=10.0)
        arrival_times = [t.arrival_time for t in tasks]
        assert all(arrival_times[i] <= arrival_times[i+1]
                   for i in range(len(arrival_times)-1))

    def test_metrics_calculation(self):
        model = StochasticQueueModel(arrival_rate=10.0)
        tasks = model.generate_tasks(duration=5.0)
        for task in tasks:
            task.completion_time = task.arrival_time + 0.1
        metrics = model.calculate_metrics(tasks)
        assert "avg_latency" in metrics
        assert "throughput" in metrics
        assert "deadline_met_ratio" in metrics


class TestXINGOrchestrator:
    def test_orchestrator_creation(self):
        constellation = LEOConstellation.create(
            num_planes=2, sats_per_plane=4
        )
        orchestrator = XINGOrchestrator(constellation)
        assert orchestrator.constellation == constellation

    def test_task_assignment(self):
        constellation = LEOConstellation.create(
            num_planes=2, sats_per_plane=4
        )
        orchestrator = XINGOrchestrator(constellation)
        tasks = [
            Task(task_id=i, computational_load=1.0,
                 data_size=10.0, deadline=1.0,
                 priority=TaskPriority.MEDIUM)
            for i in range(5)
        ]
        completed = orchestrator.assign_tasks(tasks)
        assert len(completed) > 0
        assert all(t.assigned_satellite >= 0 for t in completed)


class TestPSOOptimizer:
    def test_pso_optimization(self):
        constellation = LEOConstellation.create(
            num_planes=2, sats_per_plane=4
        )
        pso = PSOOptimizer(constellation, num_particles=10, max_iter=5)
        tasks = [
            Task(task_id=i, computational_load=1.0,
                 data_size=10.0, deadline=1.0,
                 priority=TaskPriority.MEDIUM)
            for i in range(5)
        ]
        completed = pso.optimize(tasks)
        assert len(completed) > 0


class TestGAOptimizer:
    def test_ga_optimization(self):
        constellation = LEOConstellation.create(
            num_planes=2, sats_per_plane=4
        )
        ga = GAOptimizer(constellation, pop_size=20, max_gen=10)
        tasks = [
            Task(task_id=i, computational_load=1.0,
                 data_size=10.0, deadline=1.0,
                 priority=TaskPriority.MEDIUM)
            for i in range(5)
        ]
        completed = ga.optimize(tasks)
        assert len(completed) > 0


class TestSimulationRunner:
    def test_runner_creation(self):
        runner = SimulationRunner(
            num_planes=2, sats_per_plane=4,
            duration=10.0, arrival_rate=5.0
        )
        assert runner.constellation is not None

    def test_comparison_run(self):
        runner = SimulationRunner(
            num_planes=2, sats_per_plane=4,
            duration=5.0, arrival_rate=5.0
        )
        results = runner.run_comparison()
        assert "XING" in results
        assert "PSO" in results
        assert "GA" in results
        assert all("avg_latency" in r for r in results.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
