# Análisis Formal de Resultados del Modelo de Econofísica

El siguiente informe presenta la interpretación académica de los resultados obtenidos del modelo de Desplazamiento Cuadrático Medio del Precio (MSPD) y la tentativa de ajuste del modelo GARCH(1,1), aplicado al *spread* de bonos Grecia-Alemania en el periodo de **2025-02-07 a 2025-03-06**.

---

# 1. Contexto y Limitación del Análisis

## 1.1. Restricciones del Conjunto de Datos

Es fundamental señalar que el análisis se basa en una serie temporal extremadamente limitada de **20 puntos de datos**, correspondiente a un solo mes de cotización. Esta cantidad es **insuficiente** para realizar inferencias estadísticas robustas y conclusiones académicas sólidas, especialmente para modelos de volatilidad como GARCH, que requieren cientos de observaciones.

Por lo tanto, los resultados del exponente $\alpha$ y la interpretación gráfica se consideran **tentativos** y reflejan la dinámica del *spread* en ese micromarco temporal, pero no representan el comportamiento a largo plazo (2009-2021) de la crisis soberana estudiada.

## 1.2. Resultados Cuantitativos Obtenidos

| Métrica | Valor | Régimen Teórico | Fiabilidad |
| :--- | :--- | :--- | :--- |
| **Puntos de Datos (N)** | 20 | N/A | Muy Baja |
| **Exponente $\alpha$ (MSPD)** | **$-0.1900$** | Subdifusivo Extremo | Baja (Artefacto del ajuste) |
| **Modelo GARCH** | No Convergió | N/A | Fallido |

---

# 2. Análisis del Exponente de Escala (MSPD)

El resultado clave de la Econofísica es el exponente de escala $\alpha$, que describe cómo el riesgo del *spread* (medido por la varianza) crece con el tiempo de retardo $\tau$.

$$\langle \Delta p^2(\tau) \rangle \sim \tau^\alpha$$

## 2.1. Interpretación del Valor $\alpha = -0.1900$

Un valor de $\alpha$ **negativo** o cercano a cero, como $-0.1900$, indica un régimen de **Subdifusión extrema** o **Arresto Dinámico**.

* **Arresto Dinámico:** Teóricamente, un valor tan bajo (cercano a $\alpha=0$) sugiere que el *spread* ha entrado en una fase de **"congelamiento"** o **"fase vítrea"**. En este estado, la volatilidad es insignificante, y el desplazamiento promedio del precio a lo largo del tiempo ($\langle \Delta p^2(\tau) \rangle$) es nulo o decreciente (como se ve con el valor negativo). Económicamente, implica que el mercado del *spread* no ha mostrado prácticamente ningún movimiento o señal persistente en el corto periodo analizado.
* **Artefacto del Ajuste:** Es más probable que este valor negativo sea un **artefacto numérico** de intentar ajustar una función de ley de potencias a una serie de datos demasiado corta (20 puntos) y que probablemente es ruido blanco, o a un *spread* que fue casi constante, lo que se traduce en una pendiente nula o negativa en la escala logarítmica.

---

# 3. Análisis de las Representaciones Gráficas

Las imágenes generadas son esenciales para validar la consistencia de los resultados numéricos con la dinámica visual del *spread*.

## 3.1. Gráfico 1: Serie Temporal del Spread (Grecia-Alemania)



La **Serie Temporal del Spread** (Figura 1) muestra la evolución del diferencial del riesgo.

* **Observación:** Dado el corto período (aproximadamente 20 días), el *spread* exhibe una **alta estabilidad** o una variación muy limitada. No se observan los grandes picos de volatilidad característicos de la crisis de deuda (2010-2012).
* **Consistencia:** La estabilidad visual de la serie en este micromarco temporal es **consistente** con el resultado de MSPD ($\alpha \approx -0.19$), ya que un movimiento casi nulo resulta en un exponente de escala cercano a cero.

## 3.2. Gráfico 2: Desplazamiento Cuadrático Medio del Precio (MSPD) en Escala Log-Log



El **Gráfico Log-Log del MSPD** (Figura 2) es la prueba de la Econofísica.

* **Validación Visual:** La **Línea Roja de Ajuste** muestra una pendiente que es **cercana a cero o ligeramente negativa**, situándose muy por debajo de la **Línea de Referencia $\alpha=1$ (gris discontinua)**, lo que confirma visualmente el valor numérico $\alpha = -0.19$.
* **Conclusión Gráfica:** La drástica desviación de la curva de los datos reales respecto a la línea difusiva ($\alpha=1$) indica que el *spread* en este periodo **no se comporta en absoluto como un paseo aleatorio**. El sistema se encuentra, o bien en un estado de *arresto* total, o el bajo número de puntos impide que la función de ajuste capture la dinámica correcta, interpretando cualquier ruido como una pendiente negativa.

---

# 4. Conclusiones Finales

El ejercicio de modelado ha sido exitoso en la aplicación técnica de la metodología de Econofísica, resolviendo los complejos problemas de formato y codificación.

1.  **Modelo de Econofísica (MSPD):** El *spread* muestra un comportamiento **Subdifusivo Extremo** ($\alpha = -0.1900$) en el micromarco temporal de febrero-marzo de 2025.
2.  **Modelo Econométrico (GARCH):** Falló debido a la falta de datos, destacando la necesidad de grandes muestras para modelos autorregresivos de volatilidad.
3.  **Recomendación Académica:** Para replicar y validar las conclusiones del estudio de la Universidad de Almería, es indispensable obtener la **serie temporal completa y de alta frecuencia (diaria)** de los rendimientos de bonos de **Grecia y Alemania** para el periodo **Enero 2009 a Mayo 2021**. Solo con esa base de datos se podrá confirmar si el régimen de **Arresto Dinámico** es un fenómeno estructural de la crisis de la Eurozona.