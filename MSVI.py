#%%
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

#%%
# Ordenar dataframe
df_ms = pd.read_csv('MS2025_v2.csv')
col_est=['Código Vigente','Nombre Oficial','Nombre Dependencia Jerárquica (SEREMI / Servicio de Salud)','Nombre Comuna']
col_rename={
    'Código Vigente':'IdEstablecimiento',
    'Nombre Oficial':'nombre_establecimiento',
    'Nombre Dependencia Jerárquica (SEREMI / Servicio de Salud)':'servicio_salud',
    'Nombre Comuna':'comuna'
}
df_est = pd.read_excel('Establecimientos DEIS MINSAL 28-05-2024 (1).xlsx', skiprows=1, usecols=col_est)
df_est = df_est.rename(columns=col_rename)
df_ms6 = df_ms.loc[df_ms.MetaSanitaria == 'MSVI']
df_ms6 = df_ms6.merge(df_est, on='IdEstablecimiento', how='left')
#%%
# Preparar los datos
df_ms6 = df_ms6.dropna(subset=['Ano', 'Mes'])
df_ms6['Ano'] = df_ms6['Ano'].fillna(0).astype(int)
df_ms6['Mes'] = df_ms6['Mes'].fillna(0).astype(int)
df_ms6['Numerador'] = df_ms6['Numerador'].fillna(0).astype(int)
df_ms6['Denominador'] = df_ms6['Denominador'].fillna(0).astype(int)
df_ms6['IdEstablecimiento'] = df_ms6['IdEstablecimiento'].astype(str)
df_ms6["comuna"] = df_ms6["comuna"].fillna("No especificado").astype(str)
df_ms6['nombre_establecimiento'] = df_ms6['nombre_establecimiento'].astype(str)
df_ms6 = df_ms6.dropna(subset=["servicio_salud", "comuna"])
df_ms6["servicio_salud"] = df_ms6["servicio_salud"].fillna("No especificado").astype(str)
df_ms6['codigo_nombre']=df_ms6['IdEstablecimiento']+' - '+df_ms6['nombre_establecimiento']
df_ms6 = df_ms6.groupby('IdEstablecimiento').agg({
    'Ano':'max',
    'Mes':'max',
    'Numerador':'sum',
    'Denominador':'sum',
    'codigo_nombre':'first',
    'comuna':'first',
    'Dependencia Administrativa':'first',
    'Nivel de Atención':'first',
    'servicio_salud':'first',
    }).reset_index()
df_ms6['Porcentaje'] = df_ms6['Numerador']/df_ms6['Denominador']
#%%

# Título del dashboard
st.title('Meta VI: Prevalencia de Lactancia Materna Exclusiva (LME) en menores de 6 meses de vida')


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

    df_options = apply_filters(df_ms6, exclude_col=col)
    options = sorted(df_options[col].dropna().unique())

    # Limpia selecciones inválidas (como Power BI)
    st.session_state[col] = [
        v for v in st.session_state[col] if v in options
    ]

    st.multiselect(
        label,
        options,
        key=col
    )

# DataFrame final filtrado
df_ms1_filtered = apply_filters(df_ms6)

#%%
# Mostrar datos filtrados
st.write(f"## Datos para la Meta Sanitaria")
# st.write("Fecha de corte de datos: _Enero del 2025_")

# Información de resumen
num_services = df_ms6_filtered['servicio_salud'].nunique()
num_communes = df_ms6_filtered['comuna'].nunique()
num_establishments = df_ms6_filtered['codigo_nombre'].nunique()

# Dividir las métricas en 3 columnas
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label='N° Servicios de Salud', value=num_services)
with col2:
    st.metric(label='N° de comunas', value=num_communes)
with col3:
    st.metric(label='N° de establecimientos', value=num_establishments)
#%%
# Mostrar datagrame
col_ms6=['Ano', 'Mes','codigo_nombre','servicio_salud',  'Numerador', 'Denominador','Porcentaje']
rename_ms6={
    'Ano':'Año', 
    'Mes':'Mes',
    'codigo_nombre':'Nombre del establecimeinto',
    'servicio_salud':'Servicio de Salud',  
    'Numerador':'Numerador', 
    'Denominador':'Denominador',
    'Porcentaje':'Cumplimiento de la MS'
}
st.write(f"## Tabla de establecimientos")
st.write('A continuación se muestra la tabla de los establecimientos, su numerador, denominador y cumplimiento de la meta sanitaria')
st.write(df_ms6_filtered[col_ms6].rename(columns=rename_ms6))
#%%


import io

# Filtrar columnas y renombrar para el archivo
df_export = df_ms6_filtered[col_ms6].rename(columns=rename_ms6)

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
# Calcular el total del numerador y denominador
total_numerador = df_ms6_filtered['Numerador'].sum()
total_denominador = df_ms6_filtered['Denominador'].sum()
total_porcentaje = (total_numerador / total_denominador) * 100 if total_denominador > 0 else 0
meta_nacional = 0.6
#%%
# Mostrar datos de Numerador, Denominador y Porcentaje de cumplimiento
st.write("## Cumplimiento de la Meta Sanitaria")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label='Numerador', value=total_numerador)
with col2:
    st.metric(label='Denominador', value=total_denominador)
with col3:
    st.metric(label='Porcentaje de cumplimiento', value=total_porcentaje)
with col4:
    st.metric(label='Meta Nacional', value=meta_nacional)
#%%
# Grafico Gauge
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=total_porcentaje,
    title={'text': 'INDICADOR'},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "blue"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 60], 'color': "gray"},
            {'range': [60, 100], 'color': "lightgray"}
        ],
        'threshold': {
            'line': {'color': "black", 'width': 4},
            'thickness': 0.75,
            'value': total_porcentaje
        },
        'shape': "angular"
    }
))
st.plotly_chart(fig)

# #%%
# # Grafico de metas por mes
# grouped_data = df_ms6_filtered.groupby(['Ano', 'Mes'])[['Denominador', 'Numerador']].sum().reset_index()

# grouped_data['Denominador Acumulado'] = grouped_data.groupby('Ano')['Denominador'].cumsum()
# grouped_data['Numerador Acumulado'] = grouped_data.groupby('Ano')['Numerador'].cumsum()

# grouped_data['Cumplimiento'] = (grouped_data['Numerador Acumulado'] / grouped_data['Denominador Acumulado']) * 100

# fig = go.Figure()

# # Añadir trazas para el numerador acumulado, denominador acumulado y cumplimiento
# for year in grouped_data['Ano'].unique():
#     year_data = grouped_data[grouped_data['Ano'] == year]
#     fig.add_trace(go.Scatter(
#         x=year_data['Mes'],
#         y=year_data['Numerador Acumulado'],
#         mode='lines',
#         name=f'Numerador Acumulado {year}',
#         line=dict(color='red'),
#         yaxis='y1'
#     ))

#     fig.add_trace(go.Scatter(
#         x=year_data['Mes'],
#         y=year_data['Denominador Acumulado'],
#         mode='lines',
#         name=f'Denominador Acumulado {year}',
#         line=dict(color='blue'),
#         yaxis='y1'
#     ))

#     fig.add_trace(go.Scatter(
#         x=year_data['Mes'],
#         y=year_data['Cumplimiento'],
#         mode='lines',
#         name=f'Cumplimiento {year}',
#         line=dict(color='green'),
#         yaxis='y2'
#     ))

# # Configurar el layout del gráfico
# fig.update_layout(
#     title='Denominador, Numerador y Cumplimiento por Mes (MSVI)',
#     xaxis_title='Mes',
#     yaxis=dict(
#         title='Cantidad',
#         # titlefont=dict(color='black'),
#         # tickfont=dict(color='black')
#     ),
#     yaxis2=dict(
#         title='Cumplimiento (%)',
#         # titlefont=dict(color='black'),
#         # tickfont=dict(color='black'),
#         overlaying='y',
#         side='right',
#         range=[0, 100]
#     ),
#     legend_title='Tipo',
#     legend=dict(x=0, y=1, traceorder='normal')
# )

# # Mostrar el gráfico en Streamlit
# st.write("## Denominador, Numerador y Cumplimiento por Mes (MSVI)")
# st.plotly_chart(fig)

#%%
# GRAFICO POR COMUNAS
## Crear un DataFrame con el nombre de la comuna, denominador, numerador y porcentaje de cumplimiento
df_cumplimiento = df_ms6_filtered.groupby('comuna').agg(
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
    y0=60,
    x1=len(df_cumplimiento['comuna']) - 1,
    y1=60,
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

