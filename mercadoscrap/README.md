<p align="center">
  <img src="../image/README/mercadoscraper.png" alt="mercadoScrapper" width="400" height="300" />
</p>

# MercadoLibre Scraper

Este script permite realizar scraping de productos y precios en MercadoLibre Argentina a partir de una búsqueda específica, recorriendo todas las páginas de resultados.
Genera una base de datos relacional y la guarda en el path del proyecto.
Tambien tiene una clase que se encarga de plotear algunos graficos.

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

python main.py
```

El script imprimirá en la consola los nombres y precios de los productos encontrados.

Ejemplo de salida

```bash

Introduce el artículo a buscar: cuchara madera
********************
Utensilios de Preparación CANTIDAD: 647
********************
Total de resultados: 645
Scraping página 1: https://listado.mercadolibre.com.ar/hogar-muebles-jardin/bazar-cocina/utensilios-preparacion/cuchara-madera_NoIndex_True#applied_filter_id%3Dcategory%26applied_filter_name%3DCategor%C3%ADas%26applied_filter_order%3D3%26applied_value_id%3DMLA436273%26applied_value_name%3DUtensilios+de+Preparaci%C3%B3n%26applied_value_order%3D5%26applied_value_results%3D647%26is_custom%3Dfalse
50 PRODUCTOS ENCONTRADOS 

46 PRODUCTOS ÚNICOS
Producto: 3 Utensilios Madera Bamboo Cocina Cuchara Espatula Tenedor, Precio: $3,599
Producto: Cuchara Calada Hudson Utensilio Nylon Mango Madera, Precio: $4,988
Producto: Set De 4 Utensilios Bambu Pinza 2 Espatulas Y Cuchara Color Madera, Precio: $3,873
Producto: Cuchara De Madera 35cm Cocinera Ferpa, Precio: $2,363
...
Producto: Cuchara Vertedora Para Plomo I Mabu, Precio: $33,600
Producto: Cuchara De Madera Para Cocina Utensilios Kuchen Color Marrón, Precio: $3,775
Producto: Cuchara De Madera 30 Cm - Jovifel Color Marrón, Precio: $2,615
...
```

<p align="center">
  <img src="../image/README/cuchara_madera1.png" alt="mercadoScrapper" width="600" height="400" />
</p>

<p align="center">
  <img src="../image/README/cuchara_madera2.png" alt="mercadoScrapper" width="600" height="400" />
</p>


## Notas

MercadoLibre muestra hasta 50 productos por página. Este script ajusta dinámicamente las páginas en función de los resultados totales.
Los precios se muestran formateados con comas para los decimales y puntos como separadores de miles.
En caso de que la página de MercadoLibre cambie su estructura HTML, es posible que el script necesite ajustes en las expresiones regulares.
