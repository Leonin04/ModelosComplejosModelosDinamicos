import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings
import os

# ==============================================================================
# IMPORTACIONES BAYESIANAS
# ==============================================================================
import pymc as pm
import arviz as az
import pytensor.tensor as pt
import pytensor 

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================
ARCHIVO_GERMANY = "germany.xlsx"  
ARCHIVO_GREECE = "greece.xlsx"    
KEYWORD_COL_GERMANY = "Germany" 
KEYWORD_COL_GREECE = "Grecia" 
warnings.filterwarnings('ignore')
OUTPUT_DIR = 'analisis_grecia_2012'

az.style.use("arviz-darkgrid")

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================
def convertir_coma_a_punto(x):
    if pd.isna(x): return np.nan
    if isinstance(x, (int, float)): return float(x)
    s = str(x).strip().replace(',', '.') 
    try:
        return float(s)
    except ValueError:
        return np.nan

def cargar_excel(archivo, keyword):
    print(f"--> Leyendo {archivo}...")
    try:
        df = pd.read_excel(archivo)
        col_fecha = next((c for c in df.columns if 'date' in str(c).lower() or 'fecha' in str(c).lower()), None)
        if not col_fecha: raise ValueError("Columna de fecha no encontrada.")
        
        col_dato = next((c for c in df.columns if keyword.lower() in str(c).lower()), None)
        if not col_dato:
            idx = 4 if "greece" in archivo.lower() or "grecia" in archivo.lower() else 1
            col_dato = df.columns[idx]
        
        df = df.rename(columns={col_fecha: 'Fecha', col_dato: 'Tasa'})
        df = df[['Fecha', 'Tasa']].dropna()
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)
        df['Tasa'] = df['Tasa'].apply(convertir_coma_a_punto)
        return df.set_index('Fecha').sort_index()
    except Exception as e:
        print(f"ERROR en {archivo}: {e}")
        return None

# ==============================================================================
# FASE 1: PROCESAMIENTO (DIFERENCIAS ABSOLUTAS - OPCIÓN A)
# ==============================================================================
print("\n--- FASE 1: CÁLCULO DE LA PRIMA DE RIESGO ---")
df_ger = cargar_excel(ARCHIVO_GERMANY, KEYWORD_COL_GERMANY)
df_gre = cargar_excel(ARCHIVO_GREECE, KEYWORD_COL_GREECE)

if df_ger is None or df_gre is None:
    print("Error crítico: No se pudieron cargar los archivos.")
    exit()

# Unimos datos y calculamos la Prima de Riesgo (Grecia - Alemania)
df_comb = df_gre.join(df_ger, how='inner', lsuffix='_GRE', rsuffix='_GER')
df_comb['Prima_Riesgo'] = df_comb['Tasa_GRE'] - df_comb['Tasa_GER']

# VARIACIÓN EN PUNTOS BÁSICOS (bps)
# Usamos .diff() para ver el cambio absoluto y multiplicamos por 100
variacion_bps = df_comb['Prima_Riesgo'].diff().dropna() * 100

# y_volatilidad será la base para el modelo GARCH
y_volatilidad = variacion_bps.values
n_samples = len(y_volatilidad)

print(f"Datos listos. El pico máximo detectado es de {y_volatilidad.max():.2f} bps.")

# ==============================================================================
# FASE 2: MSPD (ANÁLISIS DE DIFUSIÓN)
# ==============================================================================
print("\n--- FASE 2: ANÁLISIS DE DIFUSIÓN (MSPD) ---")
def calcular_mspd(serie, max_tau=252):
    res = {}
    vals = serie.values
    for tau in range(1, max_tau + 1):
        displacements = (vals[tau:] - vals[:-tau])**2
        res[tau] = np.mean(displacements)
    return pd.Series(res)

def power_law(t, A, alpha): return A * (t ** alpha)

# Calculamos MSPD sobre la Prima de Riesgo
mspd = calcular_mspd(df_comb['Prima_Riesgo'], max_tau=min(250, len(df_comb)//4))
x_mspd = mspd.index.values
y_mspd = mspd.values

try:
    limit = len(x_mspd)//2
    popt, _ = curve_fit(power_law, x_mspd[:limit], y_mspd[:limit], p0=[1, 0.5])
    A_fit, alpha_fit = popt
    y_fit_mspd = power_law(x_mspd, *popt)
    print(f"Exponente de difusión Alpha: {alpha_fit:.4f}")
except:
    alpha_fit = np.nan
    print("Falló el ajuste del exponente Alpha.")

# ==============================================================================
# FASE 3: GARCH(1,1) BAYESIANO SOBRE PUNTOS BÁSICOS
# ==============================================================================
print("\n--- FASE 3: ESTIMACIÓN DE VOLATILIDAD BAYESIANA ---")

with pm.Model() as garch_model:
    # Priors adaptados a la escala de puntos básicos
    mu = pm.Normal("mu", mu=0, sigma=10, initval=0.0)
    omega = pm.InverseGamma("omega", alpha=2.5, beta=1.0, initval=0.5)
    
    # Initvals para cumplir la condición de estabilidad alpha + beta < 1
    alpha = pm.Beta("alpha", alpha=2, beta=5, initval=0.1)
    beta = pm.Beta("beta", alpha=5, beta=2, initval=0.8)
    
    pm.Potential("estacionariedad", pm.math.switch(alpha + beta < 1.0, 0, -np.inf))

    sigma2_0 = pt.as_tensor_variable(np.var(y_volatilidad))
    
    def garch_step(y_tm1, sigma2_tm1, omega, alpha, beta, mu):
        return omega + alpha * ((y_tm1 - mu)**2) + beta * sigma2_tm1

    sigma2_cycle, _ = pytensor.scan(
        fn=garch_step,
        sequences=[y_volatilidad[:-1]],
        outputs_info=[sigma2_0],
        non_sequences=[omega, alpha, beta, mu]
    )
    
    sigma2 = pm.Deterministic("sigma2", pt.concatenate([[sigma2_0], sigma2_cycle]))
    sigma = pm.Deterministic("sigma", pt.sqrt(sigma2))
    
    # Verosimilitud
    # pm.Normal("obs", mu=mu, sigma=sigma, observed=y_volatilidad) con normal no lo asume bien

    # Muestreo Bayesiano
    trace = pm.sample(draws=300, tune=100, chains=2, target_accept=0.95, init="adapt_diag")

# ==============================================================================
# FASE 4: VISUALIZACIÓN DE RESULTADOS (ENFOCADA EN 2012)
# ==============================================================================
print("\n--- FASE 4: GENERANDO REPORTES GRÁFICOS ---")
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# 1. Variación Diaria (Puntos Básicos) - Aquí verás el pico real de la crisis
plt.figure(figsize=(12, 6))
plt.plot(variacion_bps.index, variacion_bps, color='teal', lw=0.7, alpha=0.8)
plt.title('Variación Diaria de la Prima de Riesgo (Puntos Básicos - bps)')
plt.ylabel('bps')
plt.savefig(f"{OUTPUT_DIR}/1_Variacion_Absoluta_bps.png")
plt.close()

# 2. MSPD
plt.figure(figsize=(6, 5))
plt.loglog(x_mspd, y_mspd, 'bo', label='Datos')
if not np.isnan(alpha_fit):
    plt.loglog(x_mspd, y_fit_mspd, 'r-', label=f'Alpha={alpha_fit:.2f}')
plt.title('Análisis de Difusión (MSPD)')
plt.legend()
plt.savefig(f"{OUTPUT_DIR}/2_Analisis_Difusion.png")
plt.close()

# 3. Volatilidad Estimada (Crisis 2012)
vol_posterior = trace.posterior["sigma"].mean(dim=["chain", "draw"]).values

plt.figure(figsize=(12, 6))
plt.plot(variacion_bps.index, np.abs(variacion_bps), color='lightgray', label='Variación Realizada (|bps|)')
plt.plot(variacion_bps.index, vol_posterior, color='darkred', label='Volatilidad Bayesiana GARCH', linewidth=1.5)
plt.title('Estimación de Volatilidad (Crisis de Deuda 2012)')
plt.ylabel('Desviación Estándar (bps)')
plt.legend()
plt.savefig(f"{OUTPUT_DIR}/3_Volatilidad_Estimada.png")
plt.close()

print(f"¡Hecho! Los archivos están en '{OUTPUT_DIR}'.")