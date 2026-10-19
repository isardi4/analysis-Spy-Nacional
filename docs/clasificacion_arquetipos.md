# Revisión de categorías agregadas

Corte: 19/10/2026; presencia presencial del 20/09 al 19/10. Se revisaron las
105 listas de categorías Other, Other Affinity y Other Tron. Se recuperaron
103 participaciones mediante combinaciones explícitas de cartas, sin asignar
un arquetipo por el color de la etiqueta. Las 2 listas restantes no muestran
información suficiente. Se excluyen además las 19 participaciones Unknown.

La muestra modelada queda en **650/671 plazas (96,9%)**, renormalizadas al 100%.
El torneo de 110 jugadores representa ese field identificado. La exclusión puede
sesgar la presencia si las plazas sin identificar tenían otra composición. Los
60 matches presenciales que involucran plazas excluidas se omiten también.
Las categorías con pocas observaciones dependen fuertemente del prior de WR.

La auditoría por participación conserva evento, etiqueta original, GUID, categoría
resuelta, cartas utilizadas como evidencia, URL pública y hash de la página en
`data/processed/classified/classification_audit.json`. Las cartas originales se
conservan en `data/raw/classification/`; las reglas en `src/classify_decks.py`.
Las etiquetas ya identificadas se mantienen de la auditoría anterior; esta
revisión no pretende homogeneizar todas las variantes del formato.

| Categoría recuperada | Participaciones |
|---|---:|
| Red Rally | 21 |
| Monster Tron | 12 |
| Red Madness | 7 |
| Sacrifice | 6 |
| Jund Wildfire | 6 |
| Pinger Tron | 5 |
| Mardu Metalcraft | 4 |
| Four Color Affinity | 3 |
| White Weenie Affinity | 3 |
| Mono Black Control | 3 |
| Esper Affinity | 2 |
| Gruul Impact Tremors | 2 |
| Synthesizer | 2 |
| Red Equipment Aggro | 2 |
| Four Color Snow | 2 |
| Skred | 1 |
| Tribe | 1 |
| White Aggro | 1 |
| Golgari Lifegain | 1 |
| Grixis Affinity | 1 |
| Flicker Tron | 1 |
| Rakdos Madness | 1 |
| Spy Combo | 1 |
| Familiars | 1 |
| Gardens | 1 |
| Turbo Fog | 1 |
| Azorius Affinity | 1 |
| Burn | 1 |
| Dimir Affinity | 1 |
| Reality Acid | 1 |
| Pizza Combo | 1 |
| Azorius Faeries | 1 |
| Bant Affinity | 1 |
| Grixis Control | 1 |
| Pactdoll Tron | 1 |
| Azorius Allies | 1 |
| Zubera Combo | 1 |
| Golgari Altar Combo | 1 |

## Win rates online

Se revisaron también las 60 etiquetas ambiguas de los lados de matches online,
identificando la lista mediante el login del jugador en cada posición del bracket
primario MTGO. Se recuperan las 60 etiquetas y se conservan los **145 matches**
previamente auditados. Un mismo jugador aparece varias veces al avanzar en el
bracket: 60 etiquetas no significan 60 mazos ni 60 matches independientes.
La auditoría está en `online_classification_audit.json` y las filas resultantes
en `online_matches.csv`, dentro de `data/processed/classified/`.
Esto solo alimenta el WR, nunca los porcentajes de presencia.

Los porcentajes del dashboard proceden de una nueva corrida compartida de
5 millones de torneos con el modelo identificado. La corrida anterior se
conserva en `results/tournament/`; la actual está en `results/classified/`.
