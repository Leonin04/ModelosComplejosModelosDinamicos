import streamlit as st

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Metodología y Algoritmos",
    page_icon="📖",
    layout="wide"
)

# Botón de volver
# st.page_link("Home.py", label="⬅️ Volver a la Portada", use_container_width=True)

st.title("📖 Metodología Técnica")
st.markdown("""
Esta sección detalla la arquitectura matemática y computacional del proyecto. 
El código presentado aquí es una extracción directa del **Jupyter Notebook** utilizado para la calibración.
""")

# Dividimos en Pestañas para que sea limpio
tab1, tab2, tab3 = st.tabs(["🧹 Preprocesamiento", "🌀 Modelo Difusión (Física)", "⚡ Modelo GARCH (Bayesiano)"])

# --- PESTAÑA 1: DATOS ---
with tab1:
    st.header("1. Ingeniería de Datos")
    st.markdown("""
    Para construir la serie temporal de la **Prima de Riesgo**, se fusionaron los rendimientos de los bonos a 10 años 
    de Grecia y Alemania. Se realizaron los siguientes pasos:
    
    1.  **Limpieza:** Conversión de formatos europeos (comas por puntos).
    2.  **Sincronización:** Inner join por fecha para asegurar que solo analizamos días donde ambos mercados operaron.
    3.  **Cálculo:** Diferencial en Puntos Básicos (bps).
    """)
    
    st.code("""
# Fragmento del script de carga
def cargar_excel(archivo, keyword):
    # ... lógica de lectura ...
    df['Tasa'] = df['Tasa'].apply(convertir_coma_a_punto)
    return df.set_index('Fecha').sort_index()

# Fusión y cálculo del spread
df_comb = df_gre.join(df_ger, how='inner', lsuffix='_GRE', rsuffix='_GER')
df_comb['Prima_Riesgo'] = df_comb['Tasa_GRE'] - df_comb['Tasa_GER']

# Cálculo de variaciones (bps)
variacion_bps = df_comb['Prima_Riesgo'].diff().dropna() * 100
    """, language="python")

# --- PESTAÑA 2: DIFUSIÓN ---
with tab2:
    st.header("2. Enfoque de Econofísica: Difusión Anómala")
    st.info("El objetivo es determinar si la serie sigue un paseo aleatorio o tiene memoria.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Fundamento Matemático")
        st.markdown(r"""
        Se utiliza el **Desplazamiento Cuadrático Medio (MSPD)**. Para un retardo temporal $\tau$, calculamos:
        
        $$
        \langle (\Delta x)^2 \rangle = \frac{1}{N-\tau} \sum_{i=1}^{N-\tau} (x(i+\tau) - x(i))^2
        $$
        
        Se asume una ley de potencia:
        $$
        MSPD(\tau) \sim \tau^\alpha
        $$
        
        * Si $\alpha = 1$: Difusión Normal (Aleatorio).
        * Si $\alpha \neq 1$: Difusión Anómala (Memoria/Fractalidad).
        """)
        
    with col2:
        st.markdown("### Implementación en Python")
        st.code("""
def calcular_mspd(serie, max_tau=252):
    res = {}
    vals = serie.values
    for tau in range(1, max_tau + 1):
        # Vectorización numpy para velocidad
        displacements = (vals[tau:] - vals[:-tau])**2
        res[tau] = np.mean(displacements)
    return pd.Series(res)

def power_law(t, A, alpha): 
    return A * (t ** alpha)
        """, language="python")

# --- PESTAÑA 3: GARCH ---
with tab3:
    st.header("3. Enfoque Econométrico: GARCH Bayesiano")
    st.warning("⚠️ Este modelo es computacionalmente intensivo y utiliza cadenas de Markov (MCMC).")
    
    st.markdown("### Especificación del Modelo")
    st.markdown(r"""
    A diferencia del GARCH clásico (frecuentista), aquí tratamos los parámetros como variables aleatorias.
    Usamos la librería **PyMC** para definir el modelo probabilístico:
    
    $$
    \begin{aligned}
    y_t &\sim \text{StudentT}(\nu, 0, \sigma_t) \\
    \sigma_t^2 &= \omega + \alpha y_{t-1}^2 + \beta \sigma_{t-1}^2
    \end{aligned}
    $$
    """)
    
    st.markdown("### Código Probabilístico (PyMC)")
    st.markdown("Extraído de `Modelo.ipynb`:")
    
    st.code("""
import pymc as pm
import pytensor.tensor as pt

with pm.Model() as garch_model:
    # 1. Priors (Débilmente informativos)
    omega = pm.InverseGamma("omega", alpha=2.5, beta=1.0)
    alpha = pm.Beta("alpha", alpha=2, beta=5)
    beta = pm.Beta("beta", alpha=5, beta=2)
    nu = pm.Gamma("nu", alpha=2, beta=0.1) 

    # 2. Definición del proceso dinámico (GARCH Loop)
    def garch_step(y_tm1, sigma2_tm1, omega, alpha, beta, mu):
        return omega + alpha * ((y_tm1 - mu)**2) + beta * sigma2_tm1

    # Pytensor scan permite bucles simbólicos eficientes
    sigma2_cycle, _ = pytensor.scan(
        fn=garch_step,
        sequences=[y_scaled[:-1]], 
        outputs_info=[sigma2_0], 
        non_sequences=[omega, alpha, beta, mu]
    )
    
    # 3. Inferencia (NUTS Sampler)
    trace = pm.sample(draws=1000, tune=1000, chains=4)
    """, language="python")

st.divider()
st.markdown("### 📥 Descarga del Código Fuente")
st.markdown("Puedes descargar el archivo `.ipynb` completo y los datos desde la página principal o desde el repositorio adjunto.")

# Enlace al dashboard para probarlo
st.info("Ahora que conoces la teoría, experimenta con los parámetros en el Dashboard.")
with st.container():
    st.page_link(
        "pages/1_Dashboard.py", 
        label="Ir al Laboratorio Interactivo", 
        icon=":material/ads_click:",  
        use_container_width=True
    )