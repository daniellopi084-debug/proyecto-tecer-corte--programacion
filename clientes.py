# ============================================================
# clientes.py — Módulo CRUD de Clientes
# Proyecto: Fideliza-Puntos (Reto Mercadeo)
# Grupo: Juan José Caballero, Martín Trujillo, Daniel Piraquive
# ============================================================

import sqlite3
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME  = os.path.join(BASE_DIR, "fideliza_puntos.db")


# ── CLASE PADRE ──────────────────────────────────────────────
class PersonaBase:
    """Clase padre: encapsula los datos personales básicos."""
    def __init__(self, nombre: str, correo: str, ciudad: str):
        self._nombre = nombre          # Atributo protegido
        self.__correo = correo         # Atributo privado
        self._ciudad = ciudad

    # get/set nombre
    def get_nombre(self) -> str:
        return self._nombre

    def set_nombre(self, nuevo: str):
        if not nuevo.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = nuevo.strip().title()

    # get/set correo
    def get_correo(self) -> str:
        return self.__correo

    def set_correo(self, nuevo: str):
        if "@" not in nuevo:
            raise ValueError("Correo inválido: debe contener '@'.")
        self.__correo = nuevo.strip().lower()

    def __str__(self):
        return f"{self._nombre} ({self.__correo}) — {self._ciudad}"


# ── CLASE HIJO ───────────────────────────────────────────────
class Cliente(PersonaBase):
    """Clase hijo: extiende PersonaBase con tipo de cliente."""
    def __init__(self, nombre: str, correo: str, ciudad: str, tipo: str = "Regular"):
        super().__init__(nombre, correo, ciudad)
        self.__tipo = tipo   # privado

    # get/set tipo
    def get_tipo(self) -> str:
        return self.__tipo

    def set_tipo(self, nuevo: str):
        opciones = ("Estudiante", "Regular", "VIP")
        if nuevo not in opciones:
            raise ValueError(f"Tipo inválido. Opciones: {opciones}")
        self.__tipo = nuevo

    def __str__(self):
        return f"[Cliente] {self._nombre} | Tipo: {self.__tipo} | Ciudad: {self._ciudad}"


# ── MANAGER (CRUD) ───────────────────────────────────────────
class ClienteManager:
    """Gestiona las operaciones CRUD de clientes en SQLite."""

    def crear(self, nombre: str, correo: str, ciudad: str, tipo: str):
        """CREATE — Insertar un nuevo cliente."""
        try:
            cli = Cliente(nombre, correo, ciudad, tipo)
            conn = sqlite3.connect(DB_NAME)
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO clientes (nombre, correo, ciudad, tipo) VALUES (?,?,?,?)",
                (cli.get_nombre(), cli.get_correo(), cli._ciudad, cli.get_tipo())
            )
            conn.commit()
            print(f"  ✅ Cliente '{cli.get_nombre()}' registrado con ID {cur.lastrowid}.")
        except ValueError as ve:
            print(f"  ⚠️  Validación: {ve}")
        except sqlite3.IntegrityError:
            print("  ❌ Error: ese correo ya está registrado.")
        except Exception as e:
            print(f"  🔥 Error inesperado: {e}")
        finally:
            conn.close()

    def leer(self):
        """READ — Mostrar todos los clientes."""
        try:
            conn = sqlite3.connect(DB_NAME)
            df = pd.read_sql_query("SELECT * FROM clientes ORDER BY id_cliente", conn)
            conn.close()
            if df.empty:
                print("  ℹ️  No hay clientes registrados.")
            else:
                print(df.to_string(index=False))
        except Exception as e:
            print(f"  🔥 Error: {e}")

    def actualizar(self, id_cliente: int, nuevo_tipo: str):
        """UPDATE — Cambiar el tipo de un cliente."""
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("UPDATE clientes SET tipo=? WHERE id_cliente=?", (nuevo_tipo, id_cliente))
            if cur.rowcount == 0:
                print(f"  ⚠️  No existe cliente con ID {id_cliente}.")
            else:
                print(f"  ✅ Cliente {id_cliente} actualizado a tipo '{nuevo_tipo}'.")
            conn.commit()
        except Exception as e:
            print(f"  🔥 Error: {e}")
        finally:
            conn.close()

    def eliminar(self, id_cliente: int):
        """DELETE — Eliminar un cliente."""
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("DELETE FROM clientes WHERE id_cliente=?", (id_cliente,))
            if cur.rowcount == 0:
                print(f"  ⚠️  No existe cliente con ID {id_cliente}.")
            else:
                print(f"  ✅ Cliente {id_cliente} eliminado.")
            conn.commit()
        except Exception as e:
            print(f"  🔥 Error: {e}")
        finally:
            conn.close()


# ── DATA CLEANER ─────────────────────────────────────────────
class ClienteDataCleaner:
    """Normaliza los datos de clientes usando Pandas."""

    @staticmethod
    def normalizar():
        try:
            conn = sqlite3.connect(DB_NAME)
            df = pd.read_sql_query("SELECT * FROM clientes", conn)
            df["nombre"] = df["nombre"].str.strip().str.title()
            df["correo"] = df["correo"].str.strip().str.lower()
            df["ciudad"] = df["ciudad"].str.strip().str.title()
            df.dropna(subset=["nombre", "correo"], inplace=True)
            cur = conn.cursor()
            for _, row in df.iterrows():
                cur.execute(
                    "UPDATE clientes SET nombre=?, correo=?, ciudad=? WHERE id_cliente=?",
                    (row["nombre"], row["correo"], row["ciudad"], row["id_cliente"])
                )
            conn.commit()
            conn.close()
            print("  🧹 Datos de clientes normalizados.")
        except Exception as e:
            print(f"  🔥 Error al normalizar: {e}")


# ── MENÚ INTERACTIVO ─────────────────────────────────────────
class ClienteInteractivo:
    """Menú de consola para gestionar clientes."""
    TIPOS = ("Estudiante", "Regular", "VIP")

    def __init__(self):
        self.mgr = ClienteManager()
        self.cleaner = ClienteDataCleaner()

    def menu(self):
        opciones = {
            "1": self._crear,
            "2": self.mgr.leer,
            "3": self._actualizar,
            "4": self._eliminar,
            "5": self.cleaner.normalizar,
        }
        while True:
            print("\n  ── GESTIÓN DE CLIENTES ──")
            print("  1. Registrar cliente")
            print("  2. Ver todos los clientes")
            print("  3. Actualizar tipo de cliente")
            print("  4. Eliminar cliente")
            print("  5. Normalizar datos")
            print("  0. Volver al menú principal")
            op = input("  Opción: ").strip()
            if op == "0":
                break
            accion = opciones.get(op)
            if accion:
                accion()
            else:
                print("  ⚠️  Opción inválida.")

    def _crear(self):
        nombre = input("  Nombre: ").strip()
        correo = input("  Correo: ").strip()
        ciudad = input("  Ciudad: ").strip()
        print(f"  Tipos disponibles: {self.TIPOS}")
        tipo   = input("  Tipo: ").strip().title()
        self.mgr.crear(nombre, correo, ciudad, tipo)

    def _actualizar(self):
        raw = input("  ID del cliente: ").strip()
        if not raw.isdigit():
            print("  ⚠️  Ingrese un número válido.")
            return
        print(f"  Tipos disponibles: {self.TIPOS}")
        tipo = input("  Nuevo tipo: ").strip().title()
        self.mgr.actualizar(int(raw), tipo)

    def _eliminar(self):
        raw = input("  ID del cliente a eliminar: ").strip()
        if not raw.isdigit():
            print("  ⚠️  Ingrese un número válido.")
            return
        self.mgr.eliminar(int(raw))
