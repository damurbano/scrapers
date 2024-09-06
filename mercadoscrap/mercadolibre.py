import requests  # 🕸️ Solicitudes HTTP
import re  # 🧙‍♂️ Expresiones regulares, la varita mágica para buscar patrones en el HTML
import math  # 🧮 Matemáticas para calcular cuántas páginas hay en total

# URL base de Mercado Libre.
URL_BASE = "https://listado.mercadolibre.com.ar/"

# Mercado Libre nos muestra 50 productos por página, así que lo guardamos como una constante
PRODUCTS_PER_PAGE = 50


def get_total_results(html: str):
    """Saca el número total de resultados de la búsqueda usando expresiones regulares"""
    # Cantidad de resultados dentro del HTML. Básicamente, estamos buscando cuántos productos hay.
    pattern = re.compile(
        r'<span class="ui-search-search-result__quantity-results">([\d\.,]+) resultados</span>'
    )

    # Buscando el patrón en el HTML
    match = pattern.search(html)

    if match:
        # group(1) devuelve lo que coincidió con el primer grupo entre paréntesis. En este caso, la expresión regular tiene un grupo ([\d\.,]+) que busca el número total de resultados (números con puntos o comas).
        total_results_str = match.group(1)
        # El número a entero
        total_results = int(total_results_str.replace(".", "").replace(",", ""))
        return total_results
    print("No se encontró el número total de resultados en el HTML.")
    return 0


def extract_products_and_prices(html: str):
    """Extrae los nombres de los productos y sus precios"""
    # Los nombres de los productos
    product_pattern = re.compile(
        r'<h2 class="poly-box poly-component__title"><a[^>]*>(.*?)</a></h2>', re.DOTALL
    )

    # Precios de los productos, pero solo los que no están en "buy box"
    price_pattern = re.compile(
        r'<div class="poly-price__current">.*?<span class="andes-money-amount__fraction" aria-hidden="true">([\d.,]+)</span>',
        re.DOTALL,
    )

    # Expresión regular especial para los precios que sí están en la "buy box" (no queremos duplicados)
    buy_box_pattern = re.compile(
        r'<div class="poly-component__buy-box">.*?<div class="poly-price__current">.*?<span class="andes-money-amount__fraction" aria-hidden="true">([\d.,]+)</span>',
        re.DOTALL,
    )

    # Buscar todos los productos y precios en el HTML:
    products = product_pattern.findall(html)
    buy_box_prices = buy_box_pattern.findall(html)
    all_prices = price_pattern.findall(html)

    # Limpiamos los precios que están en la "buy box" para que no los contemos dos veces. Buy box basicamente muestra Otra opcion de compra por otro precio. Asique lo estamos obviando para que no nos corra el indice
    filtered_prices = [price for price in all_prices if price not in buy_box_prices]

    # Lista de productos y precios
    return products, filtered_prices


def scrape_all_pages(query: str):
    """Recorre todas las páginas de resultados, buscando productos y precios"""
    # Reemplaza espacios con guiones medios porque la web no entiende espacios)
    search_query = query.replace(" ", "-")
    url = f"{URL_BASE}{search_query}#D[A:{search_query}]"
    try:
        # 🚀 Primera solicitud: búsqueda a la URL
        response = requests.get(url, timeout=300)
        html = response.text

        # Número total de resultados
        total_results = get_total_results(html)
        if total_results == 0:
            print("No se encontraron resultados.")
            return

        print(f"Total de resultados: {total_results}")

        # 🧮 Se calcula cuántas páginas necesitamos ver basándonos en el total de productos y los productos por página

        # La función math.ceil() se utiliza para redondear un número decimal al entero más cercano por arriba. Es decir, si tenés un número con decimales y querés asegurarte de que siempre sea "redondeado hacia arriba", aunque la parte decimal sea pequeña, math.ceil() es la función ideal.

        # Por ejemplo:

        #     math.ceil(3.2) te dá 4.
        #     math.ceil(7.9) te dá 8.
        #     math.ceil(5.0) te dá 5 (ya que no tiene decimales).

        total_pages = math.ceil(total_results / PRODUCTS_PER_PAGE)
        all_products = []
        all_prices = []
        # Para la primera iteración, page va a ser 1:
        for page in range(1, total_pages + 1):
            if page == 1:
                page_url = (
                    url  # La primera página siempre es la misma URL que ya tenemos
                )
            else:
                # Para las demás páginas, ajustamos la URL con un "offset" (básicamente, saltamos productos ya vistos)
                offset = (page - 1) * PRODUCTS_PER_PAGE + 1
                page_url = f"https://listado.mercadolibre.com.ar/{search_query}_Desde_{offset}_NoIndex_True"

            print(f"Scraping página {page}: {page_url}")

            # Página actual
            response = requests.get(page_url, timeout=300)
            html = response.text

            # Extraemos los productos y precios:
            products, prices = extract_products_and_prices(html)
            all_products.extend(products)  # Productos a lista de productos
            all_prices.extend(prices)  # Lo mismo con los precios

        print(len(all_products), "PRODUCTOS ENCONTRADOS \n")
        print(len(set(all_products)), "PRODUCTOS ÚNICOS")

        for product, price in zip(all_products, all_prices):
            formatted_price = price.replace(".", ",")
            print(f"Producto: {product.strip()}, Precio: ${formatted_price}")

    except requests.exceptions.ConnectTimeout as error:
        print("Error de conexión", error)


# A probar!!
search = input("Introduce el artículo a buscar: ")
scrape_all_pages(search)
