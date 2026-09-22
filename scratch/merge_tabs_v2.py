import codecs

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
    
    # We just need to replace `with tab2:` and the old h2 header.
    # The old h2 header is `    st.markdown("<h2 ... Threat Intelligence (TAXII)</h2>", unsafe_allow_html=True)`
    lines = threat_intel_code.split('\n')
    new_lines = []
    
    skip_next = False
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        if line.startswith('with tab2:'):
            new_lines.append('    st.markdown("<br><br><div class=\'hero-header\' style=\'font-size: 2.8rem; letter-spacing: -1px; margin-top: 16px;\'>Threat Intelligence</div>", unsafe_allow_html=True)')
            new_lines.append('    st.markdown("<p style=\\"font-family:\'Inter\', sans-serif; color:#64748b; margin-bottom:32px; font-size:1.1rem; font-weight:500;\\">Automated Dossier & Defense Playbook</p>", unsafe_allow_html=True)')
            
            # If the next line is the old H2 header, skip it!
            if i + 1 < len(lines) and 'Threat Intelligence (TAXII)' in lines[i+1]:
                skip_next = True
        else:
            new_lines.append(line)
                
    indented_threat_intel = '\n'.join(new_lines)
    
    text = text[:idx_tab2] + indented_threat_intel + text[idx_tab3:]
    
    # 3. Rename `with tab3:` to `with tab2:`
    text = text.replace('with tab3:', 'with tab2:')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
