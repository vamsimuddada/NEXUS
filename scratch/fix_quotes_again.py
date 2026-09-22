import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('st.markdown("<p style="font-family:\'Inter\', sans-serif; color:#475569; line-height:1.6;\'>Powered by intelligent agents', 'st.markdown("<p style=\'font-family:\\\'Inter\\\', sans-serif; color:#475569; line-height:1.6;\'>Powered by intelligent agents')
text = text.replace('st.markdown("<p style="font-family:\'Inter\', sans-serif; color:#475569; line-height:1.6;\'>The Blue Team monitors', 'st.markdown("<p style=\'font-family:\\\'Inter\\\', sans-serif; color:#475569; line-height:1.6;\'>The Blue Team monitors')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
