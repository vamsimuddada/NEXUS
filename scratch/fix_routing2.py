with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Find the injected block at the bottom
start_idx = code.find('#  ABOUT PROJECT PAGE (ROUTING)')
if start_idx != -1:
    # go up to the previous newline or comment
    start_idx = code.rfind('\\n', 0, start_idx) - 80 # roughly the banner
    
    end_idx = code.find('st.stop()\\n', start_idx)
    if end_idx != -1:
        end_idx += len('st.stop()\\n')
    else:
        end_idx = len(code)
    
    about_block = code[start_idx:end_idx]
    
    # Remove from bottom
    code = code[:start_idx] + code[end_idx:]
    
    # Inject right after st.set_page_config
    target = 'initial_sidebar_state="expanded")'
    if target in code:
        code = code.replace(target, target + '\\n\\n' + about_block.strip() + '\\n')
    else:
        print("Could not find set_page_config")
    
    with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Moved routing to top.")
else:
    print("Could not find about block.")
