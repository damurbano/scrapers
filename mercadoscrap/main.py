import requests
from mercadolibre import scrape_all_pages, get_categories
from database import insert_data
from visualizer import DataVisualizer

# URL base de Mercado Libre.
URL_BASE = "https://listado.mercadolibre.com.ar/"

# Mercado Libre nos muestra 50 productos por página, así que lo guardamos como una constante
PRODUCTS_PER_PAGE = 50


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
        
    
        insert_data(finalDict)
        visualizer = DataVisualizer("sqlite:///mi_base_de_datos.db")
        visualizer.plot_suma_precios()
        visualizer.plot_distribucion_categorias()


if __name__ == "__main__":
    main()
