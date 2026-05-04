# ============================================================
# main.py — Orquestador Principal
# Proyecto: Fideliza-Puntos (Reto Mercadeo)
# Grupo: Juan José Caballero, Martín Trujillo, Daniel Piraquive
# Clase: Programación y Decisiones — Prof. Diego Zuluaga
# Universidad de La Sabana — Corte 3
# ============================================================

import os
import sqlite3

# ── RUTA DINÁMICA (librería os) ──────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME  = os.path.join(BASE_DIR, "fideliza_puntos.db")

# ── IMPORTAR MÓDULOS ─────────────────────────────────────────
from clientes    import ClienteManager, ClienteDataCleaner, ClienteInteractivo
from sucursales  import SucursalManager, SucursalInteractivo
from compras     import CompraManager, MotorLealtad, CompraInteractivo
from categorias  import CategoriaManager, CategoriaInteractivo
from datos       import (CLIENTES_INICIALES, SUCURSALES_INICIALES,
                          CATEGORIAS_LEALTAD, COMPRAS_INICIALES)


# ── CREAR BASE DE DATOS ──────────────────────────────────────
def crear_base_datos():
    """Crea las tablas si no existen y carga datos semilla."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Tabla: clientes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente  INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT    NOT NULL,
            correo      TEXT    UNIQUE NOT NULL,
            ciudad      TEXT    NOT NULL,
            tipo        TEXT    NOT NULL DEFAULT 'Regular'
        )
    """)

    # Tabla: sucursales
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sucursales (
            id_sucursal INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            ciudad      TEXT NOT NULL,
            direccion   TEXT NOT NULL
        )
    """)

    # Tabla: categorias_lealtad
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias_lealtad (
            id_categoria    INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre          TEXT    NOT NULL,
            min_compra      REAL    NOT NULL,
            max_compra      REAL    NOT NULL,
            porcentaje_bono REAL    NOT NULL
        )
    """)

    # Tabla: compras  (tabla de hechos — FK a clientes y sucursales)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id_compra   INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente  INTEGER NOT NULL,
            id_sucursal INTEGER NOT NULL,
            valor_total REAL    NOT NULL,
            fecha       TEXT    NOT NULL,
            FOREIGN KEY (id_cliente)  REFERENCES clientes(id_cliente),
            FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal)
        )
    """)

    conn.commit()

    # ── Cargar semilla sólo si las tablas están vacías ───────
    cur.execute("SELECT COUNT(*) FROM clientes")
    if cur.fetchone()[0] == 0:
        for linea in CLIENTES_INICIALES.strip().splitlines():
            id_, nombre, correo, ciudad, tipo = linea.split(",")
            cur.execute(
                "INSERT OR IGNORE INTO clientes VALUES (?,?,?,?,?)",
                (int(id_), nombre, correo, ciudad, tipo)
            )

    cur.execute("SELECT COUNT(*) FROM sucursales")
    if cur.fetchone()[0] == 0:
        for linea in SUCURSALES_INICIALES.strip().splitlines():
            parts = linea.split(",")
            cur.execute(
                "INSERT OR IGNORE INTO sucursales VALUES (?,?,?,?)",
                (int(parts[0]), parts[1], parts[2], parts[3])
            )

    cur.execute("SELECT COUNT(*) FROM categorias_lealtad")
    if cur.fetchone()[0] == 0:
        for linea in CATEGORIAS_LEALTAD.strip().splitlines():
            id_, nombre, mn, mx, pct = linea.split(",")
            cur.execute(
                "INSERT OR IGNORE INTO categorias_lealtad VALUES (?,?,?,?,?)",
                (int(id_), nombre, float(mn), float(mx), float(pct))
            )

    cur.execute("SELECT COUNT(*) FROM compras")
    if cur.fetchone()[0] == 0:
        for linea in COMPRAS_INICIALES.strip().splitlines():
            id_, id_c, id_s, valor, fecha = linea.split(",")
            cur.execute(
                "INSERT OR IGNORE INTO compras VALUES (?,?,?,?,?)",
                (int(id_), int(id_c), int(id_s), float(valor), fecha)
            )

    conn.commit()
    conn.close()
    print("✅ Base de datos lista. Datos iniciales preservados.")


# ── MENÚ PRINCIPAL ───────────────────────────────────────────
def menu_principal():
    cli_menu  = ClienteInteractivo()
    suc_menu  = SucursalInteractivo()
    comp_menu = CompraInteractivo()
    cat_menu  = CategoriaInteractivo()

    while True:
        print("\n" + "═"*50)
        print("  🛍️  FIDELIZA-PUNTOS — Gestión de Lealtad")
        print("  Grupo: Caballero · Trujillo · Piraquive")
        print("═"*50)
        print("  1. 👤 Clientes")
        print("  2. 🏪 Sucursales")
        print("  3. 🛒 Compras y Lealtad")
        print("  4. ⭐ Categorías de Lealtad")
        print("  5. 📊 Reporte General de Clientes")
        print("  0. Salir")
        print("─"*50)
        op = input("  Seleccione módulo: ").strip()

        if op == "0":
            print("\n  👋 ¡Hasta pronto! — Fideliza-Puntos")
            break
        elif op == "1":
            cli_menu.menu()
        elif op == "2":
            suc_menu.menu()
        elif op == "3":
            comp_menu.menu()
        elif op == "4":
            cat_menu.menu()
        elif op == "5":
            MotorLealtad.reporte_clientes()
        else:
            print("  ⚠️  Opción inválida. Intente de nuevo.")


# ── PUNTO DE ENTRADA ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n⚙️  Iniciando Fideliza-Puntos...")
    crear_base_datos()
    menu_principal()
