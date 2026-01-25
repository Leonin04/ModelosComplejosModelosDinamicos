import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
import os

# Ignorar advertencias de cálculo
warnings.filterwarnings('ignore')

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Greek Debt Crisis Lab",
    page_icon="🏛️",
    layout="wide",
)

# # ==========================================
# # BOTÓN DE NAVEGACIÓN (VOLVER)
# # ==========================================
# # Esto crea un botón limpio en la parte superior para regresar
# st.page_link("Home.py", label="⬅️ Volver a la Presentación", use_container_width=True)

# st.divider() # Una línea separadora para que quede ordenado

st.title("🏛️ Laboratorio de Riesgo Soberano: La Crisis Griega")
st.markdown("""
Esta aplicación interactiva permite explorar la dinámica de la prima de riesgo griega 
(diferencial del bono a 10 años vs Alemania) durante la crisis de deuda soberana, comparando 
perspectivas de la **Econofísica (Difusión)** y la **Econometría (GARCH)**.
""")

# ==========================================
# FUNCIONES DE CARGA Y CÁLCULO
# ==========================================
@st.cache_data
def load_data_robusto():
    """
    Carga y limpia los datos de Grecia y Alemania con múltiples comprobaciones.
    """
    def limpiar_tasa(x):
        if pd.isna(x): return np.nan
        if isinstance(x, (int, float)): return float(x)
        s = str(x).strip().replace(',', '.')
        try: return float(s)
        except ValueError: return np.nan

    def leer_y_procesar(archivo, keyword_col):
        try:
            df = pd.read_excel(archivo)
            
            # Buscar columna Fecha
            cols_lower = [str(c).lower() for c in df.columns]
            col_fecha_candidates = [c for c, cl in zip(df.columns, cols_lower) if 'date' in cl or 'fecha' in cl]
            col_fecha = col_fecha_candidates[0] if col_fecha_candidates else df.columns[0]
                
            # Buscar columna Datos
            col_dato_candidates = [c for c, cl in zip(df.columns, cols_lower) if keyword_col.lower() in cl]
            
            if not col_dato_candidates:
                # Heurística de posición si falla el nombre
                idx_tentativo = 4 if "greece" in archivo.lower() or "grecia" in archivo.lower() else 1
                col_dato = df.columns[idx_tentativo] if idx_tentativo < len(df.columns) else None
                if not col_dato: return None
            else:
                col_dato = col_dato_candidates[0]

            df_final = df[[col_fecha, col_dato]].copy()
            df_final.columns = ['Fecha', 'Tasa']
            df_final['Fecha'] = pd.to_datetime(df_final['Fecha'], errors='coerce', dayfirst=True)
            df_final['Tasa'] = df_final['Tasa'].apply(limpiar_tasa)
            
            return df_final.dropna().set_index('Fecha').sort_index()
            
        except Exception as e:
            st.error(f"Error cargando {archivo}: {e}")
            return None

    df_ger = leer_y_procesar("data/germany.xlsx", "Germany")
    df_gre = leer_y_procesar("data/greece.xlsx", "Grecia")
    
    if df_ger is None or df_gre is None or df_ger.empty or df_gre.empty:
        return None
        
    df_comb = df_gre.join(df_ger, how='inner', lsuffix='_GRE', rsuffix='_GER')
    # Prima en Puntos Básicos (bps)
    df_comb['Prima_Riesgo_Bps'] = (df_comb['Tasa_GRE'] - df_comb['Tasa_GER']) * 100
    
    return df_comb

# @st.cache_data
# def calculate_ewma_volatility(series, lambda_=0.94):
#     """
#     Calcula la volatilidad EWMA (RiskMetrics), un proxy muy bueno del GARCH
#     que se puede calcular en tiempo real.
#     """
#     returns = series.diff().dropna()
#     n = len(returns)
#     variance = np.zeros(n)
#     variance[0] = returns.var()
    
#     # Bucle optimizado con numba sería mejor, pero esto es suficientemente rápido para n<5000
#     for t in range(1, n):
#         variance[t] = lambda_ * variance[t-1] + (1 - lambda_) * returns[t]**2
        
#     volatility = np.sqrt(variance)
#     return pd.Series(volatility, index=returns.index)

def calculate_ewma_volatility(series, lambda_=0.94):
    """
    Calcula la volatilidad EWMA.
    Usa .values para ignorar el índice de fechas y evitar KeyError.
    """
    # 1. Obtenemos la serie de diferencias
    returns = series.diff().dropna()
    
    # 2. ¡IMPORTANTE! Extraemos solo los números (array numpy)
    # Así podemos usar [t] como posición 0, 1, 2... sin importar si el índice es fecha.
    returns_arr = returns.values 
    
    n = len(returns)
    variance = np.zeros(n)
    variance[0] = returns.var()
    
    # 3. Iteramos sobre el array de números, no sobre la serie de pandas
    for t in range(1, n):
        # Usamos returns_arr[t] en vez de returns[t]
        variance[t] = lambda_ * variance[t-1] + (1 - lambda_) * returns_arr[t]**2
        
    # 4. Volvemos a ponerle las fechas al resultado final
    return pd.Series(np.sqrt(variance), index=returns.index)

# Carga inicial
df_total = load_data_robusto()

if df_total is None:
    st.error("⚠️ Error: No se encontraron 'germany.xlsx' o 'greece.xlsx'.")
    st.stop()

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================

tab1, tab2, tab3 = st.tabs(["📊 Fase 1: Datos", "🌀 Fase 2: Difusión (Física)", "⚡ Fase 3: Volatilidad (GARCH)"])

# --- PESTAÑA 1: DATOS ---
with tab1:
    st.subheader("Evolución de la Prima de Riesgo")
    
    with st.sidebar:
        st.header("Filtros")
        min_d, max_d = df_total.index.min().date(), df_total.index.max().date()
        start_date = st.date_input("Inicio", pd.to_datetime("2008-01-01").date(), min_value=min_d, max_value=max_d)
        end_date = st.date_input("Fin", pd.to_datetime("2013-12-31").date(), min_value=min_d, max_value=max_d)

    mask = (df_total.index.date >= start_date) & (df_total.index.date <= end_date)
    df_filtered = df_total.loc[mask]

    if not df_filtered.empty:
        fig_main = px.line(df_filtered, y='Prima_Riesgo_Bps', 
                           title=f'Diferencial Grecia-Alemania', labels={'Prima_Riesgo_Bps': 'bps'})
        fig_main.update_traces(line_color='#b71c1c')
        st.plotly_chart(fig_main, use_container_width=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Máximo", f"{df_filtered['Prima_Riesgo_Bps'].max():.0f} bps")
        c2.metric("Mínimo", f"{df_filtered['Prima_Riesgo_Bps'].min():.0f} bps")
        c3.metric("Volatilidad (Std)", f"{df_filtered['Prima_Riesgo_Bps'].std():.0f} bps")

# --- PESTAÑA 2: DIFUSIÓN ---
with tab2:
    st.subheader("Análisis de Difusión (Econofísica)")
    st.markdown(r"Ajuste de la Ley de Potencia: $MSPD(\tau) = A \cdot \tau^\alpha$")
    
    # Cálculo rápido MSPD
    vals = df_filtered['Prima_Riesgo_Bps'].values
    max_tau = min(250, len(vals) // 4)
    if max_tau > 10:
        taus = np.arange(1, max_tau + 1)
        # Vectorizado: (vals[tau:] - vals[:-tau])^2
        msd = [np.mean((vals[t:] - vals[:-t])**2) for t in taus]
        x_mspd, y_mspd = np.array(taus), np.array(msd)
        
        col_slider, col_viz = st.columns([1, 3])
        alpha = col_slider.slider("Alpha (Exponente)", 0.5, 2.0, 0.94, 0.01)
        
        # Corrección de Amplitud Automática
        # A = media(y / x^alpha)
        A_est = np.mean(y_mspd / (x_mspd ** alpha))
        y_teorica = A_est * (x_mspd ** alpha)
        
        fig_diff = go.Figure()
        fig_diff.add_trace(go.Scatter(x=x_mspd, y=y_mspd, mode='markers', name='Datos Reales'))
        fig_diff.add_trace(go.Scatter(x=x_mspd, y=y_teorica, mode='lines', 
                                      name=f'Teoría (α={alpha:.2f})', line=dict(color='red', dash='dash')))
        fig_diff.update_layout(xaxis_type="log", yaxis_type="log", title="Difusión Log-Log", height=500)
        col_viz.plotly_chart(fig_diff, use_container_width=True)
        
        interp = "Super-difusión (Crisis/Memoria)" if alpha > 1.1 else ("Sub-difusión (Estabilidad)" if alpha < 0.9 else "Paseo Aleatorio (Normal)")
        col_slider.info(f"**Régimen:** {interp}")

# --- PESTAÑA 3: GARCH (AHORA ROBUSTA) ---
with tab3:
    st.subheader("Modelo de Volatilidad Estocástica")
    
    st.markdown("""
    Aquí analizamos cómo cambia el riesgo (volatilidad) día a día.
    """)
    
    # 1. Intentar cargar imagen estática (Modelo Bayesiano Completo)
    image_path = "analisis_grecia_calibracion_mse/Modelo_GARCH_Fit.png"
    
    if os.path.exists(image_path):
        st.success("✅ Resultados del Modelo Bayesiano (MCMC) encontrados.")
        st.image(image_path, caption="Volatilidad Posterior (Sigma) estimada por MCMC", use_container_width=True)
        st.caption("Nota: Esta gráfica es estática y proviene de la ejecución previa del modelo completo.")
        
    else:
        # 2. FALLBACK: Calcular Modelo EWMA en vivo si no hay imagen
        st.warning("⚠️ No se encontró la imagen pre-calculada del modelo Bayesiano (requiere mucho tiempo de cómputo).")
        st.info("⚡ **Generando en tiempo real:** Modelo EWMA (RiskMetrics), un proxy industrial del GARCH.")
        
        if not df_filtered.empty:
            vol_ewma = calculate_ewma_volatility(df_filtered['Prima_Riesgo_Bps'])
            
            # Graficar con Plotly
            fig_vol = go.Figure()
            
            # Retornos absolutos (Fondo gris)
            retornos = df_filtered['Prima_Riesgo_Bps'].diff().abs()
            fig_vol.add_trace(go.Scatter(
                x=retornos.index, y=retornos,
                mode='lines', name='Variación Diaria Absoluta',
                line=dict(color='gray', width=1), opacity=0.3
            ))
            
            # Volatilidad Estimada (Línea Roja)
            fig_vol.add_trace(go.Scatter(
                x=vol_ewma.index, y=vol_ewma,
                mode='lines', name='Volatilidad Estimada (EWMA)',
                line=dict(color='#b71c1c', width=2)
            ))
            
            fig_vol.update_layout(
                title="Estimación Dinámica de la Volatilidad (Proxy GARCH)",
                yaxis_title="Volatilidad (bps)",
                template="plotly_white",
                height=500
            )
            st.plotly_chart(fig_vol, use_container_width=True)

    # Métricas Comparativas (Siempre visibles)
    st.markdown("---")
    st.markdown("### 📉 Comparativa de Error (MSE)")
    c1, c2 = st.columns(2)
    c1.metric("MSE Difusión", "8.39", "Ajuste Estructural")
    c2.metric("MSE Volatilidad", "1692.09", "Ajuste Diario (Alto Ruido)", delta_color="off")