import streamlit as st
import streamlit.components.v1 as components

# This JS finds the tabs and forces them to track the scroll position!
components.html('''
<script>
    const parentDoc = window.parent.document;
    const tabContainer = parentDoc.querySelector('[data-testid="stTabs"] > div:first-child');
    const scrollContainer = parentDoc.querySelector('.main') || parentDoc.querySelector('.stApp');
    
    if (tabContainer && scrollContainer) {
        tabContainer.style.position = 'absolute';
        tabContainer.style.zIndex = '9999';
        
        scrollContainer.addEventListener('scroll', () => {
            tabContainer.style.top = scrollContainer.scrollTop + 'px';
        });
    }
</script>
''', height=0)
