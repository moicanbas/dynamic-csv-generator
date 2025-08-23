import os
import sys
import json
import random
import sqlite3
import platform
from datetime import datetime
from pathlib import Path

import pandas as pd
from faker import Faker

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, Canvas, BOTH, RIGHT, LEFT, Y, X, BOTTOM, NW, HORIZONTAL, VERTICAL

# =========================
# Configuración de dominio
# =========================

IDIOMAS = {
    "Español (CO)": "es_CO",
    "Inglés (US)": "en_US",
    "Francés (FR)": "fr_FR",
    "Alemán (DE)": "de_DE",
    "Portugués (BR)": "pt_BR",
}

# Opciones globales
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

# Catálogo de categorías
config = {
    "Ventas": {
        "columns": ["Fecha", "Producto", "Cantidad", "Precio_unitario"],
        "requires": ["Productos"],
        "generator": lambda fake, choices: [
            fake.date_between(start_date="-30d", end_date="today"),
            random.choice(choices["Productos"]),
            random.randint(1, 10),
            random.randint(1000, 5000)
        ]
    },
    "Biblioteca": {
        "columns": ["Usuario", "Género", "Autor", "Días_prestamo", "Email"],
        "requires": ["Géneros", "Autores"],
        "generator": lambda fake, choices: [
            fake.first_name(),
            random.choice(choices["Géneros"]),
            random.choice(choices["Autores"]),
            random.randint(2, 14),
            fake.email()
        ]
    },
    "Clientes": {
        "columns": ["Nombre", "Ciudad", "Edad", "Email"],
        "requires": ["Ciudades"],
        "generator": lambda fake, choices: [
            fake.name(),
            random.choice(choices["Ciudades"]),
            random.randint(18, 65),
            fake.email()
        ]
    },
    "Inventario": {
        "columns": ["Producto", "Categoría", "Stock", "Precio"],
        "requires": [],
        "generator": lambda fake, choices: [
            random.choice(["Café", "Azúcar", "Leche", "Arroz", "Aceite", "Harina", "Chocolate"]),
            random.choice(["Bebidas", "Aseo", "Alimentos", "Tecnología"]),
            random.randint(0, 100),
            random.randint(1000, 50000)
        ]
    },
    "Empleados": {
        "columns": ["Nombre", "Departamento", "Salario", "Años_empresa", "Estado", "Email"],
        "requires": ["Departamentos"],
        "generator": lambda fake, choices: [
            fake.name(),
            random.choice(choices["Departamentos"]),
            random.randint(1_000_000, 6_000_000),
            random.randint(1, 20),
            random.choice(["Activo", "Inactivo"]),
            fake.company_email()
        ]
    },
    "Viajes": {
        "columns": ["Fecha", "Ruta", "Pasajeros", "Tarifa"],
        "requires": ["Rutas"],
        "generator": lambda fake, choices: [
            fake.date_between(start_date="-15d", end_date="today"),
            random.choice(choices["Rutas"]),
            random.randint(5, 50),
            random.randint(2000, 8000)
        ]
    }
}

# ===============
# Utilitarios
# ===============

def abrir_carpeta(path: str):
    if not path:
        return
    carpeta = Path(path).parent if Path(path).suffix else Path(path)
    try:
        if platform.system() == "Windows":
            os.startfile(carpeta)  # type: ignore
        elif platform.system() == "Darwin":
            os.system(f'open "{carpeta}"')
        else:
            os.system(f'xdg-open "{carpeta}"')
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{e}")

def asegurar_lista_unica(lst, n):
    """Devuelve los primeros n elementos (o todos si n>len) sin fallar."""
    return lst[:max(0, min(n, len(lst)))]

def aplicar_datos_sucios(df: pd.DataFrame, porcentaje: int,
                         habilitar_nulos=True,
                         habilitar_duplicados=True,
                         habilitar_ruido_texto=True,
                         habilitar_outliers=True,
                         habilitar_tipos_erroneos=True):
    if porcentaje <= 0 or df.empty:
        return df

    filas_afectadas = max(1, int(len(df) * porcentaje / 100))

    # 1) Nulos
    if habilitar_nulos:
        for _ in range(filas_afectadas):
            r = random.randrange(len(df))
            c = random.choice(df.columns)
            df.iat[r, df.columns.get_loc(c)] = None

    # 2) Duplicados (copiamos filas aleatorias encima de otras)
    if habilitar_duplicados and len(df) > 1:
        for _ in range(filas_afectadas // 3 + 1):
            src = df.sample(1).iloc[0]
            dst = random.randrange(len(df))
            df.loc[df.index[dst]] = src

    # 3) Ruido en texto (espacios, mayúsculas raras, caracteres)
    if habilitar_ruido_texto:
        text_cols = [c for c in df.columns if df[c].dtype == object]
        ruido_samples = max(1, filas_afectadas // 2)
        for _ in range(ruido_samples):
            if not text_cols:
                break
            c = random.choice(text_cols)
            r = random.randrange(len(df))
            val = df.at[df.index[r], c]
            if val is None:
                continue
            s = str(val)
            # Variantes de suciedad
            choice = random.choice(["spaces", "caps", "garbage", "email_break"])
            if choice == "spaces":
                s = "  " + s + "   "
            elif choice == "caps":
                s = s.swapcase()
            elif choice == "garbage":
                s = s + random.choice(["@@@", "***", "###"])
            elif choice == "email_break" and "email" in c.lower():
                s = s.replace("@", "")  # email inválido
            df.at[df.index[r], c] = s

    # 4) Outliers numéricos
    if habilitar_outliers:
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        out_samples = max(1, filas_afectadas // 2)
        for _ in range(out_samples):
            if not num_cols:
                break
            c = random.choice(num_cols)
            r = random.randrange(len(df))
            base = df.at[df.index[r], c]
            if pd.isna(base):
                continue
            factor = random.choice([10, 25, 50])
            df.at[df.index[r], c] = int(base) * factor

    # 5) Tipos erróneos en columnas numéricas
    if habilitar_tipos_erroneos:
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        err_samples = max(1, filas_afectadas // 3)
        for _ in range(err_samples):
            if not num_cols:
                break
            c = random.choice(num_cols)
            r = random.randrange(len(df))
            df.at[df.index[r], c] = "???"

    return df


# ===========================
# Clase principal de la app
# ===========================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador Avanzado de Datos para Análisis")
        self.root.geometry("920x720")
        self.fake = Faker("es_CO")

        # Estado
        self.historial = []  # lista de (fecha, ruta, formato, categorias)
        self.check_categorias = {}        # {categoria: IntVar}
        self.column_vars = {}             # {categoria: {col: IntVar}}
        self.requires_spin = {}           # {categoria: {require_key: Spinbox}}
        self.cantidad_var = tb.StringVar(value="200")
        self.formato_var = tb.StringVar(value="Excel")
        self.idioma_var = tb.StringVar(value="Español (CO)")
        self.datos_sucios_var = tb.BooleanVar(value=True)
        self.porc_sucios_var = tb.IntVar(value=10)
        self.chk_nulos = tb.BooleanVar(value=True)
        self.chk_dups = tb.BooleanVar(value=True)
        self.chk_ruido = tb.BooleanVar(value=True)
        self.chk_outliers = tb.BooleanVar(value=True)
        self.chk_tipos = tb.BooleanVar(value=True)
        self.ultima_ruta = ""

        self._construir_ui()

    # ------------- UI --------------

    def _construir_ui(self):
        # Top bar: Idioma, Cantidad, Formato
        top = tb.Frame(self.root)
        top.pack(fill=X, padx=12, pady=10)

        tb.Label(top, text="Idioma:", font=("", 10, "bold")).pack(side=LEFT, padx=(0, 6))
        self.combo_idioma = tb.Combobox(top, values=list(IDIOMAS.keys()),
                                        textvariable=self.idioma_var, width=18, state="readonly")
        self.combo_idioma.pack(side=LEFT, padx=(0, 10))

        tb.Label(top, text="Cantidad:", font=("", 10, "bold")).pack(side=LEFT, padx=(8, 6))
        tb.Entry(top, textvariable=self.cantidad_var, width=8).pack(side=LEFT)

        tb.Label(top, text="Exportar como:", font=("", 10, "bold")).pack(side=LEFT, padx=(16, 6))
        self.combo_formato = tb.Combobox(top, values=["CSV", "Excel", "JSON", "SQL"],
                                         textvariable=self.formato_var, width=10, state="readonly")
        self.combo_formato.pack(side=LEFT)

        tb.Button(top, text="Generar y Exportar", bootstyle=SUCCESS, command=self.generar_exportar).pack(side=RIGHT)
        tb.Button(top, text="Abrir carpeta", bootstyle=INFO, command=lambda: abrir_carpeta(self.ultima_ruta)).pack(side=RIGHT, padx=8)

        # Notebook
        nb = tb.Notebook(self.root)
        nb.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))

        # Tab 1: Selección dinámica
        self.tab_sel = tb.Frame(nb)
        nb.add(self.tab_sel, text="Selección y Columnas")

        # Tab 2: Opciones avanzadas
        self.tab_adv = tb.Frame(nb)
        nb.add(self.tab_adv, text="Datos Sucios & Reglas")

        # Tab 3: Historial
        self.tab_hist = tb.Frame(nb)
        nb.add(self.tab_hist, text="Historial")

        self._construir_tab_seleccion()
        self._construir_tab_avanzadas()
        self._construir_tab_historial()

    def _construir_tab_seleccion(self):
        wrapper = tb.Frame(self.tab_sel)
        wrapper.pack(fill=BOTH, expand=True)

        # Panel izquierdo: categorías
        left = tb.Labelframe(wrapper, text="Categorías", padding=10)
        left.pack(side=LEFT, fill=Y, padx=(0, 10), pady=10)

        # Scroll en categorías si crecen
        canvas_left = Canvas(left, highlightthickness=0)
        scroll_y = tb.Scrollbar(left, orient=VERTICAL, command=canvas_left.yview)
        frame_left_inner = tb.Frame(canvas_left)

        frame_left_inner.bind(
            "<Configure>",
            lambda e: canvas_left.configure(scrollregion=canvas_left.bbox("all"))
        )
        canvas_left.create_window((0, 0), window=frame_left_inner, anchor=NW)
        canvas_left.configure(yscrollcommand=scroll_y.set, width=220, height=520)

        canvas_left.pack(side=LEFT, fill=Y, expand=False)
        scroll_y.pack(side=RIGHT, fill=Y)

        for cat in config.keys():
            var = tb.IntVar(value=0)
            cb = tb.Checkbutton(frame_left_inner, text=cat, variable=var,
                                command=lambda c=cat: self._on_toggle_categoria(c))
            cb.pack(anchor="w", pady=2)
            self.check_categorias[cat] = var

        # Panel derecho: columnas + requires
        right = tb.Labelframe(wrapper, text="Columnas y Opciones por Categoría", padding=10)
        right.pack(side=LEFT, fill=BOTH, expand=True, pady=10)

        # Scroll en el panel derecho
        self.canvas_right = Canvas(right, highlightthickness=0)
        self.scroll_y_right = tb.Scrollbar(right, orient=VERTICAL, command=self.canvas_right.yview)
        self.frame_right_inner = tb.Frame(self.canvas_right)

        self.frame_right_inner.bind(
            "<Configure>",
            lambda e: self.canvas_right.configure(scrollregion=self.canvas_right.bbox("all"))
        )
        self.canvas_right.create_window((0, 0), window=self.frame_right_inner, anchor=NW)
        self.canvas_right.configure(yscrollcommand=self.scroll_y_right.set)

        self.canvas_right.pack(side=LEFT, fill=BOTH, expand=True)
        self.scroll_y_right.pack(side=RIGHT, fill=Y)

    def _construir_tab_avanzadas(self):
        f = tb.Labelframe(self.tab_adv, text="Datos Sucios (para practicar limpieza)", padding=12)
        f.pack(fill=X, padx=12, pady=12)

        tb.Checkbutton(f, text="Incluir datos sucios", variable=self.datos_sucios_var).grid(row=0, column=0, sticky="w", pady=4)
        tb.Label(f, text="Porcentaje de suciedad (0-30%)").grid(row=0, column=1, sticky="e", padx=(20, 6))
        tb.Scale(f, from_=0, to=30, orient=HORIZONTAL, variable=self.porc_sucios_var, length=220).grid(row=0, column=2, sticky="w")

        opts = tb.Labelframe(self.tab_adv, text="Tipos de suciedad", padding=12)
        opts.pack(fill=X, padx=12, pady=(0, 12))

        tb.Checkbutton(opts, text="Nulos / faltantes", variable=self.chk_nulos).grid(row=0, column=0, sticky="w", pady=4)
        tb.Checkbutton(opts, text="Duplicados", variable=self.chk_dups).grid(row=0, column=1, sticky="w", pady=4, padx=12)
        tb.Checkbutton(opts, text="Ruido en texto / emails rotos", variable=self.chk_ruido).grid(row=0, column=2, sticky="w", pady=4)
        tb.Checkbutton(opts, text="Outliers numéricos", variable=self.chk_outliers).grid(row=1, column=0, sticky="w", pady=4)
        tb.Checkbutton(opts, text="Tipos erróneos en numéricos", variable=self.chk_tipos).grid(row=1, column=1, sticky="w", pady=4, padx=12)

        tb.Label(self.tab_adv, text="Consejo: genera con 5–15% para ejercicios realistas.").pack(anchor="w", padx=16)

    def _construir_tab_historial(self):
        self.frame_hist = tb.Frame(self.tab_hist)
        self.frame_hist.pack(fill=BOTH, expand=True, padx=12, pady=12)

        self._render_historial()

    def _render_historial(self):
        for w in self.frame_hist.winfo_children():
            w.destroy()

        tb.Label(self.frame_hist, text="Últimas exportaciones", font=("", 11, "bold")).pack(anchor="w", pady=(0, 8))

        if not self.historial:
            tb.Label(self.frame_hist, text="No hay exportaciones aún.").pack(anchor="w")
            return

        for item in self.historial[-5:][::-1]:
            fecha, ruta, formato, cats = item
            row = tb.Frame(self.frame_hist)
            row.pack(fill=X, pady=4)
            tb.Label(row, text=f"• {fecha}  |  {formato}  |  {', '.join(cats)}").pack(side=LEFT)
            tb.Button(row, text="Abrir carpeta", bootstyle=INFO, command=lambda p=ruta: abrir_carpeta(p)).pack(side=RIGHT)

    # --------- Eventos dinámicos ----------

    def _on_toggle_categoria(self, categoria: str):
        # Al seleccionar/deseleccionar una categoría, añade o quita su panel
        if self.check_categorias[categoria].get() == 1:
            self._crear_panel_categoria(categoria)
        else:
            self._eliminar_panel_categoria(categoria)

        # refrescar scroll
        self.frame_right_inner.update_idletasks()
        self.canvas_right.configure(scrollregion=self.canvas_right.bbox("all"))

    def _crear_panel_categoria(self, categoria: str):
        # Evitar duplicados
        if getattr(self, f"panel_{categoria}", None):
            return

        panel = tb.Labelframe(self.frame_right_inner, text=f"{categoria}", padding=10)
        panel.pack(fill=X, padx=6, pady=6)
        setattr(self, f"panel_{categoria}", panel)

        # Columnas
        cols_frame = tb.Labelframe(panel, text="Columnas", padding=6)
        cols_frame.pack(fill=X, pady=(0, 6))
        self.column_vars.setdefault(categoria, {})
        for col in config[categoria]["columns"]:
            var = tb.IntVar(value=1)
            tb.Checkbutton(cols_frame, text=col, variable=var).pack(anchor="w")
            self.column_vars[categoria][col] = var

        # Requires (spinboxes)
        reqs = config[categoria]["requires"]
        self.requires_spin.setdefault(categoria, {})

        if reqs:
            req_frame = tb.Labelframe(panel, text="Opciones dinámicas (subconjuntos)", padding=6)
            req_frame.pack(fill=X)
            for key in reqs:
                row = tb.Frame(req_frame)
                row.pack(fill=X, pady=2)
                tb.Label(row, text=f"{key} (3-20):", width=18).pack(side=LEFT)
                spin = tb.Spinbox(row, from_=3, to=20, width=6)
                # valor por defecto = min(8, len(opciones[key]))
                defecto = min(8, len(opciones[key]))
                spin.delete(0, "end")
                spin.insert(0, defecto)
                spin.pack(side=LEFT)
                self.requires_spin[categoria][key] = spin

    def _eliminar_panel_categoria(self, categoria: str):
        panel = getattr(self, f"panel_{categoria}", None)
        if panel:
            panel.destroy()
            setattr(self, f"panel_{categoria}", None)
        # limpiar estados
        self.column_vars.pop(categoria, None)
        self.requires_spin.pop(categoria, None)

    # ------------- Generación y exportación ----------------

    def _leer_categorias_seleccionadas(self):
        return [c for c, v in self.check_categorias.items() if v.get() == 1]

    def _leer_columnas_activas(self, categoria):
        cols = self.column_vars.get(categoria, {})
        activas = [c for c, v in cols.items() if v.get() == 1]
        if not activas:
            # Si el usuario apaga todo, no generamos nada para esa categoría
            return []
        return activas

    def _build_choices_for_categoria(self, categoria):
        # Construye subconjuntos (choices) para los 'requires' de cada categoría
        reqs = config[categoria]["requires"]
        if not reqs:
            return {}

        choices = {}
        for key in reqs:
            spin = self.requires_spin.get(categoria, {}).get(key)
            if spin is None:
                # fallback: todo el catálogo
                choices[key] = opciones[key]
            else:
                try:
                    n = int(spin.get())
                except Exception:
                    n = 5
                if n < 3 or n > 20:
                    raise ValueError(f"{key} debe estar entre 3 y 20.")
                choices[key] = asegurar_lista_unica(opciones[key], n)
        return choices

    def generar_exportar(self):
        # Configurar Faker por idioma
        self.fake = Faker(IDIOMAS.get(self.idioma_var.get(), "es_CO"))

        categorias = self._leer_categorias_seleccionadas()
        if not categorias:
            messagebox.showerror("Error", "Selecciona al menos una categoría.")
            return

        # Cantidad
        try:
            cantidad = int(self.cantidad_var.get())
            if cantidad <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "La cantidad debe ser un número positivo.")
            return

        # Construcción de DataFrames por categoría
        dataframes = {}
        try:
            for cat in categorias:
                cols_activas = self._leer_columnas_activas(cat)
                if not cols_activas:
                    # Si no hay columnas activas, omitimos esta categoría
                    continue

                choices = self._build_choices_for_categoria(cat)
                registros = []
                for _ in range(cantidad):
                    row = config[cat]["generator"](self.fake, choices)
                    row_dict = dict(zip(config[cat]["columns"], row))
                    registros.append([row_dict[c] for c in cols_activas])

                df = pd.DataFrame(registros, columns=cols_activas)

                # Aplicar datos sucios si corresponde
                if self.datos_sucios_var.get():
                    df = aplicar_datos_sucios(
                        df,
                        porcentaje=int(self.porc_sucios_var.get()),
                        habilitar_nulos=self.chk_nulos.get(),
                        habilitar_duplicados=self.chk_dups.get(),
                        habilitar_ruido_texto=self.chk_ruido.get(),
                        habilitar_outliers=self.chk_outliers.get(),
                        habilitar_tipos_erroneos=self.chk_tipos.get()
                    )

                dataframes[cat] = df

            if not dataframes:
                messagebox.showerror("Error", "No hay columnas activas en las categorías seleccionadas.")
                return
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema generando los datos:\n{e}")
            return

        # Exportación
        formato = self.formato_var.get()
        ruta_export = None

        try:
            if formato == "CSV":
                if len(dataframes) == 1:
                    # Un archivo CSV
                    ruta_export = filedialog.asksaveasfilename(
                        defaultextension=".csv",
                        filetypes=[("CSV", "*.csv")],
                        initialfile=f"{list(dataframes.keys())[0].lower()}.csv"
                    )
                    if not ruta_export:
                        return
                    list(dataframes.values())[0].to_csv(ruta_export, index=False)
                else:
                    # Varios CSV: base + sufijo por categoría
                    ruta_base = filedialog.asksaveasfilename(
                        defaultextension=".csv",
                        filetypes=[("CSV", "*.csv")],
                        initialfile="dataset.csv",
                        title="Elige nombre base (se generará un archivo por categoría)"
                    )
                    if not ruta_base:
                        return
                    base = Path(ruta_base)
                    for cat, df in dataframes.items():
                        out = base.with_name(f"{base.stem}_{cat}.csv")
                        df.to_csv(out, index=False)
                    ruta_export = str(base.parent)
            elif formato == "Excel":
                ruta_export = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel", "*.xlsx")],
                    initialfile="dataset.xlsx"
                )
                if not ruta_export:
                    return
                with pd.ExcelWriter(ruta_export, engine="xlsxwriter") as writer:
                    for cat, df in dataframes.items():
                        # sheet name <= 31 chars
                        sheet = cat[:31]
                        df.to_excel(writer, sheet_name=sheet, index=False)
            elif formato == "JSON":
                ruta_export = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON", "*.json")],
                    initialfile="dataset.json"
                )
                if not ruta_export:
                    return
                payload = {cat: df.to_dict(orient="records") for cat, df in dataframes.items()}
                with open(ruta_export, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
            elif formato == "SQL":
                ruta_export = filedialog.asksaveasfilename(
                    defaultextension=".db",
                    filetypes=[("SQLite", "*.db")],
                    initialfile="dataset.db"
                )
                if not ruta_export:
                    return
                conn = sqlite3.connect(ruta_export)
                for cat, df in dataframes.items():
                    table = cat.lower().replace(" ", "_")
                    df.to_sql(table, conn, index=False, if_exists="replace")
                conn.close()
            else:
                messagebox.showerror("Error", "Formato no soportado.")
                return

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema al exportar:\n{e}")
            return

        # Historial / estado
        self.ultima_ruta = ruta_export or ""
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.historial.append((fecha, self.ultima_ruta, formato, list(dataframes.keys())))
        # Mantener últimos 20
        if len(self.historial) > 20:
            self.historial = self.historial[-20:]
        self._render_historial()

        messagebox.showinfo("Éxito", f"✅ Exportado correctamente:\n{self.ultima_ruta}")

# ===========================
# Lanzamiento
# ===========================

if __name__ == "__main__":
    # Tema moderno; puedes probar: "superhero", "darkly", "flatly", "litera", "journal", "pulse", etc.
    root = tb.Window(themename="superhero")
    app = App(root)
    root.mainloop()
