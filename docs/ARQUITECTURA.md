# Arquitectura mínima (separación explícita)

```text
                     NEXO Wealth — repositorio de app
index.html (perfil y explicación)          benchmark_summary.json (datos derivados)
                 |                                         |
                 +----------------- JSON de resultados --+
                                     ^
             Exportación verificada desde backtest de estrategia
                                     ^
           nexo-momentum-risk — repositorio hermano y separado
             KaxaNuk Strategy Template / Investment Lab
  OBJECTIVE -> Universe -> Curator -> Refinery -> Analyzer ->
  Portfolio -> Backtest Engine -> Attribution Analysis -> Paper Trading
            ^                           ^
       FMP (clave privada)         Core y Factor Model (archivos locales)
```

KaxaNuk Researcher es un **paquete de habilidades instalado por usuario**, no un código que debamos copiar dentro de NEXO Wealth. El ejemplo Golden Flow es un material de referencia, NO la estrategia que debemos alterar.

## Estado comprobado
- El Core histórico está disponible en el ZIP proporcionado; el resumen derivado se muestra en la app.
- La clave FMP se proporcionó por separado y no se probó ni se incorporó al repositorio.
- `KN_US_Equity_Factor_Model.zip` se localizó en Drive, pero su contenido no se pudo inspeccionar por límite de descarga de 256 MB, frente a un archivo de 652 MB. Para inspeccionarlo desde PC, usar `scripts/inspect_factor_model.py`.
- Todavía **no hay portafolio operado ni backtest validado**: el frontend muestra simulaciones ilustrativas.

## Contrato futuro de resultados
El motor deberá exportar un JSON/CSV con identificadores, fechas de observación/operación, moneda, benchmarks, returns netos, costos, pesos diarios mantenidos, supuestos y ventanas de prueba. La UI solo mostrará resultados como *verificados* cuando su origen y checks estén documentados.

## Modelo de factores
El Factor Model es una **entrada de atribución** para explicar el rendimiento de un portafolio ya probado. Requiere pesos diarios, benchmark, rendimientos por activo, alineación point-in-time, cobertura y licencia de Attribution Analysis. No confundirlo con un motor predictivo.
