import streamlit as st
import os
import zipfile
import io

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS ABSOLUTAS
# ==========================================
# Definimos la ruta base donde está este archivo (Home.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# 2. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Seminario de Modelización | Grupo 4",
    page_icon="🏛️",
    layout="wide"
)

# Estilos CSS para dar apariencia de documento académico
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
# 3. FUNCIONES UTILITARIAS
# ==========================================
def create_zip_of_project():
    """
    Crea un archivo ZIP en memoria con todo el contenido de la carpeta del proyecto,
    excluyendo archivos basura o pesados (venv, git, etc).
    """
    buffer = io.BytesIO()
    
    # Carpetas y archivos a ignorar para que el ZIP no pese demasiado
    EXCLUDE_DIRS = {'.git', '__pycache__', 'venv', '.venv', '.streamlit', 'environment_files', 'installers'}
    EXCLUDE_FILES = {'.DS_Store', '.gitignore'}

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(BASE_DIR):
            # Filtrar carpetas no deseadas
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES or file.endswith('.pyc'):
                    continue
                
                # Ruta absoluta del archivo
                file_path = os.path.join(root, file)
                # Ruta relativa dentro del ZIP
                arcname = os.path.relpath(file_path, BASE_DIR)
                
                try:
                    zip_file.write(file_path, arcname)
                except Exception as e:
                    print(f"No se pudo incluir {file}: {e}")
                    
    buffer.seek(0)
    return buffer

# ==========================================
# 4. CONTENIDO PRINCIPAL
# ==========================================

st.title("Análisis de la Prima de Riesgo Griega")
st.markdown("### *Un Enfoque Comparativo entre Econofísica y Econometría Bayesiana*")
st.markdown("**Seminario de Modelización 2025/26 - Grupo 4**")

st.divider()

# --- Video Introductorio y Resumen ---
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("## Presentación del Proyecto")

    # Ruta absoluta al video (carpeta web_files)
    video_path = os.path.join(BASE_DIR, "web_files", "Crisis_de_la_Deuda_Griega.mp4")
    
    if os.path.exists(video_path):
        st.video(video_path)
    else:
        st.info(f"⚠️ Video no encontrado en: {video_path}")
        
    st.markdown("### Resumen Ejecutivo")
    st.markdown("""
    Este trabajo analiza la dinámica estocástica de la prima de riesgo griega respecto al bono alemán durante la crisis de deuda soberana. 
    Se contrastan dos enfoques metodológicos fundamentales:
    
    * **Econofísica (Difusión Anómala):** Evalúa la memoria del mercado a largo plazo mediante leyes de potencia.
    * **Econometría (GARCH Bayesiano):** Modela la volatilidad condicional y el agrupamiento de volatilidad a corto plazo.
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
    
    # Enlace interno al Dashboard
    st.page_link("pages/2_Dashboard.py", label="ACCEDER AL DASHBOARD INTERACTIVO", icon="📈", use_container_width=True)

st.divider()

# --- Zona de Descargas y Autores ---
st.subheader("Recursos Adicionales y Autoría")

c_down, c_auth = st.columns([1, 1])

with c_down:
    st.markdown("**Descarga de Materiales**")
    
    # Lógica inteligente para encontrar el PDF (primero en static, luego en raíz)
    pdf_path_static = os.path.join(BASE_DIR, "static", "paper_final.pdf")
    pdf_path_root = os.path.join(BASE_DIR, "paper_final.pdf")
    
    final_pdf_path = None
    if os.path.exists(pdf_path_static):
        final_pdf_path = pdf_path_static
    elif os.path.exists(pdf_path_root):
        final_pdf_path = pdf_path_root
    
    # Botón de PDF
    if final_pdf_path:
        with open(final_pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📄 Descargar Paper Completo (PDF)",
                data=pdf_file,
                file_name="Seminario_Grupo4_Econofisica.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.warning("⚠️ El PDF del paper no se encontró en el servidor.")
    
    # Botón de ZIP (Generado al vuelo)
    try:
        st.download_button(
            label="📦 Descargar Repositorio de Código (ZIP)",
            data=create_zip_of_project(),
            file_name="Proyecto_Econofisica_Grupo4.zip",
            mime="application/zip",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error generando el ZIP: {e}")

with c_auth:
    st.markdown("**Autores**")
    st.markdown("""
    * **Ismael Sallami Moreno**
    * **David Bacas Posadas**
    """)
    st.caption("Universidad de Granada - Facultad de Ciencias Económicas y Empresariales")