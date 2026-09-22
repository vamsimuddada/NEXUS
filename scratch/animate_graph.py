import codecs

with codecs.open('core/simulation.py', 'r', 'utf-8') as f:
    text = f.read()

# Add import time at the top
if "import time" not in text:
    text = text.replace("import uuid", "import uuid\nimport time")

# Inject the sleep at the end of the turn
target = """            report.detection_results.extend(
                [self._serialise_result(r) for r in results]
            )"""

injection = """            report.detection_results.extend(
                [self._serialise_result(r) for r in results]
            )
            
            # Slow down the simulation loop so the frontend graph animates live
            time.sleep(1.5)"""

text = text.replace(target, injection)

with codecs.open('core/simulation.py', 'w', 'utf-8') as f:
    f.write(text)
