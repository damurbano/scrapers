import requests
import re
import math

# URL base sin el término de búsqueda
URL_BASE = "https://listado.mercadolibre.com.ar/"

PRODUCTS_PER_PAGE = 50  # Mercado Libre muestra 50 productos por página


def get_total_results(html):
    """Extrae el total de resultados de la búsqueda desde el HTML usando expresiones regulares."""
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


def extract_products_and_prices(html):
    """Extrae los nombres y precios de los productos desde el HTML usando expresiones regulares."""
    # Expresión regular para nombres de productos
    product_pattern = re.compile(
        r'<h2 class="poly-box poly-component__title"><a[^>]*>(.*?)</a></h2>', re.DOTALL
    )
    # Expresión regular para precios de productos, excluyendo precios en <div class="poly-component__buy-box">
    price_pattern = re.compile(
        r'<div class="poly-price__current">.*?<span class="andes-money-amount__fraction" aria-hidden="true">([\d.,]+)</span>',
        re.DOTALL,
    )
    buy_box_pattern = re.compile(
        r'<div class="poly-component__buy-box">.*?<div class="poly-price__current">.*?<span class="andes-money-amount__fraction" aria-hidden="true">([\d.,]+)</span>',
        re.DOTALL,
    )

    # Encontrar todos los nombres de productos y precios
    products = product_pattern.findall(html)
    buy_box_prices = buy_box_pattern.findall(html)
    all_prices = price_pattern.findall(html)

    # Filtrar precios que están dentro de <div class="poly-component__buy-box">
    filtered_prices = [price for price in all_prices if price not in buy_box_prices]

    return products, filtered_prices


def scrape_all_pages(query):
    """Recorre todas las páginas de resultados y extrae los productos y precios."""
    # Construir la URL con el término de búsqueda
    search_query = query.replace(" ", "_")
    url = f"{URL_BASE}{search_query}#D[A:{search_query}]"

    try:
        response = requests.get(url, timeout=300)
        html = response.text

        total_results = get_total_results(html)
        if total_results == 0:
            print("No se encontraron resultados.")
            return

        print(f"Total de resultados: {total_results}")

        total_pages = math.ceil(total_results / PRODUCTS_PER_PAGE)
        all_products = []
        all_prices = []

        for page in range(1, total_pages + 1):
            if page == 1:
                page_url = url
            else:
                offset = (page - 1) * PRODUCTS_PER_PAGE + 1
                page_url = f"https://listado.mercadolibre.com.ar/{search_query}_Desde_{offset}_NoIndex_True"

            print(f"Scraping página {page}: {page_url}")
            response = requests.get(page_url, timeout=300)
            html = response.text

            products, prices = extract_products_and_prices(html)
            all_products.extend(products)
            all_prices.extend(prices)

        # Mostrar el número total de productos extraídos
        print(len(all_products), "PRODUCTOS ENCONTRADOS")
        print(len(set(all_products)), "PRODUCTOS ÚNICOS")

        # Mostrar los nombres de los productos y sus precios
        for product, price in zip(all_products, all_prices):
            formatted_price = price.replace(".", ",")  # Reemplaza el punto por la coma
            print(f"Producto: {product.strip()}, Precio: ${formatted_price}")

    except requests.exceptions.ConnectTimeout as error:
        print("Error de conexión", error)


# Solicitar al usuario el artículo a buscar
search = input("Introduce el artículo a buscar: ").replace(" ", "-")
scrape_all_pages(search)
