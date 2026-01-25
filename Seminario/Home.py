import streamlit as st
import os
import zipfile
import io

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Seminario de Modelización | Grupo 4",
    page_icon="🏛️",
    layout="wide"
)

# Estilos CSS para dar apariencia de documento académico (tipo LaTeX)
st.markdown("""
<style>
    h1 {font-family: 'Helvetica', sans-serif; color: #2c3e50; font-weight: 700;}
    h2 {font-family: 'Helvetica', sans-serif; color: #34495e; font-weight: 600; padding-top: 1rem;}
    h3 {font-family: 'Helvetica', sans-serif; color: #7f8c8d;}
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
        color: #2c3e50;
        border: 1px solid #d1d5db;
    }
    .stButton>button:hover {
        border-color: #2c3e50;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCIONES UTILITARIAS
# ==========================================
def create_zip_of_project():
    """Empaqueta el código fuente y datos para descarga."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        allowed_extensions = {'.py', '.xlsx', '.pdf', '.mp4'}
        exclude_dirs = {'__pycache__', '.git', '.ipynb_checkpoints'}
        
        # Archivos raíz
        for file in os.listdir('.'):
            if os.path.isfile(file) and os.path.splitext(file)[1].lower() in allowed_extensions:
                zip_file.write(file, arcname=file)
        
        # Archivos en pages
        if os.path.exists('pages'):
            for file in os.listdir('pages'):
                if os.path.isfile(os.path.join('pages', file)) and os.path.splitext(file)[1].lower() in allowed_extensions:
                    zip_file.write(os.path.join('pages', file), arcname=os.path.join('pages', file))
                    
    buffer.seek(0)
    return buffer

# ==========================================
# CONTENIDO PRINCIPAL
# ==========================================

# 1. Cabecera Institucional (Sin columnas, todo a la izquierda)
st.title("Análisis de la Prima de Riesgo Griega")
st.markdown("### *Un Enfoque Comparativo entre Econofísica y Econometría Bayesiana*")
st.markdown("**Seminario de Modelización 2025/26 - Grupo 4**")

st.divider()

# 2. Video Introductorio y Resumen
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("## Presentación del Proyecto")

    HOME_DIR = os.path.dirname(os.path.abspath(__file__))

    # 2. Construir la ruta al video sumando carpetas
    # Buscamos en: Seminario/web_files/Crisis_de_la_Deuda_Griega.mp4
    video_path = os.path.join(HOME_DIR, "web_files", "Crisis_de_la_Deuda_Griega.mp4")
    
    if os.path.exists(video_path):
        st.video(video_path)
    else:
        st.info("El video introductorio no se encuentra disponible en el servidor. Ruta esperada: " + video_path)
        
    st.markdown("### Resumen Ejecutivo")
    st.markdown("""
    Este trabajo analiza la dinámica estocástica de la prima de riesgo griega respecto al bono alemán durante la crisis de deuda soberana. 
    Se contrastan dos enfoques metodológicos fundamentales:
    
    * **Econofísica (Difusión Anómala):** Evalúa la memoria del mercado a largo plazo mediante leyes de potencia.
    * **Econometría (GARCH Bayesiano):** Modela la volatilidad condicional y el agrupamiento de volatilidad a corto plazo.
    * Se incluye un **video introductorio** que contextualiza la crisis y los objetivos del estudio, para aquellos que no sepan del tema.
    """)

with col_right:
    st.markdown("## Metodología y Hallazgos")
    
    with st.container(border=True):
        st.markdown("**1. Comportamiento Super-difusivo**")
        st.markdown(r"""
        Los resultados empíricos revelan un exponente de escala $\alpha \approx 0.94$. Esto evidencia una fuerte persistencia 
        y memoria en el mercado de renta fija, contradiciendo la hipótesis del paseo aleatorio ($\alpha = 0.5$).
        """)
        
    with st.container(border=True):
        st.markdown("**2. Comparativa de Modelos (MSE)**")
        st.markdown(r"""
        El modelo de difusión ofrece un ajuste estructural superior para describir la naturaleza física del fenómeno, 
        mientras que el GARCH captura el ruido diario.
        
        * **MSE Difusión:** 8.39 (Ajuste estructural robusto)
        * **MSE GARCH:** 1692.09 (Alta sensibilidad al ruido diario)
        """)

    st.markdown("### Acceso a la Simulación")
    st.write("Ejecute los modelos, modifique los parámetros de Hurst y visualice la volatilidad en tiempo real.")
    
    # === EL ENLACE AL DASHBOARD ===
    # Esto busca el archivo en la carpeta 'pages' automáticamente
    st.page_link("pages/2_Dashboard.py", label="ACCEDER AL DASHBOARD INTERACTIVO", icon="📈", use_container_width=True)

st.divider()

# 3. Zona de Descargas y Autores
st.subheader("Recursos Adicionales y Autoría")

c_down, c_auth = st.columns([1, 1])

with c_down:
    st.markdown("**Descarga de Materiales**")
    
    # PDF
    pdf_path = "paper_final.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Descargar Paper Completo (PDF)",
                data=pdf_file,
                file_name="Seminario_Grupo4_Econofisica.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    
    # Código ZIP
    st.download_button(
        label="Descargar Repositorio de Código (ZIP)",
        data=create_zip_of_project(),
        file_name="Proyecto_Econofisica.zip",
        mime="application/zip",
        use_container_width=True
    )

with c_auth:
    st.markdown("**Autores**")
    # Sustituye con los nombres reales
    st.markdown("""
    * Ismael Sallami Moreno
    * David Bacas Posadas
    """)
    st.caption("Universidad de Granada - Facultad de Ciencias Económicas y Empresariales")