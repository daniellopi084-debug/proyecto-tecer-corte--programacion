# ============================================================
# sucursales.py — Módulo CRUD de Sucursales
# Proyecto: Fideliza-Puntos (Reto Mercadeo)
# ============================================================

import sqlite3
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME  = os.path.join(BASE_DIR, "fideliza_puntos.db")


# ── CLASE PADRE ──────────────────────────────────────────────
class LugarBase:
    """Clase padre: encapsula datos de ubicación."""
    def __init__(self, nombre: str, ciudad: str):
        self._nombre = nombre
        self._ciudad = ciudad

    def get_nombre(self) -> str:
        return self._nombre

    def set_nombre(self, nuevo: str):
        if not nuevo.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = nuevo.strip().title()

    def get_ciudad(self) -> str:
        return self._ciudad

    def set_ciudad(self, nueva: str):
        if not nueva.strip():
            raise ValueError("La ciudad no puede estar vacía.")
        self._ciudad = nueva.strip().title()

    def __str__(self):
        return f"{self._nombre} — {self._ciudad}"


# ── CLASE HIJO ───────────────────────────────────────────────
class Sucursal(LugarBase):
    """Clase hijo: extiende LugarBase con dirección."""
    def __init__(self, nombre: str, ciudad: str, direccion: str):
        super().__init__(nombre, ciudad)
        self.__direccion = direccion   # privado

    def get_direccion(self) -> str:
        return self.__direccion

    def set_direccion(self, nueva: str):
        if not nueva.strip():
            raise ValueError("La dirección no puede estar vacía.")
        self.__direccion = nueva.strip()

    def __str__(self):
        return f"[Sucursal] {self._nombre} | {self._ciudad} | {self.__direccion}"


# ── MANAGER (CRUD) ───────────────────────────────────────────
class SucursalManager:

    def crear(self, nombre: str, ciudad: str, direccion: str):
        try:
            suc = Sucursal(nombre, ciudad, direccion)
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO sucursales (nombre, ciudad, direccion) VALUES (?,?,?)",
                (suc.get_nombre(), suc.get_ciudad(), suc.get_direccion())
            )
            conn.commit()
            print(f"  ✅ Sucursal '{suc.get_nombre()}' creada con ID {cur.lastrowid}.")
        except ValueError as ve:
            print(f"  ⚠️  Validación: {ve}")
        except Exception as e:
            print(f"  🔥 Error: {e}")
        finally:
            conn.close()

    def leer(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            df = pd.read_sql_query("SELECT * FROM sucursales ORDER BY id_sucursal", conn)
            conn.close()
            if df.empty:
                print("  ℹ️  No hay sucursales.")
            else:
                print(df.to_string(index=False))
        except Exception as e:
            print(f"  🔥 Error: {e}")

    def actualizar(self, id_suc: int, nueva_ciudad: str, nueva_dir: str):
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute(
                "UPDATE sucursales SET ciudad=?, direccion=? WHERE id_sucursal=?",
                (nueva_ciudad.title(), nueva_dir.strip(), id_suc)
            )
            if cur.rowcount == 0:
                print(f"  ⚠️  No existe sucursal con ID {id_suc}.")
            else:
                print(f"  ✅ Sucursal {id_suc} actualizada.")
            conn.commit()
        except Exception as e:
            print(f"  🔥 Error: {e}")
        finally:
            conn.close()

    def eliminar(self, id_suc: int):
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("DELETE FROM sucursales WHERE id_sucursal=?", (id_suc,))
            if cur.rowcount == 0:
                print(f"  ⚠️  No existe sucursal con ID {id_suc}.")
            else:
                print(f"  ✅ Sucursal {id_suc} eliminada.")
            conn.commit()
        except Exception as e:
            print(f"  🔥 Error: {e}")
        finally:
            conn.close()


# ── MENÚ INTERACTIVO ─────────────────────────────────────────
class SucursalInteractivo:
    def __init__(self):
        self.mgr = SucursalManager()

    def menu(self):
        while True:
            print("\n  ── GESTIÓN DE SUCURSALES ──")
            print("  1. Agregar sucursal")
            print("  2. Ver sucursales")
            print("  3. Actualizar sucursal")
            print("  4. Eliminar sucursal")
            print("  0. Volver")
            op = input("  Opción: ").strip()
            if op == "0":
                break
            elif op == "1":
                n = input("  Nombre: ").strip()
                c = input("  Ciudad: ").strip()
                d = input("  Dirección: ").strip()
                self.mgr.crear(n, c, d)
            elif op == "2":
                self.mgr.leer()
            elif op == "3":
                raw = input("  ID sucursal: ").strip()
                if not raw.isdigit():
                    print("  ⚠️  Número inválido.")
                    continue
                nc = input("  Nueva ciudad: ").strip()
                nd = input("  Nueva dirección: ").strip()
                self.mgr.actualizar(int(raw), nc, nd)
            elif op == "4":
                raw = input("  ID a eliminar: ").strip()
                if not raw.isdigit():
                    print("  ⚠️  Número inválido.")
                    continue
                self.mgr.eliminar(int(raw))
            else:
                print("  ⚠️  Opción inválida.")
