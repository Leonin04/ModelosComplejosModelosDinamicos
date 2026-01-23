import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings
import os
import pymc as pm
import arviz as az
import pytensor.tensor as pt
import pytensor 

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================
ARCHIVO_GERMANY = "germany.xlsx"  
ARCHIVO_GREECE = "greece.xlsx"    
# Keywords para identificar columnas si los nombres cambian
KEYWORD_COL_GERMANY = "Germany" 
KEYWORD_COL_GREECE = "Grecia" # Ojo: en tus archivos a veces dice 'Grecia' o 'Greece'

OUTPUT_DIR = 'image'
warnings.filterwarnings('ignore')
az.style.use("arviz-darkgrid")

# ==============================================================================
# FUNCIONES ROBUSTAS DE CARGA
# ==============================================================================
def limpiar_numero(x):
    """
    Convierte cualquier formato a float.
    Prioriza el punto como decimal (formato internacional encontrado en tus archivos).
    """
    if pd.isna(x): return np.nan
    if isinstance(x, (int, float)): return float(x)
    
    s = str(x).strip()
    if s == '' or s.lower() == 'nan': return np.nan
    
    # Intento directo por si es un número limpio
    try:
        return float(s)
    except:
        pass

    # Si falla, limpiamos caracteres raros
    # Si tiene punto y coma (ej: 1.000,50), asumimos formato europeo
    if '.' in s and ',' in s:
        # Eliminar puntos de miles, cambiar coma a punto
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s and '.' not in s:
        # Solo coma, asumimos que es decimal
        s = s.replace(',', '.')
    
    try:
        return float(s)
    except:
        return np.nan

def cargar_excel_inteligente(archivo, keyword_col):
    print(f"\n--> Analizando {archivo}...")
    try:
        # 1. Leer TODAS las hojas para encontrar la que tiene los datos
        xls = pd.ExcelFile(archivo)
        hoja_datos = None
        max_filas = 0
        
        print(f"   Hojas encontradas: {xls.sheet_names}")
        
        for hoja in xls.sheet_names:
            # Leemos cabecera y un poco de datos
            df_temp = pd.read_excel(xls, sheet_name=hoja, nrows=100)
            if len(df_temp) > max_filas:
                # Criterio: La hoja de datos suele tener columnas 'Date' y valores numéricos
                cols_str = " ".join([str(c).lower() for c in df_temp.columns])
                if 'date' in cols_str or 'fecha' in cols_str:
                    max_filas = len(df_temp)
                    hoja_datos = hoja
        
        if hoja_datos is None:
            hoja_datos = xls.sheet_names[0] # Fallback
            
        print(f"   [OK] Seleccionada hoja de datos: '{hoja_datos}'")
        
        # 2. Cargar la hoja correcta
        # Header=0 suele ser correcto en tus archivos CSV, pero a veces hay filas vacías.
        # Leemos todo y buscamos la fila de encabezados real.
        df = pd.read_excel(xls, sheet_name=hoja_datos)
        
        # Buscar columna fecha
        col_fecha = next((c for c in df.columns if 'date' in str(c).lower() or 'fecha' in str(c).lower()), None)
        
        # Buscar columna datos (flexible)
        # Buscamos 'yield', 'tasa', o el keyword (Germany/Greece)
        col_dato = None
        for c in df.columns:
            c_lower = str(c).lower()
            if keyword_col.lower() in c_lower or 'yield' in c_lower:
                 if c != col_fecha:
                    col_dato = c
                    break
        
        # Si no encuentra columna por nombre, usa la segunda columna (índice 1)
        if col_dato is None and len(df.columns) > 1:
            col_dato = df.columns[1]

        if not col_fecha or not col_dato:
            print(f"   [ERROR] No se identificaron columnas en {archivo}. Cols: {df.columns}")
            return None

        print(f"   Usando columnas: Fecha='{col_fecha}', Tasa='{col_dato}'")
        
        df = df.rename(columns={col_fecha: 'Fecha', col_dato: 'Tasa'})
        df = df[['Fecha', 'Tasa']].copy()
        
        # 3. Conversiones
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df = df.dropna(subset=['Fecha']) # Eliminar filas sin fecha válida
        
        df['Tasa'] = df['Tasa'].apply(limpiar_numero)
        df = df.dropna(subset=['Tasa']) # Eliminar filas sin datos numéricos
        
        df = df.set_index('Fecha').sort_index()
        return df

    except Exception as e:
        print(f"   [ERROR CRÍTICO] Falló la lectura de {archivo}: {e}")
        return None

# ==============================================================================
# FASE 1: PROCESAMIENTO Y DIAGNÓSTICO
# ==============================================================================
print("--- FASE 1: CARGA DE DATOS ---")
df_ger = cargar_excel_inteligente(ARCHIVO_GERMANY, KEYWORD_COL_GERMANY)
df_gre = cargar_excel_inteligente(ARCHIVO_GREECE, KEYWORD_COL_GREECE)

if df_ger is None or df_gre is None: exit()

# CRUCE DE DATOS
df_comb = df_gre.join(df_ger, how='inner', lsuffix='_GRE', rsuffix='_GER')
print(f"\nDatos combinados: {len(df_comb)} registros.")
print(f"Rango de fechas: {df_comb.index.min().date()} a {df_comb.index.max().date()}")

# VERIFICACIÓN DEL PICO DE 2012
print("\n--- VERIFICACIÓN DE CRISIS 2012 ---")
datos_2012 = df_comb.loc['2011-01-01':'2013-01-01']
if len(datos_2012) > 0:
    max_spread = (datos_2012['Tasa_GER'] - datos_2012['Tasa_GRE']).abs().max()
    fecha_max = (datos_2012['Tasa_GER'] - datos_2012['Tasa_GRE']).abs().idxmax()
    print(f"Datos en 2011-2013 encontrados: {len(datos_2012)} días.")
    print(f"Máximo Spread detectado: {max_spread:.2f} el día {fecha_max.date()}")
    if max_spread < 10:
        print("[ALERTA] El spread es muy bajo (<10%). Revisa si los datos de Grecia están en porcentaje o decimales.")
else:
    print("[ERROR GRAVE] No hay datos en el rango 2011-2013. El 'inner join' o la limpieza los eliminó.")

# CÁLCULO
df_comb['Spread'] = df_comb['Tasa_GER'] - df_comb['Tasa_GRE']
retornos = df_comb['Spread'].pct_change().dropna()
y_data_garch = retornos.values * 100 

# ==============================================================================
# FASE 2, 3, 4 (ESTÁNDAR)
# ==============================================================================
# (Solo incluimos el gráfico para verificar la salida, el resto del código GARCH es igual al tuyo)

if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

plt.figure(figsize=(12, 6))
# Usamos plot simple para ver dónde están los datos
plt.plot(retornos.index, retornos, color='black', lw=0.5)
# Marcar 2012
plt.axvline(pd.to_datetime('2012-03-09'), color='red', linestyle='--', alpha=0.5, label='Restructuración Deuda (2012)')
plt.title("Retornos del Spread (Verifica que el pico coincida con la línea roja)")
plt.legend()
plt.savefig(f"{OUTPUT_DIR}/Check_Datos_2012.png")
plt.close()

print(f"\n[INFO] He generado 'Check_Datos_2012.png'. Ábrela.")
print("Si ves el pico alineado con la línea roja, el problema de fechas está resuelto.")
print("Ahora continúa con el bloque Bayesiano (GARCH).")

# ==============================================================================
# CONTINUACIÓN GARCH (Tu código original funciona bien si los datos llegan aquí)
# ==============================================================================
# ... (Pega aquí tu bloque FASE 2 y FASE 3 si el check anterior es correcto)