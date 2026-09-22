<div align="center">
  <img src="assets/images/nexus_logo.png" alt="NEXUS Logo" width="200"/>
  <h1>NEXUS</h1>
  <p><b>Advanced Autonomous Cyber Warfare & Threat Intelligence Platform</b></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
</div>

<br/>

## 🌐 Overview
**NEXUS** is a next-generation, AI-driven cyber warfare simulation and threat intelligence platform. Built for SOC teams, security researchers, and red/blue team operators, NEXUS provides a fully interactive environment to simulate advanced persistent threats (APTs), dynamically map them to the **MITRE ATT&CK®** framework, and evaluate automated defensive mitigations (SOAR).

Powered by Large Language Models (LLMs), NEXUS continuously evolves its threat landscape, executing dynamic playbooks and generating real-time executive PDF reports.

## ✨ Core Features
- **🧠 Autonomous Threat Actor Simulation:** AI-driven agents that dynamically construct and execute complex attack kill-chains.
- **🛡️ Dynamic SOAR Defenses:** Automated incident response engines that detect, isolate, and mitigate threats in real-time.
- **📊 MITRE ATT&CK® Mapping:** Automatic translation of simulation events into standardized MITRE tactics and techniques.
- **📈 Live Dashboarding:** A sleek, dark-mode Streamlit dashboard featuring live telemetry, network heatmaps, and ELO ratings for Blue vs Red teams.
- **📄 Executive Reporting:** One-click generation of beautifully formatted PDF intelligence briefings with integrated charts and analysis.

## 🏗️ Architecture
NEXUS is organized into highly modular operational layers:
- `layer1_recon/`: Threat intelligence gathering and OSINT simulation.
- `layer2_attack/`: Exploitation, payload delivery, and lateral movement.
- `layer3_detection/`: Sigma rules, honeypots, and SIEM telemetry.
- `layer4_evolution/`: Genetic algorithms and LLM-driven payload mutation.
- `layer5_soar/`: Security Orchestration, Automation, and Response playbooks.
- `layer6_scoring/`: ELO rating system evaluating attacker vs defender efficiency.
- `layer7_research/`: STIX/TAXII integrations and PDF report generation.

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/vamsimuddada/NEXUS.git
cd NEXUS
```

### 2. Install Dependencies
Ensure you have Python 3.10+ installed.
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
Launch the interactive Streamlit command center:
```bash
streamlit run scripts/dashboard.py
```

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
<div align="center">
  <i>Developed for Advanced Agentic Cyber Defense Simulations.</i>
</div>
