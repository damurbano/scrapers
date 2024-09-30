import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

matplotlib.use("QtAgg")


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
            self.productos_df = pd.read_sql_table("productos", self.conn)
            self.categorias_df = pd.read_sql_table("categorias", self.conn)
            # Fusionar las tablas productos y categorias
            self.merged_df = pd.merge(
                self.productos_df,
                self.categorias_df,
                left_on="categoria_id",
                right_on="id",
            )
        except Exception as e:
            raise Exception(
                f"Error al conectar con la base de datos o leer las tablas: {e}"
            )

        # Verificar la estructura del DataFrame combinado
        print(self.merged_df.head())
        print("***********" * 6)

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
        df_suma = self.merged_df.groupby("nombre_y")["precio"].sum().reset_index()

        # Escalar los precios a miles, millones o billones
        def scale_values(value):
            if value >= 1_000_000_000:
                return f"{value / 1_000_000_000:.1f}B $"  # Billones
            elif value >= 1_000_000:
                return f"{value / 1_000_000:.1f}M $"  # Millones
            elif value >= 1_000:
                return f"{value / 1_000:.1f}K $"  # Miles
            else:
                return f"{value:.0f} $"

        # Configuración del gráfico
        plt.figure(figsize=(12, 6))
        df_suma["precio_scaled"] = df_suma["precio"].apply(scale_values)
        colors = sns.color_palette("husl", len(df_suma))
        barplot = sns.barplot(x="nombre_y", y="precio", data=df_suma, palette=colors)

        plt.title("Suma de precios por categoría")
        plt.xlabel("Categoría")
        plt.ylabel("Suma de Precios")

        plt.xticks(rotation=45, ha="right")

        for index, row in df_suma.iterrows():
            barplot.text(
                x=index,
                y=row["precio"]
                + 0.02
                * df_suma["precio"].max(),  # Ajustar la posición vertical del texto
                s=df_suma.loc[index, "precio_scaled"],  # Texto escalado
                color="black",  # Color del texto
                ha="center",
                va="bottom",
                fontsize=10,
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
        df_count = self.merged_df.groupby("nombre_y")["id_x"].count().reset_index()
        df_count.rename(columns={"id_x": "cantidad"}, inplace=True)

        # Ordenar las categorías por cantidad en orden descendente
        df_count = df_count.sort_values(by="cantidad", ascending=False)

        # Número de categorías a mostrar sin agrupar
        num_categories_to_show = 3

        if len(df_count) > num_categories_to_show:
            # Seleccionar las primeras 'num_categories_to_show' categorías
            top_categories = df_count.head(num_categories_to_show)

            # Agrupar las categorías restantes en "otros"
            remaining_categories = df_count.iloc[num_categories_to_show:]
            if not remaining_categories.empty:
                otros_count = remaining_categories["cantidad"].sum()
                # Crear un DataFrame para la categoría "otros"
                otros_df = pd.DataFrame(
                    {"nombre_y": ["Otros"], "cantidad": [otros_count]}
                )
                # Concatenar el DataFrame de las principales categorías con "otros"
                top_categories = pd.concat(
                    [top_categories, otros_df], ignore_index=True
                )
        else:
            # Si hay 6 o menos categorías, mostrar todas
            top_categories = df_count

        # Configuración del gráfico de torta
        plt.figure(figsize=(12, 8))

        # Crear el gráfico de torta con colores personalizados
        colors = sns.color_palette("husl", len(top_categories))
        plt.pie(
            top_categories["cantidad"],
            labels=[f"{name}" for name in top_categories["nombre_y"]],
            colors=colors,
            autopct="%1.1f%%",
            startangle=140,
        )

        # Añadir leyenda con cantidades
        labels = [
            f"{name}: {count}"
            for name, count in zip(
                top_categories["nombre_y"], top_categories["cantidad"]
            )
        ]
        plt.legend(
            labels, title="Categorías", bbox_to_anchor=(1.05, 1), loc="upper left"
        )

        # Añadir título
        plt.title("Distribución de productos por categoría")

        # Ajustar el diseño
        plt.tight_layout()
        plt.show()
