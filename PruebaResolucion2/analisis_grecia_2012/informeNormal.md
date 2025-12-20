# Informe de Análisis de Riesgo Soberano: Crisis Griega (2012)

## 1. Resumen Ejecutivo

El script ha procesado la **Prima de Riesgo** (diferencia de rendimiento entre el bono griego y el alemán). El análisis detecta una **ruptura estructural del mercado**. El comportamiento de la deuda griega dejó de ser un mercado financiero "normal" (aleatorio) y se comportó como un sistema en colapso determinista (caída libre).

**Nota Técnica Crítica:** El modelo Bayesiano GARCH tuvo problemas severos de convergencia (las "divergencias"), lo que indica que la volatilidad fue tan extrema que los modelos estocásticos tradicionales no logran capturarla adecuadamente sin ajustes.

---

## 2. Análisis de los Datos de Entrada (El Contexto)

El código ha ingerido dos archivos clave:

1. **`germany.xlsx` (El activo libre de riesgo):** Muestra rendimientos bajos y estables. Es el refugio seguro.
2. **`greece.xlsx` (El activo de riesgo):**
* Según tus datos, hay un pico histórico el **08-Marzo-2012**.
* El script detectó un movimiento diario máximo (shock) de **418.50 puntos básicos (bps)**. Para ponerlo en perspectiva: un movimiento de 10 o 20 bps se considera un día muy volátil. 418 bps es un cisne negro (un evento extremo).



Este periodo coincide exactamente con la **reestructuración de la deuda griega (PSI - Private Sector Involvement)**, donde los acreedores privados tuvieron que aceptar una quita (pérdida) de más del 50% del valor de sus bonos.

---

## 3. Explicación de la Salida de Terminal

Aquí desglosamos línea por línea lo que te dijo la terminal y su significado financiero:

### A. Fase de Difusión

> `Exponente de difusión Alpha: 0.9725`

Este es quizás el dato más importante del análisis.

* **Teoría:** En un mercado sano y eficiente, Alpha debería ser cercano a **0.5** (paseo aleatorio / movimiento browniano). Significa que el precio de mañana es impredecible.
* **Tu Resultado (0.97):** Un valor de casi **1.0** indica un comportamiento **balístico**.
* **Interpretación:** El mercado de bonos griegos no estaba "negociando"; estaba en una tendencia persistente y explosiva. Los inversores no estaban especulando, estaban huyendo en masa. Es la firma matemática del pánico total.

### B. El Problema Bayesiano (Las Advertencias Rojas)

> `There were 593 divergences after tuning.`
> `The rhat statistic is larger than 1.01`

El modelo intentó ajustar una curva de volatilidad (GARCH) usando inferencia Bayesiana, pero falló técnicamente.

1. **¿Qué es una divergencia?** Imagina que el algoritmo es un explorador caminando por un mapa montañoso (la probabilidad). Una divergencia ocurre cuando el terreno es tan empinado que el explorador se cae por un precipicio.
2. **¿Por qué ocurrió?** Hubo 593 caídas en 600 intentos. Esto sucede porque los datos de 2012 son **demasiado extremos**. La varianza cambia tan rápido de un día a otro que el modelo matemático estándar se "rompe".
3. **Consecuencia:** La "volatilidad estimada" (Gráfico 3) debe interpretarse con cautela. Es probable que subestime el riesgo real o muestre líneas muy erráticas, ya que el modelo no pudo encontrar una solución estable.

---

## 4. Interpretación de los Gráficos Generados

Basado en la lógica del código, esto es lo que muestran las imágenes en `analisis_grecia_2012`:

### Imagen 1: `Variación_Absoluta_bps.png`

* **Qué ves:** Una línea plana durante años y, de repente, picos gigantescos que parecen sismógrafos de un terremoto, centrados en 2011-2012.
* **Hecho Histórico:** Esos picos corresponden a las incertidumbres de los rescates de la "Troika" (FMI, BCE, UE). Cada pico suele ser una noticia de "Grecia podría salir del Euro (Grexit)".

### Imagen 2: `Analisis_Difusion.png` (MSPD)

* **Qué ves:** Puntos azules que forman una línea recta ascendente en escala logarítmica.
* **Interpretación:** La pendiente de esa línea es el **Alpha (0.97)**. Muestra que el riesgo se propagaba linealmente con el tiempo. El miedo de hoy garantizaba más miedo mañana (efecto memoria del mercado).

### Imagen 3: `Volatilidad_Estimada.png`

* **Qué ves:** Una línea roja (la volatilidad inferida) intentando seguir a las barras grises (los datos reales).
* **El fallo del modelo:** Dado el error en la terminal, es probable que la línea roja no logre cubrir los picos más altos de las barras grises. El modelo está "asustado" por los datos y no logra ajustarse a la magnitud del evento de Marzo de 2012.

---

## 5. Conclusión y Relación con Hechos Reales

El script ha intentado modelar matemáticamente uno de los eventos económicos más violentos de la historia moderna de Europa.

1. **El Evento:** En **Marzo de 2012**, Grecia completó el mayor canje de deuda de la historia, borrando unos 100.000 millones de euros de deuda en manos privadas.
2. **La Detección:** Tu código detectó este evento como un **pico de 418 bps** y un exponente de difusión de **0.97**.
3. **El Diagnóstico:** Matemáticamente, el mercado griego dejó de funcionar como un mercado financiero (estocástico) y se comportó como un sistema físico determinista en colapso.

**Siguiente paso recomendado:**
Para arreglar el error de las "593 divergencias", el modelo necesita "colas más pesadas". Deberías cambiar la distribución de `pm.Normal` a `pm.StudentT` en el código, ya que la crisis griega tuvo eventos mucho más extremos de lo que una distribución Normal puede predecir.

