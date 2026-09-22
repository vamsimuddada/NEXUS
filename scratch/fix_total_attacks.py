import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix Total Attacks calculation
old_calc = """            f1_rows.append([f"Op {i+1}", f"{f1:.2f}", f"{p:.2f}", f"{r:.2f}", str(bdata.get("total_attacks", 0))])"""
new_calc = """            total_atk = len(bdata.get("attacker_logs", []))
            f1_rows.append([f"Op {i+1}", f"{f1:.2f}", f"{p:.2f}", f"{r:.2f}", str(total_atk)])"""

text = text.replace(old_calc, new_calc)

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
