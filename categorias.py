# ============================================================
# categorias.py — Módulo CRUD de Categorías de Lealtad
# Proyecto: Fideliza-Puntos (Reto Mercadeo)
# ============================================================

import sqlite3
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME  = os.path.join(BASE_DIR, "fideliza_puntos.db")


# ── CLASE PADRE ──────────────────────────────────────────────
class NivelBase:
    """Clase padre: encapsula datos de un nivel de lealtad."""
    def __init__(self, nombre: str):
        self._nombre = nombre

    def get_nombre(self) -> str:
        return self._nombre

    def set_nombre(self, nuevo: str):
        if not nuevo.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = nuevo.strip().title()

    def __str__(self):
        return f"Nivel: {self._nombre}"


# ── CLASE HIJO ───────────────────────────────────────────────
class CategoriaLealtad(NivelBase):
    """Clase hijo: agrega umbrales y porcentaje de bono."""
    def __init__(self, nombre: str, min_compra: float, max_compra: float, porcentaje_bono: float):
        super().__init__(nombre)
        self.__min_compra      = min_compra
        self.__max_compra      = max_compra
        self.__porcentaje_bono = porcentaje_bono

    def get_min(self) -> float:
        return self.__min_compra

    def get_max(self) -> float:
        return self.__max_compra

    def get_porcentaje(self) -> float:
        return self.__porcentaje_bono

    def set_porcentaje(self, nuevo: float):
        if not (0 < nuevo < 1):
            raise ValueError("El porcentaje debe estar entre 0 y 1 (ej: 0.10 = 10%).")
        self.__porcentaje_bono = nuevo

    def __str__(self):
        return (f"[Categoría] {self._nombre} | "
                f"Min: ${self.__min_compra:,.0f} | Max: ${self.__max_compra:,.0f} | "
                f"Bono: {self.__porcentaje_bono*100:.0f}%")


# ── MANAGER (CRUD) ───────────────────────────────────────────
class CategoriaManager:

    def crear(self, nombre: str, min_c: float, max_c: float, pct: float):
        try:
            cat = CategoriaLealtad(nombre, min_c, max_c, pct)
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO categorias_lealtad (nombre, min_compra, max_compra, porcentaje_bono) VALUES (?,?,?,?)",
                (cat.get_nombre(), cat.get_min(), cat.get_max(), cat.get_porcentaje())
            )
            conn.commit()
            print(f"  ✅ Categoría '{cat.get_nombre()}' creada.")
        except ValueError as ve:
            print(f"  ⚠️  {ve}")
        except Exception as e:
            print(f"  🔥 Error: {e}")
        finally:
            conn.close()

    def leer(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            df = pd.read_sql_query("SELECT * FROM categorias_lealtad ORDER BY min_compra", conn)
            conn.close()
            if df.empty:
                print("  ℹ️  No hay categorías.")
            else:
                print(df.to_string(index=False))
        except Exception as e:
            print(f"  🔥 Error: {e}")

    def actualizar(self, id_cat: int, nuevo_pct: float):
        try:
            if not (0 < nuevo_pct < 1):
                raise ValueError("Porcentaje debe estar entre 0 y 1.")
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("UPDATE categorias_lealtad SET porcentaje_bono=? WHERE id_categoria=?", (nuevo_pct, id_cat))
            if cur.rowcount == 0:
                print(f"  ⚠️  No existe categoría con ID {id_cat}.")
            else:
                print(f"  ✅ Categoría {id_cat} actualizada a {nuevo_pct*100:.0f}%.")
            conn.commit()
        except ValueError as ve:
            print(f"  ⚠️  {ve}")
        except Exception as e:
            print(f"  🔥 Error: {e}")
        finally:
            conn.close()

    def eliminar(self, id_cat: int):
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("DELETE FROM categorias_lealtad WHERE id_categoria=?", (id_cat,))
            if cur.rowcount == 0:
                print(f"  ⚠️  No existe categoría con ID {id_cat}.")
            else:
                print(f"  ✅ Categoría {id_cat} eliminada.")
            conn.commit()
        except Exception as e:
            print(f"  🔥 Error: {e}")
        finally:
            conn.close()


# ── MENÚ INTERACTIVO ─────────────────────────────────────────
class CategoriaInteractivo:
    def __init__(self):
        self.mgr = CategoriaManager()

    def menu(self):
        while True:
            print("\n  ── GESTIÓN DE CATEGORÍAS DE LEALTAD ──")
            print("  1. Crear categoría")
            print("  2. Ver categorías")
            print("  3. Actualizar porcentaje de bono")
            print("  4. Eliminar categoría")
            print("  0. Volver")
            op = input("  Opción: ").strip()
            if op == "0":
                break
            elif op == "1":
                n   = input("  Nombre (ej: Platino): ").strip()
                mn  = input("  Compra mínima ($): ").strip()
                mx  = input("  Compra máxima ($): ").strip()
                pct = input("  Porcentaje bono (ej: 0.08 = 8%): ").strip()
                try:
                    self.mgr.crear(n, float(mn), float(mx), float(pct))
                except ValueError:
                    print("  ⚠️  Ingrese números válidos.")
            elif op == "2":
                self.mgr.leer()
            elif op == "3":
                ri  = input("  ID categoría: ").strip()
                pct = input("  Nuevo porcentaje (ej: 0.12): ").strip()
                if not ri.isdigit():
                    print("  ⚠️  ID inválido.")
                    continue
                try:
                    self.mgr.actualizar(int(ri), float(pct))
                except ValueError:
                    print("  ⚠️  Porcentaje inválido.")
            elif op == "4":
                ri = input("  ID a eliminar: ").strip()
                if not ri.isdigit():
                    print("  ⚠️  ID inválido.")
                    continue
                self.mgr.eliminar(int(ri))
            else:
                print("  ⚠️  Opción inválida.")
