# Prompt listo para Codex: MVP NEXO Wealth (Hackathon Track 04)

Estoy trabajando en un hackathon WealthTech cuyo reto es diseñar una empresa de inversión, implementar una estrategia dinámica, someterla a backtest después de costos y compararla con el benchmark exigido (KN US Equity Core con código en el KaxaNuk Investment Lab; SPY si se participa exclusivamente mediante plataforma). Las reglas incluyen máximo 20% del portafolio en una acción individual, universo de acciones/ETFs, riesgo visible y evaluación en USD. La presentación debe incluir una lámina sobre cómo se evitó el sobreajuste.

En esta carpeta ya hay un prototipo autónomo `index.html` con cuestionario, clasificación didáctica de riesgo, propuesta de clases de activos, escenarios hipotéticos y explicación por sectores. Lee `README.md` e inspecciona su código antes de proponer cambios. NO confundas el `KaxaNuk/Researcher` (asistente de investigación) con el Investment Lab (cálculos/licencias) y NO presupongas que están disponibles datos licenciados.

## Objetivo prioritario
Entregar una demostración operativa, comprensible en teléfonos y portátiles, fácil de lanzar y que nunca presente resultados ficticios como backtests reales. Mantén funcionalidades existentes, corrige errores, añade pruebas simples y evita dependencias innecesarias. Si no hace falta cambiar HTML/CSS/JS plano, no lo migres a un framework.

## Trabajo por prioridades
1. Ejecuta o inspecciona el HTML y detecta errores de entradas/estados, redondeo, gráficos, responsividad y accesibilidad. Corrige; documenta cada cambio.
2. Separa la lógica matemática del UI, escribiendo funciones puras testeables: perfil (capacidad y disposición), pesos base, ajuste de exposición, distribución por sectores, suma de pesos y validaciones.
3. Añade 'Explicación del motor': fórmula usada, datos utilizados, decisión de rebalanceo y advertencia que la lógica ilustrativa aún no fue validada.
4. Añade modo 'Resultados verificados' que acepte resultados externos locales en un JSON/CSV de esquema documentado. Mostrar resultados reales únicamente si archivo proporcionado tiene fechas, benchmark, retornos netos, metadatos de costos, universo, método y periodo. No crear ni interpolar rendimientos que no existan.
5. En paralelo crea un directorio `research/` con: `hypothesis.md` (hipótesis antes de mirar el backtest), `backtest_plan.md` (cómo obtener, limpiar, laggear, reequilibrar, cobrar costos y comparar datos en USD), `anti_overfitting.md` (test cronológico intacto, walk-forward, sensibilidad, sesgos y número de variantes probadas), y una tabla de verificaciones.
6. Si hay acceso a librerías y datos del Investment Lab, integrar usando instrucciones REALES de la documentación del Lab. Si faltan credenciales/licencias, no abrir ni exponer secretos y dejar el conector documentado/pendiente. Ofrecer un camino reproducible independiente para una prueba educativa, claramente etiquetada como no equivalente al backtest oficial.
7. Añade instrucciones explícitas para ejecutar, probar y entregar la app y la demo. Exporta un zip y marca cuáles archivos son necesarios para reproducir resultados.

## Restricciones y pruebas
- Nunca enviar datos a un backend sin consentimiento. Por ahora, todo local y sin cuentas personales.
- Evitar consejos individualizados para inversión real: es una simulación educativa, no compra ni venta.
- No inventar resultados, no afirmar alfa sin evidencia, no inferir disponibilidad de datos.
- No usar precio de cierre del mismo día para comprar antes de conocerlo: señal al cierre previo, ejecución posterior.
- Datos de mercado y benchmarks en USD, después de costos; montos en MXN del cuestionario son solo representaciones educativas independientes.
- Riesgo: reportar volatilidad, drawdown máximo, concentración, turnover, costos, Sharpe. Mostrar también rendimiento neto versus benchmark.
- Verificar suma de pesos 100%, porcentaje por activo y sector, entradas cero/negativas, horizonte corto y ausencia de fondo de emergencia.
- Mostrar el resultado de las pruebas y los pasos manuales para verificar la interfaz.

## Plan de entrega
Empieza con un plan de máximo 6 pasos, después implementa la opción mínima que cumpla el criterio de demo. Prioriza el funcionamiento y la honestidad de los resultados frente a añadir más pantallas o IA generativa.


## Archivos recibidos del equipo (14-11-2026)
- `KN_US_Equity_Core(1).zip` contiene retornos diarios y holdings/membresía diaria, tickers. El original no es parte del ZIP ligero de la demo.
- `benchmark_summary.json` contiene métricas derivadas; `index.html` ya presenta visualmente el benchmark real (no confundir con rentabilidad de estrategia).
- Existe un documento separado con una clave FMP que NO debe leerse en pantalla, imprimirse, compartirse, incrustarse en HTML ni enviarse a GitHub. El usuario deberá introducirla en un `.env` local ignorado; jamás colocarla en cliente/browser.
- Próximo bloque: conectar FMP desde un proceso de backend/script que conserve la clave en el entorno, obtener precios históricos de los activos seleccionados, documentar calendario, sesgos y costos. Usar este benchmark como comparación exacta por fecha.


## Factor Model y atribución — actualización
Lee `research/FACTOR_MODEL_ROADMAP.md` y `research/factor_model_status.json`.
**No inventes nombres de columnas del ZIP**: aún no fue inspeccionado. Si tienes localmente `KN_US_Equity_Factor_Model.zip`, ejecuta `scripts/inspect_factor_model.py` y valida el manifiesto. Después, solo cuando exista un backtest real y la licencia, integra KaxaNuk Attribution Analysis con pesos diarios, precios y factor files. Nunca confundas datos de referencia con resultados de una estrategia propia.
