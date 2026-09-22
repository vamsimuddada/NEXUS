#!/usr/bin/env python3
"""
NEXUS — Unified Runner (Phase 4)
Modes:
  (default)      Single battle
  --campaign     Multi-battle campaign + research outputs
  --bulk         N-simulation data collection run
  --research     Generate research outputs from saved campaign JSON
"""

import argparse, sys, os, io
# Force UTF-8 output on Windows (fixes UnicodeEncodeError for ✓ ✅ ⚔️ etc.)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv()


def run_single(args):
    from core.simulation import NEXUSSimulation
    print("=" * 62)
    print(f"  NEXUS — Single Battle  provider={args.provider}  turns={args.turns}")
    print("=" * 62)
    sim = NEXUSSimulation(
        num_users=args.users, num_hosts=args.hosts,
        llm_provider=args.provider, turns=args.turns,
        normal_logs_per_turn=args.normal, gnn_pretrain_logs=args.pretrain,
        seed=args.seed, verbose=True, evolve=True,
    )
    report = sim.run()
    if args.save:
        sim.save_report()
    m = report.metrics
    print(f"\n  Winner: {report.winner.upper()} | "
          f"F1={m['f1_score']} P={m['precision']} R={m['recall']}")


def run_campaign(args):
    from core.campaign import CampaignRunner
    print("=" * 62)
    print(f"  NEXUS — Campaign  battles={args.battles}  turns={args.turns}")
    print("=" * 62)
    CampaignRunner(
        n_battles=args.battles, turns_per_battle=args.turns,
        num_users=args.users, num_hosts=args.hosts,
        llm_provider=args.provider, normal_logs_per_turn=args.normal,
        gnn_pretrain_logs=args.pretrain, seed=args.seed,
        verbose=True, save_reports=args.save,
    ).run()


def run_bulk(args):
    from research.bulk_runner import BulkRunner
    print("=" * 62)
    print(f"  NEXUS — Bulk Run  n={args.bulk_n}  turns={args.turns}")
    print("=" * 62)
    BulkRunner(
        n_sims=args.bulk_n, turns=args.turns,
        num_users=args.users, num_hosts=args.hosts,
        llm_provider=args.provider,
        normal_per_turn=args.normal,
        gnn_pretrain=args.pretrain,
        resume=True,
    ).run()


def run_research(args):
    """Generate research outputs from a saved campaign JSON."""
    import json
    if not args.campaign_file:
        print("ERROR: --research requires --campaign-file <path>")
        sys.exit(1)
    with open(args.campaign_file) as f:
        data = json.load(f)

    # Reconstruct minimal record object
    class Rec:
        def __init__(self, d):
            self.__dict__.update(d)
    record = Rec(data)

    from research.stix_generator import STIXBundleGenerator
    from research.dataset_exporter import DatasetExporter
    from research.paper_generator import PaperSectionGenerator

    cid = record.campaign_id
    print(f"[Research] Generating outputs for campaign {cid} …")

    gen = STIXBundleGenerator()
    bundle = gen.from_campaign(record)
    gen.save(bundle, f"data/stix/campaign_{cid}.json")
    print(f"  STIX objects: {gen.object_count(bundle)}")

    exporter = DatasetExporter()
    exporter.ingest_campaign(record)
    result = exporter.export_all(f"data/datasets/{cid}")
    print(f"  Dataset stats: {result['stats']}")

    paper_gen = PaperSectionGenerator(provider=args.provider)
    path = paper_gen.generate_paper(record, f"data/research/paper_{cid}.md")
    print(f"  Paper draft: {path}")


def main():
    p = argparse.ArgumentParser(description="NEXUS Unified Runner")
    p.add_argument("--campaign",       action="store_true")
    p.add_argument("--bulk",           action="store_true")
    p.add_argument("--research",       action="store_true")
    p.add_argument("--campaign-file",  type=str, default="")
    p.add_argument("--battles",        type=int, default=3)
    p.add_argument("--bulk-n",         type=int, default=20,
                   help="Number of sims for bulk run (default 20, paper uses 100)")
    p.add_argument("--turns",          type=int, default=8)
    p.add_argument("--users",          type=int, default=40)
    p.add_argument("--hosts",          type=int, default=12)
    p.add_argument("--normal",         type=int, default=20)
    p.add_argument("--pretrain",       type=int, default=200)
    p.add_argument("--provider",       type=str, default="mock",
                   choices=["mock", "ollama", "gemini", "anthropic", "openai"])
    p.add_argument("--seed",           type=int, default=42)
    p.add_argument("--save",           action="store_true")
    args = p.parse_args()

    if args.bulk:
        run_bulk(args)
    elif args.campaign:
        if not args.save:
            args.save = True   # campaign always saves for research outputs
        run_campaign(args)
    elif args.research:
        run_research(args)
    else:
        run_single(args)


if __name__ == "__main__":
    main()
