"""
NEXUS — Layer 7: Labeled Dataset Exporter
Exports battle logs as ML-ready datasets for research and publication.

Outputs:
  - nexus_logs.csv     : flat feature matrix with ground-truth labels
  - nexus_logs.jsonl   : one JSON object per log (for LLM fine-tuning)
  - nexus_summary.json : dataset statistics

Feature columns:
  event_id, is_admin, src_is_dc, dst_is_dc, dept_code,
  stealth_num, sigma_fired, sigma_count, gnn_score, gnn_flagged,
  llm_verdict_num, llm_confidence, ensemble_confidence,
  label (0=benign,1=malicious), attack_technique, attacker
"""

from __future__ import annotations

import csv
import json
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


_DEPT_CODE    = {"IT":0,"Engineering":1,"Finance":2,"HR":3,"Sales":4,"Legal":5,"Executive":6}
_STEALTH_CODE = {"low":0,"medium":1,"high":2}
_VERDICT_CODE = {"benign":0,"uncertain":1,"malicious":2}

FEATURE_COLUMNS = [
    "event_id","is_admin","src_is_dc","dst_is_dc","dept_code",
    "stealth_num","sigma_fired","sigma_count","gnn_score","gnn_flagged",
    "llm_verdict_num","llm_confidence","ensemble_confidence",
]
LABEL_COLUMNS = ["label","attack_technique","attacker","true_label_num"]
ALL_COLUMNS   = FEATURE_COLUMNS + LABEL_COLUMNS


def _encode_row(result: dict, log: dict | None = None) -> dict:
    """Encode a serialised DetectionResult (+ optional raw log) into a feature dict."""
    raw = log or {}
    host       = result.get("host", raw.get("host", ""))
    src_is_dc  = int("DC" in host)
    dst_ip     = raw.get("ip_dst", "")
    dst_is_dc  = int(dst_ip.startswith("10.0.0.1"))
    dept       = raw.get("department", "")
    stealth    = result.get("stealth_level", raw.get("stealth_level", "medium"))
    llm_v      = result.get("llm_verdict", "uncertain")
    true_label = result.get("true_label", raw.get("label", "benign"))
    lnum       = 1 if true_label == "malicious" else 0
    return {
        "event_id":            result.get("eid", raw.get("event_id", 0)),
        "is_admin":            int(raw.get("is_admin", False)),
        "src_is_dc":           src_is_dc,
        "dst_is_dc":           dst_is_dc,
        "dept_code":           _DEPT_CODE.get(dept, -1),
        "stealth_num":         _STEALTH_CODE.get(stealth, 1),
        "sigma_fired":         int(result.get("sigma_fired", False)),
        "sigma_count":         result.get("sigma_count", 0),
        "gnn_score":           round(float(result.get("gnn_score", 0.0)), 4),
        "gnn_flagged":         int(result.get("gnn_flagged", False)),
        "llm_verdict_num":     _VERDICT_CODE.get(llm_v, 1),
        "llm_confidence":      round(float(result.get("llm_confidence", 0.5)), 4),
        "ensemble_confidence": round(float(result.get("ensemble_confidence", 0.5)), 4),
        "label":               lnum,
        "attack_technique":    result.get("technique", raw.get("attack_technique", "")),
        "attacker":            result.get("attacker", raw.get("attacker", "")),
        "true_label_num":      lnum,
    }


class DatasetExporter:
    """
    Collects per-log DetectionResult rows across battles/campaigns.
    Exports as CSV, JSONL, and summary JSON.
    """

    def __init__(self):
        self.rows: list[dict] = []
        self.battles_included = 0

    # ── Ingest ────────────────────────────────────────────────────────────────

    def ingest_battle(self, battle_report):
        """
        Add all detection results from a BattleReport.
        Matches detection_results (serialised dicts) with raw attack logs where possible.
        """
        # Build host+attacker lookup from raw attack logs
        attack_lookup: dict[str, dict] = {}
        for l in battle_report.attacker_logs:
            key = f"{l.get('host','')}|{l.get('attacker','')}"
            attack_lookup[key] = l

        for r in battle_report.detection_results:
            key = f"{r.get('host','')}|{r.get('attacker','')}"
            raw = attack_lookup.get(key, {})
            row = _encode_row(r, raw)
            row["battle_id"] = battle_report.battle_id
            self.rows.append(row)

        self.battles_included += 1

    def ingest_campaign(self, campaign_record):
        """
        Ingest from a CampaignRecord.
        Uses the stored per-battle metric history to synthesise representative rows
        when raw DetectionResult objects are not available (serialised campaigns).
        """
        for i, (f1, p, r_val) in enumerate(zip(
                campaign_record.f1_history,
                campaign_record.precision_history,
                campaign_record.recall_history)):
            bid = (campaign_record.battle_ids[i]
                   if i < len(campaign_record.battle_ids) else f"battle_{i}")
            # Synthesise one malicious and one benign representative row per battle
            for lbl, sig, gnn in [(1, 1, 0.72), (0, 0, 0.38)]:
                self.rows.append({
                    "event_id": 4624 if lbl == 0 else 4662,
                    "is_admin": lbl, "src_is_dc": 0, "dst_is_dc": 0,
                    "dept_code": 0, "stealth_num": 1,
                    "sigma_fired": sig, "sigma_count": sig,
                    "gnn_score": gnn, "gnn_flagged": int(gnn > 0.55),
                    "llm_verdict_num": lbl * 2, "llm_confidence": round(p, 3),
                    "ensemble_confidence": round((p + r_val) / 2, 3),
                    "label": lbl, "attack_technique": "T1078" if lbl else "",
                    "attacker": "VIPER" if lbl else "", "true_label_num": lbl,
                    "battle_id": bid,
                })
        self.battles_included += campaign_record.battles_completed

    # ── Export ────────────────────────────────────────────────────────────────

    def export_csv(self, path: str = "data/datasets/nexus_logs.csv") -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        cols = ALL_COLUMNS + ["battle_id"]
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self.rows)
        print(f"[Dataset] CSV  → {path}  ({len(self.rows)} rows)")
        return path

    def export_jsonl(self, path: str = "data/datasets/nexus_logs.jsonl") -> str:
        """JSONL with natural-language prompts for LLM fine-tuning."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            for row in self.rows:
                technique = row.get("attack_technique", "none") or "none"
                verdict   = "malicious" if row["label"] == 1 else "benign"
                prompt = (
                    f"Analyze this Windows event: "
                    f"EventID={row['event_id']}, "
                    f"admin={bool(row['is_admin'])}, "
                    f"DC_host={bool(row['src_is_dc'])}, "
                    f"GNN_score={row['gnn_score']}, "
                    f"SIGMA_fired={bool(row['sigma_fired'])}, "
                    f"technique={technique}."
                )
                entry = {
                    "prompt":    prompt,
                    "label":     verdict,
                    "label_num": row["label"],
                    "features":  {k: row[k] for k in FEATURE_COLUMNS if k in row},
                    "metadata":  {
                        "attack_technique": technique,
                        "attacker":  row.get("attacker", ""),
                        "battle_id": row.get("battle_id", ""),
                    },
                }
                f.write(json.dumps(entry) + "\n")
        print(f"[Dataset] JSONL→ {path}  ({len(self.rows)} entries)")
        return path

    def export_summary(self, path: str = "data/datasets/nexus_summary.json") -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        stats = self.compute_stats()
        stats["generated_at"] = datetime.now(timezone.utc).isoformat()
        with open(path, "w") as f:
            json.dump(stats, f, indent=2)
        print(f"[Dataset] Summary→ {path}")
        return path

    def export_all(self, base_path: str = "data/datasets") -> dict:
        return {
            "csv":     self.export_csv(f"{base_path}/nexus_logs.csv"),
            "jsonl":   self.export_jsonl(f"{base_path}/nexus_logs.jsonl"),
            "summary": self.export_summary(f"{base_path}/nexus_summary.json"),
            "stats":   self.compute_stats(),
        }

    # ── Stats ─────────────────────────────────────────────────────────────────

    def compute_stats(self) -> dict:
        if not self.rows:
            return {}
        labels      = [r["label"] for r in self.rows]
        n_total     = len(labels)
        n_malicious = sum(labels)
        n_benign    = n_total - n_malicious
        techniques  = Counter(r["attack_technique"] for r in self.rows
                              if r.get("attack_technique") and r["label"] == 1)
        attackers   = Counter(r["attacker"] for r in self.rows
                              if r.get("attacker") and r["label"] == 1)
        gnn_scores  = [r["gnn_score"] for r in self.rows]
        sigmas      = [r["sigma_count"] for r in self.rows if r["sigma_fired"]]
        return {
            "total_rows":       n_total,
            "malicious":        n_malicious,
            "benign":           n_benign,
            "class_balance":    round(n_malicious / n_total, 3) if n_total else 0,
            "battles_included": self.battles_included,
            "technique_distribution": dict(techniques.most_common()),
            "attacker_distribution":  dict(attackers.most_common()),
            "gnn_score_stats": {
                "mean":  round(statistics.mean(gnn_scores), 4),
                "stdev": round(statistics.stdev(gnn_scores), 4) if len(gnn_scores)>1 else 0,
                "min":   round(min(gnn_scores), 4),
                "max":   round(max(gnn_scores), 4),
            },
            "avg_sigma_alerts_per_detection":
                round(statistics.mean(sigmas), 2) if sigmas else 0,
        }
