# Dashboard - Casos de Diabetes en SUSALUD

Solución de Inteligencia de Negocio: dashboard interactivo (Plotly Dash) que analiza
las atenciones por diabetes en el sistema SUSALUD (2022-2026).

## Requisitos e instalación

Python 3.10 o superior.

```bash
pip install -r requirements.txt
```

## Cómo ejecutar el dashboard

```bash
python app.py
```

Luego abre en el navegador: **http://127.0.0.1:8050**

En Windows también puedes usar el lanzador `iniciar_dashboard.bat`.

> El repositorio incluye una muestra del dataset (`data/reporte_diabetes_muestra.xlsx`)
> para que pueda ejecutarse de forma reproducible. Los KPIs mostrados corresponden a
> esa muestra, no a la base completa.

## Estructura

- `app.py` — dashboard interactivo (Plotly Dash).
- `generar_imagenes.py` — regenera los gráficos estáticos de `img/`.
- `notebooks/` — análisis y modelamiento originales (EDA).
- `data/` — muestra de los datos de atenciones.
- `img/` — imagen panorámica del dashboard y gráficos estáticos.

## Preguntas de negocio (RQ)

1. ¿Cómo evoluciona la demanda/atenciones mes a mes?
2. ¿Qué perfil (edad y sexo) concentra los casos?
3. ¿En qué departamentos se concentran?
4. ¿Cuál es la distribución por tipo de diabetes (TIPO 1 / TIPO 2)?
5. ¿Cuál es el flujo temporal por año?
6. ¿Cuáles son los perfiles con mayor gasto cubierto promedio?
7. ¿Qué porcentaje de pacientes requiere laboratorio?
