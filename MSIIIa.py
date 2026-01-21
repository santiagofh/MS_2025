# %%
# %%
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Leer los datos
df_ms = pd.read_csv('MS2025_v2.csv')
col_est = ['Código Vigente', 'Nombre Oficial', 'Nombre Dependencia Jerárquica (SEREMI / Servicio de Salud)', 'Nombre Comuna']
col_rename = {
    'Código Vigente': 'IdEstablecimiento',
    'Nombre Oficial': 'nombre_establecimiento',
    'Nombre Dependencia Jerárquica (SEREMI / Servicio de Salud)': 'servicio_salud',
    'Nombre Comuna': 'comuna'
}
df_est = pd.read_excel('Establecimientos DEIS MINSAL 28-05-2024 (1).xlsx', skiprows=1, usecols=col_est)
df_est = df_est.rename(columns=col_rename)
df_ms3a = df_ms.loc[df_ms.MetaSanitaria == 'MSIIIa']
df_ms3a = df_ms3a.merge(df_est, on='IdEstablecimiento', how='left')

# Preparar los datos
# df_ms3a = df_ms3a.fillna(subset=['Ano', 'Mes'])
# df_ms3a['Ano'] = df_ms3a['Ano'].astype(int)
# df_ms3a['Mes'] = df_ms3a['Mes'].astype(int)
df_ms3a['Porcentaje'] = df_ms3a['Numerador'] / df_ms3a['Denominador']
df_ms3a['IdEstablecimiento'] = df_ms3a['IdEstablecimiento'].astype(str)
df_ms3a['nombre_establecimiento'] = df_ms3a['nombre_establecimiento'].astype(str)
df_ms3a = df_ms3a.dropna(subset=["servicio_salud", "comuna"])
df_ms3a["servicio_salud"] = df_ms3a["servicio_salud"].fillna("No especificado").astype(str)
df_ms3a["comuna"] = df_ms3a["comuna"].fillna("No especificado").astype(str)
df_ms3a['codigo_nombre'] = df_ms3a['IdEstablecimiento'] + ' - ' + df_ms3a['nombre_establecimiento']
# Agrupar por IdEstablecimiento, sumar Numerador y calcular promedio de Denominador
df_ms3a = df_ms3a.groupby('IdEstablecimiento').agg({
    'Numerador': 'sum',
    'Denominador': 'first',
    'servicio_salud': 'first',
    'nombre_establecimiento': 'first',
    'Dependencia Administrativa':'first',
    'Nivel de Atención':'first',
    'comuna': 'first'
}).reset_index()

# Recalcular el porcentaje
df_ms3a['Porcentaje'] = df_ms3a['Numerador'] / df_ms3a['Denominador']
df_ms3a['codigo_nombre'] = df_ms3a['IdEstablecimiento'] + ' - ' + df_ms3a['nombre_establecimiento']

# Título del dashboard
st.title('Meta III.A: Control con Enfoque de Riesgo odontológico en población de 0 a 9 años​')

FILTERS = {
    "servicio_salud": "Servicio de Salud",
    "comuna": "Comuna",
    "Dependencia Administrativa": "Dependencia Administrativa",
    "Nivel de Atención": "Nivel de Atención",
    "codigo_nombre": "Establecimiento",
}

# Inicializar session_state
for col in FILTERS:
    if col not in st.session_state:
        st.session_state[col] = []

def apply_filters(df, exclude_col=None):
    df_f = df
    for col in FILTERS:
        if col == exclude_col:
            continue
        selected = st.session_state[col]
        if selected:
            df_f = df_f[df_f[col].isin(selected)]
    return df_f

st.header("Filtros")

# Render filtros bidireccionales
for col, label in FILTERS.items():

    # DataFrame para calcular opciones (excluye el filtro actual)
    df_options = apply_filters(df_ms3a, exclude_col=col)

    options = sorted(df_options[col].dropna().unique())

    # Limpia selecciones inválidas (estilo Power BI)
    st.session_state[col] = [
        v for v in st.session_state[col] if v in options
    ]

    st.multiselect(
        label,
        options,
        key=col
    )

# DataFrame final filtrado (todos los filtros aplicados)
df_ms3a_filtered = apply_filters(df_ms3a)

# Mostrar datos filtrados
st.write("## Datos para la Meta Sanitaria")
# st.write("Fecha de corte de datos: _Enero del 2025_")

# Información de resumen
num_services = df_ms3a_filtered['servicio_salud'].nunique()
num_communes = df_ms3a_filtered['comuna'].nunique()
num_establishments = df_ms3a_filtered['codigo_nombre'].nunique()

# Dividir las métricas en 3 columnas
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label='N° Servicios de Salud', value=num_services)
with col2:
    st.metric(label='N° de comunas', value=num_communes)
with col3:
    st.metric(label='N° de establecimientos', value=num_establishments)

# Mostrar dataframe
col_ms3a = ['IdEstablecimiento', 'nombre_establecimiento', 'servicio_salud', 'comuna', 'Numerador', 'Denominador', 'Porcentaje']
rename_ms3a = {
    'IdEstablecimiento': 'ID Establecimiento',
    'nombre_establecimiento': 'Nombre del establecimiento',
    'servicio_salud': 'Servicio de Salud',
    'comuna': 'Comuna',
    'Numerador': 'Numerador',
    'Denominador': 'Denominador',
    'Porcentaje': 'Cumplimiento de la MS'
}
st.write('## Tabla de establecimientos')

st.write('A continuación se muestra la tabla de los establecimientos, su numerador, denominador y cumplimiento de la meta sanitaria')
st.write(df_ms3a_filtered[col_ms3a].rename(columns=rename_ms3a))
#%%
import io

# Filtrar columnas y renombrar para el archivo
df_export = df_ms3a_filtered[col_ms3a].rename(columns=rename_ms3a)

# Crear un buffer en memoria
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_export.to_excel(writer, index=False, sheet_name='Tabla_Establecimientos')

# Botón de descarga
st.download_button(
    label="📥 Descargar tabla de establecimientos (Excel)",
    data=output.getvalue(),
    file_name="tabla_establecimientos.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


#%%

st.subheader("Cumplimiento de la Meta Sanitaria - Total General")

# Calcular el porcentaje de cumplimiento total
total_numerador = df_ms3a_filtered['Numerador'].sum()
total_denominador = df_ms3a_filtered['Denominador'].sum()
total_porcentaje = total_numerador / total_denominador
meta_nacional = 0.41
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label='Numerador', value=total_numerador)
with col2:
    st.metric(label='Denominador', value=total_denominador)
with col3:
    st.metric(label='Porcentaje de cumplimiento', value=total_porcentaje)
with col4:
    st.metric(label='Meta Nacional', value=meta_nacional)

# Graficar gauge para el cumplimiento total general

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=total_porcentaje * 100,  # Convertir a porcentaje
    title={'text': 'Cumplimiento Total General'},
    gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "blue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 41], 'color': "gray"},
                {'range': [41, 100], 'color': "lightgray"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': total_porcentaje * 100
            },
            'shape': "angular"}
))
st.plotly_chart(fig)

#%%
# GRAFICO POR COMUNAS
## Crear un DataFrame con el nombre de la comuna, denominador, numerador y porcentaje de cumplimiento
df_cumplimiento = df_ms3a_filtered.groupby('comuna').agg(
    total_numerador=('Numerador', 'sum'),
    total_denominador=('Denominador', 'sum')
).reset_index()

df_cumplimiento['porcentaje_cumplimiento'] = (df_cumplimiento['total_numerador'] / df_cumplimiento['total_denominador']) * 100

rename_cumplimiento = {
    'porcentaje_cumplimiento': 'Porcentaje de cumplimiento',
    'total_numerador': 'Numerador',
    'total_denominador': 'Denominador',
    'comuna': 'Comuna'
}

# Ordenar el DataFrame por porcentaje de cumplimiento de mayor a menor
df_cumplimiento = df_cumplimiento.sort_values(by='porcentaje_cumplimiento', ascending=False)

# Mostrar el DataFrame resultante
st.write("## Tabla de cumplimiento por comuna")
st.write(df_cumplimiento.rename(columns=rename_cumplimiento))

# Crear el gráfico de barras
fig = px.bar(
    df_cumplimiento,
    x='comuna',
    y='porcentaje_cumplimiento',
    title='Porcentaje de Cumplimiento por Comuna',
    labels={'comuna': 'Comuna', 'porcentaje_cumplimiento': 'Porcentaje de Cumplimiento'},
    text='porcentaje_cumplimiento'
)

# Agregar la línea horizontal para la meta nacional del 90%
fig.add_shape(
    type="line",
    x0=0,
    y0=35,
    x1=len(df_cumplimiento['comuna']) - 1,
    y1=35,
    line=dict(color="red", width=2, dash="dash"),
)

# Ajustar el diseño del gráfico
fig.update_layout(
    xaxis_title='Comuna',
    yaxis_title='Porcentaje de Cumplimiento',
    yaxis=dict(range=[0, 100])
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)

# %%
