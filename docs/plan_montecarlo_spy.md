# Plan: caminos de Spy al top 8 en un torneo presencial

**Actualización final:** el objetivo se amplió a una única corrida compartida de 5M torneos para todos los arquetipos, con suizo y eliminatorias. La presencia sigue siendo presencial; la matriz incorpora cruces online verificables. El método vigente está en [torneo compartido](torneo_compartido.md). La página ahora prioriza recorridos por resultado final, victorias/derrotas por rival y probabilidades de top8/top4/top2/campeón; la consulta por récord exacto es una herramienta adicional. El resto de este documento conserva el diseño inicial para trazabilidad.

Estado: implementado. Se completó el estudio original de Spy de 5M torneos y se amplió a un explorador general por arquetipo. Ver [método y resultados](metodo_y_resultados.md) y [README](../README.md).

Actualización de alcance: usar exclusivamente datos presenciales de los últimos **30/45 días**, con corte 19/10/2026. La ventana principal es 20/09–19/10 y la comparación 05/09–19/10, ambas inclusivas. Las ventanas de 90/180 días de la propuesta inicial quedan descartadas. Los 5M del estudio original y las corridas adicionales del selector se reportan separados.

## 1. Objetivo y alcance

Simular **5.000.000 de torneos completos de aproximadamente 110 participantes** para estimar la probabilidad de que un jugador de Spy llegue al top 8, qué rivales encuentra y cómo cambian esos rivales a medida que avanzan las rondas. Analizar también los torneos donde queda afuera y evaluar qué mejoras de preparación podrían tener mayor impacto.

Hipótesis de trabajo pendiente de confirmar: formato Pauper y Spy = Balustrade Spy. Confirmar fecha, región, lista de 75 cartas, cantidad de rondas, corte, byes y reglas particulares del organizador. No fijar porcentajes del metajuego hasta verificar las fuentes.

**Restricción de datos: exclusivamente torneos presenciales.** Excluir ligas, Challenges y cualquier evento de MTGO, Arena o plataformas virtuales. Un agregador que mezcle plataformas solamente sirve si se puede verificar y filtrar cada evento.

## 2. Preguntas que debe responder el informe

- Para tu plaza de Spy: ¿cuántas veces y con qué probabilidad entrás al top 8?
- Para todos los pilotos de Spy: ¿cuántos clasifican por torneo y con qué tasa de conversión? ¿Qué probabilidad hay de al menos un Spy en el top 8?
- ¿Qué probabilidad hay de enfrentar cada arquetipo en cada ronda, por récord y al menos una vez durante el suizo?
- Entre los Spy que clasifican: ¿qué rivales y secuencias de resultados aparecen más?
- Entre quienes quedan afuera: ¿qué derrotas, empates, récords y desempates se asocian con la eliminación?
- ¿Qué mejora de un matchup produce más puntos porcentuales de probabilidad de top 8 y qué costo tiene empeorar otro?

Separar siempre `P(enfrentar A)`, `P(enfrentar A | top 8)` y `P(top 8 | enfrentar A)`. Son preguntas distintas; un rival frecuente entre los clasificados no necesariamente es favorable.

## 3. Fuentes y construcción de la muestra presencial

### 3.1 Búsqueda y auditoría

Buscar resultados publicados por organizadores y plataformas de torneos presenciales, con prioridad para eventos de la región y eventos de tamaño comparable. Paupergeddon y otros eventos grandes pueden aportar información si se confirma el formato, la fecha y el carácter presencial; su representatividad local se evaluará por separado.

Ventana acordada: últimos 30 días, con comparación a 45 días, anteriores a la fecha de corte. Separar períodos si hubo cambios de legalidad o cambios sustanciales de metajuego. No usar información posterior al torneo que se quiere preparar.

Registrar por evento: URL, fecha del evento, fecha de consulta, lugar, plataforma presencial verificada, tamaño del field, rondas, reglas y cobertura disponible. Guardar copia de los datos originales y trazabilidad de cada transformación. Deduplicar eventos y partidas publicados por varias fuentes.

No confundir porcentaje de listas publicadas con porcentaje del field. Si solamente se publican listas ganadoras o del top 8, usarlas para análisis de conversión cuando exista el denominador, no para estimar directamente presencia o win rate.

### 3.2 Datos necesarios

| Archivo | Campos mínimos | Uso |
|---|---|---|
| `events.csv` | event_id, fecha, región, formato, paper_verified, participantes, rondas, fuente, cobertura | Auditoría y selección |
| `entries.csv` | event_id, player_id seudónimo, arquetipo, variante, lista disponible | Presencia y denominadores |
| `matches.csv` | event_id, ronda, jugadores, juegos ganados por lado si existen, resultado, bye, ID, drop | Matriz y reconstrucción |
| `archetype_aliases.csv` | nombre original, nombre normalizado, criterio | Unificar etiquetas |
| `sources.csv` | source_id, URL, consulta, verificación, limitaciones | Trazabilidad |
| `scenarios.json` | parámetros, semilla, ventana, reglas, versiones | Reproducibilidad |

Los empates intencionales (ID) y byes no son victorias o derrotas jugadas. Los resultados de juegos y los de matches deben tener denominadores diferentes.

### 3.3 Si faltan datos

La frecuencia de un mazo no determina su win rate. El win rate global tampoco identifica su matriz de matchups. Para simular cómo evoluciona todo el field se necesita una matriz entre **todos los arquetipos**, no solamente la fila de Spy.

Si faltan cruces, usar estimaciones regularizadas con intervalos amplios y etiquetar cada celda como observada, estimada o supuesto. Como modelo inicial se pueden usar probabilidades victoria/empate/derrota con prior Dirichlet y ajuste jerárquico para cruces escasos. Ajustar resultados desde una única orientación por pareja para conservar coherencia: victoria de A = derrota de B. Mirrors simétricos.

No completar datos ausentes con MTGO. Si la cobertura presencial no permite una predicción defendible, producir escenarios condicionales claramente identificados y mostrar cuánto depende el resultado de esos supuestos.

## 4. Modelo del metajuego

Construir el escenario central con proporciones del field presencial completo. Mostrar tamaño de muestra, eventos, fechas y cobertura. Comparar ponderación por jugador con ponderación por evento para detectar dependencia de un evento grande. Justificar cualquier ponderación regional o temporal.

Usar dos diseños separados:

1. **Tu torneo:** fijar una plaza de Spy y sortear los otros 109 participantes. Esta es la estimación principal para tu decisión de mazo.
2. **Representación natural:** sortear las 110 plazas sin forzar Spy. Medir cantidad de Spy en top 8 y conversión agregada por participante de Spy. Tratar explícitamente los torneos sin Spy.

Muestrear conteos enteros con una multinomial; comparar con escenarios de conteos fijos para separar variación del field de variación de resultados. Como sensibilidad, sortear proporciones por torneo con un modelo Dirichlet-multinomial o bootstrap de eventos, manteniendo separada la incertidumbre de las proporciones.

No agrupar indiscriminadamente mazos distintos como «Otros»: conservar los relevantes para Spy y variar el comportamiento del remanente.

## 5. Simulación del torneo

### 5.1 Reglas

Base provisional: 110 jugadores, 7 rondas suizas y corte a top 8. Confirmar con el organizador y las reglas vigentes antes de ejecutar; el número de rondas no se deduce solamente del tamaño si el evento tiene reglas propias.

- Ronda inicial aleatoria; siguientes rondas por puntos, evitando repetir rivales y gestionando flotantes entre grupos.
- Puntuación de match 3/1/0, con byes y drops explícitos cuando correspondan.
- Empates naturales separados de ID. Comparar sin ID con una política conservadora de ID; no asumir que los jugadores conocen el futuro del torneo.
- Byes asignados según las reglas implementadas y sin tratarlos como matches jugados.
- Orden final por puntos y desempates reglamentarios. Para OMW%, GW% y OGW% se necesitan historiales de oponentes y resultados de juegos, incluyendo pisos y exclusiones aplicables.
- Si solamente hay datos a nivel match, modelar los marcadores BO3 de forma consistente y declarar la incertidumbre que agregan a los desempates. No llamar «reglamentario exacto» a un desempate aproximado.
- Documentar qué parte del emparejamiento reproduce las reglas y qué parte aproxima el software del organizador. No prometer reproducir exactamente un emparejador propietario.

El resultado principal es **clasificar** al top 8; ganar sus eliminatorias es una extensión separada.

### 5.2 Dos tipos de incertidumbre

Primero ejecutar el modelo con parámetros centrales fijos para medir azar de torneo. Después variar parámetros de presencia y matchups para medir incertidumbre de los datos.

Presupuesto propuesto: 4.000.000 de torneos en el diseño de tu plaza de Spy, incluyendo escenario central y sensibilidad, y 1.000.000 en representación natural. Fijar la distribución exacta por escenario después del piloto, antes de la corrida definitiva. El manifiesto debe sumar exactamente 5.000.000, sin contar tests ni piloto. Reportar cada escenario por separado: no mezclar políticas distintas en un único porcentaje sin pesos explícitos.

Reportar denominadores y número de simulaciones de cada resultado. Cinco millones de torneos no eliminan el sesgo de los datos ni generan cinco millones de observaciones independientes para todas las métricas. Considerar agrupación por torneo y por parámetros compartidos al calcular intervalos.

## 6. Motor, rendimiento y reproducibilidad

Implementación propuesta: Python, NumPy, Numba para el núcleo si el piloto confirma que es necesario, pandas o Polars para datos y Plotly para gráficos. Notebook para explicar el análisis y **HTML autónomo con gráficos y tablas** como entrega consultable sin ejecutar Python. Este informe local no requiere publicar un sitio.

Con 110 jugadores y 7 rondas sin drops hay 385 matches por torneo: 5M torneos representan aproximadamente **1.925 millones de matches**. No estimar tiempos de ejecución antes de medir.

Procesar por lotes; guardar agregados por ronda, récord y rival, y una muestra limitada de trayectorias. Evitar almacenar todas las partidas de los 5M torneos. Para secuencias usar agregados compactos y agrupar caminos raros, sin inventar precisión donde faltan observaciones.

Ejecutar piloto de 10.000–100.000 torneos, medir tiempo y memoria, proyectar costo, elegir tamaño de lote y paralelismo. Usar semillas reproducibles y streams independientes por lote, checkpoints reanudables y manifiesto de corrida con versiones, hashes de datos, parámetros, conteos completados y tiempo real. Los resultados del piloto no se presentan como corrida final.

## 7. Análisis de clasificación y eliminación

### 7.1 Caminos al top 8

Por ronda y récord previo, calcular la distribución de oponentes. Comparar presencia inicial con presencia en mesas altas. Mostrar frecuencia de enfrentar cada mazo cero, una, dos o más veces.

Medir P(top 8), cantidad esperada de Spy clasificados, distribución 0/1/2/… y conversión por piloto. Separar «top 8 contiene Spy» de «un piloto de Spy clasifica». Presentar récord final y zona de desempate; no asumir que todo 5-2 entra o queda afuera.

Resumir caminos por secuencias W/L/D y exposición a familias de mazos. Para trayectorias poco frecuentes, mostrar conteo e intervalo o agruparlas.

### 7.2 Caminos que quedan afuera

Registrar récord, puntos, margen frente al octavo y derrotas por arquetipo. Separar quedar corto de puntos de quedar afuera por desempates. Mostrar también victorias y rivales de los no clasificados para evitar explicar todo solamente con las derrotas visibles.

Una asociación entre enfrentar un mazo y quedar eliminado no demuestra causalidad: los emparejamientos dependen del rendimiento previo. Comparar también dentro de ronda y récord.

Para priorizar preparación, repetir escenarios mejorando un matchup de Spy +2 y +5 puntos porcentuales y midiendo el cambio de P(top 8), con intervalos. Mantener explícito si la mejora convierte derrotas en victorias o afecta empates. Usar números aleatorios comunes cuando sea viable para reducir ruido entre escenarios; permitir que se recalculen los emparejamientos al cambiar resultados.

## 8. Traducir resultados a preparación del mazo

Ordenar matchups por exposición, dificultad, muestra e impacto marginal en clasificación. Comparar mejoras individuales con cambios que sacrifican otro cruce: una mejora aislada es un experimento hipotético, no evidencia de que una carta la produzca.

Con la lista de 75 confirmada, armar una tabla de candidatos de main/sideboard, matchups objetivo, cartas que salen, riesgos para el plan de combo y evidencia de testing. Las métricas agregadas no permiten atribuir derrotas a hate de cementerio, counters, mulligans o decisiones del piloto sin datos adicionales.

Entregar una agenda de pruebas de partidas preside y postside, play/draw y situaciones frecuentes, priorizada por el impacto esperado y la incertidumbre. No recomendar un sideboard «óptimo» solamente a partir de una matriz supuesta.

## 9. Notebook / HTML final

El informe debe indicar arriba: fecha de corte, fuentes exclusivamente presenciales, cobertura, supuestos, número realmente ejecutado y versión del modelo.

Gráficos mínimos:

1. Barras de presencia de arquetipos con incertidumbre y cantidad esperada en 110 jugadores.
2. Heatmap de matchups con muestra y celdas estimadas identificadas.
3. Heatmap de probabilidad de rival por ronda y récord de Spy.
4. Comparación de rivales y récords entre clasificados y no clasificados, con denominadores.
5. Barras del cambio de P(top 8) al mejorar cada matchup y escenarios de costo/beneficio.

Incluir tablas de probabilidades condicionadas, distribución de Spy en top 8, casos de desempate y enlaces a fuentes. Etiquetar claramente parámetros ingresados, resultados observados y resultados simulados. Los filtros del HTML solo ofrecerán escenarios que hayan sido calculados.

## 10. Validación

- Datos: únicamente papel verificado, sin duplicados, proporciones que suman 1 y normalización auditable.
- Matriz: probabilidades válidas, reciprocidad, mirrors y distinción entre juegos, matches, byes e ID.
- Motor: ningún jugador juega contra sí mismo o dos veces en una ronda; no repetir rivales si existe emparejamiento válido; asignación de byes y flotantes consistente.
- Puntajes y desempates: casos manuales con victoria, empate, bye, drop y pisos reglamentarios.
- Casos control: field simétrico con jugadores intercambiables, donde una plaza tiene probabilidad cercana a 8/110; resultados deterministas; reproducibilidad por semilla; reanudar sin duplicar lotes.
- Validación externa: reproducir eventos presenciales históricos sin calibrar y evaluar sobre el mismo evento. Separar eventos de ajuste y evaluación cuando la muestra lo permita.
- Convergencia: comparar checkpoints y precisión por escenario. Informar por separado error Monte Carlo e incertidumbre de parámetros.

## 11. Etapas y entregables

| Etapa | Entregable | Criterio de cierre |
|---|---|---|
| A. Definición | Configuración del torneo y lista de Spy | Formato, fecha/región y reglas identificados |
| B. Datos | Fuentes, CSV originales y normalizados, auditoría | Eventos presenciales trazables y cobertura explícita |
| C. Modelo | Presencias, matriz e incertidumbre | Celdas faltantes y supuestos visibles |
| D. Motor | Simulador y validaciones | Casos control y reglas implementadas verificadas |
| E. Piloto | Benchmark y reparto final de escenarios | Costo medido y manifiesto fijado |
| F. Corrida | Agregados y checkpoints de 5M torneos | Conteo completo y reproducible |
| G. Informe | Notebook, HTML y recomendaciones | Gráficos con denominadores, límites y agenda de preparación |

Estructura propuesta: `data/raw/`, `data/processed/`, `config/`, `src/`, `tests/`, `notebooks/`, `results/` y `reports/`. Mantener los resultados grandes fuera del control de versiones y versionar manifiestos y resúmenes.

## 12. Referencias iniciales para verificar

- [Wizards: Magic Tournament Rules, versión histórica de marzo de 2024](https://media.wizards.com/ContentResources/WPN/MTG_MTR_2024_Mar11.pdf). Referencia inicial del esquema de rondas; buscar la versión aplicable a la fecha objetivo y revisar desempates y excepciones antes de implementar.
- [Pauper World: Balustrade Spy](https://pauperworld.com/cards/balustrade-spy). Candidato para descubrir eventos/listas, no dataset aceptado: incluso etiquetas de papel pueden requerir auditoría de eventos y excluir ligas.

No se adoptó ningún porcentaje ni win rate de los resultados de búsqueda. La primera entrega de datos debe justificar las fuentes definitivas y su cobertura presencial.
