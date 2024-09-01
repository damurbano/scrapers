# Scrappy

    ![1725227622704](image/README/1725227622704.png)

**Scrappy** es una herramienta de scraping en Python diseñada para extraer información de módulos de PyPI utilizando Selenium y BeautifulSoup. Esta herramienta permite recopilar datos detallados sobre los módulos de PyPI, incluidos su nombre, versión, fecha de creación y descripción, y categorizarlos para facilitar futuras búsquedas.

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

### `scrappy.py` - Módulo para Guardar Categorías en un CSV

El módulo `scrappy.py` es responsable de extraer y guardar las categorías de PyPI en un archivo CSV, facilitando la categorización y búsqueda personalizada de módulos.

* **Extracción de Categorías** : Analiza el HTML de PyPI para extraer todas las categorías disponibles, como "Development Status", "Intended Audience", etc.
* **Organización en CSV** : Guarda las categorías y subcategorías extraídas en un archivo CSV, permitiendo su uso en futuras búsquedas y análisis.

#### Ejemplo de Uso

```

```

Este comando creará un archivo `pypi_categories.csv` con todas las categorías y subcategorías organizadas.

## Requisitos

* Python 3.x
* Selenium
* BeautifulSoup
* Pandas
* WebDriver compatible (como ChromeDriver)

## Instalación

1. **Clona el Repositorio** :

   ```
   git clone https://github.com/tu-usuario/scrappy.git
   cd scrappy

   ```
2. **Instala las Dependencias** :

   ```
   poetry 
   ```
3. **Configura WebDriver** :

* Descarga e instala el WebDriver correspondiente a tu navegador (como ChromeDriver).

## Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar Scrappy o quieres reportar un error, abre un *issue* o envía un  *pull request* .
