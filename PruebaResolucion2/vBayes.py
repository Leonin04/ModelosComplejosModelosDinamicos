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
OUTPUT_DIR = 'image'

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
# FASE 1: DATOS
# ==============================================================================
print("\n--- FASE 1: PROCESAMIENTO DE DATOS ---")
df_ger = cargar_excel(ARCHIVO_GERMANY, KEYWORD_COL_GERMANY)
df_gre = cargar_excel(ARCHIVO_GREECE, KEYWORD_COL_GREECE)

if df_ger is None or df_gre is None:
    print("Error crítico: No se pudieron cargar los archivos.")
    exit()

df_comb = df_gre.join(df_ger, how='inner', lsuffix='_GRE', rsuffix='_GER')
df_comb['Spread'] = df_comb['Tasa_GER'] - df_comb['Tasa_GRE']
retornos = df_comb['Spread'].pct_change().dropna()

# Escalado x100 (Crucial para convergencia)
y_data_garch = retornos.values * 100 
n_samples = len(y_data_garch)

print(f"Datos listos. Muestras: {n_samples}")

# ==============================================================================
# FASE 2: MSPD (Econofísica)
# ==============================================================================
print("\n--- FASE 2: ANÁLISIS MSPD ---")
def calcular_mspd(serie, max_tau=252):
    res = {}
    vals = serie.values
    for tau in range(1, max_tau + 1):
        displacements = (vals[tau:] - vals[:-tau])**2
        res[tau] = np.mean(displacements)
    return pd.Series(res)

def power_law(t, A, alpha): return A * (t ** alpha)

mspd = calcular_mspd(df_comb['Spread'], max_tau=min(250, len(df_comb)//4))
x_mspd = mspd.index.values
y_mspd = mspd.values

try:
    limit = len(x_mspd)//2
    popt, _ = curve_fit(power_law, x_mspd[:limit], y_mspd[:limit], p0=[1, 0.5])
    A_fit, alpha_fit = popt
    y_fit_mspd = power_law(x_mspd, *popt)
    print(f"Exponente Alpha: {alpha_fit:.4f}")
except:
    alpha_fit = np.nan
    print("Falló el ajuste Power Law.")

# ==============================================================================
# FASE 3: GARCH(1,1) BAYESIANO (CORREGIDO INITVALS)
# ==============================================================================
print("\n--- FASE 3: GARCH(1,1) BAYESIANO ---")
print("Iniciando muestreo MCMC...")

# Preparación de datos para el scan (Desplazamiento t vs t-1)
y_past = y_data_garch[:-1]  # Input (t-1)
y_curr = y_data_garch[1:]   # Target (t)

# Paso recursivo GARCH
def garch_step(y_tm1, sigma2_tm1, omega, alpha, beta, mu):
    epsilon_tm1 = y_tm1 - mu
    return omega + alpha * (epsilon_tm1**2) + beta * sigma2_tm1

with pm.Model() as garch_model:
    # 1. Priors con INITVALS explícitos para evitar error de -inf
    # Esto asegura que el punto de partida cumpla alpha + beta < 1
    mu = pm.Normal("mu", mu=0, sigma=10, initval=0.0)
    omega = pm.InverseGamma("omega", alpha=2.5, beta=0.25, initval=0.5)
    
    # Initval clave: 0.1 + 0.8 = 0.9 ( < 1, es seguro)
    alpha = pm.Beta("alpha", alpha=2, beta=2, initval=0.1)
    beta = pm.Beta("beta", alpha=5, beta=1, initval=0.8)
    
    # Restricción de Estacionariedad
    pm.Potential("stationarity", pm.math.switch(alpha + beta < 1.0, 0, -np.inf))

    # 2. Bucle de Volatilidad (Scan)
    sigma2_0 = pt.as_tensor_variable(np.var(y_data_garch))
    
    sigma2_cycle, _ = pytensor.scan(
        fn=garch_step,
        sequences=[y_past],
        outputs_info=[sigma2_0],
        non_sequences=[omega, alpha, beta, mu]
    )
    
    # 3. Reconstrucción
    sigma2 = pm.Deterministic("sigma2", pt.concatenate([[sigma2_0], sigma2_cycle]))
    sigma = pm.Deterministic("sigma", pt.sqrt(sigma2))
    
    # 4. Likelihood
    # Importante: sigma tiene la misma longitud que y_data_garch
    likelihood = pm.Normal("obs", mu=mu, sigma=sigma, observed=y_data_garch)

    # 5. Inferencia
    # Usamos init='adapt_diag' en lugar de 'jitter+adapt_diag' para evitar saltos locos al inicio
    trace = pm.sample(
        draws=1000, 
        tune=1000, 
        chains=2, 
        target_accept=0.9, 
        init="adapt_diag", 
        return_inferencedata=True
    )

# Resumen
print("\n--> Resumen de Parámetros Posteriores:")
summary = az.summary(trace, var_names=["mu", "omega", "alpha", "beta"])
print(summary)

# ==============================================================================
# FASE 4: GRÁFICOS
# ==============================================================================
print("\n--- FASE 4: GUARDANDO GRÁFICOS ---")
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# 1. Datos
plt.figure(figsize=(10, 6))
plt.plot(retornos.index, retornos * 100, 'k', alpha=0.5)
plt.title('Retornos (x100)')
plt.savefig(f"{OUTPUT_DIR}/1_Datos.png")
plt.close()

# 2. MSPD
plt.figure(figsize=(6, 5))
plt.loglog(x_mspd, y_mspd, 'bo')
if not np.isnan(alpha_fit):
    plt.loglog(x_mspd, y_fit_mspd, 'r-')
plt.title(f'MSPD (Alpha={alpha_fit:.2f})')
plt.savefig(f"{OUTPUT_DIR}/2_MSPD.png")
plt.close()

# 3. Trace Bayesiano
az.plot_trace(trace, var_names=["mu", "omega", "alpha", "beta"])
plt.savefig(f"{OUTPUT_DIR}/3_Bayes_Trace.png")
plt.close()

# 4. Volatilidad
vol_posterior = trace.posterior["sigma"].mean(dim=["chain", "draw"]).values
vol_real = vol_posterior / 100 # Des-escalar

plt.figure(figsize=(12, 5))
plt.plot(retornos.index, np.abs(retornos), color='silver', label='|Retornos|')
plt.plot(retornos.index, vol_real, color='darkred', label='Volatilidad Bayesiana', linewidth=1.5)
plt.title('Volatilidad Estocástica Estimada')
plt.legend()
plt.savefig(f"{OUTPUT_DIR}/4_Volatilidad_GARCH.png")
plt.close()

print(f"¡Listo! Revisa la carpeta '{OUTPUT_DIR}'")