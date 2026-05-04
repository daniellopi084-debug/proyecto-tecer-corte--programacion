# ============================================================
# compras.py — Módulo CRUD de Compras y Lealtad
# Proyecto: Fideliza-Puntos (Reto Mercadeo)
# ============================================================

import sqlite3
import os
import pandas as pd
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME  = os.path.join(BASE_DIR, "fideliza_puntos.db")


# ── CLASE PADRE ──────────────────────────────────────────────
class TransaccionBase:
    """Clase padre: encapsula los datos básicos de una transacción."""
    def __init__(self, id_cliente: int, id_sucursal: int, valor_total: float):
        self._id_cliente   = id_cliente
        self._id_sucursal  = id_sucursal
        self.__valor_total = valor_total

    def get_valor_total(self) -> float:
        return self.__valor_total

    def set_valor_total(self, nuevo: float):
        if nuevo <= 0:
            raise ValueError("El valor total debe ser mayor que cero.")
        self.__valor_total = nuevo

    def __str__(self):
        return f"Transacción | Cliente {self._id_cliente} | Sucursal {self._id_sucursal} | ${self.__valor_total:,.0f}"


# ── CLASE HIJO ───────────────────────────────────────────────
class Compra(TransaccionBase):
    """Clase hijo: agrega fecha y calcula puntos de lealtad."""
    PUNTOS_POR_MIL = 10   # 10 puntos por cada $1,000

    def __init__(self, id_cliente: int, id_sucursal: int, valor_total: float, fecha: str = None):
        super().__init__(id_cliente, id_sucursal, valor_total)
        self.__fecha = fecha or str(date.today())

    def get_fecha(self) -> str:
        return self.__fecha

    def calcular_puntos(self) -> int:
        return int(self.get_valor_total() / 1000) * self.PUNTOS_POR_MIL

    def __str__(self):
        return (f"[Compra] Cliente {self._id_cliente} | Sucursal {self._id_sucursal} "
                f"| ${self.get_valor_total():,.0f} | Fecha: {self.__fecha} "
                f"| Puntos ganados: {self.calcular_puntos()}")


# ── MOTOR DE LEALTAD ─────────────────────────────────────────
class MotorLealtad:
    """Calcula categoría y bono según compras acumuladas."""

    CATEGORIAS = [
        ("Bronce", 0,        499_999,   0.02),
        ("Plata",  500_000,  1_499_999, 0.05),
        ("Oro",    1_500_000, float("inf"), 0.10),
    ]

    @staticmethod
    def categoria_por_total(total: float) -> tuple:
        for nombre, minimo, maximo, porcentaje in MotorLealtad.CATEGORIAS:
            if minimo <= total <= maximo:
                return nombre, porcentaje
        return "Sin categoría", 0.0

    @staticmethod
    def calcular_bono(total: float) -> float:
        _, pct = MotorLealtad.categoria_por_total(total)
        return round(total * pct, 2)

    @staticmethod
    def reporte_clientes():
        """JOIN: clientes + compras + sucursales con categoría."""
        try:
            conn = sqlite3.connect(DB_NAME)
            query = """
                SELECT
                    c.id_cliente,
                    c.nombre          AS Cliente,
                    c.tipo            AS Tipo,
                    s.nombre          AS Sucursal,
                    SUM(co.valor_total) AS Total_Compras,
                    COUNT(co.id_compra) AS Num_Compras
                FROM clientes c
                LEFT JOIN compras co ON c.id_cliente = co.id_cliente
                LEFT JOIN sucursales s ON co.id_sucursal = s.id_sucursal
                GROUP BY c.id_cliente, c.nombre, c.tipo, s.nombre
                ORDER BY Total_Compras DESC
            """
            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                print("  ℹ️  No hay datos suficientes.")
                return

            df["Total_Compras"] = df["Total_Compras"].fillna(0)
            df["Categoria"] = df["Total_Compras"].apply(
                lambda t: MotorLealtad.categoria_por_total(t)[0]
            )
            df["Bono_Regalo"] = df["Total_Compras"].apply(MotorLealtad.calcular_bono)
            df["Bono_Regalo"] = df["Bono_Regalo"].apply(lambda x: f"${x:,.0f}")
            df["Total_Compras"] = df["Total_Compras"].apply(lambda x: f"${x:,.0f}")
            print("\n" + df.to_string(index=False))

            # Alerta para clientes Oro
            conn2 = sqlite3.connect(DB_NAME)
            df2 = pd.read_sql_query(
                "SELECT id_cliente, SUM(valor_total) as total FROM compras GROUP BY id_cliente",
                conn2
            )
            conn2.close()
            oros = df2[df2["total"] >= 1_500_000]
            if not oros.empty:
                print(f"\n  🏆 ¡{len(oros)} cliente(s) con categoría ORO reciben bono del 10%!")
        except Exception as e:
            print(f"  🔥 Error en reporte: {e}")


# ── MANAGER (CRUD) ───────────────────────────────────────────
class CompraManager:

    def crear(self, id_cliente: int, id_sucursal: int, valor_total: float):
        try:
            comp = Compra(id_cliente, id_sucursal, valor_total)
            conn = sqlite3.connect(DB_NAME)
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO compras (id_cliente, id_sucursal, valor_total, fecha) VALUES (?,?,?,?)",
                (comp._id_cliente, comp._id_sucursal, comp.get_valor_total(), comp.get_fecha())
            )
            conn.commit()
            print(f"  ✅ Compra registrada. Puntos ganados: {comp.calcular_puntos()}")
            cat, pct = MotorLealtad.categoria_por_total(comp.get_valor_total())
            print(f"     Categoría esta compra: {cat} | Bono: ${comp.get_valor_total()*pct:,.0f}")
        except ValueError as ve:
            print(f"  ⚠️  Validación: {ve}")
        except sqlite3.IntegrityError:
            print("  ❌ Error: Cliente o Sucursal no existe.")
        except Exception as e:
            print(f"  🔥 Error inesperado: {e}")
        finally:
            conn.close()

    def leer(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            df = pd.read_sql_query("SELECT * FROM compras ORDER BY id_compra", conn)
            conn.close()
            if df.empty:
                print("  ℹ️  No hay compras.")
            else:
                print(df.to_string(index=False))
        except Exception as e:
            print(f"  🔥 Error: {e}")

    def actualizar(self, id_compra: int, nuevo_valor: float):
        try:
            if nuevo_valor <= 0:
                raise ValueError("El valor debe ser positivo.")
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("UPDATE compras SET valor_total=? WHERE id_compra=?", (nuevo_valor, id_compra))
            if cur.rowcount == 0:
                print(f"  ⚠️  No existe compra con ID {id_compra}.")
            else:
                print(f"  ✅ Compra {id_compra} actualizada a ${nuevo_valor:,.0f}.")
            conn.commit()
        except ValueError as ve:
            print(f"  ⚠️  {ve}")
        except Exception as e:
            print(f"  🔥 Error: {e}")
        finally:
            conn.close()

    def eliminar(self, id_compra: int):
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("DELETE FROM compras WHERE id_compra=?", (id_compra,))
            if cur.rowcount == 0:
                print(f"  ⚠️  No existe compra con ID {id_compra}.")
            else:
                print(f"  ✅ Compra {id_compra} eliminada.")
            conn.commit()
        except Exception as e:
            print(f"  🔥 Error: {e}")
        finally:
            conn.close()


# ── MENÚ INTERACTIVO ─────────────────────────────────────────
class CompraInteractivo:
    def __init__(self):
        self.mgr = CompraManager()

    def menu(self):
        while True:
            print("\n  ── GESTIÓN DE COMPRAS Y LEALTAD ──")
            print("  1. Registrar compra")
            print("  2. Ver todas las compras")
            print("  3. Actualizar valor de compra")
            print("  4. Eliminar compra")
            print("  5. 🏆 Reporte de lealtad y bonos")
            print("  0. Volver")
            op = input("  Opción: ").strip()
            if op == "0":
                break
            elif op == "1":
                ri = input("  ID cliente: ").strip()
                rs = input("  ID sucursal: ").strip()
                rv = input("  Valor total de la compra ($): ").strip()
                if not ri.isdigit() or not rs.isdigit():
                    print("  ⚠️  IDs deben ser números.")
                    continue
                try:
                    valor = float(rv.replace(",", "").replace(".", ""))
                except ValueError:
                    print("  ⚠️  Valor inválido.")
                    continue
                self.mgr.crear(int(ri), int(rs), valor)
            elif op == "2":
                self.mgr.leer()
            elif op == "3":
                ri = input("  ID compra: ").strip()
                rv = input("  Nuevo valor ($): ").strip()
                if not ri.isdigit():
                    print("  ⚠️  ID inválido.")
                    continue
                try:
                    valor = float(rv.replace(",", ""))
                except ValueError:
                    print("  ⚠️  Valor inválido.")
                    continue
                self.mgr.actualizar(int(ri), valor)
            elif op == "4":
                ri = input("  ID compra a eliminar: ").strip()
                if not ri.isdigit():
                    print("  ⚠️  ID inválido.")
                    continue
                self.mgr.eliminar(int(ri))
            elif op == "5":
                MotorLealtad.reporte_clientes()
            else:
                print("  ⚠️  Opción inválida.")
