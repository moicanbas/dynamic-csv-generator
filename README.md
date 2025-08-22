# Generador Dinámico de CSV con Datos Aleatorios

Este proyecto permite generar archivos CSV con datos aleatorios de manera **dinámica y configurable**.  
El objetivo es practicar análisis de datos con distintos escenarios, controlando categorías, cantidad de registros y opciones de cada campo.

---

## 🚀 Características

- Interfaz gráfica simple (usando `tkinter`).
- Configuración dinámica de:
  - Cantidad de registros.
  - Categorías de datos (ej: ciudades, productos, nombres, correos, etc).
  - Opciones disponibles para cada categoría (mínimo 3, máximo 20).
- Uso de la librería `faker` para datos realistas (nombres, correos, direcciones, fechas).
- Exportación de resultados en formato **CSV**.

---

## 📦 Requisitos

El proyecto depende de:

- `pandas`
- `faker`
- `tkinter` (viene incluido con Python, en Linux puede requerir instalación extra)

Instalar dependencias con:

```bash
pip install -r requirements.txt
```

En **Ubuntu/Debian** puede que necesites instalar `tkinter` manualmente:
```bash
sudo apt-get install python3-tk
```

## ⚙️ Uso

Ejecuta el script principal:
```bash
python generador_csv.py
```
Se abrirá una ventana donde podrás:

1. Seleccionar cuántos registros generar.

2. Escoger la categoría de datos (ejemplo: "Ciudades").

3. Definir cuántas opciones incluir (ejemplo: 3 → Bogotá, Medellín, Cali).

4. Generar el archivo datos_generados.csv automáticamente.


## 📂 Estructura del Proyecto
```bash
.
├── main.py                # Script principal con la interfaz gráfica
├── requirements.txt       # Dependencias necesarias
└── README.md              # Documentación del proyecto
```

## 📝 Ejemplo de Uso

- Categoría: Ciudades

- Opciones: 3

- Registros: 10

El archivo generado (datos_generados.csv) puede verse así:
```
id,ciudad
1,Bogotá
2,Cali
3,Medellín
4,Bogotá
5,Cali
6,Medellín
7,Cali
8,Bogotá
9,Bogotá
10,Medellín
```

Proyecto desarrollado como material de práctica en análisis de datos y generación de datasets sintéticos.
