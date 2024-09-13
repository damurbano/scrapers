import requests  # 🕸️ Solicitudes HTTP
import re  # 🧙‍♂️ Expresiones regulares, la varita mágica para buscar patrones en el HTML
import math  # 🧮 Matemáticas para calcular cuántas páginas hay en total
from bs4 import BeautifulSoup
import pandas as pd

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
    h3 = soup.find("h3", {"aria-level": "3", "class": "ui-search-filter-dt-title"})
    nombre_categoria = h3.get_text(strip=True)
    print(nombre_categoria)
    if nombre_categoria == "Categorías":
        if h3 and h3.get_text(strip=True) :
            # Encontrar el contenedor padre <div class="ui-search-filter-dl">
            div = h3.find_parent("div", {"class": "ui-search-filter-dl"})
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


    from datetime import datetime
    from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
    from sqlalchemy.orm import relationship
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
    from sqlalchemy.orm import relationship, sessionmaker
    from sqlalchemy import create_engine

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
            # Evitar duplicados
            producto_existente = session.query(Producto).filter_by(nombre=producto_nombre).first()
            if not producto_existente:
                # Insertar el producto con el primer precio
                precio = info['Precio'][0]
                precio_limpio = limpiar_precio(precio)
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
