import codecs

with codecs.open('core/simulation.py', 'r', 'utf-8') as f:
    text = f.read()

# Make the terminal more active during the agent thinking phase
old_agent_loop = """            for agent in self.agents:
                log = agent.run_turn()
                turn_attack_logs.append(log)"""

new_agent_loop = """            for agent in self.agents:
                log = agent.run_turn()
                turn_attack_logs.append(log)
                self._log(f"  [{agent.name:8s}] Preparing attack on {log['host']:12s}...")"""

text = text.replace(old_agent_loop, new_agent_loop)

with codecs.open('core/simulation.py', 'w', 'utf-8') as f:
    f.write(text)
