import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_elo_chart(history_df: pd.DataFrame) -> go.Figure:
    """Creates a line chart for ELO history."""
    if history_df.empty:
        return px.line(title="ELO History (No Data)")
    
    if 'timestamp' in history_df.columns and 'elo_score' in history_df.columns and 'attacker_id' in history_df.columns:
        fig = px.line(history_df, x='timestamp', y='elo_score', color='attacker_id', title="Attacker ELO Over Time")
    else:
        fig = px.line(title="ELO History (Invalid Schema)")
    return fig

def create_detection_rate_chart(stats: pd.DataFrame) -> go.Figure:
    """Creates a bar chart for detection rates."""
    if stats.empty:
        return px.bar(title="Detection Rates (No Data)")
        
    if 'time_window' in stats.columns and 'detection_rate' in stats.columns:
        fig = px.bar(stats, x='time_window', y='detection_rate', title="Detection Rate over Time")
    else:
        fig = px.bar(title="Detection Rates")
    return fig

def create_technique_heatmap(technique_counts: pd.DataFrame) -> go.Figure:
    """Creates a bar chart for technique counts."""
    if technique_counts.empty:
        return px.bar(title="Technique Usage (No Data)")
        
    if 'technique' in technique_counts.columns and 'count' in technique_counts.columns:
        fig = px.bar(technique_counts, x='technique', y='count', title="Technique Usage Frequency")
    else:
        fig = px.bar(title="Technique Usage")
    return fig

def create_confusion_matrix(tp: int, fp: int, fn: int, tn: int) -> go.Figure:
    """Creates a 2x2 Plotly heatmap for a confusion matrix."""
    z = [[tn, fp], [fn, tp]]
    x = ['Predicted Benign', 'Predicted Malicious']
    y = ['Actual Benign', 'Actual Malicious']
    
    fig = px.imshow(z, x=x, y=y, text_auto=True, color_continuous_scale='Blues',
                    title="Detection Confusion Matrix", aspect="auto")
    return fig
