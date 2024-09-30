import os
import pandas as pd
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    precio = Column(Float)
    fecha_agregado = Column(
        DateTime, default=datetime.utcnow
    )  # Fecha de agregación por defecto
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    categoria = relationship("Categoria", back_populates="productos")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nombre = Column(String)

    productos = relationship("Producto", back_populates="categoria")


def limpiar_precio(precio_str):
    # Elimina el símbolo de moneda y separadores de miles
    precio_limpio = (
        precio_str.replace("$", "").replace(".", "").replace(",", ".").strip()
    )
    return float(precio_limpio.replace(".", "").replace(",", "."))


def insert_data(datadict):
    # Crear el motor de base de datos (en este caso, usando SQLite y creando un archivo local)
    engine = create_engine("sqlite:///mi_base_de_datos.db")

    # Crear las tablas en la base de datos
    Base.metadata.create_all(engine)

    # Crear una sesión para interactuar con la base de datos
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insertar categorías y productos
    for categoria_nombre, productos in datadict.items():
        categoria = session.query(Categoria).filter_by(nombre=categoria_nombre).first()
        if not categoria:
            categoria = Categoria(nombre=categoria_nombre)
            session.add(categoria)
            session.commit()

        for producto_nombre, info in productos.items():
            # Evitar duplicados de producto y precio
            precio = info["Precio"][0]
            precio_limpio = limpiar_precio(precio)

            producto_existente = (
                session.query(Producto)
                .filter_by(nombre=producto_nombre, precio=precio_limpio)
                .first()
            )

            if not producto_existente:
                # Insertar el producto con el primer precio
                nuevo_producto = Producto(
                    nombre=producto_nombre, precio=precio_limpio, categoria=categoria
                )
                session.add(nuevo_producto)

        session.commit()


def convert_to_dataframes(datadict):
    dfs = {}
    for category, products in datadict.items():
        # Crear un DataFrame para cada categoría
        category_data = []
        for product, details in products.items():
            for price in details["Precio"]:
                category_data.append({"Producto": product, "Precio": price})

        df = pd.DataFrame(category_data)
        dfs[category] = df

    return dfs
