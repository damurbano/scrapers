<p align="center">
  <img src="../image/README/mercadoscraper.png" alt="mercadoScrapper" width="400" height="300" />
</p>

# MercadoLibre Scraper

Este script permite realizar scraping de productos y precios en MercadoLibre Argentina a partir de una búsqueda específica, recorriendo todas las páginas de resultados.

El espiritu de este modulo es usar *re*, *request* y *math*.
Sin mucha sofisticacion... no hay selenium, ni BeautifulSoup, ni pandas, ni WebDriver. 😌

## Características

Extrae los nombres de los productos y sus precios de las páginas de búsqueda de MercadoLibre.
Excluye precios que están dentro de la sección "buy box".
Calcula el número total de páginas en función de los resultados encontrados.
Formatea los precios utilizando comas para los decimales y puntos para los separadores de miles.

## Uso

Clona o descarga el repositorio.
Asegúrate de tener instaladas las dependencias necesarias.
Ejecuta el script y proporciona el término de búsqueda cuando se te solicite.

```bash

python scraper.py
```

El script imprimirá en la consola los nombres y precios de los productos encontrados.

## Ejemplo de salida

```bash

Introduce el artículo a buscar: iPhone
Scraping página 1: https://listado.mercadolibre.com.ar/iPhone#D[A:iPhone]
Total de resultados: 2350
Scraping página 2: https://listado.mercadolibre.com.ar/iPhone_Desde_51_NoIndex_True
...
Producto: iPhone 13 Pro, Precio: $150.000
Producto: iPhone 12 Mini, Precio: $120.000
...
```

## Notas

MercadoLibre muestra hasta 50 productos por página. Este script ajusta dinámicamente las páginas en función de los resultados totales.
Los precios se muestran formateados con comas para los decimales y puntos como separadores de miles.
En caso de que la página de MercadoLibre cambie su estructura HTML, es posible que el script necesite ajustes en las expresiones regulares.
