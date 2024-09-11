import requests  # 🕸️ Solicitudes HTTP
import re  # 🧙‍♂️ Expresiones regulares, la varita mágica para buscar patrones en el HTML
import math  # 🧮 Matemáticas para calcular cuántas páginas hay en total
from bs4 import BeautifulSoup

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
    # print(nombre_categoria)

    if h3 and h3.get_text(strip=True):
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
                    qty = int(qty_text.strip("()"))
                    categories[nombre_categoria].update({title: qty})
            print(categories)
    else:
        print("No se encontró el encabezado 'Categorías'.")


def scrape_all_pages(query: str):
    """Recorre todas las páginas de resultados, buscando productos, precios y categorías"""
    search_query = query.replace(" ", "-")
    url = f"{URL_BASE}{search_query}#D[A:{search_query}]"
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

        for page in range(1, total_pages + 1):
            if page == 1:
                page_url = url
            else:
                offset = (page - 1) * PRODUCTS_PER_PAGE + 1
                page_url = f"https://listado.mercadolibre.com.ar/{search_query}_Desde_{offset}_NoIndex_True"

            print(f"Scraping página {page}: {page_url}")

            response = requests.get(page_url, timeout=300)
            html = response.text

            # Extraer productos y precios
            products, prices = extract_products_and_prices(html)
            all_products.extend(products)
            all_prices.extend(prices)

        print(len(all_products), "PRODUCTOS ENCONTRADOS \n")
        print(len(set(all_products)), "PRODUCTOS ÚNICOS")

        for product, price in zip(all_products, all_prices):
            formatted_price = price.replace(".", ",")
            print(f"Producto: {product.strip()}, Precio: ${formatted_price}")

        # Obtener las categorías
        # print(_html)
        categories = get_categories(_html)
        # if categories:
        #     print("\nCategorías encontradas:")
        #     for category, qty in categories:
        #         print(f"Categoría: {category}, Resultados: {qty}")

    except requests.exceptions.ConnectTimeout as error:
        print("Error de conexión", error)


# A probar!!
search = input("Introduce el artículo a buscar: ")
scrape_all_pages(search)
