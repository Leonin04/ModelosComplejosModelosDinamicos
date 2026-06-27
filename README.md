# Seminario de Modelización: Modelos Complejos vs Modelos Dinámicos
## Análisis de la Prima de Riesgo en la Crisis de Deuda Soberana (2008-2013)

**Asignatura:** Seminario de Modelización (2025-26)
**Grupo:** 4
**Autores:** Ismael Sallami Moreno & David Bacas Posadas

---

## Acceso Inmediato (Cloud)
Este proyecto ha sido desplegado en la nube. Puedes interactuar con la aplicación y visualizar los resultados sin necesidad de instalación local:

**[Ver aplicación web desplegada](https://emsemgrupo4.streamlit.app/)**


> **Advertencia:** Si se opta por realizar pruebas siguiendo las siguientes guías se debe de tener un conocimiento básico sobre como gestionar entornos y demás.

---

## Descripción del Proyecto

Este trabajo presenta un estudio comparativo computacional entre dos enfoques metodológicos dispares para explicar la dinámica del diferencial del bono griego a 10 años respecto al Bund alemán (Prima de Riesgo) durante los años más críticos de la crisis financiera.

1.  **Enfoque de Econofísica:** Utiliza modelos de **Difusión Anómala** y análisis de *Mean Squared Displacement* (MSPD) para detectar comportamientos de memoria a largo plazo (super-difusión) y leyes de potencia en la serie temporal.
2.  **Enfoque Econométrico:** Implementa modelos de **Volatilidad Estocástica GARCH(1,1)** calibrados mediante inferencia Bayesiana (MCMC - Markov Chain Monte Carlo) para capturar la agrupación de volatilidad y el riesgo diario.

---

## Estructura Detallada del Repositorio

El repositorio se divide en dos grandes bloques: `/Recursos` (entorno de desarrollo e investigación) y `/Seminario` (producto final). A continuación, se detalla la arquitectura de la carpeta de producción **`/Seminario`**:

### `/Seminario` (Entorno de Producción)
Esta carpeta contiene la aplicación final, limpia y estructurada modularmente.

#### 1. Raíz de la Aplicación
* **`Home.py`**: **Punto de Entrada.** Es el script principal que ejecuta Streamlit. Orquesta la navegación entre páginas y presenta la introducción institucional.
* **`script.py`**: **Motor de Cálculo.** Este script independiente contiene la lógica pesada del proyecto. Realiza la calibración del modelo GARCH utilizando `PyMC`, ejecuta las cadenas de Markov (MCMC) y genera las imágenes estáticas de los resultados.
* **`paper_final.pdf`**: **Memoria Académica.** El documento PDF final con todo el desarrollo teórico, matemático y las conclusiones del seminario.

#### 2. Módulos y Código (`/pages`)
La lógica de visualización se ha desacoplado en páginas independientes para facilitar el mantenimiento:
* **`1_Metodologia.py`**: Expone el marco teórico. Muestra las ecuaciones de la Ley de Potencia (Econofísica) frente a la especificación GARCH (Econometría) y permite ver fragmentos de código.
* **`2_Dashboard.py`**: **Laboratorio Interactivo.** Es el núcleo de la visualización. Carga los datos, calcula métricas en tiempo real y permite al usuario interactuar con los gráficos dinámicos de Plotly.
* **`3_Documentacion.py`**: Manual técnico integrado en la web. Explica la estructura de archivos y las instrucciones de uso.
* **`4_Conclusiones.py`**: Síntesis de hallazgos, tabla comparativa de errores (MSE) y agradecimientos.

#### 3. Datos (`/data`)
Contiene la materia prima del análisis:
* **`germany.xlsx`**: Serie temporal histórica de los rendimientos del bono alemán (Bund) a 10 años.
* **`greece.xlsx`**: Serie temporal histórica de los rendimientos del bono griego a 10 años.
    * *Nota:* Los datos son procesados y limpiados en tiempo real por el `Dashboard.py` para calcular el *Spread*.

#### 4. Cuadernos de Investigación (`/Notebooks`)
* **`Modelo.ipynb`**: **Jupyter Notebook.** Contiene el desarrollo "paso a paso" y pedagógico del proyecto. Ideal para entender la lógica secuencial del análisis de datos, las pruebas de difusión y la construcción del modelo Bayesiano antes de ser pasados a la web.

#### 5. Resultados Pre-Calculados (`/analisis_grecia_calibracion_mse`)
Almacena los artefactos generados por `script.py`. Dado que el modelo Bayesiano tarda mucho en computar, las gráficas se guardan aquí como imágenes estáticas para que la web cargue rápido:
* **`Modelo_GARCH_Fit.png`**: Visualización de la volatilidad posterior estimada (traza MCMC).
* **`Modelo_Difusion_Fit.png`**: Gráfica Log-Log del ajuste de la ley de potencia.

#### 6. Configuración del Entorno (`/environment_files`)
Archivos necesarios para replicar el entorno de Python exacto:
* **`environment.yml`**: Lista completa de dependencias (Streamlit, PyMC, ArviZ, Plotly, etc.) para Anaconda.
* **`ActivarEntorno.sh` / `DesactivarEntorno.sh`**: Scripts auxiliares para gestión manual del entorno.

#### 7. Automatización (`/installers`)
Scripts para facilitar la ejecución a usuarios sin experiencia técnica:
* **`setup_windows.bat`**: Instalador "doble clic" para Windows.
* **`setup_unix.sh`**: Instalador automático para Linux y macOS.

#### 8. Recursos Web (`/web_files`)
* **`Crisis_de_la_Deuda_Griega.mp4`**: Video generado por IA (Avatar) que se reproduce en la portada de la aplicación.

#### 9. Código Fuente LaTeX (`/Documentacion_LaTeX...`)
Contiene todos los archivos `.tex`, `.bib` y recursos vectoriales necesarios para compilar el `paper_final.pdf`.

---

## Guía de Instalación y Ejecución Local

Si deseas ejecutar el proyecto en tu propio ordenador, sigue estos pasos. Es necesario situarse dentro de la estructura del proyecto.

### A. Ejecución Automática (Recomendada)
Estos scripts configuran el entorno y lanzan la aplicación automáticamente.

* **Windows:**
    1. Navega a la carpeta `Seminario/installers`.
    2. Haz doble clic en `setup_windows.bat`.

* **Linux / macOS:**
    1. Abre una terminal en la raíz del repositorio.
    2. Ejecuta:
       ```bash
       bash Seminario/installers/setup_unix.sh
       ```

    > Nota: Debes de tener conda o miniconda instalado.

### B. Ejecución Manual (Expertos)
Si prefieres usar la terminal paso a paso:

1.  **Crear el entorno Conda:**
    ```bash
    conda env create -f Seminario/environment_files/environment.yml
    ```
2.  **Activar el entorno:**
    ```bash
    conda activate Seminario_EM
    ```
3.  **Lanzar la aplicación:**
    Es importante ejecutar el comando apuntando al archivo `Home.py` dentro de la carpeta `Seminario`.
    ```bash
    streamlit run Seminario/Home.py
    ```

### C. Ejecución Ultra-Rápida con `uv` (Experimental / Moderno)
Para usuarios avanzados que deseen tiempos de instalación casi instantáneos, soportamos **uv**, un gestor de paquetes de nueva generación escrito en Rust.

1.  **Instalar uv** (si no lo tienes):
    ```bash
    pip install uv
    ```

2.  **Configurar y Ejecutar (en segundos):**
    ```bash
    cd Seminario
    
    # 1. Crear entorno virtual
    uv venv
    
    # 2. Activar entorno
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    
    # 3. Instalar dependencias a velocidad luz
    uv pip install -r requirements.txt
    
    # 4. Lanzar
    streamlit run Home.py
    ```

---
> Alternativamente, si ya dispones de las dependencias instaladas (por ejemplo, `streamlit`, `pymc`, `plotly`, etc.), puedes lanzar la aplicación invocando Streamlit como módulo de Python. Nótese que una aplicación Streamlit no se ejecuta con `python Home.py`, sino a través de Streamlit:
>
> ```bash
> python -m streamlit run Seminario/Home.py
> ```
>
> El motor de cálculo (`script.py`) sí es un script independiente y puede ejecutarse directamente con Python. Debe lanzarse desde dentro de la carpeta `Seminario`, ya que utiliza rutas relativas hacia `data/`:
>
> ```bash
> cd Seminario
> python3 script.py
> ```

---

## Resumen de Resultados Técnicos

| Modelo              | Parámetro Clave        | MSE (Error) | Interpretación del Hallazgo                                                                      |
|---------------------|------------------------|-------------|--------------------------------------------------------------------------------------------------|
| **Difusión (Física)** | $\alpha \approx 0.94$  | **8.39** | El exponente cercano a 1 indica **super-difusión**. Los shocks en la prima de riesgo tienen memoria y persisten en el tiempo. |
| **GARCH (Bayesiano)** | $\hat{R} \approx 1.01$ | 1692.09     | El modelo captura bien los clústeres de volatilidad, pero el alto MSE refleja la dificultad de predecir el ruido diario exacto en crisis. |

---

**Licencia:** Uso académico para el Seminario de Modelización - Universidad de Granada.