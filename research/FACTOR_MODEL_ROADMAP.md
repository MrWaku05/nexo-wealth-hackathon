# NEXO Wealth — integración del KN US Equity Factor Model
Fecha de esta revisión: 14 de noviembre de 2026.

## Estado real de los archivos

**Confirmado en Google Drive:** dentro de `Hackathon Talavera Valley` están
`KN_US_Equity_Factor_Model.zip` (652,279,099 bytes), `KN_US_Equity_Core.zip`,
`FMP KEY.docx` y `Reto_WealthTech.pdf`.

**Pendiente:** no fue posible abrir el ZIP del modelo porque la conexión de Drive
limita las descargas a 268,435,456 bytes. **No hemos verificado** su listado de
archivos, columnas, fechas ni valores internos; el nombre no garantiza el formato.

**Confirmado con la copia local del Core:** contiene `Returns_Daily` (columnas
`m_date`, `return`), `Holdings_Daily` y `Membership_Daily` (fecha y tickers), y
`Tickers`. El `index.html` ya presenta la serie histórica del benchmark, pero no
existe todavía una cartera propia probada ni alfa calculado.

**La documentación pública del repositorio** describe el formato esperado del
modelo y cómo lo integra con `KaxaNuk Attribution Analysis`; esto no equivale
a una inspección de tu ZIP.

## Visión de producto

NEXO Wealth debe tener tres capas independientes:

1. **Educación y perfilamiento (frontend):** datos de Ana, objetivos, liquidez,
   horizonte, tolerancia a pérdidas y una asignación meramente ilustrativa.
2. **Motor financiero (Python / Investment Lab):** hipótesis escrita de antemano,
   selección del universo histórico, señales sin anticipación, pesos, rebalanceos,
   costos, retorno neto y comparación con KN US Equity Core en USD.
3. **Atribución (Factor Model + Attribution Analysis):** después del backtest,
   explicar cuánto de la diferencia procede del mercado, sectores u otros
   factores y cuánto queda sin explicar; reportar cobertura y limitaciones.

El modelo de factores **NO** reemplaza al backtest, los precios por acción ni
una licencia de KaxaNuk; tampoco garantiza que una cartera supere al índice.

## Mapa de entradas/salidas

| Etapa | Datos | Salida | Estado |
|---|---|---|---|
| Perfil | cuestionario | cartera didáctica | DEMO DISPONIBLE |
| Referencia | Core returns, holdings, membership, tickers | benchmark por fecha | DISPONIBLE |
| Señal | precios históricos FMP u otro proveedor | características calculadas hasta t-1 | PENDIENTE |
| Construcción | señal, límites, efectivo y calendario | pesos por fecha | PENDIENTE |
| Backtest | órdenes, precios, costos y benchmark | rendimiento neto + pesos diarios mantenidos | PENDIENTE |
| Atribución | pesos diarios, retornos de activos, holdings del índice y Factor Model | factores, residual, cobertura | PENDIENTE |

## Inspeccionar el ZIP grande sin extraerlo entero

En una computadora donde **ya esté descargado** el ZIP original, ejecutar:

```powershell
python scripts/inspect_factor_model.py "C:\ruta\KN_US_Equity_Factor_Model.zip" --output research/factor_model_manifest.json
```

El script produce un JSON pequeño con listado de CSV, primeras cabeceras,
primeros valores de la primera columna y tamaños. Compartir **solo ese
manifiesto** es suficiente para decidir la siguiente integración. No incluye
claves ni extrae 652 MB. Después, comprobar fechas y formatos con un CSV real.

## Formato esperado (NO verificado en el ZIP)

En el ejemplo `golden-flow` de KaxaNuk, el directorio de factores contiene un
CSV por factor: fecha primero (la cabecera puede estar vacía), después una
columna por acción. El nombre del archivo determina el factor. `Market`,
`Total_Factor_Returns`, `Total_Excess_Returns` e `Idyo_Returns` son series
especiales; no incluir automáticamente las tres agregadas como si fueran
factores económicos independientes. El ejemplo cita 11 sectores KN, pero su
presencia concreta en este ZIP sigue sin comprobarse.

KaxaNuk Attribution Analysis necesita:

- pesos **diarios** de estrategia después del backtest, NO solo rebalanceos;
- pesos diarios del benchmark; acciones no seleccionadas por la estrategia
  se incluyen con peso cero del lado de la cartera;
- retornos diarios por acción y series de factores alineados por fechas;
- información disponible a t-1 para justificar operaciones posteriores;
- emparejamiento explícito de tickers (`BRK.B`/`BRK-B` son un ejemplo);
- cobertura reportada si hay acciones sin precios o sin factores;
- reconciliación entre el benchmark reconstruido y sus retornos oficiales.

**Librería:** `KaxaNuk Attribution Analysis` requiere licencia/acceso separado,
según su documentación. El ZIP no es una licencia.

## Camino crítico para el hackathon (prioridades, no promesas)

### P0 — Indispensable

1. Verificar si existe acceso al motor Backtest Engine y a precios históricos.
2. Fijar la hipótesis, universo, fechas y costos ANTES de evaluar resultados.
3. Implementar una sola estrategia simple (p. ej., momentum mensual + control
   de volatilidad) y un control con solo una regla retirada.
4. Cuidar que ninguna acción individual exceda 20%; registrar efectivo y
   costes de ejecución en USD.
5. Producir resultados *por fecha*, comparables con KN US Equity Core:
   CAGR, volatilidad, máximo drawdown, Sharpe, turnover y concentración.
6. Entregar código que se ejecute, backtest, pitch y lámina anti-sobreajuste.

### P1 — Valor añadido si P0 termina

7. Obtener manifiesto y validar el Factor Model.
8. Cargar los factores en Attribution Analysis y revisar cobertura.
9. Mostrar en el pitch una atribución medible a mercado/factores/residual,
   únicamente si el cálculo se ejecutó de verdad.

### P2 — Después del evento

10. Automatizar descargas y rebalanceos, validar el modelo de perfilamiento,
    revisar seguridad, privacidad, cumplimiento regulatorio y monetización.

## Propuesta de demo en 90 segundos

- Ana introduce edad, situación, liquidez, horizonte y tolerancia.
- NEXO explica la distribución didáctica y un cambio de exposición.
- Mostrar benchmark real y **backtest propio real si existe**; no confundirlos.
- Explicar riesgo y limitaciones (costos, concentración, caídas).
- Opcional: enseñar la atribución por factores cuando esté verificada.
- Presentar el modelo de negocio como educación/investigación hasta resolver
  cualquier requisito regulatorio para asesoría personalizada.

## Fuentes técnicas

- https://github.com/KaxaNuk/Researcher
- https://github.com/KaxaNuk/Researcher/blob/main/examples/strategy/golden-flow/Experiments/attribution_analysis.py
- https://github.com/KaxaNuk/Researcher/blob/main/.apm/skills/attribution-analysis-runs/references/configuration.md
