from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time


def get_pypi_modules(module_name: str, languages: list) -> pd.DataFrame:
    """
    Función que utiliza Selenium para recopilar módulos de todas las páginas en PyPI,
    asegurándose de cerrar el navegador al terminar.

    :param module_name: Nombre del módulo a buscar (e.g., "django").
    :param languages: Lista de lenguajes de programación (e.g., ["Python", "C"]).
    :return: DataFrame con los módulos encontrados.
    """

    # Configurar el controlador de Selenium (usa la ruta de tu WebDriver)
    driver = (
        webdriver.Chrome()
    )  # Asegúrate de tener el controlador de Chrome en PATH o especifica la ruta

    try:
        # Construir la parte de la URL para los lenguajes
        language_params = "+".join(
            [f"Programming+Language+%3A%3A+{lang}" for lang in languages]
        )

        # Generar la URL de búsqueda
        url = f"https://pypi.org/search/?q={module_name}&o=&c={language_params}"

        # Navegar a la URL inicial
        driver.get(url)

        # Lista para almacenar los módulos de todas las páginas
        all_modules = []

        # Encontrar el número total de páginas
        soup = BeautifulSoup(driver.page_source, "html.parser")
        last_page_number = int(soup.select("a.button-group__button")[-2].text)

        # Iterar sobre todas las páginas disponibles
        for page in range(1, last_page_number + 1):
            # Esperar a que los elementos carguen
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "package-snippet"))
            )

            # Extraer el contenido de la página actual
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extraer los módulos de la página actual
            for package in soup.find_all("li"):
                link = package.find("a", class_="package-snippet")
                if link:
                    name = link.find("span", class_="package-snippet__name").text
                    version = link.find("span", class_="package-snippet__version").text
                    created = link.find(
                        "span", class_="package-snippet__created"
                    ).text.strip()
                    description = link.find(
                        "p", class_="package-snippet__description"
                    ).text.strip()
                    url = f"https://pypi.org{link['href']}"

                    all_modules.append(
                        {
                            "name": name,
                            "version": version,
                            "created": created,
                            "description": description,
                            "url": url,
                        }
                    )

            # Ir a la siguiente página si no es la última
            if page < last_page_number:
                try:
                    next_button = driver.find_element(By.LINK_TEXT, "Siguiente")
                    next_button.click()
                    # Esperar un momento para que la siguiente página cargue
                    time.sleep(2)
                except:
                    print(f"Error al intentar ir a la página {page + 1}")
                    break

    finally:
        # Asegurarse de que el navegador se cierra correctamente
        driver.quit()

    # Crear un DataFrame de Pandas para organizar los datos
    df = pd.DataFrame(all_modules)

    return df


# Ejemplo de uso
module_name = "hola"
languages = ["Python", "C"]
df = get_pypi_modules(module_name, languages)

# Mostrar los primeros 5 módulos encontrados
print(df.head())

# Guardar los datos en un archivo CSV
df.to_csv(f"{module_name}.csv", index=False)
