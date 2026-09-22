import codecs
import re

with codecs.open('core/simulation.py', 'r', 'utf-8') as f:
    text = f.read()

# Remove the old time.sleep(1.5) at the end of the turn
text = text.replace("            # Slow down the simulation loop so the frontend graph animates live\n            time.sleep(1.5)", "")

# Put a time.sleep(0.5) INSIDE the SIEM forward loop so each attack line draws one by one!
target_loop = """                for log, r in zip(turn_attack_logs, attack_results):
                    log["detected"] = (r.ensemble_verdict == "malicious")
                    fwd.forward(log)"""

new_loop = """                for log, r in zip(turn_attack_logs, attack_results):
                    log["detected"] = (r.ensemble_verdict == "malicious")
                    fwd.forward(log)
                    time.sleep(0.75)  # Pace the attacks out so the graph animates sequentially!"""

text = text.replace(target_loop, new_loop)

with codecs.open('core/simulation.py', 'w', 'utf-8') as f:
    f.write(text)
