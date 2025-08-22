import pandas as pd
import random
from faker import Faker
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

fake = Faker("es_CO")

# Diccionario de opciones extendidas
opciones = {
    "Productos": ["Café", "Té", "Pan", "Leche", "Queso", "Arepa", "Chocolate", "Yogurt", "Mantequilla", "Galletas"],
    "Ciudades": ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena",
                 "Bucaramanga", "Pereira", "Santa Marta", "Cúcuta", "Manizales",
                 "Neiva", "Villavicencio", "Armenia", "Ibagué", "Popayán",
                 "Montería", "Sincelejo", "Riohacha", "Quibdó", "Tunja"],
    "Departamentos": ["Ventas", "TI", "Recursos Humanos", "Logística", "Marketing", "Finanzas", "Producción"],
    "Rutas": ["Ruta A", "Ruta B", "Ruta C", "Ruta D", "Ruta E", "Ruta F", "Ruta G"],
    "Géneros": ["Novela", "Ciencia Ficción", "Historia", "Infantil", "Fantasía", "Poesía", "Ensayo", "Drama"],
    "Autores": ["Gabo", "Orwell", "Rowling", "Cervantes", "Huxley", "Tolstoi", "Shakespeare", "Borges"]
}

# Configuración de categorías
config = {
    "Ventas": {
        "columns": ["Fecha", "Producto", "Cantidad", "Precio_unitario"],
        "requires": ["Productos"],
        "generator": lambda choices: [
            fake.date_between(start_date="-30d", end_date="today"),
            random.choice(choices["Productos"]),
            random.randint(1, 10),
            random.randint(1000, 5000)
        ]
    },
    "Biblioteca": {
        "columns": ["Usuario", "Género", "Autor", "Días_prestamo"],
        "requires": ["Géneros", "Autores"],
        "generator": lambda choices: [
            fake.first_name(),
            random.choice(choices["Géneros"]),
            random.choice(choices["Autores"]),
            random.randint(2, 14)
        ]
    },
    "Clientes": {
        "columns": ["Nombre", "Ciudad", "Edad", "Email"],
        "requires": ["Ciudades"],
        "generator": lambda choices: [
            fake.name(),
            random.choice(choices["Ciudades"]),
            random.randint(18, 65),
            fake.email()
        ]
    },
    "Inventario": {
        "columns": ["Producto", "Categoría", "Stock", "Precio"],
        "requires": [],  # fijo
        "generator": lambda choices: [
            fake.word(),
            random.choice(["Bebidas", "Aseo", "Alimentos", "Tecnología"]),
            random.randint(0, 100),
            random.randint(1000, 50000)
        ]
    },
    "Empleados": {
        "columns": ["Nombre", "Departamento", "Salario", "Años_empresa", "Estado"],
        "requires": ["Departamentos"],
        "generator": lambda choices: [
            fake.name(),
            random.choice(choices["Departamentos"]),
            random.randint(1000000, 6000000),
            random.randint(1, 20),
            random.choice(["Activo", "Inactivo"])
        ]
    },
    "Viajes": {
        "columns": ["Fecha", "Ruta", "Pasajeros", "Tarifa"],
        "requires": ["Rutas"],
        "generator": lambda choices: [
            fake.date_between(start_date="-15d", end_date="today"),
            random.choice(choices["Rutas"]),
            random.randint(5, 50),
            random.randint(2000, 8000)
        ]
    }
}

# === Función para generar datos ===
def generar_datos():
    categoria = combo_categoria.get()
    cantidad = entry_cantidad.get()

    if not categoria or not cantidad.isdigit():
        messagebox.showerror("Error", "Debes seleccionar una categoría y una cantidad válida.")
        return

    cantidad = int(cantidad)

    # Preparar subconjuntos dinámicos solo para los requeridos
    choices = {}
    for key in config[categoria]["requires"]:
        num = int(spinboxes[key].get())
        if num < 3 or num > 20:
            messagebox.showerror("Error", f"{key} debe estar entre 3 y 20.")
            return
        choices[key] = opciones[key][:num]

    # Determinar columnas activas
    active_cols = [col for col, var in checkboxes_vars.items() if var.get() == 1]
    if not active_cols:
        messagebox.showerror("Error", "Debes seleccionar al menos una columna.")
        return

    # Generar registros
    data = []
    for _ in range(cantidad):
        row = config[categoria]["generator"](choices)
        row_dict = dict(zip(config[categoria]["columns"], row))
        data.append([row_dict[col] for col in active_cols])

    df = pd.DataFrame(data, columns=active_cols)

    # Guardar archivo CSV
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile=f"{categoria.lower()}.csv"
    )
    if file_path:
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Éxito", f"✅ Archivo generado correctamente:\n{file_path}")


# === Función para actualizar dinámicamente las columnas y opciones ===
def actualizar_todo(event=None):
    categoria = combo_categoria.get()

    # Actualizar columnas
    for widget in frame_cols.winfo_children():
        widget.destroy()
    global checkboxes_vars
    checkboxes_vars = {}
    if categoria:
        tk.Label(frame_cols, text=f"Columnas disponibles para {categoria}:", font=("Arial", 11, "bold")).pack()
        for col in config[categoria]["columns"]:
            var = tk.IntVar(value=1)
            chk = tk.Checkbutton(frame_cols, text=col, variable=var)
            chk.pack(anchor="w")
            checkboxes_vars[col] = var

    # Actualizar spinboxes
    for widget in frame_opts.winfo_children():
        widget.destroy()
    spinboxes.clear()
    if categoria:
        for key in config[categoria]["requires"]:
            row = tk.Frame(frame_opts)
            row.pack(pady=2, anchor="w")
            tk.Label(row, text=f"{key} (3-20):", width=15).pack(side="left")
            spin = tk.Spinbox(row, from_=3, to=20, width=5)
            spin.delete(0, "end")
            spin.insert(0, min(5, len(opciones[key])))
            spin.pack(side="left")
            spinboxes[key] = spin


# === Interfaz Tkinter ===
root = tk.Tk()
root.title("Generador de Datos Falsos")
root.geometry("550x700")
root.resizable(False, False)

# Categoría
tk.Label(root, text="Selecciona la categoría:", font=("Arial", 11)).pack(pady=5)
combo_categoria = ttk.Combobox(root, values=list(config.keys()), state="readonly", width=40)
combo_categoria.bind("<<ComboboxSelected>>", actualizar_todo)
combo_categoria.pack(pady=5)

# Cantidad
tk.Label(root, text="Cantidad de registros:", font=("Arial", 11)).pack(pady=5)
entry_cantidad = tk.Entry(root, width=10)
entry_cantidad.insert(0, "50")
entry_cantidad.pack(pady=5)

# Opciones dinámicas
tk.Label(root, text="Configura las opciones dinámicas:", font=("Arial", 11, "bold")).pack(pady=10)
frame_opts = tk.Frame(root)
frame_opts.pack()

spinboxes = {}

# Selección de columnas
frame_cols = tk.Frame(root)
frame_cols.pack(pady=15)

# Botón
btn_generar = tk.Button(root, text="Generar CSV", command=generar_datos, bg="#4CAF50", fg="white", font=("Arial", 12))
btn_generar.pack(pady=20)

root.mainloop()
