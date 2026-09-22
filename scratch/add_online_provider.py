import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Update the AI Brain dropdown to include Gemini
old_brain = 'provider = st.selectbox("AI Brain", ["Mock (Instant/Offline)", "Ollama (Live AI)"], index=0)'
new_brain = 'provider = st.selectbox("AI Brain", ["Mock (Instant/Offline)", "Ollama (Local AI)", "Gemini (Online AI)"], index=0)'
text = text.replace(old_brain, new_brain)

# 2. Add an API Key field if Gemini is selected
old_turns = 'turns = st.slider("Campaign Turns", 1, 10, 5)'
new_turns = """turns = st.slider("Campaign Turns", 1, 10, 5)
            api_key = ""
            if "Gemini" in provider:
                api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste free Google AI Studio key...")
"""
text = text.replace(old_turns, new_turns)

# 3. Update the provider string matching in the INITIATE WARGAMES button
old_prov = 'prov = "ollama" if "Ollama" in provider else "mock"'
new_prov = """if "Ollama" in provider: prov = "ollama"
                elif "Gemini" in provider: prov = "gemini"
                else: prov = "mock"
                
                if prov == "gemini" and not api_key and not os.environ.get("GEMINI_API_KEY"):
                    st.error("Missing Gemini API Key!")
                    st.stop()
                
                # Temporarily set environment variable for the subprocess if provided in UI
                if api_key:
                    os.environ["GEMINI_API_KEY"] = api_key"""
text = text.replace(old_prov, new_prov)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
