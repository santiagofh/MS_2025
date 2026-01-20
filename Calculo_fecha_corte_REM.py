#%%
import os
import pandas as pd
from datetime import datetime

path_REM_A=r"c:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\REM\REM_2025\Datos\SerieA2025.csv"
path_REM_BM=r"c:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\REM\REM_2025\Datos\SerieBM2025.csv"
path_REM_BS=r"c:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\REM\REM_2025\Datos\SerieBS2025.csv"
path_REM_D=r"c:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\REM\REM_2025\Datos\SerieP2025.csv"
path_REM_P=r"c:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\REM\REM_2025\Datos\SerieP2025.csv"

def obtener_fecha_corte(ruta_archivo):
    timestamp = os.path.getmtime(ruta_archivo)  # Obtiene el timestamp de modificación
    fecha = datetime.fromtimestamp(timestamp)   # Convierte a objeto datetime
    return fecha.strftime("%Y-%m-%d")           # Formatea como "AAAA-MM-DD"


fecha_corte_REM_A=obtener_fecha_corte(path_REM_A)
fecha_corte_REM_BM=obtener_fecha_corte(path_REM_BM)
fecha_corte_REM_BS=obtener_fecha_corte(path_REM_BS)
fecha_corte_REM_D=obtener_fecha_corte(path_REM_D)
fecha_corte_REM_P=obtener_fecha_corte(path_REM_P)
# %%
rem_list = ["REM A", "REM BM", "REM BS", "REM D", "REM P"]
fechas = [
    fecha_corte_REM_A,
    fecha_corte_REM_BM,
    fecha_corte_REM_BS,
    fecha_corte_REM_D,
    fecha_corte_REM_P
]

df_corte = pd.DataFrame({
    "REM": rem_list,
    "Fecha_corte": fechas
})

# %%
df_corte.to_csv('Fecha_corte_REM.csv')
# %%
