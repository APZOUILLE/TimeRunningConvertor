from dash import Dash, html, dcc, Input, Output, State
import re

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
                "padding": "30px 50px",
                "borderRadius": "20px",
                "boxShadow": "0 4px 15px rgba(0,0,0,0.1)",
                "width": "400px",
                "textAlign": "center",
            },
            children=[
                html.H2("🏃 Time Running Converter",
                        style={"marginBottom": "25px"}),

                html.Label("Mode de calcul :"),
                dcc.RadioItems(
                    id='mode',
                    options=[
                        {'label': ' Entrer un temps', 'value': 't'},
                        {'label': ' Entrer un rythme', 'value': 'r'}
                    ],
                    value='t',
                    inline=True,
                    style={"marginBottom": "20px"}
                ),

                html.Label("Distance (km) :", style={"display": "block"}),
                dcc.Input(
                    id='distance',
                    type='number',
                    value=10,
                    step=0.001,
                    style={
                        "width": "100%",
                        "padding": "8px",
                        "borderRadius": "8px",
                        "border": "1px solid #ccc",
                        "marginBottom": "15px"
                    }
                ),

                html.Label(id='dynamic-label', children="Temps (ex: 45min ou 1h30) :"),
                dcc.Input(
                    id='dynamic-input',
                    type='text',
                    placeholder="ex: 45min ou 1h30",
                    style={
                        "width": "100%",
                        "padding": "8px",
                        "borderRadius": "8px",
                        "border": "1px solid #ccc",
                        "marginBottom": "15px"
                    }
                ),

                html.Button(
                    'Calculer',
                    id='btn',
                    n_clicks=0,
                    style={
                        "width": "100%",
                        "backgroundColor": "#007bff",
                        "color": "white",
                        "border": "none",
                        "padding": "10px",
                        "borderRadius": "8px",
                        "fontSize": "16px",
                        "cursor": "pointer"
                    }
                ),

                html.Hr(style={"margin": "25px 0"}),

                html.Div(id='result', style={
                    "fontSize": "18px",
                    "color": "#333",
                    "fontWeight": "bold",
                    "minHeight": "40px"
                })
            ]
        )
    ]
)


# === Mise à jour du label et placeholder selon le mode ===
@app.callback(
    Output('dynamic-label', 'children'),
    Output('dynamic-input', 'placeholder'),
    Input('mode', 'value')
)
def update_label_placeholder(mode):
    if mode == 't':
        return "Temps (ex: 45min ou 1h30) :", "ex: 45min ou 1h30"
    else:
        return "Rythme (ex: 5:30 ou 6min20) :", "ex: 5:30 ou 6min20"


# === Calcul principal ===
@app.callback(
    Output('result', 'children'),
    Input('btn', 'n_clicks'),
    State('mode', 'value'),
    State('distance', 'value'),
    State('dynamic-input', 'value')
)
def compute(n, mode, distance, value):
    if not n:
        return ""
    if not value or not distance:
        return "⚠️ Merci de remplir tous les champs."

    try:
        if mode == 't':  # --- Cas : on entre un temps ---
            s = value.lower().replace(" ", "")
            total_minutes = 0
            if "h" in s:
                parts = s.split("h")
                h = int(parts[0])
                m = int(re.findall(r'\d+', parts[1])[0]) if len(parts) > 1 and re.findall(r'\d+', parts[1]) else 0
                total_minutes = h * 60 + m
            elif ":" in s:
                h, m = s.split(":")
                total_minutes = int(h) * 60 + int(m)
            else:
                nums = re.findall(r'\d+', s)
                total_minutes = int(nums[0]) if nums else 0

            vitesse = distance / (total_minutes / 60)
            rythme = total_minutes / distance
            min_r = int(rythme)
            sec_r = int((rythme - min_r) * 60)
            return html.Div([
                html.P(f"🏁 Vitesse moyenne : {vitesse:.3f} km/h", style={"margin": "5px 0"}),
                html.P(f"⏱️ Rythme : {min_r}:{sec_r:02d}/km", style={"margin": "5px 0"})
            ])

        elif mode == 'r':  # --- Cas : on entre un rythme ---
            s = value.lower().replace(" ", "")

            def parse_rythme(s: str) -> float:
                """Convertit un rythme sous diverses formes en minutes/km"""
                import re
                h = m = sec = 0

                # Cas 1 : format 1:23:45 ou 5:30
                if ":" in s:
                    parts = list(map(int, s.split(":")))
                    if len(parts) == 3:
                        h, m, sec = parts
                    elif len(parts) == 2:
                        m, sec = parts
                    elif len(parts) == 1:
                        m = parts[0]

                # Cas 2 : format texte (ex: 1h30min20s)
                elif any(x in s for x in ["h", "m", "s"]):
                    if "h" in s:
                        h = int(re.findall(r"(\d+)h", s)[0])
                    if "m" in s:
                        m = int(re.findall(r"(\d+)m", s)[0])
                    if "s" in s:
                        sec = int(re.findall(r"(\d+)s", s)[0])

                # Cas 3 : juste un nombre → minutes
                else:
                    nums = re.findall(r'\d+', s)
                    if nums:
                        m = int(nums[0])
                        if len(nums) > 1:
                            sec = int(nums[1])

                # Conversion en minutes/km
                return h * 60 + m + sec / 60

            # --- Utilisation ---
            rythme = parse_rythme(s)

            total_minutes = rythme * distance
            h = int(total_minutes // 60)
            m = int(total_minutes % 60)
            sec = int((total_minutes - h * 60 - m) * 60)
            vitesse = 60 / rythme

            return html.Div([
                html.P(f"⏱️ Temps total : {h}h{m:02d}min{sec:02d}s", style={"margin": "5px 0"}),
                html.P(f"🏁 Vitesse moyenne : {vitesse:.3f} km/h", style={"margin": "5px 0"})
            ])

    except Exception as e:
        return f"Erreur de saisie : {e}"


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port)
