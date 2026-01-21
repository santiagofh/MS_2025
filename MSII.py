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
df_ms2 = df_ms.loc[df_ms.MetaSanitaria == 'MSII']
df_ms2 = df_ms2.merge(df_est, on='IdEstablecimiento', how='left')
#%%
# Preparar los datos
df_ms2 = df_ms2.dropna(subset=['Ano', 'Mes'])
df_ms2['Ano'] = df_ms2['Ano'].astype(int)
df_ms2['Mes'] = df_ms2['Mes'].astype(int)
df_ms2['Porcentaje'] = df_ms2['Numerador']/df_ms2['Denominador']
df_ms2['IdEstablecimiento'] = df_ms2['IdEstablecimiento'].astype(str)
df_ms2['nombre_establecimiento'] = df_ms2['nombre_establecimiento'].astype(str)
df_ms2 = df_ms2.dropna(subset=["servicio_salud", "comuna"])
df_ms2["servicio_salud"] = df_ms2["servicio_salud"].fillna("No especificado").astype(str)
df_ms2['codigo_nombre']=df_ms2['IdEstablecimiento']+' - '+df_ms2['nombre_establecimiento']
#%%

# Título del dashboard
st.title('Meta II: Detección precoz del cáncer de cuello uterino')
st.write('PAPANICOLAOU (PAP) O TEST DE VPH VIGENTE EN PERSONAS DE 25 A 64 AÑOS')


st.subheader("Mes de corte")
# ---------- Filtro global de MES ----------
if "Mes" not in st.session_state:
    st.session_state["Mes"] = None

all_meses = sorted(df_ms2["Mes"].dropna().unique())

selected_mes = st.selectbox(
    "Mes de corte",
    all_meses,
    index=len(all_meses) - 1 if st.session_state["Mes"] is None
    else all_meses.index(st.session_state["Mes"])
)

st.session_state["Mes"] = selected_mes

# DataFrame base (TODOS los filtros dependen de este)
df_base = df_ms2[df_ms2["Mes"] == selected_mes]

st.subheader("Filtros en Cascada")


# ---------- Definición de filtros ----------
FILTERS = {
    "servicio_salud": "Servicio de Salud",
    "comuna": "Comuna",
    "Dependencia Administrativa": "Dependencia Administrativa",
    "Nivel de Atención": "Nivel de Atención",
    "codigo_nombre": "Establecimiento",
}

# ---------- Inicializar session_state ----------
for col in FILTERS:
    if col not in st.session_state:
        st.session_state[col] = []

# ---------- Función de filtrado bidireccional ----------
def apply_filters(df, exclude_col=None):
    df_f = df.copy()
    for col in FILTERS:
        if col == exclude_col:
            continue
        selected = st.session_state[col]
        if selected:
            df_f = df_f[df_f[col].isin(selected)]
    return df_f

# ---------- Render de filtros ----------
for col, label in FILTERS.items():

    # Opciones válidas según los otros filtros
    df_options = apply_filters(df_base, exclude_col=col)
    options = sorted(df_options[col].dropna().unique())

    # Limpia selecciones inválidas (comportamiento Power BI)
    st.session_state[col] = [
        v for v in st.session_state[col] if v in options
    ]

    st.multiselect(
        label,
        options,
        key=col
    )

# ---------- DataFrame final ----------
df_ms2_filtered = apply_filters(df_base)



#%%
# Mostrar datos filtrados
st.write("## Datos para la Meta Sanitaria")
# st.write("Fecha de corte de datos: _Enero del 2025_")

num_services = df_ms2_filtered['servicio_salud'].nunique()
num_communes = df_ms2_filtered['comuna'].nunique()
num_establishments = df_ms2_filtered['codigo_nombre'].nunique()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label='N° Servicios de Salud', value=num_services)
with col2:
    st.metric(label='N° de comunas', value=num_communes)
with col3:
    st.metric(label='N° de establecimientos', value=num_establishments)
#%%
# Mostrar DataFrame
col_ms2=['Ano', 'Mes','codigo_nombre','servicio_salud',  'Numerador', 'Denominador','Porcentaje']
rename_ms2={
    'Ano':'Año', 
    'Mes':'Mes',
    'codigo_nombre':'Nombre del establecimeinto',
    'servicio_salud':'Servicio de Salud',  
    'Numerador':'Numerador', 
    'Denominador':'Denominador',
    'Porcentaje':'Cumplimiento de la MS'
}
st.write('## Tabla de establecimientos')
st.write('A continuación se muestra la tabla de los establecimientos, su numerador, denominador y cumplimiento de la meta sanitaria')
st.write(df_ms2_filtered[col_ms2].rename(columns=rename_ms2))
#%%
#%% Descargar Excel con la tabla de establecimientos
import io

# Filtrar columnas y renombrar para el archivo
df_export = df_ms2_filtered[col_ms2].rename(columns=rename_ms2)

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
total_numerador = df_ms2_filtered['Numerador'].sum()
total_denominador = df_ms2_filtered['Denominador'].sum()
total_porcentaje = (total_numerador / total_denominador) if total_denominador > 0 else 0
meta_nacional = 0.8
st.subheader("Cumplimiento de la Meta Sanitaria")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label='Numerador', value=total_numerador)
with col2:
    st.metric(label='Denominador', value=total_denominador)
with col3:
    st.metric(label='Porcentaje de cumplimiento', value=total_porcentaje)
with col4:
    st.metric(label='Meta Nacional', value=meta_nacional)

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=total_porcentaje * 100,  # Convertir a porcentaje
    title={'text': 'Cumplimiento'},
    gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "blue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 80], 'color': "gray"},
                {'range': [80, 100], 'color': "lightgray"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': total_porcentaje* 100
            },
            'shape': "angular"}
))
st.plotly_chart(fig)

#%%
# Crear un DataFrame con el nombre de la comuna, denominador, numerador y porcentaje de cumplimiento
df_cumplimiento = df_ms2_filtered.groupby('comuna').agg(
    total_numerador=('Numerador', 'sum'),
    total_denominador=('Denominador', 'sum')
).reset_index()

df_cumplimiento['porcentaje_cumplimiento'] = (df_cumplimiento['total_numerador'] / df_cumplimiento['total_denominador']) * 100

rename_cumplimiento={
    'porcentaje_cumplimiento':'Porcentaje de cumplimiento',
    'total_numerador':'Numerador',
    'total_denominador':'Denominador',
    'comuna':'Comuna'
}

# %%
df_cumplimiento = df_ms2_filtered.groupby('comuna').agg(
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
    y0=80,
    x1=len(df_cumplimiento['comuna']) - 1,
    y1=80,
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