import time

import pandas as pd
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tabulate import tabulate

# Inicializa colorama
init(autoreset=True)


def get_pypi_modules(
    module_name: str, languages: list, save: bool = False, path: str = "."
) -> pd.DataFrame:
    """
    Función que utiliza Selenium para recopilar módulos de todas las páginas en PyPI,
    asegurándose de cerrar el navegador al terminar.

    :param module_name: Nombre del módulo a buscar (e.g., "django").
    :param languages: Lista de lenguajes de programación (e.g., ["Python", "C"]).
    :return: DataFrame con los módulos encontrados.
    """
    # Lista para almacenar los módulos de todas las páginas
    all_modules = []
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
                    next_button = driver.find_element(
                        By.XPATH,
                        "//a[contains(@class, 'button-group__button') and contains(@href, 'page=')]",
                    )
                    next_button.click()
                    # Esperar un momento para que la siguiente página cargue
                    time.sleep(2)
                except Exception as e:
                    print(f"Error al intentar ir a la página {page + 1}: {e}")
                    break

    finally:
        # Asegurarse de que el navegador se cierra correctamente
        driver.quit()

    # Crear un DataFrame de Pandas para organizar los datos
    df = pd.DataFrame(all_modules)
    if save:
        # Guardar los datos en un archivo CSV
        print(path + "/" + "".join(languages) + f"_{module_name}.csv")
        df.to_csv(path + "/" + "".join(languages) + f"_{module_name}.csv", index=False)
    colored_df(df)

    return df


# TODO: Del módulo superior crear una modificación que permita usar los valores de get_categories. get_pypi_modules(category, languages -> item?: list, module_name: str)..
# TODO: Crear un modulo que guarde en un json las categorias con sus items, para luego utilizarlo en get_pypi_modules, para constatar los argumentos pasados. Debería incluir una funcion que chequee la estructura de la pagina y si los itemes o las categorias son distintas lanzar un warning y un aviso de que se estan actualizando los parametros


def search(package_name: str) -> pd.DataFrame:
    """
    Función que utiliza Selenium para recopilar módulos en PyPI basados en el nombre del paquete.

    :param package_name: Nombre del paquete a buscar (e.g., "pyqt5").
    :return: DataFrame con los módulos encontrados.
    """
    # Lista para almacenar los módulos
    all_modules = []

    # Configurar el controlador de Selenium
    driver = (
        webdriver.Chrome()
    )  # Asegúrate de tener el controlador de Chrome en PATH o especifica la ruta

    try:
        # Generar la URL de búsqueda
        url = f"https://pypi.org/search/?q={package_name}&o="

        # Navegar a la URL inicial
        driver.get(url)

        # Encontrar el número total de páginas
        soup = BeautifulSoup(driver.page_source, "html.parser")
        pagination_buttons = soup.select("a.button-group__button")

        if pagination_buttons:
            last_page_number = int(pagination_buttons[-2].text)
        else:
            last_page_number = (
                1  # Si no hay paginación, significa que solo hay una página
            )

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
                    # Usando XPath para seleccionar el botón "Siguiente"
                    next_button = driver.find_element(
                        By.XPATH,
                        "//a[contains(@class, 'button-group__button') and contains(@href, 'page=')]",
                    )
                    next_button.click()
                    # Esperar un momento para que la siguiente página cargue
                    time.sleep(2)
                except Exception as e:
                    print(f"Error al intentar ir a la página {page + 1}: {e}")
                    break

    finally:
        # Asegurarse de que el navegador se cierra correctamente
        driver.quit()

    # Convertir la lista de diccionarios en un DataFrame
    df = pd.DataFrame(all_modules)
    colored_df(df)
    return df


def colored_df(df):
    """Colorea un dataframe y lo printea usando tabulate"""
    # Define colores para los encabezados y los datos
    header_color = Fore.RED
    data_color = Fore.GREEN

    # Formatea los nombres de columna con color
    colored_headers = [header_color + header + Style.RESET_ALL for header in df.columns]

    # Formatea los datos con color
    colored_data = [
        [data_color + str(cell) + Style.RESET_ALL for cell in row]
        for row in df.values.tolist()
    ]

    # Usa tabulate para imprimir la tabla con los colores aplicados
    print(tabulate(colored_data, headers=colored_headers, tablefmt="pipe"))


if __name__ == "__main__":
    ###Ejemplo de uso
    MODULETEST = "hola"
    languages_list = ["Python", "C"]
    data_frame = get_pypi_modules(MODULETEST, languages_list, save=True)
    # # Guardar los datos en un archivo CSV
    # data_frame.to_csv(f"{MODULETEST}.csv", index=False)

    # print(search(MODULETEST))
