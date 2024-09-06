import pandas as pd
import requests
from bs4 import BeautifulSoup


# URL de PyPI 🐍 a analizar
URL = "https://pypi.org/search/?q="


def get_categories(save=False, path: str = ".") -> pd.DataFrame:
    """ "Devuelve un dataframe y si save es True guarda una copia en formato csv"""

    try:
        # Realizar la solicitud HTTP a PyPI con un timeout de 10 segundos
        response = requests.get(URL, timeout=10)
        response.raise_for_status()  # Esto lanza una excepción para códigos de estado HTTP 4xx/5xx 💀
        soup = BeautifulSoup(response.content, "html.parser")

        # Lista para almacenar las categorías
        categories = []

        # Todos los nodos que corresponden a categorías
        accordion_sections = soup.find_all("div", class_="accordion")

        for section in accordion_sections:
            category_name = section.find(
                "button"
            ).text.strip()  # Nombre de la categoría
            category_items = []

            # Todas las subcategorías dentro de esta categoría
            for item in section.find_all("li"):
                label = item.find("label").text.strip()
                category_items.append(label)

            categories.append({"category_name": category_name, "items": category_items})

        # DataFrame para organizar los datos
        category_df = pd.DataFrame(categories)

        if save:
            # Guardar los datos en un archivo CSV
            print("Guardando en:")
            print(path + "/pypi_categories.csv")
            category_df.to_csv(path + "/pypi_categories.csv", index=False)

        return category_df

    except requests.exceptions.Timeout:
        print(f"La solicitud a {URL} excedió el tiempo de espera.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud a {URL}: {e}")
        return None

    except Exception as e:
        print(f"Error inesperado: {e}")
        return None


if __name__ == "__main__":
    print("Scrapypi at work!!")
    print(get_categories())
