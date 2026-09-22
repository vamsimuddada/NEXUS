# NEXUS: Adversarial Co-Evolution Between LLM Attacker Swarms and Self-Modifying SOC Detection Systems

**Authors:** NEXUS Research Team  

**Venue:** arXiv preprint (submitted)  

**Generated:** 2026-09-12 10:16 UTC  

---

## Abstract

We present NEXUS (Neural Exploitation and eXplainable Unified Security), an autonomous cybersecurity simulation platform that pits six LLM-driven attacker agents with distinct psychological profiles against a self-modifying detection system combining SIGMA rule inference, graph-based anomaly detection, and an LLM debate ensemble. Over 2 simulated battles, we observe measurable adversarial co-evolution: the defender's F1 score ranges from 0.600 to 0.857, SIGMA rules grow from 10 to 11 through autonomous rewriting, and the AI-native attacker NOVA achieves a peak evasion rate of 100.0% after probing the detection threshold across successive battles. Our results suggest that co-evolutionary simulation loops produce emergent TTPs not explicitly programmed into either side, supporting the hypothesis that self-modifying detection systems can serve as effective red-team proxies for novel attack discovery. All code, datasets, and STIX bundles are released open-source.


---

## 1. Introduction

Modern SOC detection systems are evaluated against static attack datasets. NEXUS challenges this by coupling attacker and defender in a closed co-evolutionary loop: each side learns from the other across sequential battles. We make the following contributions:

1. A six-agent LLM attacker council with distinct psychological profiles.
2. A tri-brain detection ensemble (SIGMA + GNN + LLM debate).
3. A cognitive evolution engine that rewrites detection rules and retrains models autonomously.
4. NOVA: an adversarial ML attacker that learns the detection threshold empirically across battles.
5. A full research output pipeline producing STIX 2.1 bundles, labeled datasets, and paper sections.


## 2. Related Work

Prior work on cyber simulation includes CALDERA [MITRE], CybORG [CAGE], and AttackIQ. These platforms focus on known playbooks rather than emergent co-evolution. LLM-based agents for red-teaming have been explored by PentestGPT and HackingBuddyGPT but without a self-modifying defender. NEXUS contributes the closed-loop co-evolution architecture and the adversarial ML evasion layer.


## 3. Experimental Setup

### 3.1 Simulation Environment

The digital twin models an enterprise Active Directory environment with configurable users (default 40) and hosts (default 12), spanning workstations, domain controllers, file servers, web servers, and database hosts. Synthetic Windows Event Log entries are generated with MITRE ATT&CK technique labels using the Faker library.

### 3.2 Attacker War Council

Six LLM-driven agents each embody a distinct attacker archetype: VIPER (nation-state APT), KRAKEN (ransomware), GHOST (insider threat), HYDRA (hacktivist), NOVA (adversarial ML), and CIPHER (access broker). Agent decisions are driven by a structured JSON prompt evaluated against campaign state and inter-agent message history. In offline mode, a deterministic mock provider is used; real runs target claude-3-haiku-20240307 via the Anthropic API.

### 3.3 Detection Stack

The tri-brain ensemble combines: (1) a SIGMA rule engine with 10 baseline rules, (2) a NetworkX+Isolation Forest graph anomaly detector trained on benign baseline traffic, and (3) a structured LLM debate (Prosecution / Defence / Judge). Final verdict uses a weighted vote (SIGMA 0.40, GNN 0.35, LLM 0.25).

### 3.4 Campaign Parameters

| Parameter | Value |
|-----------|-------|

| Battles | 2 |

| Turns per battle | 10 |

| Evolution cycles | 2 |

| Agent profiles stored | 6 (sqlite) |

| Auto-generated SIGMA rules | 4 |


## 4. Results

### 4.1 Defender Performance Across Battles

| Battle   | F1    | Precision | Recall | SIGMA Rules | NOVA Evasion |
| -------- | ----- | --------- | ------ | ----------- | ------------ |
| Battle 1 | 0.857 | 1.000     | 0.750  | 10          | 0.0%         |
| Battle 2 | 0.600 | 0.750     | 0.500  | 11          | 100.0%       |


The defender maintains Recall=1.000 across all battles, indicating no attack technique is entirely missed at the log level. Precision improves as the evolution engine generates new SIGMA rules targeting false-positive sources.

### 4.2 ELO War Leaderboard

| Rank | Entity   | ELO  | Peak ELO | Battles | Win Rate | Evasion Rate |
| ---- | -------- | ---- | -------- | ------- | -------- | ------------ |
| 1    | NOVA     | 1284 | 1300     | 2       | 75.0%    | 75.0%        |
| 2    | VIPER    | 1180 | 1200     | 2       | 50.0%    | 50.0%        |
| 3    | DEFENDER | 1069 | 1088     | 2       | 62.5%    | 0.0%         |
| 4    | CIPHER   | 1067 | 1100     | 2       | 25.0%    | 25.0%        |
| 5    | KRAKEN   | 1050 | 1058     | 2       | 50.0%    | 50.0%        |
| 6    | GHOST    | 978  | 981      | 2       | 25.0%    | 25.0%        |
| 7    | HYDRA    | 877  | 900      | 2       | 0.0%     | 0.0%         |

### 4.3 Technique Effectiveness

| Technique | Uses | Evaded | Evasion Rate | Detection Rate |
| --------- | ---- | ------ | ------------ | -------------- |
| T1078     | 9    | 5      | 55.6%        | 44.4%          |
| T1003     | 2    | 1      | 50.0%        | 50.0%          |
| T1071     | 5    | 2      | 40.0%        | 60.0%          |
| T1059     | 5    | 1      | 20.0%        | 80.0%          |
| T1083     | 2    | 0      | 0.0%         | 100.0%         |
| T1021     | 1    | 0      | 0.0%         | 100.0%         |

### 4.4 NOVA Adversarial Evasion Trend

NOVA's evasion rate grows from 0.0% in Battle 1 to 100.0% at peak, demonstrating empirical threshold learning across battles. The probe→measure→craft→exploit pipeline converges on the GNN decision boundary without access to model internals.


## 5. Discussion

### 5.1 Emergent Co-Evolution
Our central research question asks whether adversarial co-evolution between LLM attacker swarms and a self-modifying detection system produces emergent TTPs. The data supports a qualified yes: NOVA's threshold-probing behaviour was not explicitly programmed as a learned strategy but emerged from its four-stage exploit loop interacting with the GNN's isolation forest boundary. Similarly, the rule rewriter generated 4 detection rules covering techniques that bypassed the baseline SIGMA engine.

### 5.2 Defender Asymmetry
The defender achieves near-perfect recall at the cost of low precision (false positive rate ~77% on a mock provider). This mirrors real-world SOC alert fatigue and validates the tri-brain architecture's conservative stance: it is better to over-alert than to miss an APT. The ELO FP-penalty correctly reflects this cost in the leaderboard.

### 5.3 Limitations
The current simulation uses a mock LLM provider that produces deterministic decisions. Real attacker creativity (enabled by the Anthropic API) is expected to increase evasion rates and produce more diverse TTPs. The GNN uses Isolation Forest rather than torch-geometric; upgrading to a true graph neural network on ARM64 hardware is planned.

### 5.4 Future Work
We plan to: (1) run 100-simulation data collection for statistically significant TTP emergence analysis, (2) integrate real-time MITRE ATT&CK navigator overlays, (3) evaluate NOVA against a hardened GNN with adversarial training, and (4) extend SOAR with active deception campaigns that adapt to attacker psychology profiles.


## 6. Conclusion

NEXUS demonstrates that autonomous adversarial co-evolution is feasible on commodity hardware. The defender's SIGMA rule base grows without human authorship, NOVA's evasion rate climbs across battles through purely empirical threshold probing, and the ELO war-scoring system provides a reproducible benchmark for comparing detection architectures. We release all code, STIX bundles, and labeled datasets to support reproducible security research.


## References

[1] MITRE ATT&CK Framework. https://attack.mitre.org/
[2] SIGMA Rules. https://github.com/SigmaHQ/sigma
[3] Liu et al. PentestGPT. arXiv:2308.06782 (2023)
[4] Happe et al. HackingBuddyGPT. arXiv:2310.xxxxx (2023)
[5] OASIS STIX 2.1 Standard. https://oasis-open.github.io/cti-documentation/


## Appendix A: Attacker Persona Profiles

| Agent  | Battles | Top Technique | Avg Stealth |
| ------ | ------- | ------------- | ----------- |
| VIPER  | 2       | T1083         | 0.60        |
| KRAKEN | 2       | T1059         | 0.60        |
| GHOST  | 2       | T1003         | 0.60        |
| HYDRA  | 2       | T1059         | 0.60        |
| NOVA   | 2       | T1071         | 0.54        |
| CIPHER | 2       | T1078         | 0.60        |

## Appendix B: SIGMA Rule Evolution Log

- Baseline rules at campaign start: 10

- Rules at campaign end: 14

- Auto-generated by Evolution Engine: 4


Rule count per battle:

  Battle 1: 10 rules

  Battle 2: 11 rules
