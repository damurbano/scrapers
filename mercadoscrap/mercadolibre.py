import math  # 🧮 Matemáticas para calcular cuántas páginas hay en total
import os
import re  # 🧙‍♂️ Expresiones regulares, la varita mágica para buscar patrones en el HTML
from datetime import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import requests  # 🕸️ Solicitudes HTTP
import seaborn as sns
from bs4 import BeautifulSoup
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

matplotlib.use('QtAgg')
######################################################################
# Remuevo la base de datos anterior si es que existe######################################################################
db_path ="mi_base_de_datos.db"

if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Base de datos '{db_path}' eliminada exitosamente.")
else:
    print(f"El archivo '{db_path}' no existe.")
######################################################################

# URL base de Mercado Libre.
URL_BASE = "https://listado.mercadolibre.com.ar/"

# Mercado Libre nos muestra 50 productos por página, así que lo guardamos como una constante
PRODUCTS_PER_PAGE = 50


def get_total_results(html: str):
    """Saca el número total de resultados de la búsqueda usando expresiones regulares"""
    pattern = re.compile(
        r'<span class="ui-search-search-result__quantity-results">([\d\.,]+) resultados</span>'
    )
    match = pattern.search(html)

    if match:
        total_results_str = match.group(1)
        total_results = int(total_results_str.replace(".", "").replace(",", ""))
        return total_results
    print("No se encontró el número total de resultados en el HTML.")
    return 0


def extract_products_and_prices(html: str):
    """Extrae los nombres de los productos y sus precios"""
    product_pattern = re.compile(
        r'<h2 class="poly-box poly-component__title"><a[^>]*>(.*?)</a></h2>', re.DOTALL
    )
    price_pattern = re.compile(
        r'<div class="poly-price__current">.*?<span class="andes-money-amount__fraction" aria-hidden="true">([\d.,]+)</span>',
        re.DOTALL,
    )
    buy_box_pattern = re.compile(
        r'<div class="poly-component__buy-box">.*?<div class="poly-price__current">.*?<span class="andes-money-amount__fraction" aria-hidden="true">([\d.,]+)</span>',
        re.DOTALL,
    )

    products = product_pattern.findall(html)
    buy_box_prices = buy_box_pattern.findall(html)
    all_prices = price_pattern.findall(html)
    filtered_prices = [price for price in all_prices if price not in buy_box_prices]

    return products, filtered_prices


def get_categories(html: str):
    
    """Extrae las categorías y sus cantidades de resultados"""
    soup = BeautifulSoup(html, "html.parser")

    # Buscar el <h3> que le da el nombre a la categoria"
    h3_elements = soup.find_all("h3", {"aria-level": "3", "class": "ui-search-filter-dt-title"})

    # Inicializa la variable nombre_categoria
    nombre_categoria = None

    # Recorre todos los elementos encontrados
    for element in h3_elements:
        # Obtén el texto del elemento, eliminando espacios en blanco innecesarios
        text = element.get_text(strip=True)
        # Comprueba si el texto es "Categorías"
        if text == "Categorías":
            nombre_categoria = element
            
    if nombre_categoria:
        if nombre_categoria and nombre_categoria.get_text(strip=True) :
            # Encontrar el contenedor padre <div class="ui-search-filter-dl">
            div = nombre_categoria.find_parent("div", {"class": "ui-search-filter-dl"})
            if div:
                # Extraer las categorías del <ul>
                ul = div.find("ul")
                categories = {nombre_categoria: {}}
                for li in ul.find_all("li", {"class": "ui-search-filter-container"}):
                    a = li.find("a", {"class": "ui-search-link"})
                    if a:
                        title = a.find("span", {"class": "ui-search-filter-name"}).get_text(
                            strip=True
                        )
                        qty_text = a.find(
                            "span", {"class": "ui-search-filter-results-qty"}
                        ).get_text(strip=True)
                        link = a.get("href")
                        # print("Printeando link"+"**"*3)
                        # print(link)
                        qty = int(qty_text.strip("()"))
                        categories[nombre_categoria].update({title:{"cantidad":qty,"link":link}})
                #print(categories)
                return categories
    else:
        print("No se encontró el encabezado 'Categorías'.")
        categories = {}
        spans = soup.select('ol.andes-breadcrumb span')
        resultados = soup.find('span', class_='ui-search-search-result__quantity-results')
        link = soup.find('h1', class_='ui-search-breadcrumb__title')
        # Obtener el texto del último <span>
        if spans:
            ultimo_span_texto = spans[-1].get_text(strip=True)
            print(f"Texto del último <span>: {ultimo_span_texto}")
        textoResultados = resultados.get_text(strip=True)
    
        # Extraer solo los números usando una expresión regular
        cantidad_resultados = re.search(r'\d+', textoResultados)
        
        if cantidad_resultados:
            cantidad_resultados = cantidad_resultados.group()
        if link:
            link = link.get_text(strip=True)
            link_=link.replace(" ","-")
            final_link = f"https://listado.mercadolibre.com.ar/{link_}#D[A:{link}]"
        
            categories[ultimo_span_texto] = {ultimo_span_texto: {"cantidad":cantidad_resultados,"link":final_link}}
            return categories
        else:
            print("No se encontraron <span> dentro del breadcrumb.")
        

def scrape_all_pages(categories_search:str=""):
    """Recorre todas las páginas de resultados, buscando productos, precios y categorías"""
    # if query_search:
    #     search_query = query_search.replace(" ", "-")
    #     url = f"{URL_BASE}{search_query}#D[A:{search_query}]"
        
    # else:
    url = categories_search
    try:
        response = requests.get(url, timeout=300)
        _html = response.text

        # Obtener el número total de resultados
        total_results = get_total_results(_html)
        if total_results == 0:
            print("No se encontraron resultados.")
            return
        
        print(f"Total de resultados: {total_results}")

        # Calcular cuántas páginas debemos recorrer
        total_pages = math.ceil(total_results / PRODUCTS_PER_PAGE)
        all_products = []
        all_prices = []
        cleaned_url = ""
        for page in range(1, total_pages + 1):
            if page == 1:
                page_url = url
            else:
                if not cleaned_url:
                    cleaned_url = url.split("NoIndex_True")[0]
                offset = (page - 1) * PRODUCTS_PER_PAGE + 1
                page_url = f"{cleaned_url}Desde_{offset}_NoIndex_True"
            

            print(f"Scraping página {page}: {page_url}")

            response = requests.get(page_url, timeout=300)
            html = response.text

            # Extraer productos y precios
            products, prices = extract_products_and_prices(html)
            all_products.extend(products)
            all_prices.extend(prices)

            print(len(products), "PRODUCTOS ENCONTRADOS \n")
            print(len(set(products)), "PRODUCTOS ÚNICOS")

            for product, price in zip(products, prices):
                formatted_price = price.replace(".", ",")
                print(f"Producto: {product.strip()}, Precio: ${formatted_price}")
        # if categories_search:
        producto_precios = {}
        for product, price in zip(all_products, all_prices):
            formatted_price = price.replace(".", ",")
            product_name = product.strip()

            # Si el producto ya está en el diccionario, agregar el precio a la lista
            if product_name in producto_precios:
                producto_precios[product_name]["Precio"].append(f"${formatted_price}")
            else:
                # Si no está, agregar el producto con el precio inicial
                producto_precios[product_name] = {"Precio": [f"${formatted_price}"]}
        return producto_precios
        

    except requests.exceptions.ConnectTimeout as error:
        print("Error de conexión", error)

def main(input_=""):
    if input_:
        search = input_
    else:
        search = input("Introduce el artículo a buscar: ")

    search_query = search.replace(" ", "-")
    url = f"{URL_BASE}{search_query}#D[A:{search_query}]"

    try:
        response = requests.get(url, timeout=300)
        _html = response.text
        
    except:
        print("Error de conexión")

    cat = get_categories(_html)


    # print("Categorias devueltas!!"*3)
    if cat:
        finalDict = {}
        for categoryName, categoriePriceLink in cat.items():            
            print("Nombre de la categoria:")
            print(categoryName)            
            for k, v in categoriePriceLink.items():
                print("**"*10)
                print(f"{k} CANTIDAD: {v.get("cantidad")}")
                print("**"*10)
                link = v.get("link")
                if link:
                    finalDict[k]=scrape_all_pages(categories_search=link)
            print(finalDict)
        # for categoria, prod in asd.items():
        #     print(f"{categoria}:  {len(prod)}")

        # Iniciamos el ciclo por categoría
        for categoria, productos in finalDict.items():
            # Reseteamos el contador de productos por cada categoría
            total_productos = 0
            print(f"\nCategoría: {categoria}")
            
            # Recorremos los productos dentro de la categoría
            for nombre_producto, detalles in productos.items():
                cantidad_precios = len(detalles['Precio'])  # Contamos la cantidad de precios
                total_productos += cantidad_precios  # Sumamos al total de productos
                
            print(f"Total de productos en '{categoria}': {total_productos}")
        return finalDict
    
def convert_to_dataframes(data):
    dfs = {}
    for category, products in data.items():
        # Crear un DataFrame para cada categoría
        category_data = []
        for product, details in products.items():
            for price in details['Precio']:
                category_data.append({'Producto': product, 'Precio': price})
        
        df = pd.DataFrame(category_data)
        dfs[category] = df
    
    return dfs

# # Convertir el diccionario a DataFrames
#REMOVER DUPLICADOS PROCESO DE ETL


def limpiar_precio(precio_str):
    # Elimina el símbolo de moneda y separadores de miles
    precio_limpio = precio_str.replace("$", "").replace(".", "").replace(",", ".").strip()
    return float(precio_limpio)





if __name__ == '__main__':
    #dfs =  convert_to_dataframes()

    

    Base = declarative_base()

    class Producto(Base):
        __tablename__ = 'productos'
        
        id = Column(Integer, primary_key=True)
        nombre = Column(String)
        precio = Column(Float)
        fecha_agregado = Column(DateTime, default=datetime.utcnow)  # Fecha de agregación por defecto
        categoria_id = Column(Integer, ForeignKey('categorias.id'))
        
        categoria = relationship("Categoria", back_populates="productos")

    class Categoria(Base):
        __tablename__ = 'categorias'
        
        id = Column(Integer, primary_key=True)
        nombre = Column(String)
        
        productos = relationship("Producto", back_populates="categoria")

###############################################################################
###############################################################################
#TODO: ORDENAR ESTA PARTE:

    # Crear el motor de base de datos (en este caso, usando SQLite y creando un archivo local)
    engine = create_engine('sqlite:///mi_base_de_datos.db')

    # Crear las tablas en la base de datos
    Base.metadata.create_all(engine)

    # Crear una sesión para interactuar con la base de datos
    Session = sessionmaker(bind=engine)
    session = Session()


    # Insertar categorías y productos
    for categoria_nombre, productos in main().items():
        categoria = session.query(Categoria).filter_by(nombre=categoria_nombre).first()
        if not categoria:
            categoria = Categoria(nombre=categoria_nombre)
            session.add(categoria)
            session.commit()

        for producto_nombre, info in productos.items():
            # Evitar duplicados de producto y precio
            precio = info['Precio'][0]
            precio_limpio = limpiar_precio(precio)
            
            producto_existente = session.query(Producto).filter_by(nombre=producto_nombre, precio=precio_limpio).first()
            
            if not producto_existente:
                # Insertar el producto con el primer precio
                nuevo_producto = Producto(nombre=producto_nombre, precio=precio_limpio, categoria=categoria)
                session.add(nuevo_producto)

        session.commit()

    def mostrar_productos_por_categoria():
        categorias = session.query(Categoria).all()
        for categoria in categorias:
            productos = session.query(Producto).filter_by(categoria_id=categoria.id).all()
            data = [{'Producto': p.nombre, 'Precio': p.precio} for p in productos]
            df = pd.DataFrame(data)
            print(f"Categoría: {categoria.nombre}")
            print(df)

    mostrar_productos_por_categoria()

###############################################################################
###############################################################################
    class DataVisualizer:
        """
        Clase para la visualización y análisis de datos extraídos de una base de datos.

        Esta clase se conecta a una base de datos SQL utilizando una URL proporcionada,
        lee las tablas de 'productos' y 'categorias', y fusiona estos datos en un solo DataFrame.
        Luego, proporciona métodos para generar gráficos y análisis de los datos.

        Attributes:
            conn (sqlalchemy.engine.base.Connection): Conexión a la base de datos SQL.
            productos_df (pandas.DataFrame): DataFrame que contiene los datos de la tabla 'productos'.
            categorias_df (pandas.DataFrame): DataFrame que contiene los datos de la tabla 'categorias'.
            merged_df (pandas.DataFrame): DataFrame combinado que fusiona 'productos_df' y 'categorias_df'.
        """

        def __init__(self, db_url: str):
            """
            Inicializa la clase DataVisualizer y establece la conexión con la base de datos.

            Args:
                db_url (str): URL de la base de datos en formato SQLAlchemy.

            Raises:
                ValueError: Si no se proporciona una URL de base de datos.
                Exception: Si ocurre un error al conectar con la base de datos o leer las tablas.
            """
            if not db_url:
                raise ValueError("La URL de la base de datos no puede estar vacía.")

            try:
                # Conectar a la base de datos
                self.conn = create_engine(db_url)
                # Leer los datos de las tablas
                self.productos_df = pd.read_sql_table('productos', self.conn)
                self.categorias_df = pd.read_sql_table('categorias', self.conn)
                # Fusionar las tablas productos y categorias
                self.merged_df = pd.merge(self.productos_df, self.categorias_df, left_on='categoria_id', right_on='id')
            except Exception as e:
                raise Exception(f"Error al conectar con la base de datos o leer las tablas: {e}")

            # Verificar la estructura del DataFrame combinado
            print(self.merged_df.head())
            print("***********"*6)
        
        def plot_suma_precios(self):
            """
            Genera y muestra un gráfico de barras que representa la suma total de precios por categoría.

            Este método realiza los siguientes pasos:
            1. Agrupa los datos por categoría y calcula la suma total de precios para cada categoría.
            2. Escala los valores de los precios a formatos más legibles (miles, millones, billones).
            3. Crea un gráfico de barras con las categorías en el eje x y la suma de precios en el eje y.
            4. Añade etiquetas de texto sobre las barras que muestran el precio escalado.
            5. Configura el título y las etiquetas de los ejes, ajusta la rotación de las etiquetas de las categorías 
            para mejorar la legibilidad.
            6. Muestra el gráfico ajustado para evitar el recorte de las etiquetas.

            Args:
                self: La instancia de la clase `DataVisualizer` que contiene los datos y la conexión a la base de datos.

            Returns:
                None: Este método muestra el gráfico directamente y no devuelve ningún valor.
            """
            df_suma = self.merged_df.groupby('nombre_y')['precio'].sum().reset_index()

            # Escalar los precios a miles, millones o billones
            def scale_values(value):
                if value >= 1_000_000_000:
                    return f'{value / 1_000_000_000:.1f}B $'  # Billones
                elif value >= 1_000_000:
                    return f'{value / 1_000_000:.1f}M $'  # Millones
                elif value >= 1_000:
                    return f'{value / 1_000:.1f}K $'  # Miles
                else:
                    return f'{value:.0f} $'

            # Configuración del gráfico
            plt.figure(figsize=(12, 6))
            df_suma['precio_scaled'] = df_suma['precio'].apply(scale_values)
            colors = sns.color_palette('husl', len(df_suma))
            barplot = sns.barplot(x='nombre_y', y='precio', data=df_suma, palette=colors)

            plt.title('Suma de precios por categoría')
            plt.xlabel('Categoría')
            plt.ylabel('Suma de Precios')

            plt.xticks(rotation=45, ha='right')

            for index, row in df_suma.iterrows():
                barplot.text(
                    x=index,
                    y=row['precio'] + 0.02 * df_suma['precio'].max(),  # Ajustar la posición vertical del texto
                    s=df_suma.loc[index, 'precio_scaled'],  # Texto escalado
                    color='black',  # Color del texto
                    ha='center', 
                    va='bottom',
                    fontsize=10
                )

            plt.tight_layout()
            plt.show()

        def plot_distribucion_categorias(self):
            """
            Genera y muestra un gráfico de torta que representa la distribución de productos por categoría.

            Este método realiza los siguientes pasos:
            1. Agrupa los datos por categoría y cuenta la cantidad de productos en cada categoría.
            2. Selecciona las principales categorías para mostrar y agrupa las categorías restantes en una categoría "Otros".
            3. Crea un gráfico de torta con las principales categorías y "Otros".
            4. Ajusta la posición de los porcentajes para que sean legibles, colocándolos fuera del gráfico con líneas que los conectan a las porciones correspondientes.
            5. Añade una leyenda que muestra las cantidades de productos por categoría.

            Args:
                self: La instancia de la clase `DataVisualizer` que contiene los datos y la conexión a la base de datos.

            Returns:
                None: Este método muestra el gráfico directamente y no devuelve ningún valor.
            """
            df_count = self.merged_df.groupby('nombre_y')['id_x'].count().reset_index()
            df_count.rename(columns={'id_x': 'cantidad'}, inplace=True)

            # Ordenar las categorías por cantidad en orden descendente
            df_count = df_count.sort_values(by='cantidad', ascending=False)

            # Número de categorías a mostrar sin agrupar
            num_categories_to_show = 3

            if len(df_count) > num_categories_to_show:
                # Seleccionar las primeras 'num_categories_to_show' categorías
                top_categories = df_count.head(num_categories_to_show)

                # Agrupar las categorías restantes en "otros"
                remaining_categories = df_count.iloc[num_categories_to_show:]
                if not remaining_categories.empty:
                    otros_count = remaining_categories['cantidad'].sum()
                    # Crear un DataFrame para la categoría "otros"
                    otros_df = pd.DataFrame({'nombre_y': ['Otros'], 'cantidad': [otros_count]})
                    # Concatenar el DataFrame de las principales categorías con "otros"
                    top_categories = pd.concat([top_categories, otros_df], ignore_index=True)
            else:
                # Si hay 6 o menos categorías, mostrar todas
                top_categories = df_count

            # Configuración del gráfico de torta
            plt.figure(figsize=(12, 8))

            # Crear el gráfico de torta con colores personalizados
            colors = sns.color_palette('husl', len(top_categories))
            plt.pie(
                top_categories['cantidad'], 
                labels=[f"{name}" for name in top_categories['nombre_y']], 
                colors=colors, 
                autopct='%1.1f%%',
                startangle=140
            )

            # Añadir leyenda con cantidades
            labels = [f"{name}: {count}" for name, count in zip(top_categories['nombre_y'], top_categories['cantidad'])]
            plt.legend(labels, title='Categorías', bbox_to_anchor=(1.05, 1), loc='upper left')

            # Añadir título
            plt.title('Distribución de productos por categoría')

            # Ajustar el diseño
            plt.tight_layout()
            plt.show()

    # Uso de la clase
    db_url = 'sqlite:///mi_base_de_datos.db'
    visualizer = DataVisualizer(db_url)
    visualizer.plot_suma_precios()
    visualizer.plot_distribucion_categorias()
