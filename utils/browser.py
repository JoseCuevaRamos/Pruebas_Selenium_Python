"""Utilidades para inicializar el navegador y abrir URLs.
Centraliza la configuración para que los scripts importen estas funciones.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def create_chrome_driver(headless: bool = False) -> webdriver.Chrome:
    """Crea una instancia de Chrome usando webdriver-manager.

    Args:
        headless: Si True, inicia Chrome en modo headless.
    Returns:
        Instancia de webdriver.Chrome
    """
    service = Service(ChromeDriverManager().install())

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(service=service, options=options)
    return driver


def open_and_wait(driver: webdriver.Chrome, url: str, seconds: int = 3) -> None:
    """Abre una URL y espera unos segundos.

    Args:
        driver: Instancia del navegador.
        url: URL a abrir.
        seconds: Segundos a esperar tras abrir la página.
    """
    driver.get(url)
    time.sleep(seconds)
