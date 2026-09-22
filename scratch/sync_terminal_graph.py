import codecs

with codecs.open('core/simulation.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Remove the attack logging from the first loop
old_agent_loop = """            for agent in self.agents:
                log = agent.run_turn()
                turn_attack_logs.append(log)
                self._log(
                    f"  [{agent.name:8s}] {log['attack_technique']} "
                    f"-> {log['host']:12s} stealth={log.get('stealth_level','?')}"
                )"""

# In my earlier inspection, it used a weird arrow char due to encoding, let's just use regex to remove it safely
import re
text = re.sub(
    r'for agent in self\.agents:\s+log = agent\.run_turn\(\)\s+turn_attack_logs\.append\(log\)\s+self\._log\([\s\S]*?stealth_level[^\)]+\)',
    r'for agent in self.agents:\n                log = agent.run_turn()\n                turn_attack_logs.append(log)',
    text
)

# 2. Inject the attack logging into the SIEM forwarder loop
old_fwd_loop = """                for log, r in zip(turn_attack_logs, attack_results):
                    log["detected"] = (r.ensemble_verdict == "malicious")
                    fwd.forward(log)
                    time.sleep(0.75)  # Pace the attacks out so the graph animates sequentially!"""

new_fwd_loop = """                for log, r in zip(turn_attack_logs, attack_results):
                    agent_name = log.get("attacker", "UNKNOWN")
                    tech = log.get("attack_technique", "Unknown")
                    host = log.get("host", "Unknown")
                    stealth = log.get("stealth_level", "?")
                    
                    # Log to terminal perfectly in sync with the graph update
                    self._log(f"  [{agent_name:8s}] {tech} -> {host:12s} stealth={stealth}")
                    
                    log["detected"] = (r.ensemble_verdict == "malicious")
                    fwd.forward(log)
                    time.sleep(0.85)  # Pace the attacks out so the graph animates sequentially!"""

text = text.replace(old_fwd_loop, new_fwd_loop)

with codecs.open('core/simulation.py', 'w', 'utf-8') as f:
    f.write(text)
