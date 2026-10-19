# Recorridos de Pauper: un torneo compartido

**[Abrir la página publicada](https://isardi4.github.io/analysis-Spy-Nacional/)** · [Abrir informe local](reports/metagame_explorer.html)

Una corrida final de **5.000.000 de torneos**, con 110 jugadores, siete rondas suizas y eliminatorias de top8 hasta un campeón. Todos los arquetipos se registran dentro de esos mismos torneos, sin forzar un asiento.

El explorador muestra:

- Recorridos de los que hicieron top8, top4, final, campeones y quienes quedaron afuera.
- Rivales por ronda y qué cruces ganaron, perdieron o empataron.
- Probabilidades por participación de top8, top4, top2 y campeón.
- Ejemplos completos con cada rival y resultado del jugador, incluidos playoffs.
- Consulta de próximo rival por ronda y récord W/L/D exacto.
- Presencia, matriz de win rate, conteos por fuente y CSV descargables.

La presencia usa **671 plazas de 13 eventos presenciales** de los últimos 30 días, con corte 19/10/2026. El win rate suma **1.703 matches de papel y 145 cruces de top8 publicados de MTGO**. El online no determina la presencia; su muestra de eliminatorias tiene sesgo de selección. El suizo es aproximado, sin ID, drops o habilidad; los desempates y playoffs tienen supuestos explícitos en el informe.

## Método y reproducción

Ver [método del torneo compartido](docs/torneo_compartido.md).

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/build_model_v2.py
.venv/bin/python src/run_tournament.py --workers 4
.venv/bin/python src/replay_examples.py
.venv/bin/python src/report_tournament.py
.venv/bin/python -m unittest discover -s tests -v
```

Los originales ya están descargados. Para volver a consultar MTGO: `src/collect_online_v2.py`. Modelo y auditoría: `data/processed/v2/`. Corrida final: `results/tournament/`. El runner reanuda lotes locales; rechaza entradas distintas de las del manifiesto. Para cambiar el metajuego, conservar esta corrida y elegir otro directorio de resultados. El HTML funciona offline; GitHub Actions publica `reports/` en Pages al pushear a `main`.

## Antecedentes

[Plan inicial](docs/plan_montecarlo_spy.md), [método anterior](docs/metodo_y_resultados.md), [estudio anterior de Spy](reports/spy_montecarlo.html) y [selector anterior](reports/legacy_explorer.html). Se conservan para trazabilidad: **no alimentan la nueva página principal**. Las corridas anteriores tenían presupuestos repartidos entre escenarios y asientos forzados; la actual utiliza cinco millones de torneos compartidos y naturales, con eliminatorias.
