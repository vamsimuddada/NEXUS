import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Change the default dropdown index to 1 (Ollama)
text = text.replace(
    'provider = st.selectbox("AI Brain", ["Mock (Instant/Offline)", "Ollama (Local AI)", "Gemini (Online AI)"], index=0)',
    'provider = st.selectbox("AI Brain", ["Mock (Instant/Offline)", "Ollama (Local AI)", "Gemini (Online AI)"], index=1)'
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
