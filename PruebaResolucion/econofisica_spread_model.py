import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from arch import arch_model
import warnings
import os 

# --- NOMBRES DE COLUMNAS A BUSCAR Y ARCHIVO ---
COLUMNA_FECHA_BUSQUEDA = 'Fecha'  
COLUMNA_SPREAD = 'Último'         
#ARCHIVO_DATOS = "GREECE-GERMANY-SPREAD-BONOS.csv"
ARCHIVO_DATOS = "datos-largos.csv"

OUTPUT_DIR = 'image' # 

# Configuración de advertencias
warnings.filterwarnings('ignore')

# ==============================================================================
# FASE 1: CARGA Y PREPARACIÓN DE DATOS REALES (Mismo código de éxito)
# ==============================================================================

print(f"--- FASE 1: CARGANDO DATOS DESDE {ARCHIVO_DATOS} ---")
print(f"--- APLICANDO SOLUCIÓN ROBUSTA: Limpieza de encabezados y formato decimal ---")

try:
    # Lectura robusta con solución de formato
    try:
        df = pd.read_csv(ARCHIVO_DATOS, encoding='utf-8') 
    except UnicodeDecodeError:
        df = pd.read_csv(ARCHIVO_DATOS, encoding='latin1')
    
    columnas_limpias = df.columns.str.strip().str.replace('\ufeff', '')
    df.columns = columnas_limpias
    
    if df.columns[0] != COLUMNA_FECHA_BUSQUEDA:
        df = df.rename(columns={df.columns[0]: COLUMNA_FECHA_BUSQUEDA})

    df = df.set_index(COLUMNA_FECHA_BUSQUEDA)
    df.index = pd.to_datetime(df.index, errors='coerce', dayfirst=True)
    
    df['Spread_str'] = df[COLUMNA_SPREAD].astype(str)
    df['Spread'] = df['Spread_str'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df['Spread'] = pd.to_numeric(df['Spread'], errors='coerce')
    
    df = df.dropna(subset=['Spread']) 

    p_t = df['Spread'].values 
    df['Retornos'] = df['Spread'].pct_change()
    retornos = df['Retornos'].dropna().values

    print(f"Lectura exitosa.")
    print(f"Período analizado: {df.index.min().date()} a {df.index.max().date()} | Puntos: {len(p_t)}")
    
except Exception as e:
    print(f"ERROR FATAL: La lectura falló. Mensaje final: {e}")
    exit()


# ==============================================================================
# FASE 2: NÚCLEO DE LA ECONOFÍSICA - CÁLCULO DEL MSPD
# ==============================================================================
def calcular_mspd(p_t, max_tau=252):
    N = len(p_t)
    mspd_results = {}
    for tau in range(1, max_tau + 1):
        if N - tau <= 0: break
        squared_displacements = (p_t[tau:] - p_t[:-tau])**2
        mspd_results[tau] = np.mean(squared_displacements)
    return pd.Series(mspd_results)

def power_law(tau, A, alpha):
    return A * (tau ** alpha)

print("\n--- FASE 2: ANÁLISIS ECONOFÍSICO (MSPD) ---")
mspd_df = calcular_mspd(p_t, max_tau=min(252, len(p_t)//2))
tau_values = mspd_df.index.values
mspd_values = mspd_df.values
alpha_fit = np.nan 

try:
    fit_range = len(tau_values) // 2 
    params, cov = curve_fit(power_law, tau_values[:fit_range], mspd_values[:fit_range], p0=[1, 1], maxfev=5000)
    A_fit, alpha_fit = params
    fit_curve = power_law(tau_values, A_fit, alpha_fit)
    
    print(f"Exponente de Escala (alpha): {alpha_fit:.4f}")
    if alpha_fit < 1.0:
        print("  -> Interpretación: Subdifusivo (Arresto Dinámico/Memoria Lenta)")
    elif alpha_fit > 1.0:
        print("  -> Interpretación: Superdifusivo (Tendencia Fuerte)")
    else:
        print("  -> Interpretación: Difusivo (Paseo Aleatorio)")
        
except RuntimeError:
    print("Error: No se pudo realizar el ajuste de la curva Power Law.")
    
# ==============================================================================
# FASE 3: MODELO ECONOMÉTRICO (GARCH) - ¡COMPROBACIÓN DE ROBUSTEZ!
# ==============================================================================
print("\n--- FASE 3: MODELO ECONOMÉTRICO (GARCH) ---")

if len(retornos) < 100:
    print(f"ADVERTENCIA: Solo se encontraron {len(retornos)} puntos de datos. El análisis GARCH se omite o no es fiable.")
    alpha_1 = np.nan
    beta_1 = np.nan
else:
    try:
        am = arch_model(retornos * 100, mean='Constant', vol='Garch', p=1, q=1, dist='StudentsT')
        res = am.fit(update_freq=5, disp='off')
        
        if 'arch[1]' in res.params and 'garch[1]' in res.params:
            alpha_1 = res.params['arch[1]']
            beta_1 = res.params['garch[1]']
            print(f"Coeficiente ARCH (alfa_1): {alpha_1:.4f}")
            print(f"Coeficiente GARCH (beta_1): {beta_1:.4f}")
            print(f"Persistencia de Volatilidad (alfa_1 + beta_1): {alpha_1 + beta_1:.4f}")
        else:
            print("ERROR DE GARCH: El modelo no convergió y no se encontraron los parámetros.")
            alpha_1 = np.nan
            beta_1 = np.nan
    except Exception as e:
        print(f"ERROR DE GARCH: Falló el intento de ajuste del modelo. Mensaje: {e}")
        alpha_1 = np.nan
        beta_1 = np.nan

# ==============================================================================
# FASE 4: VISUALIZACIÓN Y GUARDADO DE RESULTADOS
# ==============================================================================
print("\n--- FASE 4: GENERANDO Y GUARDANDO GRÁFICOS ---")

# 1. Crear el directorio 'image' si no existe
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Directorio '{OUTPUT_DIR}' creado.")

# 2. Gráfico 1: Serie Temporal del Spread
plt.figure(figsize=(14, 6))
plt.plot(df.index, df['Spread'], label='Spread de Bonos Grecia-Alemania', color='tab:blue')
plt.title('1. Serie Temporal del Spread de Bonos (Grecia-Alemania)')
plt.xlabel('Fecha')
plt.ylabel('Spread (puntos base)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.savefig(os.path.join(OUTPUT_DIR, '1_Serie_Temporal_Spread.png'))
plt.close() # Cierra la figura para liberar memoria

# 3. Gráfico 2: MSPD en Escala Log-Log
plt.figure(figsize=(10, 8))
plt.loglog(tau_values, mspd_values, 'o', label='MSPD (Datos Reales)')
if not np.isnan(alpha_fit):
    plt.loglog(tau_values, fit_curve, '-', label=f'Ajuste Power Law (α={alpha_fit:.2f})', color='red')
    power_law_difusivo = power_law(tau_values, A_fit, 1.0)
    plt.loglog(tau_values, power_law_difusivo, '--', label=r'Referencia $\alpha=1$ (Difusivo)', color='gray')
    
plt.title('2. Desplazamiento Cuadrático Medio del Precio (MSPD) - Escala Log-Log')
plt.xlabel(r'Lag Time $\tau$ (días) - Log Scale')
plt.ylabel(r'MSPD $\langle \Delta p^2(\tau) \rangle$ - Log Scale')
plt.legend()
plt.grid(True, which="both", ls="--")
plt.savefig(os.path.join(OUTPUT_DIR, '2_MSPD_Log_Log.png'))
plt.close() # Cierra la figura para liberar memoria

print(f" Gráficos guardados en la carpeta '{OUTPUT_DIR}'.")
print("\n¡Ejecución completada! Analice los resultados y los gráficos generados.")