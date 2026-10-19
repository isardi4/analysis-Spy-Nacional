# Método y resultados de la entrega

## Muestra

Corte 19/10/2026. Principal 20/09–19/10 (30 días inclusivos): 13 eventos presenciales, 671 plazas, 1.703 matches seleccionados y 30 participaciones de Spy. Comparación 05/09–19/10 (45 días inclusivos): 21 eventos, 1.127 plazas, 2.886 matches y 49 participaciones de Spy.

Se verificó sede física y fecha en Melee, tabla completa de primera ronda y respuestas completas de todas las rondas suizas. Se excluyeron eventos sin sede publicada, byes, eliminatorias, resultados 0-0, concesiones marcadas y victorias sin llegar a dos juegos ganados. Se mantienen los empates jugados. Algunos acuerdos de empate después de juegos no son identificables. El índice de descubrimiento no se usa como denominador del field.

Los conteos son plazas por evento; un piloto puede repetirse. La muestra incluye varios países y varias fechas de una misma liga presencial. No es una muestra aleatoria del metajuego mundial ni del Nacional. Los eventos encontrados pero sin sede verificable se excluyen aunque puedan ser presenciales. No se usan ligas virtuales, MTGO ni Arena.

## Modelo

Reserva una plaza del mazo elegido y sortea los 109 restantes con las proporciones presenciales. Los pares se forman por puntos, con azar dentro del grupo, flotantes y sin repetir oponente. Es una política aproximada, no una reproducción de un emparejador oficial. Son 7 rondas sin drops, ID, byes o diferencias de habilidad. El corte se ordena por puntos, OMW%, GW%, OGW% y azar residual; el desempate depende del supuesto BO3: 50% 2-0 / 50% 2-1 y empate 1-1.

El WR decisivo de A contra B es `(W_A + 5)/(W_A + W_B + 10)` y la tasa de empate se estima aparte con prior de media 5%. No usar el WR decisivo como probabilidad incondicional de ganar. Cada tabla distingue observaciones y probabilidades regularizadas. Hay aliases que fusionan variantes; Other y Unknown se mantienen explícitos. Se recomienda revisar listas antes de afinar una decisión de sideboard.

El estudio original de Spy corre 5M torneos distribuidos entre: principal30 (1,5M), ventana45 (0,5M), parámetros30 (0,5M), field natural30 (1M) y seis intervenciones (0,25M cada una). Las intervenciones usan +2 y +5 pp de WR decisivo para Red Madness, Mono Blue Terror y White Aggro. Se comparte semilla con lotes centrales de referencia, recalculando emparejamientos.

El selector general completó **11.000.000 de torneos adicionales**, con **47 opciones** (45 arquetipos/familias y las categorías Other/Unknown). Hay 158 escenarios, separados del estudio original de 5M. Usa corridas adicionales por mazo y ventana. Cada escenario base de un mazo tiene 100.000 torneos de 30 días y otros 100.000 de 45. Las intervenciones disponibles usan 25.000 torneos por cruce y +5 pp. Si no hay cruces con al menos cinco observaciones, no se calculan intervenciones para ese arquetipo. Su manifiesto registra el presupuesto total efectivo. Las categorías Other y Unknown no representan mazos concretos.

## Primeras conclusiones de Spy

En el escenario principal del estudio original, Spy clasifica 155.552 veces en 1.500.000 torneos: **10,37%**. Con la ventana de 45 días resulta **8,43%**. Esa diferencia muestra que la selección temporal importa mucho más que las centésimas del error Monte Carlo.

La probabilidad de enfrentar al menos una vez Red Madness es 45,24%; Elves 43,66%; Mono Blue Terror 30,45%; White Aggro 21,64%; Dimir Faeries 19,83%. Son probabilidades del torneo completo, no proporciones del field.

Entre las plazas eliminadas, 94,86% termina por debajo de los puntos del octavo y 5,14% empata esos puntos y pierde por desempate. Eso describe la eliminación en el modelo: no demuestra que una carta o decisión específica haya causado la derrota.

En el experimento sin plaza de Spy forzada, al menos un Spy aparece en top 8 en 40,91% de los torneos. Este resultado y P(top8 de tu plaza) tienen denominadores diferentes.

Los 100 sorteos de parámetros de Spy producen tasas por lote entre 6,77% y 15,71% en los percentiles 2,5–97,5. Ese rango incluye ruido de cada lote de 5.000 torneos y depende de priors independientes; no es un intervalo predictivo validado. Los datos escasos, la región y la clasificación de mazos agregan incertidumbre no incluida.

## Cómo interpretar el explorador general

Elegir un mazo y una ventana actualiza todas las métricas del torneo. Ronda y puntos afectan únicamente al gráfico del próximo rival. La tabla de exposición distingue `P(enfrentar A)`, `P(enfrentar A | top8)` y `P(top8 | enfrentar A)`.

No comparar mazos por diferencias pequeñas de P(top8) sin considerar muestras, aliases y supuestos. El selector no simula incertidumbre de parámetros para todos los mazos: su intervalo principal mide solo error Monte Carlo. Su corrida de Spy tiene menos torneos que el estudio detallado y puede mostrar valores ligeramente distintos por azar.

Las mejoras de matchup son experimentos hipotéticos sin costo en otros cruces. Para decidir preparación, se necesita contrastarlas con partidas pre/postside, play/draw y efectos sobre la consistencia de la lista. No hay una recomendación de 75 cartas ni un sideboard óptimo inferible de estos datos.

## Validación y pendientes

Se verificaron: fechas/sedes y denominadores, deduplicación, reciprocidad de matriz, conteos por escenario, conservación de estadísticas, prevención de revancha, simetría de field intercambiable (referencia 8/110), empates, piso de OMW y reproducibilidad por semilla. Los manifiestos registran hashes de modelos y motor; los checkpoints permiten reanudar.

Pendientes de investigación: calibración regional, confirmación de lista/formato y reglas del organizador, clasificación completa de cartas, ID y drops, dependencia por piloto/evento, marcadores de juegos estimados con datos, y evaluación externa con eventos reservados. Estas limitaciones figuran dentro del HTML, junto a los resultados.
