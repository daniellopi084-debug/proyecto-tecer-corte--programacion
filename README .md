# 🛍️ Fideliza-Puntos — Sistema de Lealtad para Retail
**Proyecto Corte 3 — Arquitectura End-to-End (Backend → Power BI)**

---

## 👥 Integrantes del Grupo

| Nombre | Correo | Rol |
|---|---|---|
| Juan José Caballero Mantilla | juancabma@unisabana.edu.co | Backend Lead |
| Martín Trujillo Rodríguez | martintr@unisabana.edu.co | DB Architect |
| Daniel Piraquive López | danielpi@unisabana.edu.co | Analytics Lead |

**Profesor:** Diego Mauricio Zuluaga Rodríguez  
**Clase:** Programación y Decisiones — Universidad de La Sabana  
**Reto seleccionado:** 🛍️ Reto 4 — MERCADEO "Fideliza-Puntos"

---

## 🎯 Descripción del Proyecto

Sistema de gestión de lealtad para una cadena de tiendas de ropa. Permite registrar compras acumuladas de clientes, asignar categorías (Bronce, Plata, Oro) y otorgar bonos automáticos del 10% a clientes Oro. Conectado a Power BI para analítica en tiempo real.

---

## 🏗️ Arquitectura del Sistema

```
FidelizaPuntos_Corte3/
├── datos.py              ← Semilla de datos iniciales (CSV en strings)
├── clientes.py           ← POO + CRUD: PersonaBase → Cliente
├── sucursales.py         ← POO + CRUD: LugarBase → Sucursal
├── compras.py            ← POO + CRUD + Lealtad: TransaccionBase → Compra
├── categorias.py         ← POO + CRUD: NivelBase → CategoriaLealtad
├── main.py               ← Orquestador: importa todo, crea BD con os, menú interactivo
├── power_bi.py           ← Script ETL para conectar a Power BI Desktop
├── fideliza_puntos.db    ← Base de datos SQLite (generada automáticamente)
└── design/
    ├── diagrama_clases.pdf   ← UML: Herencia, Encapsulamiento, get/set
    └── modelo_erd.pdf        ← Modelo Entidad-Relación (Esquema Estrella)
```

---

## 🧬 Arquitectura POO (Rúbrica cumplida)

### Clases Padre (3 requeridas → 4 implementadas)
| Clase Padre | Archivo | Encapsulamiento |
|---|---|---|
| `PersonaBase` | clientes.py | `_nombre`, `__correo` con get/set |
| `LugarBase` | sucursales.py | `_nombre`, `_ciudad` con get/set |
| `TransaccionBase` | compras.py | `__valor_total` privado con get/set |
| `NivelBase` | categorias.py | `_nombre` protegido con get/set |

### Clases Hijo (3 requeridas → 4 implementadas)
| Clase Hijo | Padre | Polimorfismo |
|---|---|---|
| `Cliente` | PersonaBase | `__tipo` privado + `__str__` propio |
| `Sucursal` | LugarBase | `__direccion` privado + `__str__` propio |
| `Compra` | TransaccionBase | `calcular_puntos()` + `__str__` propio |
| `CategoriaLealtad` | NivelBase | `__porcentaje_bono` privado + `__str__` propio |

---

## 🗄️ Base de Datos SQLite (Esquema Estrella)

```sql
clientes     (id_cliente PK, nombre, correo UNIQUE, ciudad, tipo)
sucursales   (id_sucursal PK, nombre, ciudad, direccion)
categorias_lealtad (id_categoria PK, nombre, min_compra, max_compra, porcentaje_bono)
compras      (id_compra PK, id_cliente FK, id_sucursal FK, valor_total, fecha)
```

- **Tabla de Hechos:** `compras` (centro del esquema estrella)
- **Dimensiones:** `clientes`, `sucursales`, `categorias_lealtad`
- **Integridad referencial:** `PRAGMA foreign_keys = ON`
- **Registros por tabla:** mínimo 5 por tabla ✅

---

## 🛒 CRUD + Operaciones de Lealtad

Cada módulo implementa las 4 operaciones obligatorias:
- **CREATE** → Registrar nuevo registro con validación
- **READ** → Listar todos los registros con Pandas
- **UPDATE** → Modificar campo específico
- **DELETE** → Eliminar por ID

**Lógica de Lealtad (MotorLealtad):**
```python
Bronce: compras < $500,000     → bono 2%
Plata:  $500,000 - $1,499,999  → bono 5%
Oro:    ≥ $1,500,000           → bono 10% 🏆
```

---

## 🛡️ Robustez (try-except)

Todos los métodos CRUD incluyen:
```python
try:
    # Validación de tipo: .isdigit(), float(), @
    # INSERT / UPDATE / DELETE en SQLite
except ValueError as ve:
    print(f"⚠️  Validación: {ve}")
except sqlite3.IntegrityError:
    print("❌ FK no existe")
except Exception as e:
    print(f"🔥 Error: {e}")
finally:
    conn.close()
```

---

## 📊 Power BI — Conexión End-to-End

1. Abrir Power BI Desktop → **Obtener datos → Script de Python**
2. Pegar el contenido de `power_bi.py`
3. Cargar las 4 tablas: `df_clientes`, `df_sucursales`, `df_compras`, `df_categorias`
4. En la pestaña **Modelo**, conectar `id_cliente` y `id_sucursal` (relación 1:N)

**Gráficas sugeridas:**
- Ventas totales por sucursal (barras)
- Distribución de categorías de lealtad (pastel)
- Evolución de compras por fecha (línea)
- Top clientes por valor acumulado (tabla)

---

## ▶️ Cómo Ejecutar

```bash
# 1. Ir a la carpeta del proyecto
cd ruta/al/proyecto

# 2. Ejecutar el orquestador
python main.py
```

La base de datos `fideliza_puntos.db` se crea automáticamente con datos iniciales.

---

> *"El éxito de la inteligencia de negocios no radica en hacer gráficas bonitas, sino en estructurar bases de datos robustas que las respalden."*  
> — Prof. Diego Zuluaga
