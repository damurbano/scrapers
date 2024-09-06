import time
import pandas as pd
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from tabulate import tabulate

# Inicializa colorama para manejar colores en la salida de la consola
init(autoreset=True)


def get_pypi_modules(
    module_name: str, languages: list, save: bool = False, path: str = "."
) -> pd.DataFrame:
    """
    Utiliza Selenium para obtener módulos de PyPI en todas las páginas de resultados.

    :param module_name: Nombre del módulo a buscar (por ejemplo, "django").
    :param languages: Lista de lenguajes de programación (por ejemplo, ["Python", "C"]).
    :param save: Booleano para indicar si se desea guardar el resultado en un archivo.
    :param path: Ruta donde se guardará el archivo CSV si 'save' es True.
    :return: DataFrame con los módulos encontrados.
    """
    all_modules = []  # Lista para almacenar los módulos de todas las páginas
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Ejecutar en modo headless (sin interfaz gráfica)
    chrome_options.add_argument(
        "--no-sandbox"
    )  # Necesario para algunos entornos de Linux
    chrome_options.add_argument(
        "--disable-dev-shm-usage"
    )  # Mejora el uso de memoria compartida
    chrome_options.add_argument(
        "--disable-gpu"
    )  # Acelera el inicio en algunos sistemas
    # Inicia el controlador Chrome
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 🛠️ Construye la URL
        language_params = "+".join(
            [f"Programming+Language+%3A%3A+{lang}" for lang in languages]
        )
        url = f"https://pypi.org/search/?q={module_name}&o=&c={language_params}"

        # Abre la URL en el navegador
        driver.get(url)

        # Usa BeautifulSoup para analizar el HTML de la página
        soup = BeautifulSoup(driver.page_source, "html.parser")
        last_page_number = int(
            soup.select("a.button-group__button")[-2].text
        )  # Número total de páginas

        # Recorre todas las páginas de resultados
        for page in range(1, last_page_number + 1):
            # ⏳ Espera a que los elementos de la página se carguen
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "package-snippet"))
            )

            # Extrae el HTML de la página
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extrae información de cada módulo en la página actual
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

            # Pasa a la siguiente página, si existe
            if page < last_page_number:
                try:
                    next_button = driver.find_element(
                        By.XPATH,
                        "//a[contains(@class, 'button-group__button') and contains(@href, 'page=')]",
                    )
                    next_button.click()
                    time.sleep(2)  #  Pausa para permitir que la nueva página cargue
                except Exception as e:
                    print(f"Error al intentar ir a la página {page + 1}: {e}")
                    break

    finally:
        # Cierra el navegador al terminar
        driver.quit()

    # 📊 DataFrame
    df = pd.DataFrame(all_modules)

    if save:
        # 💾 Guarda el DataFrame
        df.to_csv(f"{path}/{module_name}.csv", index=False)

    # 🎨 DataFrame coloreado
    colored_df(df)

    return df


def search(package_name: str) -> pd.DataFrame:
    """
    Función para buscar módulos en PyPI según el nombre del paquete.

    :param package_name: Nombre del paquete a buscar (por ejemplo, "pyqt5").
    :return: DataFrame con los módulos encontrados.
    """
    all_modules = []  #  Lista para almacenar los módulos
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Ejecutar en modo headless (sin interfaz gráfica)
    chrome_options.add_argument(
        "--no-sandbox"
    )  # Necesario para algunos entornos de Linux
    chrome_options.add_argument(
        "--disable-dev-shm-usage"
    )  # Mejora el uso de memoria compartida
    chrome_options.add_argument(
        "--disable-gpu"
    )  # Acelera el inicio en algunos sistemas
    # Inicia el controlador Chrome
    # Inicia el controlador Chrome
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 🛠️ Genera la URL:
        url = f"https://pypi.org/search/?q={package_name}&o="

        # Abre la URL en el navegador
        driver.get(url)

        # BeautifulSoup para analizar el HTML de la página
        soup = BeautifulSoup(driver.page_source, "html.parser")
        pagination_buttons = soup.select("a.button-group__button")

        if pagination_buttons:
            last_page_number = int(pagination_buttons[-2].text)
        else:
            last_page_number = 1  # Si no hay paginación, solo hay una página

        # Recorre todas las páginas de resultados
        for page in range(1, last_page_number + 1):
            # ⏳ Espera a que los elementos de la página se carguen
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "package-snippet"))
            )

            # Extrae el HTML de la página
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extrae información de cada módulo en la página actual
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

            # Pasa a la siguiente página, si existe
            if page < last_page_number:
                try:
                    next_button = driver.find_element(
                        By.XPATH,
                        "//a[contains(@class, 'button-group__button') and contains(@href, 'page=')]",
                    )
                    next_button.click()
                    time.sleep(2)  # Pausa para permitir que la nueva página cargue
                except Exception as e:
                    print(f"Error al intentar ir a la página {page + 1}: {e}")
                    break

    finally:
        # Cierra el navegador al terminar
        driver.quit()

    # 📊 DataFrame
    df = pd.DataFrame(all_modules)
    # 🎨 DataFrame coloreado
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


# TODO: Del módulo superior crear una modificación que permita usar los valores de get_categories. get_pypi_modules(category, languages -> item?: list, module_name: str)..
# TODO: Crear un modulo que guarde en un json las categorias con sus items, para luego utilizarlo en get_pypi_modules, para constatar los argumentos pasados. Debería incluir una funcion que chequee la estructura de la pagina y si los itemes o las categorias son distintas lanzar un warning y un aviso de que se estan actualizando los parametros

if __name__ == "__main__":
    ### Ejemplo de uso
    MODULETEST = "hola"
    languages_list = ["Python", "C"]
    data_frame = get_pypi_modules(MODULETEST, languages_list, save=True)
