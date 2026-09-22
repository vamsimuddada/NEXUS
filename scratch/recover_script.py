import re
import codecs

lines = []
with codecs.open("scratch/original.txt", "r", "utf-8") as f:
    for line in f:
        # Match lines like "123: code" or "123: "
        m = re.match(r"^\d+:\s?(.*)", line)
        if m:
            lines.append(m.group(1))

with codecs.open("scratch/recovered_part1.py", "w", "utf-8") as out:
    out.write("\n".join(lines))
    print(f"Recovered {len(lines)} lines from original.txt!")
