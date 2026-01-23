### 1. `1_Datos.png`: Los Retornos (El "Ruido" del Mercado)

**¿Qué vemos?**
Es el gráfico de los cambios porcentuales diarios del *Spread* (diferencia de tasas) entre Alemania y Grecia a lo largo del tiempo.
* **Eje X:** Años (2000 - 2022).
* **Eje Y:** La magnitud del cambio diario (escalada x100).

**Interpretación:**
* **La calma antes de la tormenta (2000-2009):** La línea es casi plana. El mercado no percibía riesgo diferencial entre Grecia y Alemania (efecto Euro).
* **El estallido (2010-2015):** Aquí es donde ocurre la **Crisis de Deuda Griega**. Vemos picos gigantescos. La volatilidad explota. Hay días donde el spread se movió una barbaridad (esos picos grises enormes).
* **Heterocedasticidad:** Este "gráfico feo" justifica por qué usas GARCH. La varianza no es constante; hay periodos tranquilos y periodos de locura. Un modelo normal fallaría aquí.

---

### 2. `2_MSPD.png`: Análisis de Econofísica (Difusión)

**¿Qué vemos?**
Un gráfico log-log que compara cómo se desplaza la serie temporal (puntos azules) frente a una difusión aleatoria pura (línea roja).
* **Resultado Clave:** `Alpha = 0.97`.

**Interpretación:**
* En física, $\alpha = 1.0$ representa el **Movimiento Browniano** (paseo aleatorio puro, mercado eficiente).
* Tu resultado (**0.97**) es **extremadamente cercano a 1**.
* **Significado:** A pesar de la crisis, la dinámica *estructural* del spread se comporta casi como un paseo aleatorio normal. Es ligeramente "sub-difusivo" (<1), lo que implica una muy leve tendencia a revertir a la media (el spread intenta volver a su cauce), pero es casi imperceptible.
* **Conclusión:** El mercado es eficiente en su aleatoriedad, pero la *magnitud* de los saltos cambia (lo que nos lleva a la siguiente imagen).

---

### 3. `3_Bayes_Trace.png`: El "Cerebro" del Modelo Bayesiano

**¿Qué vemos?**
Este es el diagnóstico de tu simulación MCMC. Muestra qué valores han encontrado tus parámetros.
* **Izquierda (Histogramas):** La distribución de probabilidad de cada parámetro.
* **Derecha (Trazas):** El camino que siguió el algoritmo para encontrar esos valores.

**Análisis de los parámetros:**
1.  **`mu` (Media):** Está cerca de 0. Tiene sentido, el cambio promedio diario es casi nulo.
2.  **`omega` (Varianza base):** Alrededor de 0.5. Es el riesgo "mínimo" basal.
3.  **`alpha` (~0.18):** Es la **reacción a las noticias**. Un valor de 0.18 es alto. Significa que cuando hay un susto en el mercado (un dato malo de Grecia), la volatilidad salta fuerte inmediatamente.
4.  **`beta` (~0.81):** Es la **memoria del miedo**. Un valor de 0.81 es muy alto. Significa que, una vez que la volatilidad sube, tarda mucho tiempo en bajar. El mercado "no olvida" el riesgo fácilmente.

*Nota técnica:* En los gráficos de la derecha (Trazas) para Alpha y Beta, las líneas no están perfectamente mezcladas (parecen dos caminos un poco separados). Esto indica que al modelo le costó un poco decidirse, pero los valores son coherentes. La suma $\alpha + \beta \approx 0.99$ indica una **persistencia extrema** de la volatilidad.

---

### 4. `4_Volatilidad_GARCH.png`: El Resultado Final (El Riesgo Real)

**¿Qué vemos?**
* **Gris (Fondo):** Los retornos originales (el gráfico 1).
* **Rojo (Línea):** La **Volatilidad Condicional Estimada ($\sigma_t$)** por tu modelo Bayesiano.

**Interpretación (La joya del análisis):**
Esta línea roja es lo que buscan los economistas. Representa el **Riesgo Latente**.
1.  Fíjate cómo la línea roja captura perfectamente los clústers de la crisis (2011-2015).
2.  **El efecto memoria:** Mira los picos grandes en 2012. El retorno (gris) da un salto y baja, pero la línea roja se queda alta un tiempo y baja suavemente. Eso es el efecto de tu `beta` alto. El modelo nos dice: *"Aunque hoy no haya pasado nada grave, el mercado sigue nervioso por lo que pasó ayer"*.
3.  Hacia el final (2019-2020), la volatilidad roja está muy baja, indicando que la percepción de riesgo de quiebra de Grecia ha desaparecido casi por completo comparado con Alemania.

---

### Resumen para tu presentación:
> "Hemos analizado el spread Alemania-Grecia. La econofísica (MSPD) nos dice que el movimiento es casi aleatorio (Browniano), pero el modelo GARCH Bayesiano revela que el **riesgo tiene memoria**. Detectamos una persistencia del 99% ($\alpha+\beta$), lo que significa que durante la crisis, el miedo en el mercado tardaba muchísimo en disiparse, creando periodos prolongados de alta incertidumbre."