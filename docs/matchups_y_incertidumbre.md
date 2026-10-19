# Win rates y confianza

La pestaña `?view=comparador` agrega una tabla de 20×20 con los 20 arquetipos
con mayor presencia presencial, estable al cambiar el mazo del encabezado.
Cada celda enfrenta la fila contra la columna y abre ese par en un comparador.
Muestra solo el porcentaje desde la perspectiva de la fila, con nombres
horizontales. W/L/D quedan en el tooltip y en el comparador. «Ampliar matriz» ocupa casi toda la pantalla;
se puede reducir con el botón o Escape. Los encabezados permanecen fijos.
El comparador admite todos los arquetipos identificados del modelo, incluso
los que solo tienen observaciones online. El par y el modo de la matriz se
conservan en los parámetros `a`, `b` y `wrmode` del enlace y al navegar.

## Datos y medidas

Se utiliza el mismo modelo auditado y la misma ventana 20/09–19/10/2026.
Los 1.643 matches presenciales y 145 online alimentan las observaciones; los
5 millones de torneos simulados no aumentan la muestra estadística del WR.
No se cambia la matriz ni se recalculan las simulaciones por esta vista.

- WR observado: W/(W+L), excluyendo empates. Sin decisivos se muestra sin muestra.
- IC 95% observado: Wilson con z=1,959963984540054 y n=W+L.
- WR ajustado: (W+5)/(W+L+10), exactamente el valor usado en la simulación.
- Desvío posterior: desviación estándar de Beta(W+5,L+5), expresada en puntos
  porcentuales: sqrt(αβ / ((α+β)^2(α+β+1))). No es el IC de Wilson ni la
  desviación estándar de los resultados binarios individuales.
- El desglose por papel, online y total muestra W/L/D, decisivos, matches, WR
  observado e IC de Wilson. Las probabilidades de victoria, empate y derrota
  combinan el WR decisivo y el modelo de empates ya existente.

La matriz permite alternar observado y ajustado; muestra n decisivos por celda.
En observado, un cruce sin decisivos muestra «—»; en ajustado muestra el prior.
El color codifica WR, sin representar significación o calidad de la muestra.

## Espejos y límites

El modelo almacena un ganador por match decisivo espejo y dos apariciones
por empate. La vista cuenta W[i,i] decisivos y D[i,i]/2 empates. Se presenta
50% nominal por simetría, sin fabricar W y L duplicados, IC o desvío posterior.
La única matriz usa este mismo conteo para los espejos.

Wilson presupone observaciones binomiales independientes. No contempla
agrupación por piloto, selección de playoffs online, diferencias de región,
error de etiquetas ni corrección por comparaciones múltiples. Los intervalos
no constituyen probabilidades de que el parámetro pertenezca al intervalo.
El desvío posterior depende del prior elegido, especialmente con pocos datos.

Referencias: [Wilson · NIST](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm)
y [ejemplo público de WR e IC Wilson en MetaMage](https://www.metamages.com/sessions/c4cbfe6a-4dcc-43ff-98c7-74ca5a1c9c63).
El ejemplo sirve como referencia de presentación; no se presupone que describa
todos los cálculos internos de MetaMage ni se utiliza como fuente de matches.

## Verificación

`node tests/test_matchup_stats.cjs` comprueba Wilson, extremos 0/100%, ausencia
de datos, reciprocidad, desvío posterior, fuentes y espejos. El recorrido de
navegador `node tests/test_tournament_dashboard.cjs --matchups-only` verifica
las 400 celdas, ambos modos, fuente, intercambio, enlaces, casos sin evidencia
y desplazamiento móvil. `--tabs-only` verifica las diez vistas y su navegación.

La pestaña única es «Win rates». Los enlaces anteriores `?view=winrates` se
redirigen a `comparador`, conservando sus filtros. Se eliminó la matriz modelada
duplicada; se conserva el selector de observado/ajustado en la única matriz.

La diagonal de la matriz se muestra en gris suave y con «—», sin porcentaje
ni récord. Los conteos de mirrors siguen disponibles en el comparador.

La escala del fondo es rojo–blanco–verde: 50% blanco; la intensidad aumenta
continuamente con la distancia a 50%. Los mirrors conservan el gris neutro.

Se retira el W–L de las celdas para simplificar la lectura de la matriz.

Los porcentajes usan negro. La intensidad del fondo rojo/verde llega al 50% de
opacidad en los extremos y se reduce continuamente hasta blanco en 50% de WR.
