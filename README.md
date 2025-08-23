# Generador Avanzado de Datos Sintéticos 🧪📊

Este proyecto permite generar **datasets sintéticos, realistas y con datos sucios opcionales** para practicar **análisis de datos** en distintos escenarios.  
Ofrece una interfaz gráfica moderna basada en `ttkbootstrap`, con soporte multi-categoría, selección dinámica de columnas, internacionalización y exportación a múltiples formatos.

---

## 🚀 Características principales

- **Interfaz moderna** con `ttkbootstrap` (sobre `tkinter`).
- **Internacionalización**: genera datos en distintos idiomas (`es_CO`, `en_US`, `fr_FR`, `de_DE`, `pt_BR`, ...).
- **Selección dinámica**:
  - Categorías disponibles:  
    - 📦 Inventario  
    - 👥 Clientes  
    - 🧑‍💼 Empleados  
    - 📚 Biblioteca  
    - 🛒 Ventas  
    - 🚌 Viajes  
  - Selección personalizada de columnas por categoría.  
  - Subconjuntos configurables de opciones (ej: número de ciudades, productos, autores, etc).  
- **Generación de datos sucios (opcionales)**:
  - Valores nulos/faltantes.
  - Registros duplicados.
  - Texto con ruido / emails inválidos.
  - Outliers numéricos.
  - Tipos erróneos en columnas numéricas.
- **Formatos de exportación**:
  - CSV (uno por categoría o múltiple).
  - Excel (`.xlsx`) con varias hojas (una por categoría).
  - JSON estructurado.
  - SQL (SQLite con tablas por categoría).
- **Historial de exportaciones**:
  - Guarda las últimas 5 exportaciones realizadas.
  - Opción de abrir la carpeta del archivo directamente.

---

## 📦 Requisitos

Dependencias principales:

- `pandas`
- `faker`
- `ttkbootstrap`
- `xlsxwriter`

Instalar con:

```bash
pip install -r requirements.txt
```

En **Ubuntu/Debian** puede que necesites instalar `tkinter` manualmente:
```bash
sudo apt-get install python3-tk
```

---

## ⚙️ Uso

Ejecuta el script principal:

```bash
python generador_datos_avanzado.py
```

Se abrirá una ventana donde podrás:

1. Seleccionar el idioma de los datos.  
2. Definir cuántos registros generar.  
3. Escoger una o varias categorías (Clientes, Ventas, etc).  
4. Seleccionar las columnas que deseas incluir.  
5. Configurar subconjuntos de opciones (ej: 5 ciudades, 10 productos).  
6. (Opcional) Activar **datos sucios** y su porcentaje.  
7. Elegir el formato de exportación (CSV, Excel, JSON o SQL).  
8. Guardar el archivo en tu computadora.  

---

## 📂 Estructura del Proyecto

```bash
.
├── main.py                       # Script principal con la interfaz gráfica
├── requirements.txt              # Dependencias necesarias
└── README.md                     # Documentación del proyecto
```

---

## 📝 Ejemplo de Exportación

**Excel con múltiples hojas** (Clientes y Ventas seleccionados):  

- Hoja `Clientes`:
```
Nombre, Ciudad, Edad, Email
Juan Pérez, Bogotá, 34, juanperez@mail.com
María Gómez, Medellín, 29, mariagomez@mail.com
```

- Hoja `Ventas`:
```
Fecha, Producto, Cantidad, Precio_unitario
2025-08-10, Café, 5, 3500
2025-08-12, Pan, 2, 1200
```

---

Proyecto desarrollado como herramienta de práctica para **análisis, limpieza y transformación de datos**.