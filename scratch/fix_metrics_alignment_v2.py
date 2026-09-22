import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

start_str = '# 4-Column Grid'
idx_start = text.find(start_str)
idx_end = text.find('<hr style=', idx_start)
idx_end = text.rfind('st.markdown', idx_start, idx_end)

if idx_start != -1 and idx_end != -1:
    new_grid = """# 4-Column Grid
                origin_val = profile.get('origin', 'Unknown')
                mot_val = profile.get('motivation', 'Unknown')
                target_val = ", ".join(profile.get('targets', ['Unknown']))
                soph_val = "VERY HIGH" if selected_apt in ["APT29", "APT28"] else "HIGH"
                
                grid_html = f'''
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; margin-top: 16px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px;">
                        <div style="font-family:'Inter', sans-serif; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 8px;">Origin</div>
                        <div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{origin_val}</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px;">
                        <div style="font-family:'Inter', sans-serif; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 8px;">Motivation</div>
                        <div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{mot_val}</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px;">
                        <div style="font-family:'Inter', sans-serif; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 8px;">Target Sector</div>
                        <div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{target_val}">{target_val}</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px;">
                        <div style="font-family:'Inter', sans-serif; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 8px;">Sophistication</div>
                        <div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #ef4444;">{soph_val}</div>
                    </div>
                </div>
                '''
                st.markdown(grid_html, unsafe_allow_html=True)
                
                """
    
    text = text[:idx_start] + new_grid + text[idx_end:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
