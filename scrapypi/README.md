# Scrapypi

<p align="center">
  <img src="../image/README/1725227622704.png" alt="Scrapypi" />
</p>

**Scrapypi** es una herramienta de scraping en Python diseñada para extraer información de módulos de PyPI utilizando Selenium y BeautifulSoup. Esta herramienta permite recopilar datos detallados sobre los módulos de PyPI, incluidos su nombre, versión, fecha de creación y descripción, y categorizarlos para facilitar futuras búsquedas.

## Y qué es Pypi?

El Índice de paquetes de Python (PyPI) es un repositorio de *software* para el lenguaje de programación Python. 🐍

## Funcionalidades Principales

### `finder.py` - Módulo para Buscar Módulos en PyPI

El módulo `finder.py` contiene la función `get_pypi_modules()`, que se encarga de:

- **Buscar Módulos Específicos**: Realiza una búsqueda en PyPI para un módulo específico, como `django`.
- **Filtrar por Lenguajes**: Permite filtrar los resultados por lenguajes de programación, como `Python` y `C`.
- **Navegar por Múltiples Páginas**: Utiliza Selenium para navegar por todas las páginas de resultados disponibles en PyPI, asegurando que se recopilen todos los módulos correspondientes a la búsqueda.
- **Recopilar Información Detallada**: Extrae datos clave de cada módulo, como el nombre, versión, fecha de creación y descripción.
- **Devolver los Resultados en un DataFrame**: Organiza los datos recopilados en un `pandas.DataFrame` para facilitar su manipulación y análisis.

#### Ejemplo de Uso

```python
from finder import get_pypi_modules

module_name = "hola"
languages = ["Python", "C"]

df = get_pypi_modules(module_name, languages)

# Mostrar los primeros 5 módulos encontrados
print(df.head())

# Guardar los datos en un archivo CSV
df.to_csv(f"{module_name}.csv", index=False)
```

### `scrapypi.py` - Módulo para obtener y guardar Categorías en un CSV

Este proyecto incluye un script para extraer categorías y subcategorías del Python Package Index (PyPI). Utiliza requests para realizar solicitudes HTTP y BeautifulSoup para analizar el contenido HTML. Los datos extraídos se organizan en un DataFrame de pandas y se pueden guardar en un archivo CSV para su posterior uso.

#### Ejemplo de Uso

```python
import scrapypi

# Obtener un dataframe con las categorias:
scrapypi.get_categories()

```

Si deseas guardar los datos en un archivo CSV, modifica la llamada a get_categories pasándole ***save=True***. Esto hará que se guarde la información en el directorio que se ejecute el script.
De todas formas, puedes pasarle como parametro un ***path*** en formato *str*.
Por ejemplo:

```python
scrapypi.get_categories(save=True, path="MI_PATH")
```

## Requisitos

* Python 3.x
* Selenium
* BeautifulSoup
* Pandas
* Requests
* Colorama
* Tabulate
* WebDriver compatible (como ChromeDriver)

## Instalación

1. **Clona el Repositorio** :

   ```
   git clone https://github.com/damurbano/scrapypi.git
   cd scrapypi
   ```
2. **Instala las Dependencias** :

   ```
   poetry install
   ```
3. **Configura WebDriver** :

* Descarga e instala el WebDriver correspondiente a tu navegador (como ChromeDriver).

## Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar Scrapypi o quieres reportar un error, abre un *issue* o envía un  *pull request* .
