# Capturas de fuentes

Las capturas de `events45.html`, `events/`, `primary/` y `rounds/` documentan los eventos recientes. `primary_audit.json` vincula el identificador de descubrimiento con la página primaria y sus rondas. Las tablas usadas son las respuestas `standings_*.json` de primera ronda y `matches_*.json` de las rondas suizas. El lector exige respuestas completas (`len(data) == recordsTotal`).

`paths/` y los archivos de muestra de Melee son consultas exploratorias que permitieron descubrir la estructura de resultados. No intervienen en `build_model.py` ni en la corrida definitiva. Las tablas de posiciones de `GetTournamentViewData` solo muestran los primeros ocho: no se usan como denominador del field.

`summer2026_meta.html` y `summer2026_matches.html` son fuentes exploratorias de julio, **excluidas** por la restricción final de 30/45 días. No son entradas de ningún modelo. Las páginas `recent_meta.html`, `recent_matrix.html` y `meta45.html` también son exploratorias: devolvieron ausencia de matriz con el filtro paper y no se usaron.

Los CSV aceptados están en `../processed/`; sus filas se reconstruyen exclusivamente desde las fuentes recientes verificadas. Los originales pueden contener nombres públicos de pilotos; los CSV finales usan identificadores seudónimos. El usuario autorizó subir el proyecto a GitHub el 19/10/2026. Los originales son capturas de páginas públicas; no contienen credenciales.

## Actualización: matriz con online

`online_v2/` contiene páginas primarias de MTGO y sus índices de etiquetas. Se aceptaron 145 resultados individuales de playoffs de 21 eventos; cinco páginas sin payload primario de partidas se excluyeron. Solo la matriz de la nueva corrida utiliza estos matches, nunca la presencia. Ver `data/processed/online_sources_v2.csv`, `data/processed/v2/sources.json` y `docs/torneo_compartido.md`. Las páginas `online_matrix30.html` y `mixed_matrix30.html` fueron consultas exploratorias sin matriz y no se usan.
