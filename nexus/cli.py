import argparse
import sys
import json
from nexus.simulation import BattleEngine, ScenarioLoader, ResultsCollector
from nexus.utils import get_logger

logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="NEXUS Cybersecurity Simulation Platform CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # run-simulation
    run_parser = subparsers.add_parser("run-simulation", help="Run a new simulation")
    run_parser.add_argument("--rounds", type=int, default=20, help="Number of rounds to run")
    run_parser.add_argument("--scenario", type=str, default=None, help="Name of the scenario to load")
    run_parser.add_argument("--employees", type=int, default=100, help="Number of employees in environment")
    
    # list-scenarios
    subparsers.add_parser("list-scenarios", help="List available scenarios")
    
    # show-results
    results_parser = subparsers.add_parser("show-results", help="Show results for a simulation")
    results_parser.add_argument("--sim-id", type=str, required=True, help="Simulation ID")
    
    args = parser.parse_args()
    
    if args.command == "run-simulation":
        engine = BattleEngine()
        engine.setup_simulation(num_employees=args.employees)
        try:
            engine.run_simulation(num_rounds=args.rounds, scenario_name=args.scenario)
            print(engine.get_summary())
            print(f"To see detailed results, run: nexus show-results --sim-id {engine.sim_id}")
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            sys.exit(1)
            
    elif args.command == "list-scenarios":
        scenarios = ScenarioLoader.list_scenarios()
        print("Available Scenarios:")
        for name, details in scenarios.items():
            print(f" - {name}: {details.get('rounds')} rounds, Attackers: {', '.join(details.get('attackers', []))}")
            
    elif args.command == "show-results":
        collector = ResultsCollector()
        try:
            results = collector.get_simulation_results(args.sim_id)
            if not results:
                print(f"No results found for Simulation ID {args.sim_id}")
                return
            
            print(f"Results for {args.sim_id}:")
            print(f"Total events: {len(results)}")
            
            # basic breakdown
            event_types = {}
            for r in results:
                t = r.get('event_type')
                event_types[t] = event_types.get(t, 0) + 1
                
            print("\nEvent Breakdown:")
            for t, count in event_types.items():
                print(f" - {t}: {count}")
                
        except Exception as e:
            logger.error(f"Failed to fetch results: {e}")
            sys.exit(1)
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
