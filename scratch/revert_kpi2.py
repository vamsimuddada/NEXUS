import codecs

with codecs.open('scratch/current_dash.py', 'r', 'utf-16') as f:
    orig = f.read()

orig_kpi_card = orig[orig.find('def kpi_card'):orig.find('c1, c2, c3, c4 = st.columns(4)')].strip()

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    dash = f.read()

dash_kpi_start = dash.find('def kpi_card')
dash_kpi_end = dash.find('with tab1:')

new_dash = dash[:dash_kpi_start] + orig_kpi_card + '\n\n' + dash[dash_kpi_end:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(new_dash)
