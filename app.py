# -*- coding: utf-8 -*-
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

CSV = r"C:\Users\Usuario\Desktop\CURSOS\CURSO LUNES\DASHBOARD_POWER_BI\datos_diabetes_dashboard.csv"

df = pd.read_csv(CSV)
df["FECHA_PRESTACION"] = pd.to_datetime(df["FECHA_PRESTACION"])
df = df.sort_values("PERIODO")

COLORES = {
    "Masculino": "#1f77b4",
    "Femenino": "#e377c2",
    "TIPO 1": "#ff7f0e",
    "TIPO 2": "#2ca02c",
}

app = Dash(__name__)
app.title = "Dashboard - Casos de Diabetes SUSALUD"

app.layout = html.Div(
    style={
        "fontFamily": "Segoe UI, Arial, sans-serif",
        "margin": "0",
        "padding": "0",
        "backgroundColor": "#f4f6f9",
    },
    children=[
        html.Div(
            style={
                "backgroundColor": "#0b3d91",
                "color": "white",
                "padding": "18px 28px",
            },
            children=[
                html.H2("Dashboard - Casos de Diabetes en SUSALUD (2022-2026)",
                        style={"margin": "0"}),
                html.P("Solución de Inteligencia de Negocio - Escuela Zegel",
                       style={"margin": "4px 0 0", "opacity": "0.85"}),
            ],
        ),
        html.Div(
            style={
                "display": "flex",
                "gap": "18px",
                "flexWrap": "wrap",
                "padding": "18px 28px",
                "backgroundColor": "white",
                "borderBottom": "1px solid #ddd",
            },
            children=[
                html.Div([html.Label("Año"), dcc.Dropdown(
                    id="dd_anio", options=[{"label": str(a), "value": a} for a in sorted(df["AÑO_PRESTACION"].unique())],
                    multi=True, placeholder="Todos",
                    style={"minWidth": "140px"})]),
                html.Div([html.Label("Departamento"), dcc.Dropdown(
                    id="dd_dep", options=[{"label": d, "value": d} for d in sorted(df["DEPARTAMENTO"].dropna().unique())],
                    multi=True, placeholder="Todos",
                    style={"minWidth": "180px"})]),
                html.Div([html.Label("Tipo de diabetes"), dcc.Dropdown(
                    id="dd_tipo", options=[{"label": t, "value": t} for t in df["TIPO_DIABETES"].unique()],
                    multi=True, placeholder="Todos",
                    style={"minWidth": "150px"})]),
                html.Div([html.Label("Sexo"), dcc.Dropdown(
                    id="dd_sexo", options=[{"label": s, "value": s} for s in ["Masculino", "Femenino"]],
                    multi=True, placeholder="Todos",
                    style={"minWidth": "140px"})]),
                html.Div([html.Label("Grupo etario"), dcc.Dropdown(
                    id="dd_edad", options=[{"label": g, "value": g} for g in ["<18", "18-35", "36-50", "51-65", ">65"]],
                    multi=True, placeholder="Todos",
                    style={"minWidth": "140px"})]),
            ],
        ),
        html.Div(id="cards", style={
            "display": "flex", "gap": "16px", "flexWrap": "wrap", "padding": "18px 28px",
        }),
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(2, 1fr)",
                "gap": "16px",
                "padding": "0 28px 24px",
            },
            children=[
                dcc.Graph(id="g_mensual"),
                dcc.Graph(id="g_anio"),
                dcc.Graph(id="g_edad_sexo"),
                dcc.Graph(id="g_tipo"),
                dcc.Graph(id="g_dep"),
                dcc.Graph(id="g_lab"),
                dcc.Graph(id="g_perfil", style={"gridColumn": "span 2"}),
            ],
        ),
    ],
)


def filtrar(anio, dep, tipo, sexo, edad):
    d = df
    if anio:
        d = d[d["AÑO_PRESTACION"].isin(anio)]
    if dep:
        d = d[d["DEPARTAMENTO"].isin(dep)]
    if tipo:
        d = d[d["TIPO_DIABETES"].isin(tipo)]
    if sexo:
        d = d[d["SEXO_LABEL"].isin(sexo)]
    if edad:
        d = d[d["GRUPO_ETARIO"].isin(edad)]
    return d


@app.callback(
    Output("cards", "children"),
    [Input("dd_anio", "value"), Input("dd_dep", "value"),
     Input("dd_tipo", "value"), Input("dd_sexo", "value"),
     Input("dd_edad", "value")],
)
def update_cards(anio, dep, tipo, sexo, edad):
    d = filtrar(anio, dep, tipo, sexo, edad)
    total = len(d)
    gasto = d["TOTAL_GASTOS_CUBIERTOS"].sum()
    pct2 = d["TIPO_DIABETES"].eq("TIPO 2").mean() * 100
    pctlab = d["REQUIERE_LABORATORIO"].mean() * 100
    return [
        tarjeta("Atenciones", f"{total:,}"),
        tarjeta("Gasto cubierto (S/)", f"{gasto:,.0f}"),
        tarjeta("Diabetes tipo 2", f"{pct2:.1f}%"),
        tarjeta("Requiere laboratorio", f"{pctlab:.1f}%"),
    ]


def tarjeta(titulo, valor):
    return html.Div(
        style={
            "flex": "1", "minWidth": "180px", "backgroundColor": "white",
            "borderRadius": "10px", "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,.1)",
        },
        children=[
            html.Div(titulo, style={"color": "#666", "fontSize": "13px"}),
            html.Div(valor, style={"fontSize": "26px", "fontWeight": "700", "color": "#0b3d91"}),
        ],
    )


@app.callback(
    Output("g_mensual", "figure"), Output("g_anio", "figure"),
    Output("g_edad_sexo", "figure"), Output("g_tipo", "figure"),
    Output("g_dep", "figure"), Output("g_lab", "figure"),
    Output("g_perfil", "figure"),
    [Input("dd_anio", "value"), Input("dd_dep", "value"),
     Input("dd_tipo", "value"), Input("dd_sexo", "value"),
     Input("dd_edad", "value")],
)
def update_graficos(anio, dep, tipo, sexo, edad):
    d = filtrar(anio, dep, tipo, sexo, edad)
    vacio = d.empty

    if vacio:
        return tuple([fig_vacio(t) for t in
                      ["Evolución mensual", "Flujo anual", "Edad y sexo",
                       "Tipo de diabetes", "Casos por departamento",
                       "Laboratorio", "Top perfiles por gasto"]])

    mensual = d.groupby("PERIODO", as_index=False).size().rename(columns={"size": "n"})
    f_mensual = px.line(mensual, x="PERIODO", y="n",
                        title="RQ1 - Evolución mensual de atenciones",
                        markers=True)
    f_mensual.update_layout(paper_bgcolor="white", plot_bgcolor="#fbfbfb")

    anio = d.groupby("AÑO_PRESTACION", as_index=False).size().rename(columns={"size": "n"})
    f_anio = px.bar(anio, x="AÑO_PRESTACION", y="n", text="n",
                    title="RQ5 - Flujo temporal (casos por año)", color_discrete_sequence=["#0b3d91"])
    f_anio.update_traces(textposition="outside")
    f_anio.update_layout(paper_bgcolor="white", plot_bgcolor="#fbfbfb")

    es = d.groupby(["GRUPO_ETARIO", "SEXO_LABEL"], as_index=False).size().rename(columns={"size": "n"})
    f_es = px.bar(es, x="GRUPO_ETARIO", y="n", color="SEXO_LABEL", barmode="stack",
                  title="RQ2 - Pacientes por grupo etario y sexo",
                  color_discrete_map=COLORES)
    f_es.update_layout(paper_bgcolor="white", plot_bgcolor="#fbfbfb")

    td = d["TIPO_DIABETES"].value_counts().reset_index()
    td.columns = ["TIPO_DIABETES", "n"]
    f_td = px.pie(td, names="TIPO_DIABETES", values="n", hole=0.45,
                  title="RQ4 - Distribución por tipo de diabetes",
                  color="TIPO_DIABETES", color_discrete_map=COLORES)
    f_td.update_layout(paper_bgcolor="white")

    depg = d.groupby("DEPARTAMENTO", as_index=False).size().rename(columns={"size": "n"}).sort_values("n", ascending=False)
    f_dep = px.bar(depg.head(15), x="DEPARTAMENTO", y="n",
                   title="RQ3 - Casos por departamento (Top 15)",
                   color_discrete_sequence=["#ff7f0e"])
    f_dep.update_layout(paper_bgcolor="white", plot_bgcolor="#fbfbfb")

    lab = d["REQUIERE_LABORATORIO"].value_counts().reset_index()
    lab.columns = ["REQUIERE_LABORATORIO", "n"]
    lab["LABEL"] = lab["REQUIERE_LABORATORIO"].map({1: "Sí requiere", 0: "No requiere"})
    f_lab = px.bar(lab, x="LABEL", y="n", text="n",
                   title="RQ7 - Pacientes que requieren laboratorio",
                   color="LABEL",
                   color_discrete_map={"Sí requiere": "#2ca02c", "No requiere": "#d62728"})
    f_lab.update_traces(textposition="outside")
    f_lab.update_layout(paper_bgcolor="white", plot_bgcolor="#fbfbfb", showlegend=False)

    perf = (d.groupby(["GRUPO_ETARIO", "SEXO_LABEL", "TIPO_AFILIACION_DEL_PACIENTE",
                       "TIPO_COBERTURA", "DEPARTAMENTO"], as_index=False)["TOTAL_GASTOS_CUBIERTOS"]
            .mean().sort_values("TOTAL_GASTOS_CUBIERTOS", ascending=False).head(15))
    perf["PERFIL"] = (perf["GRUPO_ETARIO"] + " / " + perf["SEXO_LABEL"] + " / " +
                      perf["TIPO_AFILIACION_DEL_PACIENTE"] + " / " + perf["TIPO_COBERTURA"] + " / " +
                      perf["DEPARTAMENTO"])
    f_perf = px.bar(perf, x="PERFIL", y="TOTAL_GASTOS_CUBIERTOS",
                    title="RQ6 - Top 15 perfiles de pacientes según gasto cubierto promedio",
                    color_discrete_sequence=["#2ca02c"])
    f_perf.update_layout(paper_bgcolor="white", plot_bgcolor="#fbfbfb", xaxis_tickangle=-45)

    return f_mensual, f_anio, f_es, f_td, f_dep, f_lab, f_perf


def fig_vacio(titulo):
    return px.scatter(title=titulo).update_layout(
        annotations=[dict(text="Sin datos con los filtros seleccionados", showarrow=False)],
        paper_bgcolor="white")


if __name__ == "__main__":
    app.run(debug=True, port=8050)
