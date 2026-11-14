# Codex y Git, paso a paso — Windows / Hackathon WealthTech

## Parte A — NEXO Wealth: este repositorio

1. Descarga el paquete del proyecto y extrae la carpeta `nexo_wealth_git` en una ruta corta, por ejemplo `C:\Hackathon\nexo-wealth-hackathon`. **No** copies aquí `FMP KEY.docx`, `.env`, ni los ZIP grandes.
2. Abre **Codex (app de escritorio o CLI)** en esa carpeta. Codex debe trabajar en una carpeta de proyecto, no solo en un chat web sin acceso a tus archivos.
3. En Codex, pide: `Lee README.md, AGENTS.md y docs/CODEX_PASO_A_PASO.md. Verifica las pruebas y explícame el estado actual. No publiques ni leas secretos. No modifiques KaxaNuk/Researcher.`
4. Verifica `git status` y `git log --oneline -3`. El paquete incluye historial Git: no es necesario repetir `git init`.
5. Crea desde GitHub un repositorio **vacío y privado**, llamado `nexo-wealth-hackathon` bajo tu cuenta `MrWaku05`. **No marques** crear README, licencia o `.gitignore`, pues ya existen localmente.
6. En la terminal de Codex, desde esta carpeta, escribe:

```powershell
git remote add origin https://github.com/MrWaku05/nexo-wealth-hackathon.git
git push -u origin main
```

Si la URL ya existe como `origin`, comprobarla con `git remote -v` antes de reemplazarla. GitHub puede abrir el navegador para autorizar. Si te aparece "Repository not found", confirma que el repositorio esté creado y que Codex/terminal tenga acceso.

7. Abre `index.html` y prueba el cuestionario, datos negativos y cambio del escenario. Para pruebas automáticas:

```powershell
python -m unittest discover -s tests -v
python scripts/verify_benchmark.py --summary benchmark_summary.json
```

8. En Codex, el primer encargo debe ser **validar y mantener lo que funciona**. Solo después crea una rama para cambios nuevos:

```powershell
git switch -c feat/financial-engine
```

Codex podrá hacer cambios en esa rama, ejecutar pruebas y preparar un PR hacia `main` en TU repositorio.

## Parte B — KaxaNuk Researcher: instalar habilidades, NO clonar la aplicación

Este paquete tiene instalación propia. En Codex, abre una conversación distinta y pega literalmente el mensaje que recomienda el README oficial:

```text
Please install this repo for me and set up my researcher, start to finish in this conversation — install everything it needs without asking first: https://github.com/KaxaNuk/Researcher
```

Lee: https://github.com/KaxaNuk/Researcher/blob/main/SETUP.md

El instalador debe seguir los pasos 0–6: idioma, herramientas Git y uv, instalación del paquete vía APM, creación del investigador, entrevista y entrega. Responde **Español** si te lo pregunta. Autoriza los cambios locales que esperas. En Codex puede requerir permisos fuera de sandbox para instalar en tu carpeta de usuario.

El `SETUP.md` oficial lista, entre otros, estos comandos (es mejor dejar que el asistente los gestione):

```powershell
git --version
uv --version
uv tool install apm-cli==0.33.0
uvx --from apm-cli==0.33.0 apm install -g KaxaNuk/Researcher --target codex
```

**Esto NO instala automáticamente** las licencias del Backtest Engine, Portfolio Construction o Attribution Analysis.

## Parte C — Aprender la estrategia con el ejemplo y crear la propia

Con Researcher instalado:

1. En una conversación nueva, pide `init-example` para **estudiar** Golden Flow. No modificarlo para que parezca nuestro.
2. En el lugar donde guardarás **una estrategia separada**, pide `init-strategy nexo-momentum-risk`. Generará una carpeta repositorio hermana, NO dentro del repo web. Sigue su propio `SETUP.md`.
3. Pide `objective` para documentar una hipótesis antes del backtest; después `blueprint 1` y los pasos de universo/datos.
4. Comprueba acceso a FMP y datos de Analytics Factory (factor model y Core), sin mostrar la clave ni subirlos a GitHub.
5. Construye señales laggeadas, pesos, rebalanceos, costos, control sin el filtro, benchmark por fecha, evaluación fuera de muestra y atribución si existe licencia.
6. Exporta únicamente resultados verificados y permitidos a un archivo pequeño que pueda leer la app NEXO Wealth, con procedencia y advertencias.

No uses `uv sync` sin `--inexact` después de añadir manualmente las librerías licenciadas: el documento de KaxaNuk advierte que la sincronización exacta puede quitarlas. Para el ejemplo, usa `uv sync --group notebook --inexact`.

## Si algo falla
- `uv` no existe: solicita a Codex instalarlo según `SETUP.md` y verificarlo.
- Credenciales FMP: ponerlas exclusivamente en variables de entorno local, no en JS, README, chats compartidos ni repositorio.
- Modelo de factores de 652 MB: ejecutar `python scripts/inspect_factor_model.py "C:\\ruta\\KN_US_Equity_Factor_Model.zip" --output research/factor_model_manifest.json` en la PC donde se descargó.
- No hay licencia del Lab: detenerse en outputs de cartera y documentar el bloqueo; no llamar *backtest oficial* a un simulador alternativo.
- No hay repo remoto todavía: el repo Git local y su historial siguen funcionando.
