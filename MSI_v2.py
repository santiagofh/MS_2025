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
df_ms1 = df_ms.loc[df_ms.MetaSanitaria == 'MSI']
df_ms1 = df_ms1.merge(df_est, on='IdEstablecimiento', how='left')
#%%
# Preparar los datos
df_ms1 = df_ms1.dropna(subset=['Ano', 'Mes'])
df_ms1['Ano'] = df_ms1['Ano'].fillna(0).astype(int)
df_ms1['Mes'] = df_ms1['Mes'].fillna(0).astype(int)
df_ms1['Año_Mes'] = df_ms1['Ano'] * 100 + df_ms1['Mes']
df_ms1['Numerador'] = df_ms1['Numerador'].fillna(0).astype(int)
df_ms1['Denominador'] = df_ms1['Denominador'].fillna(0).astype(int)
df_ms1['IdEstablecimiento'] = df_ms1['IdEstablecimiento'].astype(str)
df_ms1['nombre_establecimiento'] = df_ms1['nombre_establecimiento'].astype(str)
df_ms1 = df_ms1.dropna(subset=["servicio_salud", "comuna"])
df_ms1["servicio_salud"] = df_ms1["servicio_salud"].fillna("No especificado").astype(str)
df_ms1['codigo_nombre']=df_ms1['IdEstablecimiento']+' - '+df_ms1['nombre_establecimiento']
df_ms1 = df_ms1.groupby(['IdEstablecimiento']).agg({
    'Año_Mes':'max',
    'Numerador':'sum',
    'Denominador':'sum',
    'codigo_nombre':'first',
    'Dependencia Administrativa':'first',
    'Nivel de Atención':'first',
    'comuna':'first',
    'servicio_salud':'first',
    }).reset_index()
df_ms1['Porcentaje'] = df_ms1['Numerador']/df_ms1['Denominador']
#%%

st.title('Meta I: Recuperación del Desarrollo Psicomotor')
# %%
from streamlit_dynamic_filters import DynamicFilters
dynamic_filters = DynamicFilters(df_ms1, filters=['servicio_salud', 'comuna', 'Dependencia Administrativa', 'Nivel de Atención', 'codigo_nombre'])
dynamic_filters.display_filters(location='sidebar')
new_df = dynamic_filters.filter_df()


#%%
col_ms1=['Año_Mes','codigo_nombre','servicio_salud',  'Numerador', 'Denominador','Porcentaje']

rename_ms1={
    'Año_Mes':'Año y Mes', 
    'codigo_nombre':'Nombre del establecimeinto',
    'servicio_salud':'Servicio de Salud',  
    'Numerador':'Numerador', 
    'Denominador':'Denominador',
    'Porcentaje':'Cumplimiento de la MS'
}
st.write(f"## Tabla de establecimientos")
st.write('A continuación se muestra la tabla de los establecimientos, su numerador, denominador y cumplimiento de la meta sanitaria')
st.write(new_df[col_ms1].rename(columns=rename_ms1))
# %%
import io

# Filtrar columnas y renombrar para el archivo
df_export = new_df[col_ms1].rename(columns=rename_ms1)

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
import streamlit as st

df = df_ms1.copy()

FILTERS = {
    "servicio_salud": "Servicio de Salud",
    "comuna": "Comuna",
    "Dependencia Administrativa": "Dependencia Administrativa",
    "Nivel de Atención": "Nivel de Atención",
    "codigo_nombre": "Establecimiento",
}

# Inicializar estado
for col in FILTERS:
    if col not in st.session_state:
        st.session_state[col] = []

# Motor de filtros cross-filter
def apply_filters(df, exclude_col=None):
    df_f = df
    for col in FILTERS:
        if col == exclude_col:
            continue
        selected = st.session_state[col]
        if selected:
            df_f = df_f[df_f[col].isin(selected)]
    return df_f

st.sidebar.header("Filtros")

# Render de filtros bidireccionales
for col, label in FILTERS.items():

    df_options = apply_filters(df, exclude_col=col)
    options = sorted(df_options[col].dropna().unique())

    # Limpia selecciones inválidas (como Power BI)
    st.session_state[col] = [
        v for v in st.session_state[col] if v in options
    ]

    st.sidebar.multiselect(
        label,
        options,
        key=col
    )

# DataFrame final
df_final = apply_filters(df)

st.metric("Registros", len(df_final))
st.dataframe(df_final)

# Reset
if st.sidebar.button("🔄 Limpiar filtros"):
    for col in FILTERS:
        st.session_state[col] = []
    st.rerun()
