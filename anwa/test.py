import sqlite3
import os

# Verificar si el archivo existe
db_path = "db.sqlite3"
if not os.path.exists(db_path):
    print(f"Error: El archivo {db_path} no existe.")
    exit()

# Conectar a la base de datos
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f"Conexión exitosa a la base de datos: {db_path}")
except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")
    exit()

# Obtener las tablas
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    if not tables:
        print("No se encontraron tablas en la base de datos.")
    else:
        print("Tablas:", [table[0] for table in tables])
except Exception as e:
    print(f"Error al obtener las tablas: {e}")
    conn.close()
    exit()

# Obtener la estructura de cada tabla
for table in tables:
    table_name = table[0]
    try:
        print(f"\nEstructura de la tabla: {table_name}")
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        structure = cursor.fetchall()
        if not structure:
            print(f"La tabla {table_name} no tiene columnas.")
        else:
            print(structure)
    except Exception as e:
        print(f"Error al obtener la estructura de la tabla {table_name}: {e}")

# Relaciones (foreign keys)
for table in tables:
    table_name = table[0]
    try:
        print(f"\nRelaciones (foreign keys) de la tabla: {table_name}")
        cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
        foreign_keys = cursor.fetchall()
        if not foreign_keys:
            print(f"La tabla {table_name} no tiene claves foráneas.")
        else:
            print(foreign_keys)
    except Exception as e:
        print(f"Error al obtener claves foráneas de la tabla {table_name}: {e}")

conn.close()
