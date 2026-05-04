# ============================================================
# power_bi.py — Script de Extracción ETL para Power BI
# Proyecto: Fideliza-Puntos (Reto Mercadeo)
# ============================================================
# INSTRUCCIONES POWER BI:
#   1. Abrir Power BI Desktop → Obtener datos → Script de Python
#   2. Pegar este código completo
#   3. Cargar las 4 tablas: df_clientes, df_sucursales,
#      df_compras, df_categorias
# ============================================================

import sqlite3
import pandas as pd
import os

# Ruta dinámica — funciona en cualquier equipo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta_bd  = os.path.join(BASE_DIR, "fideliza_puntos.db")

conexion = sqlite3.connect(ruta_bd)

# ── Tablas base ──────────────────────────────────────────────
df_clientes   = pd.read_sql_query("SELECT * FROM clientes",          conexion)
df_sucursales = pd.read_sql_query("SELECT * FROM sucursales",         conexion)
df_compras    = pd.read_sql_query("SELECT * FROM compras",            conexion)
df_categorias = pd.read_sql_query("SELECT * FROM categorias_lealtad", conexion)

# ── Vista enriquecida con JOIN (para gráficas avanzadas) ─────
df_reporte = pd.read_sql_query("""
    SELECT
        c.nombre          AS Cliente,
        c.tipo            AS Tipo_Cliente,
        c.ciudad          AS Ciudad,
        s.nombre          AS Sucursal,
        s.ciudad          AS Ciudad_Sucursal,
        co.valor_total    AS Valor_Compra,
        co.fecha          AS Fecha,
        CASE
            WHEN SUM(co.valor_total) OVER (PARTITION BY c.id_cliente) >= 1500000 THEN 'Oro'
            WHEN SUM(co.valor_total) OVER (PARTITION BY c.id_cliente) >= 500000  THEN 'Plata'
            ELSE 'Bronce'
        END               AS Categoria_Lealtad
    FROM compras co
    JOIN clientes   c ON co.id_cliente  = c.id_cliente
    JOIN sucursales s ON co.id_sucursal = s.id_sucursal
    ORDER BY co.fecha DESC
""", conexion)

conexion.close()

print("✅ Datos cargados para Power BI:")
print(f"   Clientes:   {len(df_clientes)} registros")
print(f"   Sucursales: {len(df_sucursales)} registros")
print(f"   Compras:    {len(df_compras)} registros")
print(f"   Categorías: {len(df_categorias)} registros")
print(f"   Reporte:    {len(df_reporte)} registros")
