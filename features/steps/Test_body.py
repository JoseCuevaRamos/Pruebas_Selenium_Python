"""Pruebas del cuerpo (menú principal 2) y enlaces de investigación/internacionalización.
CP-14: Sobre Cayetano — Desplegable (listar opciones visibles)
CP-15: Admisión — Desplegable (listar subcategorías)
CP-16: Pregrado — Desplegable (listar carreras)
CP-17: Posgrado — Desplegable (listar categorías)
CP-18: Educación Continua — Desplegable (listar cursos/diplomados/talleres)
CP-19: Investigación — Hipervínculo (redirige y vuelve atrás tras 3s)
CP-20: Internacionalización — Hipervínculo (redirige y vuelve atrás tras 3s)
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


def _find_element_any(driver, wait: WebDriverWait, xpaths: list[str], visible: bool = False):
    """Intenta encontrar el primer elemento que coincida con alguna XPath de la lista."""
    for xp in xpaths:
        try:
            locator = (By.XPATH, xp)
            el = wait.until(
                EC.visibility_of_element_located(locator) if visible else EC.presence_of_element_located(locator)
            )
            return el
        except Exception:
            continue
    raise Exception(f"No se encontró ningún elemento usando los XPaths: {xpaths}")


def _listar_opciones_desplegable(driver, button_xpaths: list[str], wait: WebDriverWait, titulo: str):
    # Buscar el botón con múltiples alternativas (más robusto ante variaciones)
    btn = _find_element_any(driver, wait, button_xpaths, visible=True)
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
    except Exception:
        pass
    # Click para desplegar
    btn.click()
    # Espera corta basada en estado (aria-expanded) en lugar de sleep fijo
    try:
        WebDriverWait(driver, 1).until(
            lambda d: ((btn.get_attribute("aria-expanded") or "").lower() == "true")
        )
    except Exception:
        pass
    # Submenú bajo el li contenedor
    li = btn.find_element(By.XPATH, "./ancestor::li[1]")
    anchors = li.find_elements(By.XPATH, ".//a[@class='wp-block-navigation-item__content']")
    visibles = [a for a in anchors if a.is_displayed() and (a.text or "").strip()]
    nombres = [a.text.strip() for a in visibles]
    if nombres:
        print(f"{titulo}: opciones visibles -> {nombres}")
        # Evidencia visual: desplegables 1.5s
        time.sleep(1.5)
    else:
        print(f"{titulo}: no se encontraron opciones visibles.")
    return nombres


def _listar_opciones_desplegable_exacto(driver, button_xpath: str, wait: WebDriverWait, titulo: str):
    """Abre un desplegable usando el XPath exacto del botón y lista sus opciones visibles."""
    # Asegurar que el nav principal está en viewport
    try:
        nav = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//nav[@aria-label='Menú Principal 2']"))
        )
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", nav)
        except Exception:
            pass
    except Exception:
        pass

    # Esperar a que el botón sea cliqueable
    btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, button_xpath))
    )
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
    except Exception:
        pass

    # Click normal, con fallback JS si falla por overlays
    try:
        btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn)
    # Espera corta basada en aria-expanded
    try:
        WebDriverWait(driver, 1).until(
            lambda d: ((btn.get_attribute("aria-expanded") or "").lower() == "true")
        )
    except Exception:
        pass

    # Submenú bajo el li contenedor
    li = btn.find_element(By.XPATH, "./ancestor::li[1]")
    anchors = li.find_elements(By.XPATH, ".//a[@class='wp-block-navigation-item__content']")
    if not anchors:
        # Fallback: cualquier <a> visible dentro del li
        anchors = li.find_elements(By.XPATH, ".//a")
    visibles = [a for a in anchors if a.is_displayed() and (a.text or "").strip()]
    nombres = [a.text.strip() for a in visibles]
    if nombres:
        print(f"{titulo}: opciones visibles -> {nombres}")
        time.sleep(1.5)
    else:
        print(f"{titulo}: no se encontraron opciones visibles.")
    return nombres


def _listar_opciones_desplegable_basico(
    driver,
    wait: WebDriverWait,
    primary_xpath: str,
    fallback_xpath: str,
    titulo: str,
):
    """Versión básica: intenta con el XPath primario y si falla, usa el fallback; luego lista opciones visibles."""
    el = None
    # Intento rápido sin espera para el primario
    primarios = driver.find_elements(By.XPATH, primary_xpath)
    if primarios:
        el = primarios[0]
    else:
        # Espera corta para el primario
        try:
            el = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, primary_xpath))
            )
        except Exception:
            # Intento rápido sin espera para el fallback
            fallbacks = driver.find_elements(By.XPATH, fallback_xpath)
            if fallbacks:
                el = fallbacks[0]
            else:
                # Espera corta para el fallback
                try:
                    el = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.XPATH, fallback_xpath))
                    )
                except Exception:
                    el = None

    if not el:
        print(f"{titulo}: no se encontró el botón con XPaths básicos.")
        return

    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
    except Exception:
        pass

    try:
        el.click()
    except Exception:
        driver.execute_script("arguments[0].click();", el)
    # Espera corta basada en aria-expanded
    try:
        WebDriverWait(driver, 1).until(
            lambda d: ((el.get_attribute("aria-expanded") or "").lower() == "true")
        )
    except Exception:
        pass

    li = el.find_element(By.XPATH, "./ancestor::li[1]")
    anchors = li.find_elements(By.XPATH, ".//a[@class='wp-block-navigation-item__content']")
    visibles = [a for a in anchors if a.is_displayed() and (a.text or "").strip()]
    nombres = [a.text.strip() for a in visibles]
    if nombres:
        print(f"{titulo}: opciones visibles -> {nombres}")
        time.sleep(1.5)
    else:
        print(f"{titulo}: no se encontraron opciones visibles.")
    return nombres


def run(url: str = "https://cayetano.edu.pe/", headless: bool = False) -> None:
    driver = create_chrome_driver(headless=headless)

    try:
        open_and_wait(driver, url, seconds=3)
        print(f"Página abierta: {driver.title}")
        wait = WebDriverWait(driver, 10)
        # Reporte compartido
        REPORT_PATH = get_report_path(ROOT_DIR)
        ensure_report_exists(REPORT_PATH)
        SUITE = "Test_body"

        # ===== Inicio CP-14: Sobre Cayetano — Desplegable =====
        cp14_primary = "//nav[@aria-label='Menú Principal 2']//button[@aria-label='Submenú de Sobre Cayetano']"
        cp14_fallback = "(//button[@aria-label='Submenú de Sobre Cayetano'])[2]"
        try:
            nombres_14 = _listar_opciones_desplegable_basico(driver, wait, cp14_primary, cp14_fallback, "CP-14 Sobre Cayetano")
            status_14 = "PASS" if nombres_14 else "FAIL"
            append_result(REPORT_PATH, SUITE, "CP-14", "Sobre Cayetano — Desplegable", status_14, ", ".join(nombres_14))
        except Exception as e:
            append_result(REPORT_PATH, SUITE, "CP-14", "Sobre Cayetano — Desplegable", "FAIL", str(e))
        # ===== Fin CP-14 =====

        # ===== Inicio CP-15: Admisión — Desplegable (básico: exacto + fallback) =====
        cp15_primary = "//nav[@aria-label='Menú Principal 2']//button[@aria-label='Submenú de Admisión']"
        cp15_fallback = "(//button[@aria-label='Submenú de Admisión'])[2]"
        try:
            nombres_15 = _listar_opciones_desplegable_basico(driver, wait, cp15_primary, cp15_fallback, "CP-15 Admisión")
            status_15 = "PASS" if nombres_15 else "FAIL"
            append_result(REPORT_PATH, SUITE, "CP-15", "Admisión — Desplegable", status_15, ", ".join(nombres_15))
        except Exception as e:
            append_result(REPORT_PATH, SUITE, "CP-15", "Admisión — Desplegable", "FAIL", str(e))
        # ===== Fin CP-15 =====

        # ===== Inicio CP-16: Pregrado — Desplegable (básico: exacto + fallback) =====
        cp16_primary = "//nav[@aria-label='Menú Principal 2']//button[@aria-label='Submenú de Pregrado']"
        cp16_fallback = "(//button[@aria-label='Submenú de Pregrado'])[2]"
        try:
            nombres_16 = _listar_opciones_desplegable_basico(driver, wait, cp16_primary, cp16_fallback, "CP-16 Pregrado")
            status_16 = "PASS" if nombres_16 else "FAIL"
            append_result(REPORT_PATH, SUITE, "CP-16", "Pregrado — Desplegable", status_16, ", ".join(nombres_16))
        except Exception as e:
            append_result(REPORT_PATH, SUITE, "CP-16", "Pregrado — Desplegable", "FAIL", str(e))
        # ===== Fin CP-16 =====

        # ===== Inicio CP-17: Posgrado — Desplegable (básico: exacto + fallback) =====
        cp17_primary = "//nav[@aria-label='Menú Principal 2']//button[@aria-label='Submenú de Posgrado']"
        cp17_fallback = "(//button[@aria-label='Submenú de Posgrado'])[2]"
        try:
            nombres_17 = _listar_opciones_desplegable_basico(driver, wait, cp17_primary, cp17_fallback, "CP-17 Posgrado")
            status_17 = "PASS" if nombres_17 else "FAIL"
            append_result(REPORT_PATH, SUITE, "CP-17", "Posgrado — Desplegable", status_17, ", ".join(nombres_17))
        except Exception as e:
            append_result(REPORT_PATH, SUITE, "CP-17", "Posgrado — Desplegable", "FAIL", str(e))
        # ===== Fin CP-17 =====

        # ===== Inicio CP-18: Educación Continua — Desplegable (básico: exacto + fallback) =====
        cp18_primary = "//nav[@aria-label='Menú Principal 2']//button[@aria-label='Submenú de Educación Continua']"
        cp18_fallback = "(//button[@aria-label='Submenú de Educación Continua'])[2]"
        try:
            nombres_18 = _listar_opciones_desplegable_basico(driver, wait, cp18_primary, cp18_fallback, "CP-18 Educación Continua")
            status_18 = "PASS" if nombres_18 else "FAIL"
            append_result(REPORT_PATH, SUITE, "CP-18", "Educación Continua — Desplegable", status_18, ", ".join(nombres_18))
        except Exception as e:
            append_result(REPORT_PATH, SUITE, "CP-18", "Educación Continua — Desplegable", "FAIL", str(e))
        # ===== Fin CP-18 =====

        # ===== Inicio CP-19: Investigación — Hipervínculo =====
        cp19_primary = "//body[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/nav[1]/ul[1]/li[6]/a[1]"
        cp19_fallback = "(//a)[123]"
        a_investigacion = _find_element_any(driver, wait, [cp19_primary, cp19_fallback], visible=False)
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", a_investigacion)
        except Exception:
            pass
        try:
            prev_url_19 = driver.current_url
            a_investigacion.click()
            WebDriverWait(driver, 10).until(lambda d: d.current_url != prev_url_19)
            _wait_page_ready(driver, timeout=10)
            time.sleep(3)
            print(f"CP-19: Click en 'Investigación'. URL: {driver.current_url}")
            append_result(REPORT_PATH, SUITE, "CP-19", "Investigación — Hipervínculo", "PASS", driver.current_url)
        except Exception as e:
            append_result(REPORT_PATH, SUITE, "CP-19", "Investigación — Hipervínculo", "FAIL", str(e))
        finally:
            try:
                driver.back()
                open_and_wait(driver, url, seconds=2)
            except Exception:
                pass
        # ===== Fin CP-19 =====

        # ===== Inicio CP-20: Internacionalización — Hipervínculo =====
        cp20_primary = "//body[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/nav[1]/ul[1]/li[7]/a[1]"
        cp20_fallback = "(//a)[124]"
        a_internac = _find_element_any(driver, wait, [cp20_primary, cp20_fallback], visible=False)
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", a_internac)
        except Exception:
            pass
        try:
            prev_url_20 = driver.current_url
            a_internac.click()
            WebDriverWait(driver, 10).until(lambda d: d.current_url != prev_url_20)
            _wait_page_ready(driver, timeout=10)
            time.sleep(3)
            print(f"CP-20: Click en 'Internacionalización'. URL: {driver.current_url}")
            append_result(REPORT_PATH, SUITE, "CP-20", "Internacionalización — Hipervínculo", "PASS", driver.current_url)
        except Exception as e:
            append_result(REPORT_PATH, SUITE, "CP-20", "Internacionalización — Hipervínculo", "FAIL", str(e))
        finally:
            try:
                driver.back()
                open_and_wait(driver, url, seconds=2)
            except Exception:
                pass
        # ===== Fin CP-20 =====

    finally:
        driver.quit()
        print("Navegador cerrado.")


if __name__ == "__main__":
    run()
