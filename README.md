# Pruebas Selenium con Python — Cayetano

Este repositorio contiene scripts de Selenium en Python para automatizar pruebas de navegación y funcionalidad del sitio de la Universidad Peruana Cayetano Heredia. Se cubren menús del header, buscadores y menú principal del cuerpo, con esperas robustas y evidencia visual controlada.

## Qué incluye

- Utilidades compartidas:
	- `utils/browser.py`: creación centralizada del driver de Chrome (con `webdriver-manager`) y helper para abrir URL con espera.
	- `utils/reporting.py`: reporter compartido que escribe un Excel único `Test_Report.xlsx` en la raíz, con el estado de cada caso (PASS/FAIL).
- Suites de pruebas:
	- `features/steps/Test_header.py`: CP-01..CP-09 (hover y enlaces del header).
	- `features/steps/test_Buscadores.py`: CP-10..CP-13 (postula, noticias, selector de idioma EN/ES, buscador).
	- `features/steps/Test_body.py`: CP-14..CP-20 (desplegables del menú principal y enlaces de Investigación/Internacionalización).

## Requisitos

Instala estas dependencias en tu entorno de Python:

```powershell
pip install selenium
pip install webdriver-manager
pip install openpyxl
```

Notas:
- `selenium` es el núcleo para la automatización del navegador.
- `webdriver-manager` resuelve automáticamente la versión de ChromeDriver compatible sin descargas manuales.
- `openpyxl` permite escribir el reporte Excel compartido.

## Cómo ejecutar

Cada script puede ejecutarse de forma independiente desde PowerShell en Windows:

```powershell
python .\features\steps\Test_header.py
python .\features\steps\test_Buscadores.py
python .\features\steps\Test_body.py
```

Por defecto los scripts abren `https://cayetano.edu.pe/`. Si deseas ejecutar en modo headless, puedes editar los archivos para pasar `headless=True` a `create_chrome_driver` o ajustar el parámetro en las funciones `run` si lo expones.

## Reporte compartido (Excel)

- El archivo `utils/reporting.py` crea si no existe y escribe en `Test_Report.xlsx` (en la raíz del proyecto).
- Todas las suites registran el resultado de cada CP con estas columnas: `Timestamp`, `Suite`, `CaseID`, `Description`, `Status`, `Details`.
- Se usa una única hoja llamada `Results` para mantener el historial.

## Comportamiento de esperas

- Dropdowns (CP-14..CP-18):
	- Se reemplazó el `sleep` fijo post-click por una espera corta basada en `aria-expanded == "true"` (≈1s).
	- Evidencia visual mantenida a 1.5s tras abrir el desplegable.
- Enlaces con redirección (Investigación/Internacionalización y header):
	- Tras el click, se espera carga completa y se mantiene 3s para evidencia.

## Estructura del proyecto

```
Pruebas_Selenium_Python/
├─ features/
│  └─ steps/
│     ├─ Test_header.py        # CP-01..CP-09
│     ├─ test_Buscadores.py    # CP-10..CP-13
│     └─ Test_body.py          # CP-14..CP-20
├─ utils/
│  ├─ browser.py               # Driver y helpers
│  └─ reporting.py             # Excel reporter
└─ README.md
```

## Tips y buenas prácticas

- Usa `WebDriverWait` + `expected_conditions` para evitar dependencias rígidas de `time.sleep`.
- Valida `document.readyState == "complete"` para confirmar cargas antes de tomar evidencia.
- Mantén XPaths simples y con fallback cuando el DOM cambia entre páginas (ej. `(//a)[123]`).
- Si el sitio muestra banners/overlays, considera cerrar el overlay antes de interactuar.

## Próximos pasos (opcionales)

- Añadir modo headless configurable desde línea de comandos.
- Generar también un reporte CSV para integración con otras herramientas.
- Resumen por ejecución (totales PASS/FAIL) al final del Excel.

---

Resumen: Se implementaron CP-01..CP-20 con esperas robustas, evidencia visual controlada y reporter Excel único para todas las suites. Los scripts comparten utilidades comunes y mantienen la independencia entre casos mediante `back()` y recarga de home.