import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from arch import arch_model
import warnings
import os

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================
ARCHIVO_GERMANY = "germany.xlsx"  
ARCHIVO_GREECE = "greece.xlsx"    

# Keywords para buscar la columna de datos
KEYWORD_COL_GERMANY = "Germany" 
KEYWORD_COL_GREECE = "Grecia" 

# Configuración de advertencias
warnings.filterwarnings('ignore')
OUTPUT_DIR = 'image'

# ==============================================================================
# FUNCIÓN DE LIMPIEZA SIMPLIFICADA (RESPETANDO LA COMA DECIMAL)
# ==============================================================================
def convertir_coma_a_punto(x):
    """
    Toma el valor tal cual. Si tiene coma, la cambia por punto para que Python
    pueda calcular. No altera nada más.
    Ejemplo: "3,5" -> 3.5
    """
    if pd.isna(x):
        return np.nan
    
    # Si ya es un número (ej: Excel lo leyó como 3.5), lo devolvemos tal cual
    if isinstance(x, (int, float)):
        return float(x)
    
    # Si es texto (ej: "3,5"), cambiamos la coma por punto
    s = str(x).strip()
    s = s.replace(',', '.') 
    
    try:
        return float(s)
    except ValueError:
        return np.nan

# ==============================================================================
# FASE 1: CARGA Y LIMPIEZA
# ==============================================================================
def cargar_excel(archivo, keyword):
    print(f"--> Leyendo {archivo}...")
    try:
        # Leemos el excel
        df = pd.read_excel(archivo)
        
        # 1. Buscar fecha
        col_fecha = next((c for c in df.columns if 'date' in str(c).lower() or 'fecha' in str(c).lower()), None)
        if not col_fecha: raise ValueError("Columna de fecha no encontrada.")
        
        # 2. Buscar datos (Yield)
        col_dato = next((c for c in df.columns if keyword.lower() in str(c).lower()), None)
        # Si no encuentra por nombre, intenta por posición
        if not col_dato:
            idx = 4 if "greece" in archivo.lower() or "grecia" in archivo.lower() else 1
            col_dato = df.columns[idx]
            print(f"   (Aviso) Usando columna por posición: {col_dato}")
        else:
            print(f"   Columna detectada: {col_dato}")

        # 3. Renombrar
        df = df.rename(columns={col_fecha: 'Fecha', col_dato: 'Tasa'})
        df = df[['Fecha', 'Tasa']].dropna()
        
        # Formato Fecha
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)
        
        # 4. APLICAR LA CONVERSIÓN SIMPLE (COMA -> PUNTO)
        df['Tasa'] = df['Tasa'].apply(convertir_coma_a_punto)
        
        # Verificar un dato de muestra
        print(f"   Dato original con coma procesado a: {df['Tasa'].iloc[0]} (Tipo: {df['Tasa'].dtype})")
        
        return df.set_index('Fecha').sort_index()

    except Exception as e:
        print(f"ERROR en {archivo}: {e}")
        return None

print("\n--- FASE 1: PROCESAMIENTO DE DATOS ---")
df_ger = cargar_excel(ARCHIVO_GERMANY, KEYWORD_COL_GERMANY)
df_gre = cargar_excel(ARCHIVO_GREECE, KEYWORD_COL_GREECE)

if df_ger is None or df_gre is None:
    print("Error crítico en la carga de archivos.")
    exit()

# Sincronizar fechas (Inner Join)
print("--> Sincronizando series temporales...")
df_comb = df_gre.join(df_ger, how='inner', lsuffix='_GRE', rsuffix='_GER')

# Calcular Spread (Diferencia simple)
# df_comb['Spread'] = df_comb['Tasa_GRE'] - df_comb['Tasa_GER']
df_comb['Spread'] = df_comb['Tasa_GER'] - df_comb['Tasa_GRE']
p_t = df_comb['Spread'].values

# Retornos para GARCH
retornos = df_comb['Spread'].pct_change().replace([np.inf, -np.inf], np.nan).dropna()

print(f"Datos listos. Periodo: {df_comb.index.min().date()} al {df_comb.index.max().date()}")
print(f"Muestras: {len(df_comb)}")

# ==============================================================================
# FASE 2: ECONOFÍSICA (MSPD)
# ==============================================================================
print("\n--- FASE 2: ANÁLISIS MSPD ---")

def calcular_mspd(serie, max_tau=252):
    res = {}
    vals = serie.values
    for tau in range(1, max_tau + 1):
        # Diferencia al cuadrado
        displacements = (vals[tau:] - vals[:-tau])**2
        res[tau] = np.mean(displacements)
    return pd.Series(res)

def power_law(t, A, alpha):
    return A * (t ** alpha)

# Calculamos MSPD
mspd = calcular_mspd(df_comb['Spread'], max_tau=min(250, len(p_t)//4))
x_data = mspd.index.values
y_data = mspd.values

# Ajuste de curva
try:
    limit = len(x_data)//2
    popt, _ = curve_fit(power_law, x_data[:limit], y_data[:limit], p0=[1, 0.5])
    A_fit, alpha_fit = popt
    y_fit = power_law(x_data, *popt)
    
    print(f"Exponente Alpha (Hurst proxy): {alpha_fit:.4f}")
    if alpha_fit < 1: print("-> Régimen: Subdifusivo (Confinamiento/Mean Reverting)")
    elif alpha_fit > 1: print("-> Régimen: Superdifusivo (Tendencia)")
    else: print("-> Régimen: Difusivo (Browniano)")
except:
    alpha_fit = np.nan
    print("Falló el ajuste Power Law.")

# ==============================================================================
# FASE 3: ECONOMETRÍA (GARCH)
# ==============================================================================
print("\n--- FASE 3: ANÁLISIS GARCH ---")

try:
    # Escalamos por 100 para estabilidad numérica
    model = arch_model(retornos * 100, vol='Garch', p=1, q=1, dist='Normal')
    res_garch = model.fit(disp='off')
    print(res_garch.summary())
    
    alpha_g = res_garch.params['alpha[1]']
    beta_g = res_garch.params['beta[1]']
    print(f"\nPersistencia (alpha + beta): {alpha_g + beta_g:.4f}")
except Exception as e:
    print(f"Error GARCH: {e}")

# ==============================================================================
# FASE 4: GRÁFICOS
# ==============================================================================
print("\n--- FASE 4: GUARDANDO GRÁFICOS ---")
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# Gráfico 1: Spread y Rendimientos
plt.figure(figsize=(12, 8))
plt.subplot(2,1,1)
plt.plot(df_comb.index, df_comb['Tasa_GRE'], 'b', label='Grecia', alpha=0.7)
plt.plot(df_comb.index, df_comb['Tasa_GER'], 'k', label='Alemania', alpha=0.7)
plt.title('Rendimientos Soberanos 10Y')
plt.ylabel('%')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(2,1,2)
plt.plot(df_comb.index, df_comb['Spread'], 'r', label='Spread')
plt.title('Spread (Riesgo Relativo)')
plt.ylabel('Diferencia %')
plt.fill_between(df_comb.index, df_comb['Spread'], 0, color='r', alpha=0.1)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/1_Rendimientos_Spread.png")
plt.close()

# Gráfico 2: MSPD
plt.figure(figsize=(8, 6))
plt.loglog(x_data, y_data, 'o', label='MSPD Real', markersize=3)
if not np.isnan(alpha_fit):
    plt.loglog(x_data, y_fit, 'r-', label=f'Ajuste (α={alpha_fit:.2f})')
    # Referencia Browniana
    plt.loglog(x_data, power_law(x_data, A_fit, 1), 'k--', label='Aleatorio (α=1)', alpha=0.5)

plt.title('Dinámica del Spread (MSPD)')
plt.xlabel(r'Tiempo $\tau$ (días)')
plt.ylabel(r'Desplazamiento $\langle \Delta x^2 \rangle$')
plt.legend()
plt.grid(True, which="both", alpha=0.2)
plt.savefig(f"{OUTPUT_DIR}/2_MSPD_Econofisica.png")
plt.close()

print(f"¡Listo! Revisa la carpeta '{OUTPUT_DIR}'")