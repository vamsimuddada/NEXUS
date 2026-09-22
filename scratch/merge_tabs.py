import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Update the tabs definition
text = text.replace(
    'tab1, tab2, tab3 = st.tabs(["SOC Overview", "Threat Intelligence", "Analytics & Export"])',
    'tab1, tab2 = st.tabs(["SOC Overview", "Analytics & Export"])'
)

# 2. Extract the Threat Intelligence block (from `with tab2:` to `with tab3:`)
idx_tab2 = text.find('with tab2:')
idx_tab3 = text.find('with tab3:')

if idx_tab2 != -1 and idx_tab3 != -1:
    threat_intel_code = text[idx_tab2:idx_tab3]
    
    # We want to insert this at the end of tab1
    # But wait, we can just replace `with tab2:` with a spacer inside tab1!
    # Because if we just change `with tab2:` to `    # Threat Intelligence Section`,
    # we need to INDENT all of `threat_intel_code` by 4 spaces!
    
    # Let's split the lines of threat_intel_code and indent them by 4 spaces, 
    # except the first line which we replace.
    lines = threat_intel_code.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('with tab2:'):
            new_lines.append('    st.markdown("<br><br><div class=\'hero-header\' style=\'font-size: 2.8rem; letter-spacing: -1px; margin-top: 16px;\'>Threat Intelligence</div>", unsafe_allow_html=True)')
            new_lines.append('    st.markdown("<p style=\\"font-family:\'Inter\', sans-serif; color:#64748b; margin-bottom:32px; font-size:1.1rem; font-weight:500;\\">Automated Dossier & Defense Playbook</p>", unsafe_allow_html=True)')
        else:
            if line.strip() == '':
                new_lines.append('')
            else:
                new_lines.append('    ' + line)
                
    indented_threat_intel = '\n'.join(new_lines)
    
    # Replace the old tab2 block with our new indented block
    text = text[:idx_tab2] + indented_threat_intel + text[idx_tab3:]
    
    # 3. Rename `with tab3:` to `with tab2:`
    text = text.replace('with tab3:', 'with tab2:')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
