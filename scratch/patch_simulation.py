import codecs
import re

with codecs.open('core/simulation.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Remove the old SIEM forward block
old_fwd = """                # Forward to SIEM
                try:
                    from integrations.siem_forwarder import get_forwarder
                    fwd = get_forwarder()
                    fwd.forward(log)
                except Exception:
                    pass"""
text = text.replace(old_fwd, "")

# 2. Inject the correct SIEM forward block after analyze_stream
target = """            tp_turn = sum(
                1 for r in results
                if r.ensemble_verdict == "malicious" and r.true_label == "malicious"
            )"""

new_fwd = """            try:
                from integrations.siem_forwarder import get_forwarder
                fwd = get_forwarder()
                attack_results = results[-len(turn_attack_logs):]
                for log, r in zip(turn_attack_logs, attack_results):
                    log["detected"] = (r.ensemble_verdict == "malicious")
                    fwd.forward(log)
            except Exception:
                pass

            tp_turn = sum(
                1 for r in results
                if r.ensemble_verdict == "malicious" and r.true_label == "malicious"
            )"""

text = text.replace(target, new_fwd)

with codecs.open('core/simulation.py', 'w', 'utf-8') as f:
    f.write(text)
