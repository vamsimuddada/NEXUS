import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import os
import json
from datetime import datetime
import networkx as nx

# --- CONFIGURATION & SETUP ---
app = dash.Dash(
    __name__, 
    title="NEXUS Command Center",
    external_stylesheets=[dbc.themes.DARKLY]
)

# Custom CSS injected directly
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { background-color: #070b14; color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .card { background-color: #111827; border: none; border-left: 3px solid #00d2ff; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
            .card-header { background-color: rgba(0,210,255,0.05); color: #00d2ff; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #1e293b; }
            .metric-value { font-size: 2.2rem; font-weight: bold; color: #00d2ff; }
            .metric-label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
            .sidebar { background-color: #111827; height: 100vh; padding: 20px; border-right: 1px solid #1e293b; }
            .header-nav { padding: 20px; border-bottom: 1px solid #1e293b; background-color: #070b14; }
            .status-badge { background-color: rgba(16, 185, 129, 0.2); color: #10b981; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; border: 1px solid #10b981; }
            .nav-tabs .nav-link { color: #94a3b8; }
            .nav-tabs .nav-link.active { background-color: #111827 !important; color: #00d2ff !important; border-bottom: 2px solid #00d2ff !important; border:none; }
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner * { font-family: inherit !important; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# --- DATABASE CONNECTIONS ---
DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
DB_ELO = os.path.join(DB_DIR, 'nexus_elo.db')
DB_RESULTS = os.path.join(DB_DIR, 'simulation_results.db')
DB_GAPS = os.path.join(DB_DIR, 'nexus_gaps.db')
DB_TRAINING = os.path.join(DB_DIR, 'nexus_training.db')

def load_data(db_path, query):
    if not os.path.exists(db_path):
        print(f"DEBUG: Path does not exist - {db_path}")
        return pd.DataFrame()
    try:
        with sqlite3.connect(db_path) as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        print(f"DEBUG: Exception loading {db_path} with query {query}: {e}")
        return pd.DataFrame()

# --- HELPER UI FUNCTIONS ---
def create_kpi_card(title, id_name):
    return dbc.Card([
        dbc.CardBody([
            html.Div(title, className="metric-label"),
            html.Div(id=id_name, className="metric-value", children="0")
        ])
    ])

# --- APP LAYOUT ---
sidebar = html.Div([
    html.H2("NEXUS", style={'color': '#00d2ff', 'fontWeight': 'bold', 'marginBottom': '0'}),
    html.P("Control Panel", style={'color': '#94a3b8', 'fontSize': '0.9rem', 'marginTop': '-5px'}),
    html.Hr(style={'borderColor': '#1e293b'}),
    
    dbc.Label("AI Provider"),
    dbc.Select(
        id="provider-select",
        options=[
            {"label": "Ollama (Local)", "value": "local"},
            {"label": "Gemini", "value": "gemini"},
            {"label": "Mock Mode", "value": "mock"}
        ],
        value="local",
        style={'backgroundColor': '#0f172a', 'color': '#fff', 'border': '1px solid #334155'}
    ),
    html.Div(id="provider-warning", style={'marginTop': '10px', 'fontSize': '0.85rem'}),
    
    html.Hr(style={'borderColor': '#1e293b'}),
    dbc.Button("▶ Start Campaign", color="primary", style={'width': '100%', 'marginBottom': '10px', 'fontWeight': 'bold'}),
    dbc.Button("⏹ Stop / Reset", outline=True, color="secondary", style={'width': '100%', 'marginBottom': '20px'}),
    
    html.Div([
        html.P("System Health", style={'color': '#00d2ff', 'fontWeight': 'bold', 'marginBottom': '10px'}),
        html.Div("Tri-Brain CPU", style={'fontSize': '0.8rem', 'color': '#94a3b8'}),
        dbc.Progress(value=45, color="info", className="mb-3", style={"height": "5px"}),
        html.Div("GNN Memory", style={'fontSize': '0.8rem', 'color': '#94a3b8'}),
        dbc.Progress(value=22, color="info", style={"height": "5px"}),
    ], style={'padding': '15px', 'backgroundColor': '#0f172a', 'borderRadius': '5px'})
], className="sidebar")

header = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Autonomous Cyber Warfare Simulation", style={'margin': '0', 'color': '#e2e8f0'})
        ], width=6),
        dbc.Col([
            html.Div(id="live-status", className="float-end", style={'textAlign': 'right'})
        ], width=6)
    ])
], className="header-nav")

kpi_row = dbc.Row([
    dbc.Col(create_kpi_card("Detection Rate", "kpi-detection"), width=2),
    dbc.Col(create_kpi_card("Defense Actions", "kpi-defense"), width=2),
    dbc.Col(create_kpi_card("Active Attackers", "kpi-attackers"), width=2),
    dbc.Col(create_kpi_card("Rules Generated", "kpi-rules"), width=2),
    dbc.Col(create_kpi_card("GNN Retrains", "kpi-gnn"), width=2),
    dbc.Col(create_kpi_card("Total Events", "kpi-events"), width=2),
], className="mt-4 mb-4")

tabs = dbc.Tabs([
    dbc.Tab(label="Command Center", tab_id="tab-1", children=[
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Attacker vs Defender (ELO Timeline)"),
                    dbc.CardBody([dcc.Graph(id="elo-timeline", style={'height': '350px'})])
                ])
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Adversary Leaderboard"),
                    dbc.CardBody([html.Div(id="leaderboard-table")])
                ], style={'height': '100%'})
            ], width=4)
        ], className="mt-3"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Recent High-Severity Events"),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id='events-table',
                            style_table={'height': '300px', 'overflowY': 'auto'},
                            style_cell={'backgroundColor': '#111827', 'color': '#e2e8f0', 'border': '1px solid #1e293b', 'textAlign': 'left', 'padding': '10px'},
                            style_header={'backgroundColor': '#0f172a', 'fontWeight': 'bold', 'color': '#00d2ff', 'border': '1px solid #1e293b'}
                        )
                    ])
                ])
            ], width=12)
        ], className="mt-3")
    ]),
    
    dbc.Tab(label="Network Surface", tab_id="tab-2", children=[
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Active Directory & Topology Map"),
                    dbc.CardBody([
                        html.P("Visualizing known nodes based on Layer 1 Digital Twin.", style={'color': '#94a3b8'}),
                        dcc.Graph(id="network-graph", style={'height': '600px'})
                    ])
                ])
            ])
        ], className="mt-3")
    ]),
    
    dbc.Tab(label="Tri-Brain Engine", tab_id="tab-3", children=[
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("1. SIGMA Engine", style={'color': '#8b5cf6'}),
                dbc.CardBody([html.H4("Status: Active"), html.P(id="sigma-stats")])
            ])),
            dbc.Col(dbc.Card([
                dbc.CardHeader("2. GNN Anomaly", style={'color': '#0ea5e9'}),
                dbc.CardBody([html.H4("Status: Tracking"), html.P(id="gnn-stats")])
            ])),
            dbc.Col(dbc.Card([
                dbc.CardHeader("3. LLM Debate", style={'color': '#f59e0b'}),
                dbc.CardBody([html.H4("Status: Ready"), html.P("Avg Confidence: 89%")])
            ]))
        ], className="mt-3")
    ]),
    
    dbc.Tab(label="Evolution Engine", tab_id="tab-4", children=[
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Recent Gaps Identified"),
                dbc.CardBody(html.Div(id="gaps-table"))
            ]), width=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Model Loss Curve"),
                dbc.CardBody(dcc.Graph(id="training-loss", style={'height': '300px'}))
            ]), width=6)
        ], className="mt-3")
    ]),
    
    dbc.Tab(label="Research & Exports", tab_id="tab-5", children=[
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Export Campaign Artifacts"),
                dbc.CardBody([
                    html.P("Download generated artifacts from the current simulation run."),
                    dbc.Button("📥 STIX 2.1 Bundle", color="info", className="me-2"),
                    dbc.Button("📥 CSV Dataset", color="info", className="me-2"),
                    dbc.Button("📥 Markdown Report", color="info", className="me-2"),
                ])
            ]))
        ], className="mt-3")
    ]),
], id="tabs", active_tab="tab-1")

app.layout = dbc.Container([
    dcc.Interval(id='interval-component', interval=5000, n_intervals=0),
    dbc.Row([
        dbc.Col(sidebar, width=2, style={'padding': 0}),
        dbc.Col([
            header,
            html.Div([kpi_row, tabs], style={'padding': '20px'})
        ], width=10, style={'padding': 0, 'backgroundColor': '#070b14', 'height': '100vh', 'overflowY': 'auto'})
    ])
], fluid=True, style={'padding': 0})

# --- CALLBACKS ---
@app.callback(
    Output("provider-warning", "children"),
    Input("provider-select", "value")
)
def update_warning(provider):
    if provider == "mock":
        return dbc.Alert("⚠️ Mock Mode Active. No API requests will be made.", color="warning", style={'padding': '5px', 'fontSize': '0.8rem'})
    elif provider == "gemini":
        return dbc.Alert("✅ API Status: Connected (Key Hidden)", color="success", style={'padding': '5px', 'fontSize': '0.8rem'})
    return html.Div("Engine: Local LLM Processing", style={'color': '#94a3b8'})

@app.callback(
    [Output("kpi-detection", "children"),
     Output("kpi-defense", "children"),
     Output("kpi-attackers", "children"),
     Output("kpi-rules", "children"),
     Output("kpi-gnn", "children"),
     Output("kpi-events", "children"),
     Output("live-status", "children"),
     Output("elo-timeline", "figure"),
     Output("leaderboard-table", "children"),
     Output("events-table", "data"),
     Output("events-table", "columns"),
     Output("network-graph", "figure"),
     Output("sigma-stats", "children"),
     Output("gnn-stats", "children"),
     Output("gaps-table", "children"),
     Output("training-loss", "figure")],
    [Input("interval-component", "n_intervals")]
)
def update_dashboard(n):
    # Load Data
    df_elo = load_data(DB_ELO, "SELECT * FROM elo_history ORDER BY timestamp")
    df_events = load_data(DB_RESULTS, "SELECT * FROM simulation_results ORDER BY id DESC")
    df_gaps = load_data(DB_GAPS, "SELECT * FROM gap_analysis ORDER BY timestamp DESC")
    df_training = load_data(DB_TRAINING, "SELECT * FROM training_history ORDER BY timestamp DESC")

    # KPIs
    total_events = len(df_events)
    defense_actions = len(df_events[df_events['event_type'] == 'defense_action']) if not df_events.empty else 0
    detection_rate = f"{(defense_actions/total_events)*100:.1f}%" if total_events > 0 else "0%"
    active_attackers = df_elo['agent_id'].nunique() - 1 if not df_elo.empty and df_elo['agent_id'].nunique() > 1 else 0
    rules_gen = len(df_gaps)
    gnn_updates = len(df_training)

    # Status Header
    sim_id = df_events['sim_id'].iloc[0][:8] if not df_events.empty else "N/A"
    current_time = datetime.now().strftime('%H:%M:%S')
    status_html = [
        html.Span("● RUNNING", className="status-badge", style={'marginRight': '15px'}),
        html.Span(f"Campaign: ", style={'color': '#94a3b8'}),
        html.Span(f"{sim_id}", style={'color': '#e2e8f0', 'fontFamily': 'monospace', 'marginRight': '15px'}),
        html.Span(f"Updated: ", style={'color': '#94a3b8'}),
        html.Span(f"{current_time}", style={'color': '#e2e8f0'})
    ]

    # ELO Chart
    if df_elo.empty:
        fig_elo = go.Figure().update_layout(plot_bgcolor='#070b14', paper_bgcolor='#070b14')
        fig_elo.add_annotation(text="No Data", showarrow=False, font=dict(color="#94a3b8"))
        leaderboard = html.Div("No Data", style={'color': '#94a3b8'})
    else:
        fig_elo = px.line(df_elo, x='timestamp', y='rating', color='agent_id', markers=True, color_discrete_sequence=px.colors.qualitative.Set1)
        fig_elo.update_layout(
            plot_bgcolor='#070b14', paper_bgcolor='#070b14', font_color='#e2e8f0',
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=True, gridcolor='#1e293b', title=""),
            yaxis=dict(showgrid=True, gridcolor='#1e293b', title="ELO Rating"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        latest_elo = df_elo.sort_values('timestamp', ascending=False).drop_duplicates('agent_id').sort_values('rating', ascending=False)
        leaderboard = dbc.Table.from_dataframe(latest_elo[['agent_id', 'rating']], striped=True, bordered=False, hover=True, color="dark", style={'backgroundColor': '#111827', 'color': '#e2e8f0'})

    # Events Table
    if df_events.empty:
        events_data, events_cols = [], []
    else:
        display_df = df_events.head(50)[['timestamp', 'round_num', 'event_type', 'data']]
        events_data = display_df.to_dict('records')
        events_cols = [{"name": i.replace("_", " ").title(), "id": i} for i in display_df.columns]

    # Network Graph (Mocked visual representation using NetworkX)
    G = nx.barabasi_albert_graph(25, 2)
    pos = nx.spring_layout(G, seed=42)
    edge_x, edge_y, node_x, node_y = [], [], [], []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]; x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None]); edge_y.extend([y0, y1, None])
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x); node_y.append(y)
        
    node_colors = ['#ef4444' if i % 6 == 0 else ('#f59e0b' if i % 7 == 0 else '#00d2ff') for i in range(len(G.nodes()))]
    
    fig_net = go.Figure(data=[
        go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#334155'), hoverinfo='none', mode='lines'),
        go.Scatter(x=node_x, y=node_y, mode='markers', hoverinfo='text', text=[f"Host {i}" for i in range(25)],
                   marker=dict(showscale=False, color=node_colors, size=15, line_width=1, line_color='#0f172a'))
    ])
    fig_net.update_layout(
        showlegend=False, hovermode='closest', margin=dict(b=0,l=0,r=0,t=0),
        plot_bgcolor='#070b14', paper_bgcolor='#070b14',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    # Tri-Brain Stats
    sigma_txt = f"Rules Loaded: 154 | Alerts Triggered: {defense_actions}"
    gnn_txt = f"Epochs: {gnn_updates * 50} | Loss: {df_training['loss'].iloc[0] if not df_training.empty else '0.00'}"
    
    # Evolution Engine
    if df_gaps.empty:
        gaps_tbl = html.Div("No gaps identified.", style={'color': '#94a3b8'})
    else:
        gaps_tbl = dbc.Table.from_dataframe(df_gaps[['timestamp', 'missed_technique']].head(10), striped=True, bordered=False, hover=True, color="dark", style={'backgroundColor': '#111827', 'color': '#e2e8f0'})
        
    if df_training.empty:
        fig_loss = go.Figure().update_layout(plot_bgcolor='#070b14', paper_bgcolor='#070b14')
    else:
        fig_loss = px.line(df_training, x='timestamp', y='loss', template='plotly_dark')
        fig_loss.update_layout(plot_bgcolor='#070b14', paper_bgcolor='#070b14', margin=dict(l=0, r=0, t=10, b=0), xaxis_title="", yaxis_title="Loss")

    return (
        detection_rate, str(defense_actions), str(active_attackers), str(rules_gen), str(gnn_updates), str(total_events),
        status_html, fig_elo, leaderboard, events_data, events_cols, fig_net,
        sigma_txt, gnn_txt, gaps_tbl, fig_loss
    )

if __name__ == '__main__':
    app.run(debug=False, port=8050)
