# Experimento piloto (demostración técnica, no estrategia oficial)

**Estado:** sin factor model, sin precios por valor y sin Backtest Engine licenciado. Este ejemplo evalúa únicamente la mecánica de una regla de exposición al **índice sintético** KN US Equity Core y una reserva de efectivo al 0%. **Un índice no es directamente negociable** y estos resultados no permiten afirmar alfa ni cumplir por sí solos el reto de la cartera invertible.

## Protocolo fijo (no optimizado con los resultados)
- Datos: `KN_US_Equity_Core_Returns_Daily.csv` del ZIP del equipo, retorno diario dado por su proveedor.
- Histórico de señal: 60 sesiones pasadas; volatilidad anualizada = desviación estándar muestral * raíz(252).
- Al primer día de cada mes, se calcula la nueva exposición con datos conocidos **hasta el cierre anterior**.
- Peso objetivo en el índice: `clip(0.15 / sigma_anualizada, 0.60, 1.00)`.
- Efectivo complementario: `1 - peso`; rendimiento del efectivo supuesto en 0%.
- Costo de rebalanceo: 5 puntos básicos por dólar de exposición modificado, al inicio del día de operación.
- Los pesos se dejan derivar con el movimiento del índice entre rebalanceos.
- Se comparan benchmark sin costo y piloto sintético con costo desde el mismo día posterior a 60 observaciones.
- Se reportan CAGR, volatilidad, caída máxima y Sharpe con tasa libre de riesgo 0% (supuesto simplificador).
- El tramo posterior al 1 de enero de 2018 se reporta descriptivamente; **no** se llamará validación fuera de muestra sin asegurar que el diseño fue previo a su inspección.

## Ejecución

```powershell
python scripts/benchmark_risk_pilot.py --zip "C:\\Hackathon\\KN_US_Equity_Core.zip" --output research/benchmark_risk_pilot_LOCAL.json
python -m unittest discover -s tests -v
```

**No publicar** el ZIP o resultados derivados de sus series sin revisar los permisos de redistribución. El reporte local `research/benchmark_risk_pilot_LOCAL.json` está excluido de Git.

## Próxima etapa real del reto
Obtener precios de activos, usar una cartera de acciones y ETFs seleccionados mediante reglas expresas, respetar el límite del 20% por acción, incorporar costos y comparar los rendimientos netos de una cartera **invertible** con el benchmark oficial. **Después** aplicar el Factor Model y Attribution Analysis con pesos diarios y precios verificables.
