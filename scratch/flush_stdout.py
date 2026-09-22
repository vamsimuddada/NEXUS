import codecs

with codecs.open('core/simulation.py', 'r', 'utf-8') as f:
    text = f.read()

# Add sys.stdout.flush() to the _log method
old_log = """    def _log(self, msg: str):
        if self.verbose:
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
            print(f"[{ts}] {msg}")"""

new_log = """    def _log(self, msg: str):
        if self.verbose:
            import sys
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
            print(f"[{ts}] {msg}")
            sys.stdout.flush()"""

text = text.replace(old_log, new_log)

with codecs.open('core/simulation.py', 'w', 'utf-8') as f:
    f.write(text)
