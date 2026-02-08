"""Ejemplo mínimo colocado en features/steps.
Abre una página, espera 3 segundos y cierra el navegador.
Puedes modificar la URL o las opciones según necesites.
"""
"""Ejemplo mínimo colocado en features/steps.
Abre una página, hace hover sobre un elemento (XPath) y cierra el navegador.
Puedes modificar la URL, el XPath o las opciones según necesites.
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


def run(
    url: str = "https://cayetano.edu.pe/",
    headless: bool = False,
    hover_xpath: str = (
        "//body/div[@class='wp-site-blocks']/div[@class='entry-content wp-block-post-content is-layout-flow']/div[@class='wp-block-cover alignfull is-light content-00 page-content']/div[@class='wp-block-cover__inner-container']/div[@class='wp-block-upch-container nav-top-container has-glass-dark-background-color has-background alignfull upch-bg-dark']/div[@class='wp-block-upch-container__inner']/div[@class='wp-block-group is-content-justification-space-between is-nowrap is-layout-flex wp-container-5']/nav[@aria-label='Nav Top 1']/ul[@class='wp-block-navigation__container']/li[1]"
    ),
) -> None:
    """Abre la URL pasada, espera 3 segundos y cierra el navegador.

    Args:
        url: URL a abrir.
        headless: si True, ejecuta Chrome en modo headless.
    """
    # Usar la configuración centralizada
    driver = create_chrome_driver(headless=headless)

    try:
        open_and_wait(driver, url, seconds=3)
        print(f"Página abierta: {driver.title}")

        wait = WebDriverWait(driver, 10)
        # Reporte compartido
        REPORT_PATH = get_report_path(ROOT_DIR)
        ensure_report_exists(REPORT_PATH)
        SUITE = "Test_header"

        # ===== Inicio CP-01: Soy Cayetano — Desplegable =====
        # Mostrar opciones de perfil (Alumno, Docente, etc.) y validar redirección de uno de ellos.
        # Usamos tu XPath proporcionado con contains() para mayor robustez:
        cp1_li_xpath = (
            "(//li[contains(@class,'wp-block-navigation-item has-child open-on-hover-click wp-block-navigation-submenu')])[1]"
        )
        el_cp1 = wait.until(EC.presence_of_element_located((By.XPATH, cp1_li_xpath)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el_cp1)
        except Exception:
            pass
        ActionChains(driver).move_to_element(el_cp1).perform()
        time.sleep(1)

        # Listar opciones visibles del submenu después del hover (sin click)
        submenu_links = driver.find_elements(
            By.XPATH, cp1_li_xpath + "//a[@class='wp-block-navigation-item__content']"
        )
        visibles = [a for a in submenu_links if a.is_displayed() and (a.text or "").strip()]
        if visibles:
            nombres = [a.text.strip() for a in visibles]
            print(f"CP-01: Opciones visibles tras hover: {nombres}")
            append_result(REPORT_PATH, SUITE, "CP-01", "Soy Cayetano — Desplegable (hover)", "PASS", ", ".join(nombres))
        else:
            print("CP-01: No se encontraron opciones visibles tras el hover.")
            append_result(REPORT_PATH, SUITE, "CP-01", "Soy Cayetano — Desplegable (hover)", "FAIL", "Sin opciones visibles")
        # ===== Fin CP-01 =====

        # ===== Inicio CP-02: Facultades — Desplegable =====
        # Listar las facultades y validar que al elegir una, la URL cambie a la facultad correspondiente.
        # Localizamos el enlace 'Facultades' y navegamos dentro de su submenu.
        cp2_anchor_xpath = (
            "(//a[@class='wp-block-navigation-item__content'][normalize-space()='Facultades'])[1]"
        )
        el_cp2 = wait.until(EC.presence_of_element_located((By.XPATH, cp2_anchor_xpath)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el_cp2)
        except Exception:
            pass
        # Hover sobre el enlace para abrir el submenu
        ActionChains(driver).move_to_element(el_cp2).perform()
        time.sleep(1)

        # Contenedor <li> de Facultades
        li_fac = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, cp2_anchor_xpath + "/ancestor::li[contains(@class,'has-child')]")
            )
        )
        # Listar las opciones visibles del submenu (facultades)
        fac_links = li_fac.find_elements(By.XPATH, ".//a[@class='wp-block-navigation-item__content']")
        fac_visibles = [a for a in fac_links if a.is_displayed() and (a.text or "").strip() and a.text.strip().lower() != "facultades"]
        if fac_visibles:
            nombres_fac = [a.text.strip() for a in fac_visibles]
            print(f"CP-02: Facultades encontradas: {nombres_fac}")
            prev_url_2 = driver.current_url
            fac_visibles[0].click()
            WebDriverWait(driver, 10).until(lambda d: d.current_url != prev_url_2)
            # Esperar carga completa y 3s para evidencia visual
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except Exception:
                pass
            time.sleep(3)
            print(f"CP-02: Click en '{nombres_fac[0]}'. URL cambió a: {driver.current_url}")
            append_result(REPORT_PATH, SUITE, "CP-02", "Facultades — Desplegable", "PASS", f"{nombres_fac[0]} -> {driver.current_url}")
            # Volver atrás para continuar con CP-03
            driver.back()
            open_and_wait(driver, url, seconds=2)
        else:
            print("CP-02: No se encontraron facultades visibles en el desplegable.")
            append_result(REPORT_PATH, SUITE, "CP-02", "Facultades — Desplegable", "FAIL", "Sin facultades visibles")
        # ===== Fin CP-02 =====

        # ===== Inicio CP-03: Publicaciones — Desplegable =====
        # Mostrar categorías de publicaciones (libros, revistas), listar y validar redirección de una.
        # Usamos tu patrón de <li> con contains() filtrando por el enlace 'Publicaciones'.
        cp3_li_xpath = (
            "(//li[contains(@class,'wp-block-navigation-item has-child open-on-hover-click wp-block-navigation-submenu')][.//a[normalize-space()='Publicaciones']])[1]"
        )
        li_pub = wait.until(EC.presence_of_element_located((By.XPATH, cp3_li_xpath)))
        # Encontrar el anchor principal 'Publicaciones' para posicionar el hover
        anchor_pub = li_pub.find_element(By.XPATH, ".//a[@class='wp-block-navigation-item__content'][normalize-space()='Publicaciones']")
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", anchor_pub)
        except Exception:
            pass
        # Hover para abrir el menú de Publicaciones
        ActionChains(driver).move_to_element(anchor_pub).perform()
        time.sleep(1)

        # Buscar las opciones visibles dentro del submenu, excluyendo el propio enlace 'Publicaciones'
        submenu_items = li_pub.find_elements(By.XPATH, ".//a[@class='wp-block-navigation-item__content']")
        categorias = [
            a for a in submenu_items
            if a.is_displayed() and (a.text or "").strip() and a.text.strip().lower() != "publicaciones"
        ]

        # Si no se desplegó con hover, intentar con click y reintentar
        if not categorias:
            anchor_pub.click()
            time.sleep(1)
            submenu_items = li_pub.find_elements(By.XPATH, ".//a[@class='wp-block-navigation-item__content']")
            categorias = [
                a for a in submenu_items
                if a.is_displayed() and (a.text or "").strip() and a.text.strip().lower() != "publicaciones"
            ]

        if categorias:
            nombres = [a.text.strip() for a in categorias]
            print(f"CP-03: Categorías encontradas bajo 'Publicaciones': {nombres}")
            prev_url_3 = driver.current_url
            # Click a la primera categoría visible
            categorias[0].click()
            WebDriverWait(driver, 10).until(lambda d: d.current_url != prev_url_3)
            # Esperar carga completa y 3s para evidencia visual
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except Exception:
                pass
            time.sleep(3)
            print(f"CP-03: Click en '{nombres[0]}'. URL cambió a: {driver.current_url}")
            append_result(REPORT_PATH, SUITE, "CP-03", "Publicaciones — Desplegable", "PASS", f"{nombres[0]} -> {driver.current_url}")
            # Volver atrás para continuar con CP-04
            driver.back()
            open_and_wait(driver, url, seconds=2)
        else:
            print("CP-03: No se encontraron categorías visibles bajo 'Publicaciones'.")
            append_result(REPORT_PATH, SUITE, "CP-03", "Publicaciones — Desplegable", "FAIL", "Sin categorías visibles")
        # ===== Fin CP-03 =====

        # ===== Inicio CP-04: Egresados — Hipervínculo =====
        # Redirigir directamente al portal de la comunidad de egresados.
        cp4_span_xpath = (
            "(//span[@class='wp-block-navigation-item__label'][normalize-space()='Egresados'])[1]"
        )
        span_egresados = wait.until(EC.presence_of_element_located((By.XPATH, cp4_span_xpath)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_egresados)
        except Exception:
            pass
        prev_url_4 = driver.current_url
        anchor_egresados = span_egresados.find_element(By.XPATH, "./ancestor::a[1]")
        anchor_egresados.click()
        WebDriverWait(driver, 10).until(lambda d: d.current_url != prev_url_4)
        # Esperar carga completa y 3s para evidencia visual
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass
        time.sleep(3)
        print(f"CP-04: Click en 'Egresados'. URL cambió a: {driver.current_url}")
        append_result(REPORT_PATH, SUITE, "CP-04", "Egresados — Hipervínculo", "PASS", driver.current_url)
        driver.back()
        open_and_wait(driver, url, seconds=2)
        # ===== Fin CP-04 =====

        # ===== Inicio CP-05: Filantropía — Hipervínculo =====
        # Cargar la sección de donaciones o proyectos sociales.
        cp5_span_xpath = (
            "//li[@class='has-small-font-size wp-block-navigation-item wp-block-navigation-link']//span[@class='wp-block-navigation-item__label'][normalize-space()='Filantropia']"
        )
        span_filantropia = wait.until(EC.presence_of_element_located((By.XPATH, cp5_span_xpath)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_filantropia)
        except Exception:
            pass
        prev_url_5 = driver.current_url
        anchor_filantropia = span_filantropia.find_element(By.XPATH, "./ancestor::a[1]")
        anchor_filantropia.click()
        WebDriverWait(driver, 10).until(lambda d: d.current_url != prev_url_5)
        # Esperar carga completa y 3s para evidencia visual
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass
        time.sleep(3)
        print(f"CP-05: Click en 'Filantropia'. URL cambió a: {driver.current_url}")
        append_result(REPORT_PATH, SUITE, "CP-05", "Filantropía — Hipervínculo", "PASS", driver.current_url)
        driver.back()
        open_and_wait(driver, url, seconds=2)
        # ===== Fin CP-05 =====

        # ===== Inicio CP-06: Idiomas — Hipervínculo =====
        # Navegar a la página del Centro de Idiomas.
        cp6_span_xpath = (
            "//li[@class='has-small-font-size wp-block-navigation-item wp-block-navigation-link']//span[@class='wp-block-navigation-item__label'][normalize-space()='Idiomas']"
        )
        span_idiomas = wait.until(EC.presence_of_element_located((By.XPATH, cp6_span_xpath)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_idiomas)
        except Exception:
            pass
        prev_url_6 = driver.current_url
        anchor_idiomas = span_idiomas.find_element(By.XPATH, "./ancestor::a[1]")
        anchor_idiomas.click()
        WebDriverWait(driver, 10).until(lambda d: d.current_url != prev_url_6)
        # Esperar carga completa y 3s para evidencia visual
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass
        time.sleep(3)
        print(f"CP-06: Click en 'Idiomas'. URL cambió a: {driver.current_url}")
        append_result(REPORT_PATH, SUITE, "CP-06", "Idiomas — Hipervínculo", "PASS", driver.current_url)
        driver.back()
        open_and_wait(driver, url, seconds=2)
        # ===== Fin CP-06 =====

        # ===== Inicio CP-07: Pre-Cayetano — Hipervínculo =====
        # Cargar el portal de la academia preuniversitaria.
        cp7_span_xpath = (
            "//li[@class='has-small-font-size wp-block-navigation-item wp-block-navigation-link']//span[@class='wp-block-navigation-item__label'][normalize-space()='Pre-Cayetano']"
        )
        span_precayetano = wait.until(EC.presence_of_element_located((By.XPATH, cp7_span_xpath)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_precayetano)
        except Exception:
            pass
        prev_url_7 = driver.current_url
        anchor_precayetano = span_precayetano.find_element(By.XPATH, "./ancestor::a[1]")
        anchor_precayetano.click()
        WebDriverWait(driver, 10).until(lambda d: d.current_url != prev_url_7)
        # Esperar carga completa y 3s para evidencia visual
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass
        time.sleep(3)
        print(f"CP-07: Click en 'Pre-Cayetano'. URL cambió a: {driver.current_url}")
        append_result(REPORT_PATH, SUITE, "CP-07", "Pre-Cayetano — Hipervínculo", "PASS", driver.current_url)
        driver.back()
        open_and_wait(driver, url, seconds=2)
        # ===== Fin CP-07 =====

        # ===== Inicio CP-08: Mesa de Partes — Hipervínculo =====
        # Redirigir al sistema de trámites virtuales.
        cp8_span_xpath = (
            "//li[@class='has-small-font-size wp-block-navigation-item wp-block-navigation-link']//span[@class='wp-block-navigation-item__label'][normalize-space()='Mesa de Partes']"
        )
        span_mesa = wait.until(EC.presence_of_element_located((By.XPATH, cp8_span_xpath)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_mesa)
        except Exception:
            pass
        prev_url_8 = driver.current_url
        anchor_mesa = span_mesa.find_element(By.XPATH, "./ancestor::a[1]")
        anchor_mesa.click()
        WebDriverWait(driver, 10).until(lambda d: d.current_url != prev_url_8)
        # Esperar carga completa y 3s para evidencia visual
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass
        time.sleep(3)
        print(f"CP-08: Click en 'Mesa de Partes'. URL cambió a: {driver.current_url}")
        append_result(REPORT_PATH, SUITE, "CP-08", "Mesa de Partes — Hipervínculo", "PASS", driver.current_url)
        driver.back()
        open_and_wait(driver, url, seconds=2)
        # ===== Fin CP-08 =====

        # ===== Inicio CP-09: Canal de Denuncias — Hipervínculo =====
        # Cargar la plataforma de ética y transparencia.
        cp9_span_xpath = (
            "//li[@class='has-small-font-size wp-block-navigation-item wp-block-navigation-link']//span[@class='wp-block-navigation-item__label'][normalize-space()='Canal de Denuncias']"
        )
        span_canal = wait.until(EC.presence_of_element_located((By.XPATH, cp9_span_xpath)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_canal)
        except Exception:
            pass
        prev_url_9 = driver.current_url
        anchor_canal = span_canal.find_element(By.XPATH, "./ancestor::a[1]")
        anchor_canal.click()
        WebDriverWait(driver, 10).until(lambda d: d.current_url != prev_url_9)
        # Esperar carga completa y 3s para evidencia visual
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass
        time.sleep(3)
        print(f"CP-09: Click en 'Canal de Denuncias'. URL cambió a: {driver.current_url}")
        append_result(REPORT_PATH, SUITE, "CP-09", "Canal de Denuncias — Hipervínculo", "PASS", driver.current_url)
        driver.back()
        open_and_wait(driver, url, seconds=2)
        # ===== Fin CP-09 =====
    finally:
        driver.quit()
        print("Navegador cerrado.")


if __name__ == "__main__":
    # Ejecución por defecto: abre example.com, no headless
    run()
