import marshal
import struct
import types
import dis

with open('scripts/__pycache__/dashboard.cpython-312.pyc', 'rb') as f:
    f.read(16) # Skip the magic number and timestamp
    code = marshal.load(f)

def extract_strings(c):
    strings = []
    for const in c.co_consts:
        if isinstance(const, str):
            if len(const) > 20: # Only get meaningful blocks
                strings.append(const)
        elif isinstance(const, types.CodeType):
            strings.extend(extract_strings(const))
    return strings

all_strings = extract_strings(code)

with open('scratch/extracted_strings.txt', 'w', encoding='utf-8') as out:
    for i, s in enumerate(all_strings):
        out.write(f"--- STRING {i} ---\n{s}\n\n")

print(f"Extracted {len(all_strings)} large strings!")
