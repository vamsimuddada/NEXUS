# NEXUS — Autonomous Cyber Warfare Simulation & Self-Evolving SOC Platform
> Neural Exploitation & eXplainable Unified Security

## Architecture Overview

```
NEXUS
├── Layer 1 — Digital Twin Environment     (core/)
├── Layer 2 — Attacker War Council         (attackers/)
├── Layer 3 — Tri-Brain Detection Ensemble (defender/)
├── Layer 4 — Cognitive Evolution Engine   (evolution/)
├── Layer 5 — Autonomous SOAR/Counterstrike(soar/)
├── Layer 6 — War Score & Gamification     (scoring/)
└── Layer 7 — Research Output Engine       (research/)
```

## Setup (ARM64 / Apple Silicon / Raspberry Pi compatible)

### Requirements
- Python 3.11+
- pip
- 8GB RAM recommended
- ARM64-safe packages only (no x86-only binaries)

### Install

```bash
# Clone and enter project
git clone <your-repo>
cd nexus

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (ARM64-safe)
pip install -r requirements.txt
```

### Run

```bash
# Start a simulation (Phase 1 — Foundation)
python3 scripts/run_simulation.py

# Launch the war-room dashboard
streamlit run scripts/dashboard.py
```

## Roadmap

| Phase | Weeks | Focus |
|-------|-------|-------|
| 1 — Foundation  | 1–6   | Digital twin, attacker agents, comms |
| 2 — Intelligence| 7–12  | SIGMA engine, GNN detector, LLM debate |
| 3 — Evolution   | 13–16 | Self-rewriting rules, fine-tuning, memory |
| 4 — Publication | 17–20 | ELO scoring, STIX output, arXiv draft |

## Attacker Personas

| Agent  | Type              | Strategy |
|--------|-------------------|----------|
| VIPER  | Nation-state APT  | Patient, living-off-the-land |
| KRAKEN | Ransomware        | Fast, double extortion |
| GHOST  | Insider threat    | Env-aware, conflicted |
| HYDRA  | Hacktivist        | Chaotic, message-driven |
| NOVA   | AI-native         | Probes and evades the ML detector |
| CIPHER | Criminal broker   | Initial access specialist |

## Research Question
> Does adversarial co-evolution between LLM attacker agents and a self-modifying
> detection system produce emergent TTPs that mirror real-world APT evolution patterns?
