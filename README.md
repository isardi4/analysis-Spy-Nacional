# Metajuego presencial y caminos al top 8

**Página publicada:** https://isardi4.github.io/analysis-Spy-Nacional/

Informe para elegir un arquetipo de Pauper y explorar sus resultados en un torneo simulado de 110 plazas, 7 rondas suizas y corte a top 8.

- **[Abrir explorador de mazos](reports/metagame_explorer.html)**: selector de mazo, ventana 30/45 días, ronda y puntos; gráficos y tablas funcionan sin conexión.
- **[Análisis detallado de Spy](reports/spy_montecarlo.html)**: estudio original de 5 millones de torneos, incluyendo field natural e incertidumbre de parámetros.
- **[Plan y decisiones](docs/plan_montecarlo_spy.md)**.
- **[Método y resultados](docs/metodo_y_resultados.md)**.

Los datos tienen corte fijo al **19/10/2026**. Ventanas inclusivas: **20/09–19/10** y **05/09–19/10**. No se usan resultados online ni eventos anteriores a esas ventanas. Son participaciones en eventos, no personas únicas. La región y las listas de 75 no están calibradas al torneo del usuario.

## Ejecutar con las fuentes ya descargadas

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/build_model.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python src/run.py --workers 4
.venv/bin/python src/report.py
.venv/bin/python src/run_general.py
.venv/bin/python src/report_general.py
```

Abrir el HTML en un navegador. No hace falta servidor ni conexión a internet.

`run.py` y `run_general.py` reanudan lotes existentes. Rechazan entradas distintas de las del manifiesto: para otro metajuego o motor, usar otro directorio de resultados, conservando el anterior. El estudio original suma exactamente 5M; el selector general tiene una corrida adicional con su propio manifiesto, conteos y semillas. No se mezclan escenarios para estimar una única probabilidad.

## Datos y auditoría

`data/processed/events_accepted.csv` contiene fechas primarias y sedes de los eventos usados. `entries.csv` incluye el field completo de primera ronda, con `Unknown` si falta lista. `matches.csv` contiene cruces suizos deduplicados; `archetype_aliases.csv` documenta normalización. Los archivos `model30.npz` y `model45.npz` son matrices recíprocas regularizadas, no win rates puros observados.

La búsqueda comenzó en MetaMage con filtro de papel; los participantes y resultados se reconstruyen desde las tablas públicas de Melee. La colección exploratoria puede reproducirse con `collect.py`, `prepare.py`, `audit_primary.py` y `collect_rounds.py`; el acceso a esas páginas requiere internet. Las fechas de descubrimiento están fijadas en el código para esta entrega, no se actualizan silenciosamente al día de ejecución.

## Límites

El suizo es una aproximación, con flotantes y prevención de revancha. No simula ID, drops, byes ni habilidad. El desempate usa puntajes y resultados de juegos simulados; los marcadores BO3 se suponen. Las celdas poco observadas se acercan a 50% mediante un prior, y las categorías agregadas pueden ocultar diferencias entre listas. Un intervalo Monte Carlo estrecho no equivale a una predicción precisa del torneo real.
