# E1 — Rotación de ETFs sectoriales (hipótesis registrada antes de consultar precios de ETF)

**Estado al 14/11/2026:** motor programado y probado sobre datos sintéticos. **No se ha ejecutado con precios reales de los nueve ETFs ni hay resultados de rendimiento.** Este documento registra una hipótesis para una primera evaluación, no demuestra que sea rentable ni fuera de muestra.

## Pregunta
¿Una cartera con momentum y filtro de tendencia, rebalanceada mensualmente, presenta una relación entre rentabilidad y riesgo atractiva frente a **KN US Equity Core**, en USD, considerando costos hipotéticos?

## Universo (fijo y predefinido)
Nueve ETFs sectoriales con historia suficiente: `XLB`, `XLE`, `XLF`, `XLI`, `XLK`, `XLP`, `XLU`, `XLV`, `XLY`. Cada ticker representa un sector o rama económica. Los ETFs no son una lista de miembros históricos del KN US Equity Core; esta estrategia **no usa** `Membership_Daily.csv` para su universo. En particular, seleccionarlos hoy puede introducir sesgos de diseño: es una **limitación declarada**.

## Reglas fijadas antes de conocer los resultados

1. Datos diarios `adjClose` (ajustados por dividendos y splits), con al menos 200 sesiones previas al inicio del periodo de evaluación.
2. En el primer día hábil de cada mes, calcular señales **hasta el cierre de la sesión anterior**.
3. Filtro de tendencia: último cierre ajustado anterior > SMA(200) anterior.
4. Momentum intermedio: cierre ajustado de t−22 / cierre ajustado de t−127 − 1, positivo. La última ventana mensual se excluye para reducir la sensibilidad al último mes.
5. Ordenar los candidatos por momentum decreciente, romper empates por ticker y elegir hasta cinco.
6. Asignar 20% de la cartera a cada ETF elegido; conservar cualquier remanente en efectivo al 0% (supuesto conservador y simplificador).
7. Rebalanceo al **cierre del primer día bursátil del mes**; los nuevos pesos producen rentabilidad **desde la siguiente sesión**. Nunca usar el cierre del día de operación como señal del propio día.
8. Cobrar costo hipotético de 10 puntos básicos sobre el valor comprado o vendido. Costo para una rotación del 100% de los ETFs a otros ETFs: 20 puntos básicos.
9. Comparar estrategia neta con benchmark oficial KN US Equity Core sobre **exactamente los mismos días**, a partir del primer día posterior al rebalanceo inicial.
10. Reportar CAGR, volatilidad anualizada, drawdown máximo, Sharpe (RF=0), suma de nocionales operados y cartera por rebalanceo.

## Restricciones y sesgos
- El reto exige 20% máximo por **acción individual**. Este experimento impone además un límite voluntario del 20% **por ETF**, que es más restrictivo.
- La estrategia depende de nueve ETFs preseleccionados. No evalúa sesgo de supervivencia de acciones individuales ni prueba que los ETF escogidos fueran óptimos en su momento.
- **No** contiene dividendos/impuestos fuera de la serie ajustada, costos reales de horquilla ni slippage observado. Se desconoce si la clave FMP tiene acceso al endpoint.
- Sin la librería privada de KaxaNuk no se le debe llamar "backtest con Investment Lab".
- Se usan precios históricos total-return para señales y marcado contable, con ejecución aproximada a cierre; para trading real, precios ajustados no son precios negociables y necesitaríamos datos de apertura/cierre efectivos.
- Las exposiciones de un **ETF no equivalen a las columnas por acción** del factor model de KaxaNuk. El Factor Model puede no cubrir estos tickers: **no inventar atribución ni cobertura**; para un análisis real quizá requiera replicar por holdings históricos de ETF o pasar a una cartera de acciones individuales dentro del universo KN.
- Un periodo posterior a 2018 descrito en el informe no debe llamarse fuera de muestra si los parámetros se escogieron tras ver datos de esos años.

## Datos y procedimiento local
1. Obtener **nueva** clave FMP tras rotar la anterior, habilitar `FMP_API_KEY` en entorno local, **nunca en Git**.
2. Descargar con `python scripts/fmp_fetch_prices.py` los nueve ETFs al directorio privado `data/private/prices/`.
3. Ejecutar `python scripts/sector_etf_backtest.py --core-zip "KN_US_Equity_Core(1).zip" --prices data/private/prices --start 2019-01-01 --end 2026-11-06`.
4. Revisar el archivo `research/sector_etf_result_LOCAL.json` (se ignora en Git por privacidad y derechos sobre datos).
5. Si hay resultados reproducibles, preparar una **salida derivada revisada** para la app con el consentimiento de uso de los datos.

## Resultado pendiente
**No calculado con datos de mercado individuales.** Solo se han comprobado propiedades del código con datos sintéticos claramente identificados.