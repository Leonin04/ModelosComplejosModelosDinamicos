# Seminario de Modelización: Modelos Complejos vs Modelos Dinámicos
## Análisis de la Prima de Riesgo en la Crisis de Deuda Soberana (2008-2013)

**Asignatura:** Seminario de Modelización (2025-26)
**Grupo:** 4
**Autores:** Ismael Sallami Moreno & David Bacas Posadas

Este proyecto presenta un estudio comparativo computacional entre dos enfoques metodológicos para explicar la dinámica del diferencial del bono griego a 10 años respecto al Bund alemán:

1.  **Enfoque de Econofísica:** Modelos de Difusión Anómala y Mean Squared Displacement (MSPD).
2.  **Enfoque Econométrico:** Modelos de Volatilidad Estocástica GARCH(1,1) con inferencia Bayesiana (MCMC).

---

## 🏗️ Estructura del Proyecto

La aplicación se ha estructurado como una **Single Page Application (SPA)** multipágina utilizando Streamlit. A continuación se describe la arquitectura de archivos:

### Raíz del Proyecto
* **`Home.py`**: 🏠 **Punto de entrada**. Portada institucional que presenta el video introductorio, el resumen ejecutivo y los enlaces de navegación.
* **`script.py`**: ⚙️ Motor de cálculo intensivo. Realiza la calibración del modelo GARCH mediante cadenas de Markov (Monte Carlo) y guarda los resultados estáticos en `analisis_grecia_calibracion_mse/`.
* **`Modelo.ipynb`**: 📓 Cuaderno Jupyter con el desarrollo pedagógico paso a paso.
* **`Crisis_de_la_Deuda_Griega.mp4`**: 📹 Video generado por IA (Avatar) que introduce el seminario.
* **`paper_final.pdf`**: 📄 Memoria académica completa del proyecto.
* **`ActivarEntorno.sh` / `DesactivarEntorno.sh`**: 🛠️ Scripts de automatización DevOps para configurar el entorno Conda.
* **`germany.xlsx` / `greece.xlsx`**: Datos brutos de los rendimientos de los bonos.

### Módulos de la Aplicación (`pages/`)
La lógica de visualización se divide en módulos independientes (nombres técnicos limpios):
* **`1_Metodologia.py`**: Explica la fundamentación matemática (Leyes de Potencia vs Ecuaciones GARCH) y muestra el código fuente.
* **`2_Dashboard.py`**: Laboratorio interactivo. Permite visualizar las series temporales, ajustar el exponente Alpha en tiempo real y comparar los errores (MSE).
* **`3_Documentacion.py`**: Visor de documentación técnica, guía de instalación y arquitectura.
* **`4_Conclusiones.py`**: Síntesis de hallazgos, métricas finales y agradecimientos.

---

## 💻 Guía de Instalación y Ejecución NO AUTOMÁTICA

El proyecto requiere un entorno aislado de Python (3.10+) para gestionar las librerías de cálculo numérico como `PyMC`, `ArviZ` y `Streamlit`.

### 1. Configuración del Entorno
Ejecute el script de automatización en su terminal bash para crear y activar el entorno `Seminario_EM` usando las dependencias de `environment.yml`:

```bash
source ActivarEntorno.sh
```

### 2. Ejecución de la Aplicación

Para lanzar la interfaz web, ejecute el siguiente comando desde la raíz del proyecto (apuntando siempre a `Home.py`):

```bash
streamlit run Home.py
```

La aplicación se abrirá automáticamente en [http://localhost:8501](http://localhost:8501).

> **Nota:** Si necesita recalibrar el modelo GARCH y regenerar las gráficas estáticas, ejecute `python script.py` antes de iniciar la web.


## 🖱️ Instalación y Ejecución Automática

Este proyecto incluye scripts de automatización para simplificar el despliegue en cualquier sistema operativo.

### Requisitos Previos
* Tener instalado **Anaconda** o **Miniconda**.

### Instrucciones

**Para Usuarios de Windows:**
1. Busque el archivo `setup_windows.bat` en la carpeta raíz.
2. Haga doble clic sobre él.
3. El script creará el entorno y abrirá la aplicación automáticamente.

**Para Usuarios de Linux / macOS:**
1. Abra una terminal en la carpeta del proyecto.
2. Ejecute el siguiente comando:
   ```bash
   bash setup_unix.sh
Nota: La primera ejecución puede demorarse unos minutos mientras se descargan las librerías necesarias.


---

## 📊 Resumen de Resultados Técnicos

El análisis comparativo arroja las siguientes conclusiones métricas sobre la crisis griega:

| Modelo              | Métrica Clave           | MSE (Error) | Interpretación                                                                                   |
|---------------------|------------------------|-------------|--------------------------------------------------------------------------------------------------|
| Difusión (Física)   | $\alpha \approx 0.94$  | 8.39        | El mercado muestra super-difusión y memoria persistente a largo plazo. Ajuste estructural superior. |
| GARCH (Bayesiano)   | $\hat{R} \approx 1.01$ | 1692.09     | Captura eficazmente los clústeres de volatilidad diaria, aunque con mayor error puntual debido al ruido estocástico. |

---

**Licencia:** Uso académico para el Seminario de Modelización - Universidad de Granada.