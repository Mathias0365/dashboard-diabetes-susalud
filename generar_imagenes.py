# -*- coding: utf-8 -*-
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
from PIL import Image, ImageDraw, ImageFont

CSV = r"C:\Users\Usuario\Desktop\CURSOS\CURSO LUNES\DASHBOARD_POWER_BI\datos_diabetes_dashboard.csv"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(CSV)
df["FECHA_PRESTACION"] = pd.to_datetime(df["FECHA_PRESTACION"])
df = df.sort_values("PERIODO")

COLORES = {
    "Masculino": "#1f77b4",
    "Femenino": "#e377c2",
    "TIPO 1": "#ff7f0e",
    "TIPO 2": "#2ca02c",
}

d = df
figs = {}

mensual = d.groupby("PERIODO", as_index=False).size().rename(columns={"size": "n"})
figs["g_mensual"] = px.line(mensual, x="PERIODO", y="n",
                            title="RQ1 - Evolucion mensual de atenciones", markers=True)

anio = d.groupby("AÑO_PRESTACION", as_index=False).size().rename(columns={"size": "n"})
figs["g_anio"] = px.bar(anio, x="AÑO_PRESTACION", y="n", text="n",
                        title="RQ5 - Flujo temporal (casos por año)",
                        color_discrete_sequence=["#0b3d91"])
figs["g_anio"].update_traces(textposition="outside")

es = d.groupby(["GRUPO_ETARIO", "SEXO_LABEL"], as_index=False).size().rename(columns={"size": "n"})
figs["g_edad_sexo"] = px.bar(es, x="GRUPO_ETARIO", y="n", color="SEXO_LABEL", barmode="stack",
                             title="RQ2 - Pacientes por grupo etario y sexo",
                             color_discrete_map=COLORES)

td = d["TIPO_DIABETES"].value_counts().reset_index()
td.columns = ["TIPO_DIABETES", "n"]
figs["g_tipo"] = px.pie(td, names="TIPO_DIABETES", values="n", hole=0.45,
                        title="RQ4 - Distribucion por tipo de diabetes",
                        color="TIPO_DIABETES", color_discrete_map=COLORES)

depg = d.groupby("DEPARTAMENTO", as_index=False).size().rename(columns={"size": "n"}).sort_values("n", ascending=False)
figs["g_dep"] = px.bar(depg.head(15), x="DEPARTAMENTO", y="n",
                       title="RQ3 - Casos por departamento (Top 15)",
                       color_discrete_sequence=["#ff7f0e"])

lab = d["REQUIERE_LABORATORIO"].value_counts().reset_index()
lab.columns = ["REQUIERE_LABORATORIO", "n"]
lab["LABEL"] = lab["REQUIERE_LABORATORIO"].map({1: "Si requiere", 0: "No requiere"})
figs["g_lab"] = px.bar(lab, x="LABEL", y="n", text="n",
                       title="RQ7 - Pacientes que requieren laboratorio",
                       color="LABEL",
                       color_discrete_map={"Si requiere": "#2ca02c", "No requiere": "#d62728"})
figs["g_lab"].update_traces(textposition="outside")
figs["g_lab"].update_layout(showlegend=False)

perf = (d.groupby(["GRUPO_ETARIO", "SEXO_LABEL", "TIPO_AFILIACION_DEL_PACIENTE",
                   "TIPO_COBERTURA", "DEPARTAMENTO"], as_index=False)["TOTAL_GASTOS_CUBIERTOS"]
        .mean().sort_values("TOTAL_GASTOS_CUBIERTOS", ascending=False).head(15))
perf["PERFIL"] = (perf["GRUPO_ETARIO"] + " / " + perf["SEXO_LABEL"] + " / " +
                  perf["TIPO_AFILIACION_DEL_PACIENTE"] + " / " + perf["TIPO_COBERTURA"] + " / " +
                  perf["DEPARTAMENTO"])
figs["g_perfil"] = px.bar(perf, x="PERFIL", y="TOTAL_GASTOS_CUBIERTOS",
                          title="RQ6 - Top 15 perfiles de pacientes segun gasto cubierto promedio",
                          color_discrete_sequence=["#2ca02c"])
figs["g_perfil"].update_layout(xaxis_tickangle=-45)

for name, fig in figs.items():
    fig.update_layout(template="plotly_white", font=dict(size=12),
                      paper_bgcolor="white", plot_bgcolor="#fbfbfb",
                      margin=dict(l=50, r=30, t=55, b=50))
    pio.write_image(fig, os.path.join(OUT, name + ".png"),
                    width=880, height=470, scale=2)
    print("generated", name)

def compone(paths, kpis=None, cols=3, cell_w=500, header_h=120, kpi_h=118, pad=20,
            bg="#f4f6f9", header_bg="#0b3d91",
            title="Dashboard - Casos de Diabetes en SUSALUD (2022-2026)"):
    rows = (len(paths) + cols - 1) // cols
    cell_h = int(cell_w * 470 / 880)
    kpis = kpis or []
    W = cols * cell_w + (cols + 1) * pad
    H = header_h + (kpi_h if kpis else 0) + rows * cell_h + (rows + 2) * pad
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    try:
        f_title = ImageFont.truetype("arialbd.ttf", 52)
        f_sub = ImageFont.truetype("arial.ttf", 26)
        f_kpi_lab = ImageFont.truetype("arial.ttf", 26)
        f_kpi_val = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        f_title = f_sub = f_kpi_lab = f_kpi_val = ImageFont.load_default()
    draw.rectangle([0, 0, W, header_h], fill=header_bg)
    draw.text((pad + 10, 16), title, font=f_title, fill="white")
    draw.text((pad + 10, header_h - 54), "Solucion de Inteligencia de Negocio - Escuela Zegel | Filtros: Anio, Departamento, Tipo, Sexo, Grupo etario",
              font=f_sub, fill=(220, 228, 240, 255))
    if kpis:
        card_w = (W - (len(kpis) + 1) * pad) // len(kpis)
        y0 = header_h + pad
        for i, (lab, val) in enumerate(kpis):
            x0 = pad + i * (card_w + pad)
            draw.rounded_rectangle([x0, y0, x0 + card_w, y0 + kpi_h], radius=14, fill="white")
            draw.rectangle([x0, y0 + kpi_h - 6, x0 + card_w, y0 + kpi_h], fill="#2ca02c")
            draw.text((x0 + 16, y0 + 12), lab, font=f_kpi_lab, fill="#666666")
            draw.text((x0 + 16, y0 + 46), val, font=f_kpi_val, fill="#0b3d91")
        grid_y = header_h + kpi_h + pad
    else:
        grid_y = header_h + pad
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB").resize((cell_w, cell_h), Image.LANCZOS)
        col = i % cols
        fila = i // cols
        x = pad + col * (cell_w + pad)
        y = grid_y + fila * (cell_h + pad)
        img.paste(im, (x, y))
    return img

paths = [os.path.join(OUT, "g_mensual.png"), os.path.join(OUT, "g_anio.png"),
         os.path.join(OUT, "g_edad_sexo.png"), os.path.join(OUT, "g_tipo.png"),
         os.path.join(OUT, "g_dep.png"), os.path.join(OUT, "g_lab.png"),
         os.path.join(OUT, "g_perfil.png")]

final = compone(paths, kpis=[
    ("Atenciones", "{:,}".format(len(df))),
    ("Gasto cubierto (S/)", "S/ {:,}".format(int(df["TOTAL_GASTOS_CUBIERTOS"].sum()))),
    ("Diabetes tipo 2", "{:.1f}%".format(df["TIPO_DIABETES"].eq("TIPO 2").mean() * 100)),
    ("Requiere laboratorio", "{:.1f}%".format(df["REQUIERE_LABORATORIO"].mean() * 100)),
], cell_w=620, pad=16)
outfile = os.path.join(OUT, "dashboard_panoramico.png")
final.save(outfile)
print("composed", outfile, final.size)
