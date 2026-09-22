import codecs

with codecs.open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# The error was caused by unescaped quotes in the generated python file.
# We'll just replace 'font-family:"Space Grotesk"' with 'font-family:\\'Space Grotesk\\''
code = code.replace('font-family:"Space Grotesk"', "font-family:\\'Space Grotesk\\'")
code = code.replace('font-family:\\"Space Grotesk\\"', "font-family:\\'Space Grotesk\\'")
code = code.replace('font-family:"Inter"', "font-family:\\'Inter\\'")

with codecs.open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
