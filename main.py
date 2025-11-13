from dash import Dash, html, dcc, Input, Output, State
from flask import send_from_directory
import os

# si ton app s'appelle `app`
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


app = Dash(__name__, title="Time Running Converter")

app.layout = html.Div(
    style={
        "fontFamily": "Segoe UI, sans-serif",
        "backgroundColor": "#f8f9fa",
        "minHeight": "100vh",
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "padding": "40px",
    },
    children=[
        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "30px 40px",
                "borderRadius": "20px",
                "boxShadow": "0 4px 15px rgba(0,0,0,0.1)",
                "width": "380px",
                "textAlign": "center",
                "boxSizing": "border-box",
            },
            children=[
                html.H2("🏃 Time Running Converter", style={"marginBottom": "25px"}),

                html.Label("Mode de calcul :", style={"fontWeight": "bold"}),
                dcc.RadioItems(
                    id="mode",
                    options=[
                        {"label": " Entrer un temps", "value": "t"},
                        {"label": " Entrer un rythme", "value": "r"},
                    ],
                    value="t",
                    inline=True,
                    style={"marginBottom": "20px"},
                ),

                html.Label("Distance (km) :", style={"display": "block", "fontWeight": "bold"}),
                dcc.Input(
                    id="distance",
                    type="number",
                    value=10,
                    step=0.001,
                    style={
                        "width": "100%",
                        "padding": "8px",
                        "borderRadius": "8px",
                        "border": "1px solid #ccc",
                        "marginBottom": "15px",
                        "boxSizing": "border-box",
                    },
                ),

                html.Label(
                    id="dynamic-label",
                    children="Temps total :",
                    style={"fontWeight": "bold"},
                ),

                html.Div(
                    [
                        dcc.Input(
                            id="hours",
                            type="number",
                            placeholder="h",
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "padding": "6px",
                                "borderRadius": "8px",
                                "border": "1px solid #ccc",
                                "textAlign": "center",
                                "boxSizing": "border-box",
                            },
                        ),
                        dcc.Input(
                            id="minutes",
                            type="number",
                            placeholder="min",
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "padding": "6px",
                                "borderRadius": "8px",
                                "border": "1px solid #ccc",
                                "textAlign": "center",
                                "boxSizing": "border-box",
                            },
                        ),
                        dcc.Input(
                            id="seconds",
                            type="number",
                            placeholder="s",
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "padding": "6px",
                                "borderRadius": "8px",
                                "border": "1px solid #ccc",
                                "textAlign": "center",
                                "boxSizing": "border-box",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "gap": "5px",
                        "marginBottom": "15px",
                        "width": "100%",
                        "boxSizing": "border-box",
                    },
                ),

                html.Button(
                    "Calculer",
                    id="btn",
                    n_clicks=0,
                    style={
                        "width": "100%",
                        "backgroundColor": "#007bff",
                        "color": "white",
                        "border": "none",
                        "padding": "10px",
                        "borderRadius": "8px",
                        "fontSize": "16px",
                        "cursor": "pointer",
                    },
                ),

                html.Hr(style={"margin": "25px 0"}),

                html.Div(
                    id="result",
                    style={
                        "fontSize": "18px",
                        "color": "#333",
                        "fontWeight": "bold",
                        "minHeight": "40px",
                        "lineHeight": "1.5",
                    },
                ),
            ],
        )
    ],
)


def compute(mode, distance, h, m, s):
    h, m, s = [int(x or 0) for x in (h, m, s)]
    total_minutes = h * 60 + m + s / 60
    if not distance or distance <= 0 or total_minutes == 0:
        return "⚠️ Erreur lors du remplissage des champs."

    if mode == "t":
        vitesse = distance / (total_minutes / 60)
        rythme = total_minutes / distance
        min_r, sec_r = int(rythme), int((rythme % 1) * 60)
        return html.Div([
            html.P(f"🏁 Vitesse moyenne : {vitesse:.3f} km/h", style={"margin": "5px 0"}),
            html.P(f"⏱️ Rythme : {min_r}:{sec_r:02d}/km", style={"margin": "5px 0"}),
        ])
    else:
        total_minutes *= distance
        vitesse = 60 / (h * 60 + m + s / 60)
        h_tot, m_tot = int(total_minutes // 60), int(total_minutes % 60)
        sec_tot = int((total_minutes - h_tot * 60 - m_tot) * 60)
        return html.Div([
            html.P(f"⏱️ Temps total : {h_tot}h{m_tot:02d}min{sec_tot:02d}s", style={"margin": "5px 0"}),
            html.P(f"🏁 Vitesse moyenne : {vitesse:.3f} km/h", style={"margin": "5px 0"}),
        ])


@app.callback(
    Output("result", "children"),
    Input("btn", "n_clicks"),
    State("mode", "value"),
    State("distance", "value"),
    State("hours", "value"),
    State("minutes", "value"),
    State("seconds", "value"),
)
def update_result(n, mode, distance, h, m, s):
    return compute(mode, distance, h, m, s) if n else ""


@app.callback(Output("dynamic-label", "children"), Input("mode", "value"))
def update_label(mode):
    return (
        "Temps total :"
        if mode == "t"
        else "Rythme (par km) — heures / minutes / secondes :"
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
