<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/images/github_banner_dark.png">
    <source media="(prefers-color-scheme: light)" srcset="assets/images/github_banner_light.png">
    <img alt="NEXUS Banner" src="assets/images/github_banner_light.png" width="100%">
  </picture>

  <p align="center">
    <strong>Advanced Autonomous Cyber Warfare & Threat Intelligence Simulation</strong>
  </p>
  
  <p align="center">
    <a href="https://github.com/vamsimuddada/NEXUS/stargazers"><img src="https://img.shields.io/github/stars/vamsimuddada/NEXUS?style=for-the-badge&color=0f172a" alt="Stars"></a>
    <a href="https://github.com/vamsimuddada/NEXUS/network/members"><img src="https://img.shields.io/github/forks/vamsimuddada/NEXUS?style=for-the-badge&color=0f172a" alt="Forks"></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge&color=0f172a" alt="License: MIT"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&color=0f172a" alt="Python 3.10+"></a>
    <a href="https://streamlit.io"><img src="https://img.shields.io/badge/Streamlit-1.28+-red.svg?style=for-the-badge&color=0f172a" alt="Streamlit"></a>
    <a href="https://nexus-vamsimuddada.streamlit.app/"><img src="https://img.shields.io/badge/Live_Demo-Online-success.svg?style=for-the-badge&color=0f172a" alt="Live Demo"></a>
  </p>
</div>

<br/>

> **NEXUS** is an enterprise-grade, AI-driven cyber warfare simulation environment. Designed for SOC teams, security researchers, and red/blue team operators, NEXUS provides a deeply interactive platform to simulate Advanced Persistent Threats (APTs), dynamically map behaviors to the **MITRE ATT&CK®** framework, and evaluate automated defensive mitigations.

<br/>

<div align="center">
  <img src="assets/images/dashboard_demo.gif" alt="NEXUS Dashboard Demo" width="100%" style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/>
</div>

<br/>

## ⚡ Executive Summary
Traditional breach and attack simulation tools rely on static, pre-defined playbooks. **NEXUS** introduces a paradigm shift by utilizing Large Language Models (LLMs) to power autonomous threat actors that continuously evolve their attack vectors. Coupled with a real-time Security Orchestration, Automation, and Response (SOAR) defense engine, NEXUS creates a dynamic, high-fidelity wargaming environment.

<br/>

## 🏗️ System Architecture

The platform operates on a modular, multi-layered architecture, separating the intelligence engines from the presentation layer.

```mermaid
graph TD;
    subgraph "NEXUS Core Engine"
        A[Reconnaissance Layer] -->|Target Intel| B(Attack Layer)
        B -->|Exploits| C{Detection Layer}
        C -->|Alerts| D[SOAR Defense Layer]
        D -->|Mitigation| B
    end
    
    subgraph "Analytics & UI"
        E[(Data Lake / Reports)]
        F[ELO Scoring Engine]
        G[Streamlit Live Dashboard]
        
        C -.-> E
        C -.-> F
        F -.-> G
    end
    
    style A fill:#1e293b,stroke:#3b82f6,color:#fff
    style B fill:#7f1d1d,stroke:#ef4444,color:#fff
    style C fill:#1e293b,stroke:#3b82f6,color:#fff
    style D fill:#14532d,stroke:#22c55e,color:#fff
    style G fill:#0f172a,stroke:#6366f1,color:#fff
```

<br/>

## 🚀 Core Capabilities

| Feature | Description | Engine |
| :--- | :--- | :--- |
| **🧠 Autonomous APTs** | Threat actors powered by LLMs (Ollama/Claude) that dynamically adapt. | `debate_engine.py` |
| **🛡️ Tri-Brain Defense** | Ensembled detection using Rules, Graph Neural Networks (GNN), and LLMs. | `tri_brain.py` |
| **📊 Real-Time Telemetry** | Live, interactive graphs mapping lateral movement across the network. | `graph_detector.py` |
| **📑 Executive Reporting** | One-click generation of professional PDF Threat Intel Reports. | `paper_gen.py` |
| **🎯 MITRE ATT&CK®** | Native mapping of all actor maneuvers to MITRE T-Codes. | `stix_exporter.py` |

<br/>

<details>
<summary><b>📂 Explore Project Structure</b> (Click to expand)</summary>

```text
NEXUS/
├── core/                  # Core simulation orchestrator
│   └── simulation.py      # Main state machine
├── defender/              # Blue Team AI
│   ├── gnn/               # Graph Neural Network detectors
│   ├── llm/               # LLM Debate engines
│   └── tri_brain.py       # Defense ensemble logic
├── scripts/               # Entrypoints
│   ├── dashboard.py       # Streamlit UI
│   └── run_simulation.py  # Headless CLI
└── requirements.txt       # Optimized dependencies
```
</details>

<br/>

## 💻 Quick Start

You can run NEXUS entirely locally. The system is designed to gracefully fallback to mocked telemetry if heavy local AI models (like Ollama) are unavailable.

```bash
# 1. Clone the repository
git clone https://github.com/vamsimuddada/NEXUS.git
cd NEXUS

# 2. Install requirements
pip install -r requirements.txt

# 3. Launch the Command Center
streamlit run scripts/dashboard.py
```

<br/>

## 🤝 Contributing & License
NEXUS is open-source and built for the security community. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

This project is licensed under the **MIT License** - see the [`LICENSE`](LICENSE) file for details.
