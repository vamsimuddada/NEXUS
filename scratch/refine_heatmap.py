import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

old_heatmap = """fig_heatmap = px.imshow(hm_pivot.values, 
                                        labels=dict(x="", y="", color="Events"),
                                        x=hm_pivot.columns, 
                                        y=hm_pivot.index, 
                                        color_continuous_scale="Blues", aspect="auto")
                fig_heatmap.update_layout(NEXUS_LAYOUT)
                fig_heatmap.update_layout(height=350, margin=dict(l=160, r=20, t=20, b=40))
                fig_heatmap.update_xaxes(title_text="")
                fig_heatmap.update_yaxes(title_text="")"""

new_heatmap = """fig_heatmap = px.imshow(hm_pivot.values, 
                                        labels=dict(x="", y="", color="Events"),
                                        x=hm_pivot.columns, 
                                        y=hm_pivot.index, 
                                        color_continuous_scale=[[0, "#f1f5f9"], [0.5, "#3b82f6"], [1.0, "#0f172a"]], 
                                        aspect="auto",
                                        text_auto=True)
                fig_heatmap.update_traces(xgap=4, ygap=4, textfont=dict(family="Inter", size=13, color="white"))
                fig_heatmap.update_layout(NEXUS_LAYOUT)
                fig_heatmap.update_layout(height=350, margin=dict(l=160, r=20, t=20, b=40))
                fig_heatmap.update_xaxes(title_text="", showgrid=False)
                fig_heatmap.update_yaxes(title_text="", showgrid=False)
                fig_heatmap.update_coloraxes(showscale=False)"""

text = text.replace(old_heatmap, new_heatmap)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
