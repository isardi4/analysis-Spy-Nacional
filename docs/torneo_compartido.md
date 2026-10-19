# Torneo compartido: recorridos, récords y eliminatorias

Esta entrega reemplaza la metodología visible de la página principal. El análisis usa **una sola corrida final de 5.000.000 de torneos completos**, compartida por todos los arquetipos, sin reservar un asiento para ningún mazo. Los experimentos previos se conservan, pero no alimentan estos resultados.

## Preguntas que responde

- Entre los jugadores de un arquetipo que hicieron top8, ¿a qué rivales enfrentaron en cada ronda y qué ganaron, perdieron o empataron?
- ¿Cómo difieren esos recorridos de quienes quedaron afuera, llegaron a semifinales, a la final o ganaron el torneo?
- ¿Cuál es la probabilidad global por participación de top8, top4, top2 y campeón?
- Antes de una ronda, con un W/L/D exacto, ¿qué rivales pueden aparecer y con qué frecuencia?

El filtro de recorrido condiciona al resultado futuro para estudiar historias. La consulta por récord exacto usa a todos los jugadores que llegaron a ese estado, independientemente de cómo terminaron. Son dos preguntas diferentes y el HTML las separa.

## Fuentes y matriz

Corte fijo: 19/10/2026. Ventana de 30 días inclusivos: 20/09–19/10/2026.

- Presencia: **671 plazas de 13 eventos presenciales**. Se usan las tablas completas de primera ronda de Melee y sedes verificadas. Un piloto puede aportar participaciones en distintos eventos; no son personas únicas.
- Matriz: **1.703 matches de suizo presencial + 145 matches de eliminatorias publicadas de 21 eventos MTGO**. Se descubrieron 26 eventos online; cinco páginas no publicaron el payload primario requerido. Algunos cruces tampoco pudieron etiquetarse. El listado conserva inclusiones y exclusiones.
- Los resultados online **no entran en la presencia**. Se usan parejas con resultado individual, no el récord global para inventar cruces. La muestra online está seleccionada por top8: aporta observaciones, pero no garantiza menor sesgo ni representa todo el suizo online.
- Peso 1 por match observado de cualquiera de las dos fuentes. WR decisivo `(W + 5)/(W + L + 10)`. Empates por separado con prior de media 5%. Los cruces de poca muestra dependen del prior.
- Se conservan las etiquetas auditadas y se separan errores inequívocos de colores, por ejemplo Mardu Metalcraft de White Aggro. Las etiquetas no sustituyen una revisión de todas las listas de cartas.

Datos actuales en `data/processed/v2/`, fuentes online en `data/raw/online_v2/`. Los CSV de papel previamente auditados y las tablas primarias de rondas permiten reconstruir la nueva matriz.

## Torneo

Cada torneo sortea las 110 plazas según la presencia de papel. Siete rondas suizas por puntos, con azar dentro del grupo, flotantes y sin revancha. No se modelan ID, drops, byes ni habilidad. No se reproduce un emparejador propietario.

Se registra a cada jugador antes de cada ronda en uno de **84 estados W/L/D exactos**. No se mezclan estados que sumen los mismos puntos. Se guardan rival, resultado de ese match y desenlace final del jugador.

El corte usa puntos, OMW%, GW%, OGW% y azar residual. Los marcadores de juegos para desempatar son supuestos: mitad 2-0 y mitad 2-1 en decisivos; empate 1-1.

Top8 por seeds: 1–8 / 4–5 / 2–7 / 3–6, luego ganadores adyacentes. Las eliminatorias usan el WR decisivo y no tienen empates. No se estima la ventaja de play/draw que puede dar el seed. Cada torneo produce ocho top8, cuatro top4, dos finalistas y un campeón.

## Denominadores y recorridos

La corrida registra **550.000.000 de participaciones**, **1.925.000.000 matches suizos** y **35.000.000 matches de eliminatorias**. En el suizo hay 3.850.000.000 encuentros dirigidos: cada match se observa desde cada jugador.

P(top8/top4/top2/campeón) divide clasificaciones del arquetipo por todas sus participaciones. La probabilidad del rival en una ronda/estado divide encuentros de ese rival por encuentros de jugadores del arquetipo en ese estado. Un torneo puede aportar varios jugadores del mismo mazo; se muestra también cuántos torneos distintos aportaron el estado.

Las tablas por ronda de clasificados y eliminados incluyen W/L/D contra cada rival. Las secuencias W/L/D guardan correlación temporal de resultados. Los mapas de rivales son marginales por ronda; no se presentan como una secuencia individual.

Para mostrar recorridos completos con identidad de cada rival, se reprodujeron las primeras 5.000 simulaciones del lote inicial, sin agregar ni cambiar consumos de RNG, guardando hasta cuatro ejemplos por arquetipo y desenlace. Se verificó que los once agregados del replay coincidan exactamente con el motor original en ese prefijo. Son ejemplos reales de esa corrida, limitados y no representativos; no intervienen en los denominadores.

## Resultado de Spy en esta corrida

Spy tuvo **24.589.114 participaciones**:

| Logro | Cantidad | Probabilidad por participación |
|---|---:|---:|
| Top8 | 2.378.237 | 9,67% |
| Top4 | 1.256.702 | 5,11% |
| Top2 | 662.755 | 2,70% |
| Campeón | 349.644 | 1,42% |

Estos valores corresponden al nuevo field natural y matriz mixta. No deben mezclarse con las corridas anteriores con una plaza forzada y solo datos de papel.

## Reproducir

```sh
.venv/bin/python src/collect_online_v2.py
.venv/bin/python src/build_model_v2.py
.venv/bin/python src/run_tournament.py --workers 4
.venv/bin/python src/replay_examples.py
.venv/bin/python src/report_tournament.py
.venv/bin/python -m unittest discover -s tests -v
```

La colección requiere red; con las fuentes guardadas puede reconstruirse el resto offline. El manifiesto conserva hashes de modelo, núcleo y runner, semillas y tamaños. Los 100 lotes de 50.000 torneos permiten reanudar localmente y se excluyen de Git; se publican el agregado, manifiestos, conteos y ejemplos.

Los IC Monte Carlo de rivales se calculan con momentos de los 100 lotes independientes para la razón de encuentros. Contemplan agrupación dentro del torneo; no incluyen error de la matriz ni sesgos de región, pilotos recurrentes, etiquetas o muestra de playoffs. La validación externa con torneos reservados sigue pendiente.
