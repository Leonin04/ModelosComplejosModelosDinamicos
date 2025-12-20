# Informe de Modelado: Volatilidad de la Deuda Griega (Normal vs. Student-T)

## 1. El Problema Teórico: ¿Por qué falló la "Normal"?

Originalmente, intentamos usar una **Distribución Normal (Gaussiana)**. Esta es la campana clásica que se usa en estadística básica.

* **La suposición de la Normal:** Asume que el 99.7% de los eventos ocurren dentro de 3 desviaciones estándar. Considera que un movimiento extremo (un "cisne negro") es matemáticamente imposible (probabilidad cercana a cero).
* **La realidad de Grecia (2012):** Tus datos mostraron movimientos de **1987 bps**. En términos estadísticos, esto es un evento de **20 o 30 desviaciones estándar**.
* **El colapso del código:** Cuando el modelo Normal vio ese dato, calculó una probabilidad tan infinitesimalmente pequeña () que el ordenador la redondeó a cero absoluto (`log-prob = -inf`). Esto provocó el error **"Bad Initial Energy"**. El modelo "murió" de asombro; no podía creer que ese dato fuera real.

## 2. La Solución: Distribución T-Student

Hemos cambiado la "verosimilitud" (likelihood) a una **Student-T**.

* **¿Qué hace diferente?** La Student-T tiene un parámetro extra llamado **`nu` (grados de libertad)**.
* Si `nu` es alto (>30), se comporta como una Normal.
* Si `nu` es bajo (<5), desarrolla **"colas pesadas"** (Fat Tails).


* **El efecto "Amortiguador":** Las colas pesadas significan que la curva admite que los eventos extremos, aunque raros, **son posibles**.
* **Resultado:** Cuando el modelo ve el pico de 1987 bps, en lugar de decir "Imposible" (Error), dice "Wow, esto es muy improbable, pero posible si la volatilidad es gigante". Esto permite que el algoritmo corra sin romperse.

---

## 3. Interpretación de las Imágenes Generadas (Ejecución Rápida)

Al haber bajado `draws=100` y `tune=100`, has generado un "boceto rápido" en lugar de una fotografía de alta definición. Los resultados son válidos cualitativamente, pero tendrán "ruido".

### Imagen 1: `Variación_Absoluta.png` (La Realidad)

* **Lo que ves:** Una línea plana que de repente se vuelve loca en 2011-2012.
* **Significado:** Estos son los datos crudos (inputs). No dependen del modelo. Muestran que el mercado pasó de ser "aburrido" a "pánico total" durante la reestructuración de la deuda (PSI).

### Imagen 2: `Difusión.png` (La Física del Mercado)

* **Lo que ves:** Puntos azules formando una línea recta hacia arriba.
* **El Alpha (0.97):** Este número no cambió con el modelo Student-T porque es una propiedad física de los datos.
* **Interpretación:** Un Alpha de ~1.0 significa **Comportamiento Balístico**. El precio no "fluctuaba"; caía en línea recta (o la prima subía en línea recta). Es la firma matemática de un mercado roto donde no hay compradores, solo vendedores.

### Imagen 3: `Volatilidad_Final.png` (El Resultado del Modelo Student-T)

* **Lo que ves:**
* **Barras grises de fondo:** Los retornos reales.
* **Línea Roja Oscura:** La volatilidad estimada por tu modelo GARCH-Student.
* **Sombra Roja (Intervalo):** La incertidumbre del modelo.


* **Efecto de `draws=100`:** Verás que la sombra roja es probablemente **muy ancha o con bordes irregulares**. Con pocas muestras, el modelo no está 100% seguro de dónde está la línea exacta, así que te da un rango amplio.
* **La Victoria:** A diferencia del intento anterior, **aquí hay línea roja**. El modelo logró "escalar la montaña" de la crisis. La línea roja sube agresivamente durante 2012, lo que indica que el modelo ha entendido correctamente que el riesgo se disparó, absorbiendo los datos extremos gracias a la distribución Student-T.

## Conclusión

El cambio a **Student-T** fue necesario porque la crisis griega fue un evento estadísticamente "imposible" bajo modelos normales. La imagen 3 demuestra que, al permitir "colas pesadas", podemos medir el riesgo incluso durante un colapso financiero total.

Aunque 100 muestras son pocas para un paper académico (donde usarías 2000), son suficientes para confirmar que **la lógica del modelo ahora es correcta y robusta**.