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
OUTPUT_DIR = 'analisis_grecia_final_v3'

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
        try:
            df = pd.read_excel(archivo)
        except:
            df = pd.read_excel(archivo, engine='openpyxl')

        col_fecha = next((c for c in df.columns if 'date' in str(c).lower() or 'fecha' in str(c).lower()), None)
        if not col_fecha: col_fecha = df.columns[0]
        
        col_dato = next((c for c in df.columns if keyword.lower() in str(c).lower()), None)
        if not col_dato: col_dato = df.columns[1]
        
        print(f"    Columna detectada: {col_dato}")
        df = df.rename(columns={col_fecha: 'Fecha', col_dato: 'Tasa'})
        df = df[['Fecha', 'Tasa']].dropna()
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)
        df = df.dropna(subset=['Fecha'])
        df['Tasa'] = df['Tasa'].apply(convertir_coma_a_punto)
        return df.set_index('Fecha').sort_index()
    except Exception as e:
        print(f"ERROR: {e}")
        return None

# ==============================================================================
# FASE 1: PROCESAMIENTO
# ==============================================================================
print("\n--- FASE 1: PREPARACIÓN DE DATOS ---")
df_ger = cargar_excel(ARCHIVO_GERMANY, KEYWORD_COL_GERMANY)
df_gre = cargar_excel(ARCHIVO_GREECE, KEYWORD_COL_GREECE)

if df_ger is None or df_gre is None: exit()

df_comb = df_gre.join(df_ger, how='inner', lsuffix='_GRE', rsuffix='_GER')
df_comb['Prima_Riesgo'] = df_comb['Tasa_GRE'] - df_comb['Tasa_GER']

variacion_bps = df_comb['Prima_Riesgo'].diff().dropna() * 100
y_original = variacion_bps.values

# REESCALADO
scale_factor = np.std(y_original)
y_scaled_raw = (y_original - np.mean(y_original)) / scale_factor

# --- CORRECCIÓN DE TIPO ---
# Obtenemos el tipo de float que usa PyTensor (usualmente float64)
floatX = pytensor.config.floatX
# Convertimos los datos de entrada a ese tipo exacto
y_scaled = y_scaled_raw.astype(floatX)

print(f"Datos originales Max: {np.max(np.abs(y_original)):.2f} bps")
print(f"Datos escalados: Max={np.max(np.abs(y_scaled)):.2f} | Tipo={y_scaled.dtype}")

# ==============================================================================
# FASE 2: MSPD
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

mspd = calcular_mspd(df_comb['Prima_Riesgo'], max_tau=min(250, len(df_comb)//4))
x_mspd = mspd.index.values
y_mspd = mspd.values

try:
    popt, _ = curve_fit(power_law, x_mspd[:100], y_mspd[:100], p0=[1, 0.5])
    alpha_fit = popt[1]
    y_fit_mspd = power_law(x_mspd, *popt)
    print(f"Exponente de difusión Alpha: {alpha_fit:.4f}")
except:
    alpha_fit = np.nan

# ==============================================================================
# FASE 3: GARCH ROBUSTO (CORREGIDO)
# ==============================================================================
print("\n--- FASE 3: ESTIMACIÓN DE VOLATILIDAD (MODELO T-STUDENT) ---")

with pm.Model() as garch_model:
    # 1. PRIORS
    mu = pm.Normal("mu", mu=0, sigma=1, initval=0.0)
    
    omega = pm.InverseGamma("omega", alpha=2.5, beta=1.0, initval=0.1)
    alpha = pm.Beta("alpha", alpha=2, beta=5, initval=0.1)
    beta = pm.Beta("beta", alpha=5, beta=2, initval=0.8)
    
    pm.Potential("constraint", pm.math.switch(alpha + beta < 1.0, 0, -np.inf))

    nu = pm.Gamma("nu", alpha=2, beta=0.1, initval=3.0) 

    # 2. DINÁMICA (CORRECCIÓN FINAL AQUÍ)
    # Usamos pt.as_tensor_variable en lugar de pt.tensor
    sigma2_0 = pt.as_tensor_variable(1.0, dtype=floatX)
    
    def garch_step(y_tm1, sigma2_tm1, omega, alpha, beta, mu):
        return omega + alpha * ((y_tm1 - mu)**2) + beta * sigma2_tm1

    sigma2_cycle, _ = pytensor.scan(
        fn=garch_step,
        sequences=[y_scaled[:-1]], 
        outputs_info=[sigma2_0], 
        non_sequences=[omega, alpha, beta, mu],
        strict=True 
    )
    
    sigma2 = pm.Deterministic("sigma2", pt.concatenate([[sigma2_0], sigma2_cycle]))
    sigma = pm.Deterministic("sigma", pt.sqrt(sigma2))
    
    # 3. LIKELIHOOD
    pm.StudentT("obs", nu=nu, mu=mu, sigma=sigma, observed=y_scaled)

    # 4. MUESTREO
    print("Iniciando muestreo...")
    trace = pm.sample(draws=100, tune=100, chains=2, target_accept=0.95, init="adapt_diag")

# ==============================================================================
# FASE 4: VISUALIZACIÓN
# ==============================================================================
print("\n--- FASE 4: GENERANDO GRÁFICOS ---")
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# Reescalamos resultados
vol_scaled = trace.posterior["sigma"].mean(dim=["chain", "draw"]).values
vol_bps = vol_scaled * scale_factor

# Gráfico 1
plt.figure(figsize=(12, 6))
plt.plot(variacion_bps.index, variacion_bps, color='teal', lw=0.7, alpha=0.8)
plt.title('Variación Diaria (bps)')
plt.savefig(f"{OUTPUT_DIR}/1_Variacion.png")
plt.close()

# Gráfico 2
plt.figure(figsize=(6, 5))
plt.loglog(x_mspd, y_mspd, 'bo', label='Datos')
if not np.isnan(alpha_fit):
    plt.loglog(x_mspd, y_fit_mspd, 'r-', label=f'Alpha={alpha_fit:.2f}')
plt.title(f'Difusión (Alpha={alpha_fit:.2f})')
plt.legend()
plt.savefig(f"{OUTPUT_DIR}/2_Difusion.png")
plt.close()

# Gráfico 3
hdi = az.hdi(trace.posterior["sigma"], hdi_prob=0.90)
hdi_lower = hdi["sigma"].sel(hdi="lower").values * scale_factor
hdi_upper = hdi["sigma"].sel(hdi="higher").values * scale_factor

plt.figure(figsize=(14, 7))
plt.plot(variacion_bps.index, np.abs(y_original), color='gray', alpha=0.3, label='|Retornos Reales|')
plt.plot(variacion_bps.index, vol_bps, color='darkred', lw=1.5, label='Volatilidad Estimada')
plt.fill_between(variacion_bps.index, hdi_lower, hdi_upper, color='red', alpha=0.15)
plt.title('Volatilidad Estocástica (Modelo Corregido)')
plt.legend()
plt.savefig(f"{OUTPUT_DIR}/3_Volatilidad_Final.png")
plt.close()

print(f"¡Éxito! Resultados en {OUTPUT_DIR}")