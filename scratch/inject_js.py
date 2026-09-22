with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

import_statement = "import streamlit.components.v1 as components"
if import_statement not in code:
    code = code.replace('import streamlit as st', 'import streamlit as st\n' + import_statement)

js_code = '''
# ------------------------------------------------------------------------------
#  JAVASCRIPT TABS SCROLL SYNC
# ------------------------------------------------------------------------------
components.html("""
<script>
    // Wait for the Streamlit DOM to fully render
    setTimeout(() => {
        const parentDoc = window.parent.document;
        // The container that Streamlit scrolls
        const scrollContainer = parentDoc.querySelector('.main') || parentDoc.querySelector('[data-testid="stMain"]');
        // The tabs container we want to float
        const tabContainer = parentDoc.querySelector('[data-testid="stTabs"] > div:first-child');
        
        if (scrollContainer && tabContainer) {
            tabContainer.style.position = 'relative';
            tabContainer.style.transition = 'transform 0.05s linear';
            
            // Sync the Y translation to the exact scroll position
            scrollContainer.addEventListener('scroll', () => {
                tabContainer.style.transform = 	ranslateY(px);
            });
        }
    }, 1000);
</script>
""", height=0, width=0)
'''

# inject right before st.set_page_config? No, components.html must be called after set_page_config.
# Inject right after st.set_page_config(...)
target = 'initial_sidebar_state="expanded",\n)'
code = code.replace(target, target + '\n' + js_code)

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Injected.")
