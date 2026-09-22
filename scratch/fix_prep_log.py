import codecs
import re

with codecs.open('core/simulation.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the Preparing attack log so it prints BEFORE the agent starts thinking, not after!
old_agent_loop = """            for agent in self.agents:
                log = agent.run_turn()
                turn_attack_logs.append(log)
                self._log(f"  [{agent.name:8s}] Preparing attack on {log['host']:12s}...")"""

new_agent_loop = """            for agent in self.agents:
                self._log(f"  [{agent.name:8s}] Synthesizing attack vectors...")
                log = agent.run_turn()
                turn_attack_logs.append(log)"""

text = text.replace(old_agent_loop, new_agent_loop)

with codecs.open('core/simulation.py', 'w', 'utf-8') as f:
    f.write(text)
