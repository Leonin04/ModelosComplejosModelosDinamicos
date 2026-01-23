import streamlit as st

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Conclusiones y Agradecimientos",
    page_icon=":material/flag:", # Icono de meta/final
    layout="wide"
)

# Botón de volver a la portada
# st.page_link("Home.py", label="⬅️ Volver a la Portada", use_container_width=True)

st.title("🏁 Conclusiones del Estudio")
st.markdown("Síntesis de hallazgos y cierre del proyecto.")

st.divider()

# --- SECCIÓN 1: RESULTADOS TÉCNICOS ---
st.header("1. Hallazgos Cuantitativos")

col_metrics, col_text = st.columns([1, 2], gap="large")

with col_metrics:
    # Tarjetas métricas visuales
    with st.container(border=True):
        st.metric(
            label="Exponente de Hurst (α)", 
            value="0.94", 
            delta="Super-difusión",
            help="Un valor cercano a 1 indica comportamiento balístico y fuerte memoria."
        )
    
    with st.container(border=True):
        st.metric(
            label="Error GARCH (MSE)", 
            value="1692.09", 
            delta="Alta Volatilidad", 
            delta_color="inverse",
            help="El modelo econométrico captura los clústeres pero tiene mayor error puntual debido al ruido."
        )

with col_text:
    st.markdown("""
    **Interpretación Final:**
    
    1.  **Memoria del Mercado:** La serie temporal de la deuda griega no sigue un paseo aleatorio ($\\alpha \\neq 0.5$). El valor $\\alpha \\approx 0.94$ confirma una estructura de **memoria de largo alcance** persistente durante la crisis.
    
    2.  **Dualidad Metodológica:**
        * El enfoque de **Econofísica** (Difusión) resultó superior para describir la tendencia estructural y la naturaleza del fenómeno.
        * El enfoque de **Econometría** (GARCH) sigue siendo indispensable para la gestión de riesgos a corto plazo, a pesar de su complejidad computacional.
    """)

st.divider()

# --- SECCIÓN 2: AGRADECIMIENTOS (CARTA) ---
st.header("2. Agradecimientos")

# Diseño tipo "Carta" o "Diploma"
with st.container(border=True):
    col_logo, col_note = st.columns([1, 4])
    
    with col_logo:
        # Icono de birrete o universidad
        st.markdown("<div style='text-align: center; font-size: 4em;'>🎓</div>", unsafe_allow_html=True)
    
    with col_note:
        st.markdown("#### A la atención del Profesor José Luis Sáez Lozano")
        st.markdown("*Universidad de Granada*")
        
        st.write("") # Espacio
        
        st.markdown("""
        > Queremos expresar nuestro más sincero agradecimiento por su **asistencia, supervisión y guía** durante el desarrollo de este proyecto.
        >
        > Sus orientaciones en el marco del **Seminario de Modelización** han sido fundamentales para comprender la complejidad de los sistemas dinámicos y para integrar con rigor las perspectivas de la Física y la Economía. Gracias por impulsarnos a explorar más allá de los modelos tradicionales.
        """)
        
        st.write("")
        st.caption("Atentamente, El Grupo 4 (Ismael Sallami Moreno & David Bacas Posadas).")

st.divider()
st.caption("Seminario de Modelización 2025/26 - Facultad de Ciencias Económicas y Empresariales UGR")