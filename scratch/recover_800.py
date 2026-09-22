import json
import re
import codecs

with codecs.open('scratch/view_file_output.json', 'r', 'utf-8') as f:
    text = f.read()

d = json.loads(text)

def find_strings(obj):
    res = []
    if type(obj) == str:
        res.append(obj)
    elif type(obj) == dict:
        for v in obj.values():
            res.extend(find_strings(v))
    elif type(obj) == list:
        for item in obj:
            res.extend(find_strings(item))
    return res

lines = []
for s in find_strings(d):
    if '1: """' in s:
        for line in s.split('\n'):
            m = re.match(r'^\d+:\s(.*)', line)
            if m: lines.append(m.group(1))
            elif re.match(r'^\d+:$', line.strip()): lines.append('')
        
        with codecs.open('scratch/recovered_800_lines.py', 'w', 'utf-8') as out:
            out.write('\n'.join(lines))
        print(f'Recovered {len(lines)} lines!')
        break
