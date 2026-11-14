# NEXO Wealth — prototipo educativo para Hackathon WealthTech

Abre `index.html` con doble clic en cualquier navegador reciente. No se requieren instalaciones, bases de datos ni acceso a internet.

## Actualización: datos reales del benchmark
- Se integró al HTML una curva histórica interactiva del **KN US Equity Core**, construida desde `KN_US_Equity_Core_Returns_Daily.csv` incluido en el ZIP del equipo.
- Incluye CAGR, volatilidad, máxima caída, rendimiento acumulado, composición y periodos comparables.
- El panel funciona **offline**, porque el benchmark agregado va embebido en el HTML; no requiere clave FMP.
- El nuevo archivo `benchmark_summary.json` contiene métricas y la curva mensual extraídas del ZIP.
- Estos resultados son **solo del benchmark**, NO de NEXO Wealth.
- La clave FMP recibida no se ha utilizado ni probado: no se copia ni se incluye en el ZIP del proyecto. Para usarla en el futuro, guardarla en `.env` (ignorado por git), siguiendo `.env.example`.

## Qué hace
- Cuestionario: edad (20 a 35), situación, ingreso, capital, aportación, horizonte y fondo de emergencia.
- Cuatro respuestas de tolerancia a caídas y selección de objetivos.
- Perfil didáctico por el menor de dos niveles: tolerancia y capacidad.
- Calcula porcentajes y cantidades ilustrativas para acciones, bonos, instrumentos de corto plazo y oro.
- Permite variar **manualmente** un escenario de volatilidad y muestra la redistribución.
- Desglosa el bloque accionario en sectores ilustrativos.

## Qué NO hace
- Sí muestra una serie histórica de benchmark recibida del equipo, pero NO consulta precios de las acciones ni realiza backtest de la estrategia; tampoco demuestra alfa o predice rendimientos.
- No usa IA, no crea cuentas de inversión, no realiza transacciones y no ofrece asesoría personalizada regulada.
- Los parámetros educativos NO provienen de un modelo validado.

## Siguientes pasos en Codex
1. Crear un proyecto React/Vite o seguir con HTML estático; conservar las funciones de cálculo de perfil y asignación independientes de UI.
2. Conectar datos de mercado y construir una estrategia cuantitativa con hipótesis previa, reglas de entrada/salida, timing y costos.
3. Validar su backtest frente al benchmark indicado por los organizadores: KN US Equity Core con código en Lab o SPY en plataforma.
4. Añadir curvas y métricas solo desde resultados reproducibles. Etiquetar todas las simulaciones y limitaciones.
5. Probar casos límite: sin ingresos, aporte mayor que ingreso, horizonte corto, escenario adverso y tope de concentración.
6. Preparar entregables: código, instrucciones, backtest, pitch y lámina anti-sobreajuste.

## Nota de implementación
Los nombres de sectores son explicativos, no se traducen todavía en operaciones con acciones/ETFs. La regla de volatilidad se manipula por un selector demostrativo: el próximo motor debe obtenerla exclusivamente de precios históricos disponibles antes de cada fecha de decisión.


## Integración Factor Model (14 nov 2026)
- Se localizó `KN_US_Equity_Factor_Model.zip` en Google Drive, pero **no se pudo abrir**: 652 MB superan el límite de descarga de la conexión.
- Se añadió el estado honesto de la integración a `index.html` (sin atribuciones ficticias).
- `research/FACTOR_MODEL_ROADMAP.md` explica arquitectura, prerequisitos y prioridades de ejecución.
- `scripts/inspect_factor_model.py` permite inspeccionar cabeceras del ZIP desde una computadora que tenga el archivo, sin extraerlo completamente.
- `research/factor_model_status.json` registra el bloqueo y el paso de desbloqueo.
- Factor Model no reemplaza al backtest. No se incluye ni publica ninguna credencial FMP.

## Git y Codex (inicio rápido)

Este directorio es un **repositorio Git local independiente del repositorio público de KaxaNuk**. Para crear el repositorio remoto y continuar sin perder el historial, consulta [`docs/CODEX_PASO_A_PASO.md`](docs/CODEX_PASO_A_PASO.md).

- [`AGENTS.md`](AGENTS.md): reglas obligatorias para Codex y protección de claves/datos.
- [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md): separación frontend, motor/backtest y atribución.
- [`research/HYPOTHESIS.md`](research/HYPOTHESIS.md): idea candidata, todavía sin resultados.
- [`research/FACTOR_MODEL_ROADMAP.md`](research/FACTOR_MODEL_ROADMAP.md): integración de factores pendiente de inspección.
- [`scripts/inspect_factor_model.py`](scripts/inspect_factor_model.py): genera un manifiesto pequeño del ZIP de 652 MB desde tu PC.
- [`scripts/verify_benchmark.py`](scripts/verify_benchmark.py): valida el resumen del Core; opcionalmente lo recalcula desde el ZIP original.

Ejecuta pruebas con `python -m unittest discover -s tests -v`. El archivo `benchmark_summary.json` se versiona como **resumen del benchmark**, no como rendimiento de nuestra estrategia. Los originales grandes y secretos se excluyen en `.gitignore`.

**Seguridad:** el documento FMP que contiene una clave se ha compartido previamente fuera de un gestor de secretos. Revoca/rota esa clave y restringe los permisos del documento y de la carpeta antes de desplegar servicios o abrir el repositorio a colaboradores. No pegues claves en un chat ni en el navegador.
