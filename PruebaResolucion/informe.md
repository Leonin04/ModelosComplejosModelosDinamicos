# Informe Detallado: Modelo de Econofísica de Series Temporales

## 1\. Introducción y Fundamento del Modelo

Este informe detalla la aplicación de una metodología de **Econofísica** basada en la **Física Estadística de la Materia Blanda** (particularmente la dinámica de sistemas coloidales y vidrios de *spin*) al análisis de una serie temporal financiera, como el **diferencial de bonos soberanos (spread)**.

## Objetivo

El objetivo principal es determinar el régimen dinámico del *spread* a través del **Desplazamiento Cuadrático Medio del Precio (MSPD)**, y compararlo con el modelo econométrico estándar **GARCH**. Buscamos evidencia de:

1.  **Difusión Browniana** ($\alpha \approx 1$): Coherente con la Hipótesis del Mercado Eficiente (paseo aleatorio).
2.  **Subdifusión/Arresto Dinámico** ($\alpha < 1$): Indicativo de fuertes **efectos de memoria** o un **comportamiento vítreo** donde los precios están "atrapados" o "enjaulados" temporalmente, como se teoriza en la econofísica de crisis.
3.  **Superdifusión** ($\alpha > 1$): Indicativo de fuertes tendencias o correlaciones de largo alcance.

## La Métrica Clave: MSPD

El **MSPD** es el análogo financiero del Desplazamiento Cuadrático Medio (MSD) en la física. Mide la volatilidad promedio del precio $p(t)$ a través de un intervalo de tiempo $\tau$:
$$\langle \Delta p^2(\tau) \rangle \sim \tau^\alpha$$

## 2\. Metodología y Análisis del MSPD

## A. Cálculo

El código implementa la fórmula del MSPD. Para un $\tau$ (días), se calcula la diferencia cuadrática entre el precio en $t_0 + \tau$ y $t_0$, y se promedia sobre todos los puntos de partida $t_0$.

## B. Exponente de Escala ($\alpha$)

El paso crítico es el **ajuste de ley de potencias** en una escala logarítmica. Al graficar $\log(\text{MSPD})$ vs $\log(\tau)$, el resultado es, idealmente, una línea recta cuya **pendiente** es el exponente $\alpha$.

| Valor de $\alpha$ | Régimen Dinámico | Implicación Económica |
| :---: | :---: | :--- |
| **$\alpha \approx 1$** | **Difusión Normal** | Los cambios de precio son independientes y sin memoria significativa. |
| **$\alpha < 1$** | **Subdifusión/Arresto** | **Memoria fuerte**. Los precios tienden a volver a su nivel, o el mercado está "estancado" (similar a un vidrio de *spin*). |
| **$\alpha > 1$** | **Superdifusión** | **Momentum fuerte**. Los cambios de precio pasados refuerzan los futuros. |

**Interpretación del Gráfico Log-Log (Gráfico 2):**

  * **Zona Inicial (pequeño $\tau$):** Esta zona suele ser la más relevante para detectar la dinámica intrínseca. Si la curva se inclina menos que la línea $\alpha=1$ (línea de referencia), indica subdifusión.
  * **Meseta (Plateau):** Si el gráfico muestra una meseta donde el MSPD se mantiene casi constante (es decir, $\alpha \approx 0$), esta es la firma más clara de un **arresto dinámico** o **fase vítrea**, como se encontró en el documento de Almería.

## C. Resultado del Ajuste

El valor de **$\alpha$** reportado por el código (**`alpha_fit`**) es el principal resultado. Si este valor es significativamente menor a 1 (p.ej., $0.5 < \alpha < 0.9$), existe evidencia cuantitativa de dinámicas de **memoria de corto/medio plazo** o **efectos Kovacs** en el *spread*.

## 3\. Modelo Econométrico de Referencia (GARCH)

Para contextualizar el resultado de la econofísica, se utiliza el modelo **GARCH(1,1)** sobre los **retornos** del *spread*.

$$\sigma_t^2 = \omega + \alpha_1 \epsilon_{t-1}^2 + \beta_1 \sigma_{t-1}^2$$

Donde $\sigma_t^2$ es la varianza condicional (volatilidad).

| Coeficiente | Descripción | Interpretación |
| :---: | :---: | :--- |
| **$\alpha_1$ (ARCH)** | Impacto de las noticias (choques) pasadas. | Sensibilidad de la volatilidad a los retornos pasados. |
| **$\beta_1$ (GARCH)** | Persistencia de la volatilidad pasada. | Memoria de la volatilidad del sistema. |
| **$\alpha_1 + \beta_1$** | **Persistencia Total** | Si se acerca a 1, la volatilidad es muy persistente y lenta en disiparse (similar a la dinámica lenta de la fase vítrea). |

**Comparación:**

  * **MSPD (Econofísica):** Captura la **memoria en el precio/spread** (dinámica del precio).
  * **GARCH (Econometría):** Captura la **memoria en la volatilidad** (dinámica del riesgo).

Si el GARCH arroja una alta persistencia ($\alpha_1 + \beta_1 \approx 1$) Y el MSPD arroja un $\alpha < 1$, ambos modelos, desde perspectivas diferentes, están confirmando la existencia de **dinámicas lentas o efectos de memoria** en el *spread*.