"""Pruebas de buscadores y enlaces en el header.
CP-10: Postula aquí — Hipervínculo
CP-11: Noticias Cayetano 360 — Hipervínculo
CP-12: Selector Idioma (Bandera) — Hipervínculo (toggle EN/ES, sin usar back)
CP-13: Lupa (Buscador) — Desplegable (abrir campo de búsqueda)
"""

# Asegura que el directorio raíz del proyecto esté en sys.path para importar utils/
import os
import sys
CURRENT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.browser import create_chrome_driver, open_and_wait
from utils.reporting import append_result, get_report_path, ensure_report_exists
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _wait_page_ready(driver, timeout: int = 10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except Exception:
        pass


def _handle_possible_new_tab(driver, prev_handles):
    # Si se abrió una nueva pestaña, cambiar a ella; de lo contrario, quedarse
    new_handles = driver.window_handles
    if len(new_handles) > len(prev_handles):
        # Cambiar al último handle (nuevo tab)
        driver.switch_to.window(new_handles[-1])
        return True
    return False


def run(url: str = "https://cayetano.edu.pe/", headless: bool = False) -> None:
    """Ejecuta CP-10 a CP-13 sobre el sitio principal.

    - Usa utils.browser para crear el driver y abrir la página.
    - Incluye comentarios claros de inicio/fin en cada caso.
    - Espera de carga y 3s de evidencia visual después de cada redirección.
    """
    driver = create_chrome_driver(headless=headless)

    try:
        open_and_wait(driver, url, seconds=3)
        print(f"Página abierta: {driver.title}")
        wait = WebDriverWait(driver, 10)
        # Reporte compartido
        REPORT_PATH = get_report_path(ROOT_DIR)
        ensure_report_exists(REPORT_PATH)
        SUITE = "test_Buscadores"

        # ===== Inicio CP-10: Postula aquí — Hipervínculo =====
        xpath_postula = "//a[normalize-space()='Postula aquí']"
        link_postula = wait.until(EC.presence_of_element_located((By.XPATH, xpath_postula)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_postula)
        except Exception:
            pass
        prev_url_10 = driver.current_url
        prev_handles = driver.window_handles
        try:
            link_postula.click()
        except Exception as e:
            append_result(REPORT_PATH, SUITE, "CP-10", "Postula aquí — Hipervínculo", "FAIL", str(e))
            raise
        # Manejar posible nueva pestaña
        opened_new_tab = _handle_possible_new_tab(driver, prev_handles)
        # Esperar carga y evidencia
        _wait_page_ready(driver, timeout=10)
        time.sleep(3)
        print(f"CP-10: Click en 'Postula aquí'. URL ahora: {driver.current_url} | new_tab={opened_new_tab}")
        append_result(REPORT_PATH, SUITE, "CP-10", "Postula aquí — Hipervínculo", "PASS", f"new_tab={opened_new_tab} -> {driver.current_url}")
        # Volver al origen
        if opened_new_tab:
            driver.close()
            driver.switch_to.window(prev_handles[0])
        else:
            driver.back()
        open_and_wait(driver, url, seconds=2)
        # ===== Fin CP-10 =====

        # ===== Inicio CP-11: Noticias Cayetano 360 — Hipervínculo =====
        xpath_noticias = "//a[normalize-space()='Noticias Cayetano 360']"
        link_noticias = wait.until(EC.presence_of_element_located((By.XPATH, xpath_noticias)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_noticias)
        except Exception:
            pass
        prev_url_11 = driver.current_url
        prev_handles = driver.window_handles
        try:
            link_noticias.click()
        except Exception as e:
            append_result(REPORT_PATH, SUITE, "CP-11", "Noticias Cayetano 360 — Hipervínculo", "FAIL", str(e))
            raise
        opened_new_tab = _handle_possible_new_tab(driver, prev_handles)
        _wait_page_ready(driver, timeout=10)
        time.sleep(3)
        print(f"CP-11: Click en 'Noticias Cayetano 360'. URL ahora: {driver.current_url} | new_tab={opened_new_tab}")
        append_result(REPORT_PATH, SUITE, "CP-11", "Noticias Cayetano 360 — Hipervínculo", "PASS", f"new_tab={opened_new_tab} -> {driver.current_url}")
        if opened_new_tab:
            driver.close()
            driver.switch_to.window(prev_handles[0])
        else:
            driver.back()
        open_and_wait(driver, url, seconds=2)
        # ===== Fin CP-11 =====

        # ===== Inicio CP-12: Selector Idioma (Bandera) — Hipervínculo =====
        # 1) Click en Inglés, validar /en/ y esperar 3s
        xpath_en = "//img[@alt='Inglés']"
        img_en = wait.until(EC.presence_of_element_located((By.XPATH, xpath_en)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img_en)
        except Exception:
            pass
        prev_url_12 = driver.current_url
        try:
            img_en.click()
        except Exception as e:
            append_result(REPORT_PATH, SUITE, "CP-12", "Selector Idioma — Inglés", "FAIL", str(e))
            raise
        WebDriverWait(driver, 10).until(lambda d: ("/en/" in d.current_url) or (d.current_url != prev_url_12))
        _wait_page_ready(driver, timeout=10)
        time.sleep(3)
        print(f"CP-12: Cambiado a Inglés. URL: {driver.current_url}")
        append_result(REPORT_PATH, SUITE, "CP-12A", "Selector Idioma — Inglés", "PASS", driver.current_url)

        # 2) Click en Español (sin usar back), esperar 3s y validar que se quitó /en/
        xpath_es = "//img[@alt='Site in spanish']"
        img_es = wait.until(EC.presence_of_element_located((By.XPATH, xpath_es)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img_es)
        except Exception:
            pass
        try:
            img_es.click()
        except Exception as e:
            append_result(REPORT_PATH, SUITE, "CP-12", "Selector Idioma — Español", "FAIL", str(e))
            raise
        WebDriverWait(driver, 10).until(lambda d: ("/en/" not in d.current_url))
        _wait_page_ready(driver, timeout=10)
        time.sleep(3)
        print(f"CP-12: Regresado a Español. URL: {driver.current_url}")
        append_result(REPORT_PATH, SUITE, "CP-12B", "Selector Idioma — Español", "PASS", driver.current_url)
        # Volver a home explícitamente para continuar (sin usar back)
        open_and_wait(driver, url, seconds=2)
        # ===== Fin CP-12 =====

        # ===== Inicio CP-13: Lupa (Buscador) — Desplegable =====
        # Intentar abrir el campo de búsqueda en el header.
        # Probamos varios selectores comunes del bloque de búsqueda de WordPress.
        search_icon_xpaths = [
            "//button[contains(@class,'wp-block-search__button')]",
            "//form[contains(@class,'wp-block-search')]//button[contains(@class,'wp-block-search__button')]",
            "//button[@aria-label='Buscar' or @aria-label='Search']",
            "//img[contains(@alt,'Buscar') or contains(@alt,'Search')]/ancestor::button[1]",
        ]
        search_clicked = False
        for sx in search_icon_xpaths:
            try:
                btn = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, sx)))
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                except Exception:
                    pass
                btn.click()
                search_clicked = True
                break
            except Exception:
                continue

        if not search_clicked:
            print("CP-13: No se encontró el botón de búsqueda con selectores conocidos.")
            append_result(REPORT_PATH, SUITE, "CP-13", "Lupa (Buscador) — Desplegable", "FAIL", "No se encontró botón de búsqueda")
        else:
            # Esperar que aparezca el input del buscador
            input_xpath = "//input[contains(@class,'wp-block-search__input')] | //input[@type='search']"
            try:
                inp = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, input_xpath))
                )
                ActionChains(driver).move_to_element(inp).perform()
                # Evidencia visual: mantener el campo abierto 3s
                time.sleep(3)
                print("CP-13: Campo de búsqueda visible.")
                append_result(REPORT_PATH, SUITE, "CP-13", "Lupa (Buscador) — Desplegable", "PASS", "Campo visible")
            except Exception:
                print("CP-13: No se pudo mostrar el campo de búsqueda.")
                append_result(REPORT_PATH, SUITE, "CP-13", "Lupa (Buscador) — Desplegable", "FAIL", "No se mostró el campo")
        # ===== Fin CP-13 =====

    finally:
        driver.quit()
        print("Navegador cerrado.")


if __name__ == "__main__":
    run()
