# Cognitive Edge Orchestration for LEO Satellite Networks

**Paper:** Cognitive Edge Orchestration for LEO Satellite Networks under Stochastic Resource Constraints
**Venue:** CCIOT 2026 — Cloud Computing and Internet of Things
**Authors:** Fernando May Fuentes et al.
**ORCID:** https://orcid.org/0009-0002-3953-5224
**Conference deadline:** September 1, 2026 (verify current CFP status)
**Submission site:** http://cciot.org

## Overview

This repository contains the simulation code, experiments, and paper manuscript for the LEO Edge Orchestration paper. The XING cognitive orchestrator applies adaptive routing and swarm intelligence to optimize task assignment in LEO satellite edge networks.

## Structure

```
├── src/
│   └── simulation.py          # Main simulation code
├── tests/
│   └── test_simulation.py     # Pytest test suite
├── latex/
│   └── paper.tex              # LaTeX manuscript
├── figures/                   # Generated figures
├── data/                      # Simulation data
├── requirements.txt
├── Dockerfile
└── README.md
```

## Quick Start

### Local Setup

```bash
pip install -r requirements.txt
python src/simulation.py
```

### Docker

```bash
docker build -t leo-edge-orch .
docker run leo-edge-orch
```

### Run Tests

```bash
pytest tests/ -v
```

## Methods

1. **XING Orchestrator:** Cognitive edge orchestration with adaptive routing
2. **PSO Optimizer:** Particle Swarm Optimization baseline
3. **GA Optimizer:** Genetic Algorithm baseline

## Results

| Method | Avg Latency (s) | Deadline Met (%) | Exec Time (s) |
|--------|-----------------|------------------|---------------|
| XING-inspired | 28.07 | 39.5% | 0.047 |
| PSO | 0.40 | 98.7% | 0.415 |
| GA | 0.40 | 98.7% | 1.815 |

## Citation

```bibtex
@inproceedings{may2026leo,
  title={Cognitive Edge Orchestration for LEO Satellite Networks under Stochastic Resource Constraints},
  author={May, Fernando},
  booktitle={Proc. CCIOT 2026},
  year={2026}
}
```

## License

MIT
