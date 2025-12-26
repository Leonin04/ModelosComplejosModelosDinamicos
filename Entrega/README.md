# Seminario de Modelizacion: Modelos Complejos vs Modelos Dinamicos
## Analisis de la Prima de Riesgo en la Crisis de Deuda Soberana (2008-2013)

**Asignatura:** Seminario de Modelización (2025-26)
**Grupo:** 4

Este proyecto presenta un estudio comparativo entre dos enfoques metodológicos para explicar la dinámica del diferencial del bono griego a 10 años respecto al Bund alemán:
1. **Enfoque de Econofísica:** Modelos de Difusión Anómala y Mean Squared Displacement (MSPD).
2. **Enfoque Econométrico:** Modelos de Volatilidad Estocástica GARCH(1,1) con inferencia Bayesiana (MCMC).

---

## Estructura del Proyecto

A continuación se describe la funcionalidad de cada archivo contenido en el directorio raíz:

* **ActivarEntorno.sh**: Script de bash para automatizar la creación y activación del entorno virtual Conda.
* **DesactivarEntorno.sh**: Script para desactivar el entorno y liberar recursos de la terminal.
* **app.py**: Aplicación web interactiva (Dashboard) desarrollada en Streamlit. Permite la visualización de datos y la simulación del modelo de difusión en tiempo real.
* **script.py**: Script principal de cálculo intensivo. Realiza la limpieza de datos, el cálculo del exponente de difusión y, principalmente, la calibración del modelo GARCH mediante cadenas de Markov (Monte Carlo). Genera los reportes gráficos estáticos.
* **Modelo.ipynb**: Cuaderno Jupyter. Contiene el desarrollo paso a paso, análisis exploratorio y fundamentación teórica del código. Ideal para uso pedagógico.
* **germany.xlsx / greece.xlsx**: Archivos de datos brutos (series temporales de rendimientos de bonos).
* **environment.yml**: Archivo de configuración que lista todas las dependencias y librerías necesarias para reproducir el entorno.
* **analisis_grecia_calibracion_mse/**: Directorio generado automáticamente por `script.py` que contiene las gráficas de salida y métricas de error.
* **Grupo_4_Seminario_Modelizacion_2025_26/**: Directorio que contiene la documentación académica y la memoria en PDF.

---

## Instrucciones de Instalacion y Entorno

El proyecto requiere un entorno aislado de Python para gestionar las librerías de cálculo numérico (PyMC, ArviZ, Plotly, etc.).

### 1. Activación del Entorno
Para configurar y activar el entorno automáticamente, ejecute el siguiente comando en su terminal:

```bash
source ActivarEntorno.sh

```

Este script leerá el archivo `environment.yml`, instalará las dependencias si no existen y activará el entorno llamado `Seminario_EM`.

### 2. Desactivación

Al finalizar la sesión de trabajo, utilice:

```bash
source DesactivarEntorno.sh

```

### 3. Actualización de Dependencias

Si durante el desarrollo instala nuevas librerías, actualice el archivo de configuración con:

```bash
conda env export > environment.yml

```

---

## Guia de Ejecucion

Existen tres formas de interactuar con el proyecto, dependiendo del objetivo:

### A. Ejecución del Modelo Completo (Cálculo Intensivo)

Para realizar la calibración completa del modelo Bayesiano (que requiere alto coste computacional) y generar los reportes estáticos de error cuadrático medio (MSE):

```bash
python script.py

```

*Nota: Este proceso generará las imágenes en la carpeta `analisis_grecia_calibracion_mse` que posteriormente serán consumidas por el dashboard.*

### B. Aplicación Interactiva (Dashboard)

Para explorar los datos visualmente, ajustar el exponente de difusión manualmente y ver la comparativa de modelos:

```bash
streamlit run app.py

```

La aplicación se abrirá automáticamente en su navegador predeterminado (normalmente en `http://localhost:8501`).

### C. Jupyter Notebook (Análisis Exploratorio)

Para examinar el código paso a paso en Visual Studio Code:

1. Abra el archivo `Modelo.ipynb`.
2. Diríjase a la esquina superior derecha y haga clic en **Select Kernel** (Seleccionar Kernel).
3. Seleccione la opción **Python Environments**.
4. Elija el entorno específico de este proyecto: `Seminario_EM`.

---

## Resumen de Resultados Tecnicos

El análisis comparativo arroja las siguientes conclusiones métricas:

1. **Modelo de Difusión (Física):**
* Exponente Hurst/Alpha observado: ~0.94 (Super-difusión / Persistencia).
* MSE (Error Cuadrático Medio): 8.39.
* Interpretación: Excelente ajuste a la estructura de largo plazo y detección de memoria en la serie temporal.


2. **Modelo GARCH Bayesiano (Econometría):**
* MSE: 1692.09.
* Interpretación: Aunque presenta un error cuadrático mayor en términos absolutos debido al ruido diario, captura eficazmente los clústeres de volatilidad y proporciona intervalos de credibilidad para la gestión del riesgo (VaR).


