from bs4 import BeautifulSoup
import pandas as pd

# Cargar el archivo HTML localmente
with open("/home/damian/mirepo/scrappy/pypi_modules.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, 'html.parser')
print(soup)
# Inicializar una lista para almacenar las categorías
categories = []

# Buscar todos los nodos que corresponden a categorías
accordion_sections = soup.find_all('div', class_='accordion')

for section in accordion_sections:
    category_name = section.find('button').text.strip()  # Nombre de la categoría
    category_items = []

    # Buscar todas las subcategorías dentro de esta categoría
    for item in section.find_all('li'):
        label = item.find('label').text.strip()
        category_items.append(label)

    categories.append({
        'category_name': category_name,
        'items': category_items
    })

# Crear un DataFrame de Pandas para organizar los datos
category_df = pd.DataFrame(categories)

# Mostrar las primeras categorías extraídas
print("Categorías y sus valores:")
print(category_df.head())

# Guardar los datos en un archivo CSV
category_df.to_csv('pypi_categories.csv', index=False)
