import os
import tkinter as tk
from tkinter import filedialog
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import relationship, sessionmaker

# Crear motor y sesión SQLAlchemy
engine = create_engine('mysql+mysqlconnector://root:piteravi07@localhost:3306/analisis_datos')
Session = sessionmaker(bind=engine)

# Definir una clase base
Base = declarative_base()

# Definir las clases de las tablas
class Usuario(Base):
    __tablename__ = 'Usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255))
    correo_electronico = Column(String(255))
    conjuntos_datos = relationship("ConjuntoDatos", back_populates="usuario")

class ConjuntoDatos(Base):
    __tablename__ = 'Conjuntos_datos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255))
    archivo = Column(LargeBinary)  # Cambiado a LargeBinary para almacenar el contenido del archivo
    usuario_id = Column(Integer, ForeignKey('Usuarios.id'))  # Cambiado a usuario_id
    usuario = relationship("Usuario", back_populates="conjuntos_datos")
    resultados_analisis = relationship("ResultadoAnalisis", back_populates="conjunto_datos")
    variables = relationship("Variable", back_populates="conjunto_datos")

class ResultadoAnalisis(Base):
    __tablename__ = 'Resultados_analisis'
    id = Column(Integer, primary_key=True)
    id_conjunto_datos = Column(Integer, ForeignKey('Conjuntos_datos.id'))
    tipo_analisis = Column(String(100))
    resultado = Column(String(255))
    conjunto_datos = relationship("ConjuntoDatos", back_populates="resultados_analisis")

class Variable(Base):
    __tablename__ = 'Variables'
    id = Column(Integer, primary_key=True)
    id_conjunto_datos = Column(Integer, ForeignKey('Conjuntos_datos.id'))
    nombre = Column(String(255))
    tipo = Column(String(50))
    conjunto_datos = relationship("ConjuntoDatos", back_populates="variables")

# Crear todas las tablas si no existen
Base.metadata.create_all(engine)

def menu():
    print("Menu:")
    print("1. Insertar un nuevo usuario")
    print("2. Listar todos los usuarios")
    print("3. Subir archivo")
    print("4. Registrar conjunto de datos")
    print("5. Listar todos los conjuntos de datos")
    print("6. Salir")

def insertar_usuario():
    nombre = input("Ingrese el nombre del usuario: ")
    correo = input("Ingrese el correo electrónico del usuario: ")
    nuevo_usuario = Usuario(nombre=nombre, correo_electronico=correo)
    session = Session()
    try:
        session.add(nuevo_usuario)
        session.commit()
        print("Usuario insertado correctamente.")
    except Exception as e:
        session.rollback()
        print(f"Error al insertar el usuario: {e}")
    finally:
        session.close()

def listar_usuarios():
    session = Session()
    try:
        usuarios = session.query(Usuario).all()
        for usuario in usuarios:
            print("ID:", usuario.id, "Nombre:", usuario.nombre, "Correo electrónico:", usuario.correo_electronico)
    except Exception as e:
        print(f"Error al listar usuarios: {e}")
    finally:
        session.close()

def subir_archivo():
    root = tk.Tk()
    file_path = filedialog.askopenfilename()  # Abrir ventana de selección de archivo
    root.destroy()  # Cerrar la ventana después de seleccionar el archivo
    if not file_path:
        print("No se seleccionó ningún archivo.")
        return
    
    nombre_archivo = os.path.basename(file_path)
    extension_valida = nombre_archivo.endswith(('.txt', '.csv', '.xlsx', '.docx', '.pdf'))
    if not extension_valida:
        print("Error: Extensión de archivo no válida. Se requiere un archivo de texto, CSV, Word o PDF.")
        return
    
    try:
        with open(file_path, 'rb') as file:
            contenido = file.read()
        nuevo_conjunto_datos = ConjuntoDatos(nombre=nombre_archivo, archivo=contenido)
        session = Session()
        try:
            session.add(nuevo_conjunto_datos)
            session.commit()
            print(f"Archivo '{nombre_archivo}' subido correctamente a la base de datos.")
        except Exception as e:
            session.rollback()
            print(f"Error al subir el archivo: {e}")
        finally:
            session.close()
    except Exception as e:
        print(f"Error al leer el archivo: {e}")

def registrar_conjunto_datos():
    nombre = input("Ingrese el nombre del conjunto de datos: ")
    id_usuario = int(input("Ingrese el ID del usuario al que pertenece el conjunto de datos: "))
    
    session = Session()
    try:
        usuario = session.query(Usuario).filter_by(id=id_usuario).first()
        if usuario:
            nuevo_conjunto_datos = ConjuntoDatos(nombre=nombre, usuario=usuario)  
            session.add(nuevo_conjunto_datos)
            session.commit()
            print(f"Conjunto de datos '{nombre}' registrado correctamente.")
        else:
            print("El usuario especificado no existe.")
    except Exception as e:
        session.rollback()
        print(f"Error al registrar conjunto de datos: {e}")
    finally:
        session.close()

def listar_conjuntos_datos():
    session = Session()
    try:
        conjuntos_datos = session.query(ConjuntoDatos).all()
        for conjunto_datos in conjuntos_datos:
            print("ID:", conjunto_datos.id, "Nombre:", conjunto_datos.nombre)
    except Exception as e:
        print(f"Error al listar conjuntos de datos: {e}")
    finally:
        session.close()

# Ejecutar el programa
while True:
    menu()
    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        insertar_usuario()
    elif opcion == "2":
        listar_usuarios()
    elif opcion == "3":
        subir_archivo()
    elif opcion == "4":
        registrar_conjunto_datos()
    elif opcion == "5":
        listar_conjuntos_datos()
    elif opcion == "6":
        print("Saliendo del programa...")
        break
    else:
        print("Opción no válida. Por favor, seleccione una opción válida")
