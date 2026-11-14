# Reglas de colaboración para Codex — NEXO Wealth

**Lee `README.md` y `docs/CODEX_PASO_A_PASO.md` antes de cambiar código.**
Esta carpeta es una **app educativa** de hackathon. El paquete `KaxaNuk/Researcher` no es nuestro código ni nuestro backend: instalarlo para el usuario mediante su `SETUP.md` es un paso separado. Una estrategia KaxaNuk se crea con `init-strategy` en una carpeta hermana, NO dentro de este repositorio.

## Restricciones irrenunciables
1. No leer, imprimir, copiar, versionar, subir ni citar literalmente claves API, contraseñas, `FMP KEY.docx`, `.env` u otros secretos. **Nunca colocar credenciales en HTML/JS ni en una URL client-side.** Un `.env` local se usa solo en scripts/servicios de backend. Antes de `git add`, revisar `git status --short` y `git diff --cached --name-only`.
2. No subir los ZIPs de Analytics Factory ni datos originales con licencia. Publicar únicamente scripts, notas y los resúmenes redistribuibles autorizados por el equipo.
3. Distinguir tres objetos: portafolio ilustrativo de la app, serie histórica *real* del benchmark y backtest *real* de la estrategia. No atribuir a NEXO las rentabilidades del Core. No fabricar precios, alfa ni resultados.
4. No modificar `benchmark_summary.json` sin reproducir su procedencia. Un simulador educativo no cuenta como experimento válido del Investment Lab.
5. Portafolios: señales observables antes de ejecutar operaciones, costos y moneda explícitos, concentración por acción <=20%, sin sesgo de supervivencia, validación fuera de muestra.
6. Para el modelo de factores, esperar a tener su manifiesto de contenido, pesos diarios del libro, precios y acceso a Attribution Analysis. El ZIP solo no ejecuta el cálculo.
7. No hacer cambios de infraestructura innecesarios: conservar `index.html` estático mientras cumpla; evitar migrar a React sin justificación.
8. Trabajar en ramas de funcionalidad y hacer commits pequeños. Ejemplo: `feat/benchmark-validation` y `feat/strategy-export`. No subir cambios a KaxaNuk/Researcher.
9. Antes de cada entrega ejecutar `python -m unittest discover -s tests -v` y, si está instalado Node.js, `node --check` al JS exportado o pasar el smoke test de HTML.

## Meta
Diseñar una estrategia cuantitativa explicable y evaluar evidencia frente a KN US Equity Core. Si alguna dependencia falta, conservar demo y marcar resultados como **pendientes**, no simular que se hizo.
