with open('.streamlit/config.toml', 'w', encoding='utf-8') as f:
    f.write('''[theme]
base="light"
primaryColor="#1a73e8"
backgroundColor="#f8f9fa"
secondaryBackgroundColor="#ffffff"
textColor="#202124"
font="sans serif"
''')
