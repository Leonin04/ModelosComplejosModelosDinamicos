import streamlit as st
import os

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Documentación Técnica",
    page_icon=":material/folder_open:", 
    layout="wide"
)

# Botón de volver a la portada
# st.page_link("Home.py", label="⬅️ Volver a la Portada", use_container_width=True)

st.title("📂 Documentación del Proyecto")
st.markdown("Especificaciones técnicas, arquitectura de despliegue y manual de uso.")

# --- ENLACE A GITHUB ---
# Recuerda poner tu enlace real aquí
GITHUB_LINK = "https://github.com/Leonin04/ModelosComplejosModelosDinamicos"

col_repo, col_req = st.columns([1, 2])
with col_repo:
    st.info("🌐 **Repositorio Remoto**")
    st.markdown("Código fuente y control de versiones.")
    st.link_button("Acceder a GitHub", GITHUB_LINK, type="primary", icon=":material/code:", use_container_width=True)

with col_req:
    st.warning("⚠️ **Stack Tecnológico**")
    st.markdown("Este proyecto opera sobre un entorno **Conda** aislado debido a la complejidad de las dependencias Bayesianas (`PyMC` + `ArviZ`).")

st.divider()

# ==========================================
# VISUALIZADOR DE DOCUMENTACIÓN
# ==========================================

tab_struct, tab_install, tab_readme = st.tabs([
    "🏗️ Arquitectura de Archivos", 
    "💻 Instalación y Uso", 
    "📄 README.md (Original)"
])

# --- PESTAÑA 1: ARQUITECTURA (VISUAL) ---
with tab_struct:
    st.subheader("Mapa de la Aplicación")
    st.markdown("El proyecto sigue una estructura **Multi-Page App** con nombres técnicos limpios:")
    
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("📂 Raíz (Configuración y Datos)", expanded=True):
            st.markdown("""
            * `Home.py`: **Main Entry Point**. Portada institucional.
            * `script.py`: Motor de calibración (Backend).
            * `Modelo.ipynb`: Cuaderno de desarrollo y teoría.
            * `Crisis_de_la_Deuda_Griega.mp4`: Video introductorio.
            * `paper_final.pdf`: Memoria del proyecto.
            * `ActivarEntorno.sh`: Script de configuración.
            * `germany.xlsx` / `greece.xlsx`: Dataset.
            """)
    with c2:
        with st.expander("📂 pages/ (Módulos de la App)", expanded=True):
            st.markdown("""
            * `1_Metodologia.py`: Teoría Matemática.
            * `2_Dashboard.py`: Laboratorio Interactivo.
            * `3_Documentacion.py`: Esta página técnica.
            * `4_Conclusiones.py`: Hallazgos y agradecimientos.
            """)

# --- PESTAÑA 2: INSTALACIÓN (COMANDOS) ---
with tab_install:
    st.subheader("🚀 Guía de Ejecución Automática")
    st.markdown("Este proyecto incluye scripts de autoinstalación que configuran el entorno y lanzan la aplicación en un solo paso.")

    col_win, col_unix = st.columns(2, gap="medium")

    # Columna Windows
    with col_win:
        st.info("🪟 **Para Windows**")
        st.markdown("""
        1. Localice el archivo `setup_windows.bat` en la raíz.
        2. Haga **doble clic** sobre él.
        3. Espere a que se configure el entorno y se abra el navegador.
        """)
        st.caption("Requisito: Tener Anaconda/Miniconda instalado.")

    # Columna Linux/Mac
    with col_unix:
        st.info("🐧 **Para Linux / macOS**")
        st.markdown("Abra una terminal en la carpeta del proyecto y ejecute:")
        st.code("bash setup_unix.sh", language="bash")
        st.markdown("El script verificará Conda, instalará dependencias y lanzará la web.")

    st.divider()
    
    st.markdown("#### 🛠️ Ejecución Manual (Alternativa)")
    st.markdown("Si prefiere tener control total sobre el proceso, use los comandos estándar:")
    st.code("""
# 1. Crear entorno
conda env create -f environment.yml

# 2. Activar
conda activate Seminario_EM

# 3. Lanzar
streamlit run Home.py
    """, language="bash")

# --- PESTAÑA 3: README RAW (Lectura dinámica) ---
with tab_readme:
    st.markdown("### Contenido del archivo README.md")
    
    # Lógica para encontrar el README desde la carpeta pages/
    readme_path = "../README.md"
    
    if not os.path.exists(readme_path):
        readme_path = "README.md" # Fallback por si cambia la estructura

    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()
        st.markdown(readme_content)
    else:
        st.error("No se encontró el archivo README.md en la ruta esperada.")

st.divider()
st.caption("Seminario de Modelización 2025/26 - Grupo 4")