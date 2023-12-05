# Importación de librerías necesarias
import numpy as np
import pandas as pd
import csv
import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk, simpledialog, filedialog, messagebox
from prettytable import PrettyTable

def procesamiento_datos(n, m, muestras):
    """
    Calcula las matrices de transición para el canal y el estado a partir de las muestras dadas.

    Parameters:
        n (int): Número de muestras.
        m (int): Número de canales.
        muestras (list): Lista de muestras, donde cada muestra es una lista de bits.

    Returns:
        tuple: Tupla con las matrices de transición y las muestras originales.
            - EstadoCanalF (np.ndarray): Matriz de transición para el canal al futuro.
            - EstadoEstadoF (np.ndarray): Matriz de transición para el estado al futuro.
            - EstadoCanalP (np.ndarray): Matriz de transición para el canal al pasado.
            - EstadoEstadoP (np.ndarray): Matriz de transición para el estado al pasado.
            - EstadoCanalF_aux (np.ndarray): Matriz auxiliar de transición para el canal al futuro.
            - EstadoEstadoF_aux (np.ndarray): Matriz auxiliar de transición para el estado al futuro.
            - muestras_almacenadas (list): Lista de muestras original.
    """
    # Matrices de transición para el canal y el estado
    EstadoCanalF = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoEstadoF = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoCanalP = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoEstadoP = np.zeros((2 ** m, 2 ** m), dtype=float)
    
    # Matrices auxiliares para el cálculo del estado futuro
    EstadoCanalF_aux = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoEstadoF_aux = np.zeros((2 ** m, 2 ** m), dtype=float)
    
    # Copia de las muestras para mantener los datos originales
    muestras_almacenadas = muestras.copy()

    # Bucle sobre las muestras
    for i in range(n):
        muestra = muestras[i]

        # Actualización de matrices de transición para el canal y el estado
        for j in range(m):
            EstadoCanalF[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / (n - (i == n-1))
            if j < m - 1:
                EstadoEstadoF[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra[j + 1:])), 2)] += 1 / (n - (i == n-1))

        # Actualización de matrices auxiliares
        if i > 0:
            EstadoCanalF_aux[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / n
            EstadoEstadoF_aux[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / n

        # Actualización de matrices de transición para el estado pasado
        for j in range(m):
            muestra_previa = muestra.copy()
            muestra_previa[j] = 1 - muestra_previa[j]
            EstadoCanalP[int(''.join(map(str, muestra_previa)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / (n - (i == n-1))
        if i > 0:
            EstadoEstadoP[int(''.join(map(str, muestras[i - 1])), 2)][int(''.join(map(str, muestra)), 2)] += 1 / (n - (i == n-1))

    # Devuelve las matrices calculadas y las muestras originales
    return (
        EstadoCanalF,
        EstadoEstadoF,
        EstadoCanalP,
        EstadoEstadoP,
        EstadoCanalF_aux,
        EstadoEstadoF_aux,
        muestras_almacenadas,
    )

#def marginalizar(matriz, indices):
#    """
#    Realiza la marginalización de una matriz dado un conjunto de índices.
#
#    Parameters:
#        matriz (np.ndarray): Matriz a marginalizar.
#        indices (list): Lista de índices de columnas a marginalizar.
#
#    Returns:
#        np.ndarray: Matriz marginalizada.
#    """
#    if matriz is None:
#        return np.zeros((0,))  # Retorna una matriz vacía si la matriz es None
#    return np.sum(matriz[:, indices], axis=1) / 2  # Dividimos entre 2 para ajustar según la lógica mencionada
#
#def normalizar(matriz):
#    """
#    Normaliza una matriz dividiendo cada fila por la suma de sus elementos.
#
#    Parameters:
#        matriz (np.ndarray): Matriz a normalizar.
#
#    Returns:
#        np.ndarray: Matriz normalizada.
#    """
#    suma_filas = np.sum(matriz, axis=1, keepdims=True)
#
#    # Reemplazar ceros en la suma para evitar divisiones por cero
#    suma_filas[suma_filas == 0] = 1
#
#    # Normalizar la matriz
#    matriz_normalizada = matriz / suma_filas
#
#    return matriz_normalizada
#
#def marginalizar_y_normalizar(matriz, indices_filas, indices_columnas):
#    """
#    Realiza la marginalización y normalización de una matriz dado un conjunto de índices de filas y columnas.
#
#    Parameters:
#        matriz (np.ndarray): Matriz a procesar.
#        indices_filas (list): Lista de índices de filas a marginalizar.
#        indices_columnas (list): Lista de índices de columnas a marginalizar.
#
#    Returns:
#        np.ndarray: Matriz resultante después de la marginalización y normalización.
#    """
#    matriz_marginalizada = marginalizar(matriz, indices_columnas)
#    matriz_normalizada = normalizar(matriz_marginalizada.reshape(-1, 2 ** len(indices_filas)))
#    return matriz_normalizada.reshape(-1, 2 ** len(indices_columnas))

def generar_entradas_aleatorias(n, m):
    """
    Genera muestras aleatorias de longitud m.

    Parameters:
        n (int): Número de muestras a generar.
        m (int): Longitud de cada muestra.

    Returns:
        list: Lista de muestras generadas.
    """
    muestras = []
    for i in range(n):
        muestra = np.random.randint(2, size=m)
        muestras.append(muestra)
    return muestras

# Clase para la interfaz gráfica
class InterfazGrafica:
    def __init__(self):
        """
        Inicializa la interfaz gráfica y configura elementos como la ventana principal, etiquetas, botones, y estilos.
        """
        self.window = ThemedTk(theme="arc")
        self.window.title("Proyecto Matrices de Datos y Estados")
        self.window.geometry("800x600")

        self.muestras_almacenadas = None
        self.matrices = None

        style = ttk.Style()
        style.configure("TButton", padding=5, font=('Helvetica', 12))

        self.n_label = ttk.Label(self.window, text="Número de muestras (n):", font=('Helvetica', 12))
        self.m_label = ttk.Label(self.window, text="Número de canales (m):", font=('Helvetica', 12))
        self.n_entry = ttk.Entry(self.window)
        self.m_entry = ttk.Entry(self.window)

        self.btn_manual = ttk.Button(self.window, text="Ingresar datos manualmente", command=self.ingresar_manualmente, style="TButton")
        self.btn_aleatorio = ttk.Button(self.window, text="Generar datos aleatorios", command=self.generar_aleatorios, style="TButton")
        self.btn_mostrar_canal_f = ttk.Button(self.window, text="Mostrar EstadoCanalF", command=self.mostrar_canal_f, style="TButton")
        self.btn_mostrar_estado_f = ttk.Button(self.window, text="Mostrar EstadoEstadoF", command=self.mostrar_estado_f, style="TButton")
        self.btn_mostrar_canal_p = ttk.Button(self.window, text="Mostrar EstadoCanalP", command=self.mostrar_canal_p, style="TButton")
        self.btn_mostrar_estado_p = ttk.Button(self.window, text="Mostrar EstadoEstadoP", command=self.mostrar_estado_p, style="TButton")
        self.btn_mostrar_matriz_ejemplo = ttk.Button(self.window, text="Mostrar Matriz Ejemplo", command=lambda: self.mostrar_matriz_ejemplo("Matriz Ejemplo"), style="TButton")
        #self.btn_marginalizar_y_normalizar = ttk.Button(self.window, text="Marginalizar y Normalizar", command=self.marginalizar_y_normalizar, style="TButton")
        self.btn_mostrar_datos = ttk.Button(self.window, text="Mostrar Datos", command=self.mostrar_datos, style="TButton")
        self.btn_cargar_csv = ttk.Button(self.window, text="Cargar desde CSV", command=self.cargar_csv, style="TButton")
        self.btn_salir = ttk.Button(self.window, text="Salir", command=self.window.quit, style="TButton")

        self.n_label.grid(row=0, column=0, pady=5, padx=5)
        self.n_entry.grid(row=0, column=1, pady=5, padx=5)
        self.m_label.grid(row=1, column=0, pady=5, padx=5)
        self.m_entry.grid(row=1, column=1, pady=5, padx=5)

        self.btn_manual.grid(row=2, column=0, columnspan=2, pady=5)
        self.btn_aleatorio.grid(row=3, column=0, columnspan=2, pady=5)
        self.btn_mostrar_canal_f.grid(row=4, column=0, columnspan=2, pady=5)
        self.btn_mostrar_estado_f.grid(row=5, column=0, columnspan=2, pady=5)
        self.btn_mostrar_canal_p.grid(row=6, column=0, columnspan=2, pady=5)
        self.btn_mostrar_estado_p.grid(row=7, column=0, columnspan=2, pady=5)
        self.btn_mostrar_datos.grid(row=8, column=0, columnspan=2, pady=5)
        self.btn_cargar_csv.grid(row=9, column=0, columnspan=2, pady=5)
        #self.btn_marginalizar_y_normalizar.grid(row=10, column=0, columnspan=2, pady=5)
        self.btn_mostrar_matriz_ejemplo.grid(row=11, column=0, columnspan=2, pady=5)
        self.btn_salir.grid(row=12, column=0, columnspan=2, pady=5)

        # Ventanas internas para mostrar las matrices de estados y los datos
        self.matrices_window = None
        self.datos_window = None

    def ingresar_manualmente(self):
        """
        Permite al usuario ingresar manualmente el número de muestras y los valores de cada muestra.
        """
        try:
            n = int(self.n_entry.get())
            m = int(self.m_entry.get())
            muestras = []
            for i in range(n):
                muestra_str = simpledialog.askstring(f"Ingresar datos manualmente", f"Ingrese la muestra {i + 1} como una cadena de {m} valores binarios:")
                muestra = [int(bit) for bit in muestra_str]
                muestras.append(muestra)
            self.matrices = procesamiento_datos(n, m, muestras)
            self.muestras_almacenadas = muestras
            messagebox.showinfo("Éxito", "Datos ingresados correctamente.")
        except ValueError:
            messagebox.showerror("Error", "Debe ingresar valores numéricos.")

    def generar_aleatorios(self):
        """
        Genera datos aleatorios con el número de muestras y canales especificados.
        """
        try:
            n = int(self.n_entry.get())
            m = int(self.m_entry.get())
            muestras = [np.random.randint(2, size=m) for _ in range(n)]
            muestras = [list(muestra) + [0] * (m - len(muestra)) for muestra in muestras]
            self.matrices = procesamiento_datos(n, m, muestras)
            self.muestras_almacenadas = muestras  # Actualiza muestras_almacenadas con los datos generados
            messagebox.showinfo("Éxito", "Datos aleatorios generados correctamente.")
        except ValueError:
            messagebox.showerror("Error", "Debe ingresar valores numéricos.")

    def mostrar_canal_f(self):
        """
        Muestra la matriz EstadoCanalF en una ventana.
        """
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[0], "Matriz EstadoCanalF")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_estado_f(self):
        """
        Muestra la matriz EstadoEstadoF en una ventana.
        """
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[1], "Matriz EstadoEstadoF")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_canal_p(self):
        """
        Muestra la matriz EstadoCanalP en una ventana.
        """
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[2], "Matriz EstadoCanalP")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_estado_p(self):
        """
        Muestra la matriz EstadoEstadoP en una ventana.
        """
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[3], "Matriz EstadoEstadoP")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_datos(self):
        """
        Muestra la matriz de datos almacenada en una ventana.
        """
        if self.muestras_almacenadas is not None:
            df = pd.DataFrame(self.muestras_almacenadas, columns=[f'Canal {i + 1}' for i in range(len(self.muestras_almacenadas[0]))])
            self.mostrar_dataframe(df, "Matriz de Datos")
        else:
            messagebox.showwarning("Advertencia", "No hay datos generados.")

    #def marginalizar_y_normalizar(self):
    #    """
    #    Muestra la matriz EstadoFuturoBC y EstadoFuturoABC marginalizadas y normalizadas en una ventana de mensaje.
    #    """
    #    if self.matrices is not None:
    #        EstadoFuturo_BC = self.calcular_estado_futuro_BC()
    #        EstadoFuturo_ABC = self.calcular_estado_futuro_ABC()

    #        resultado_BC = marginalizar_y_normalizar(EstadoFuturo_BC, [0], [1])
    #        resultado_ABC = marginalizar_y_normalizar(EstadoFuturo_ABC, [0, 1], [2])

    #        self.mostrar_matriz(resultado_BC, "Estado Futuro BC (Marginalizado y Normalizado)")
    #        self.mostrar_matriz(resultado_ABC, "Estado Futuro ABC (Marginalizado y Normalizado)")
    #    else:
    #        messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    #def calcular_estado_futuro_BC(self):
    #    matriz_marginalizada = marginalizar_y_normalizar(self.matrices[1], [1, 2], [1, 2])
    #    if matriz_marginalizada.shape == (2 ** 2, 2 ** 2):
    #        return matriz_marginalizada / 2  # Dividimos entre 2 para ajustar según la lógica mencionada
    #    else:
    #        messagebox.showerror("Error", "Dimensiones incorrectas para la matriz marginalizada")

    #def calcular_estado_futuro_ABC(self):
    #    resultado_marginalizacion = marginalizar_y_normalizar(self.matrices[1], [0, 2], [0, 2])
    #    if resultado_marginalizacion.shape == (2 ** 3, 2 ** 3):
    #        return resultado_marginalizacion / 2  # Dividimos entre 2 para ajustar según la lógica mencionada
    #    else:
    #        messagebox.showerror("Error", "Dimensiones incorrectas para la matriz marginalizada")

    def cargar_csv(self):
        """
        Permite al usuario cargar un archivo CSV con las muestras.
        """
        archivo = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("CSV files", "*.csv")])
        if archivo:
            try:
                with open(archivo, newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    muestras = []
                    for row in reader:
                        muestra = [int(bit) for bit in row]
                        muestras.append(muestra)
                    n = len(muestras)
                    m = len(muestras[0])
                    self.matrices = procesamiento_datos(n, m, muestras)
                    self.muestras_almacenadas = muestras
                    messagebox.showinfo("Éxito", "Datos cargados desde CSV correctamente.")
            except FileNotFoundError:
                messagebox.showerror("Error", "Archivo no encontrado.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo CSV: {str(e)}")

    def mostrar_matriz_ejemplo(self, titulo):
        """
        Muestra una matriz de ejemplo aleatoria en una ventana con el título proporcionado.
        """
        matriz_ejemplo = np.random.randint(2, size=(8, 8))  # Matriz aleatoria de 0 y 1
        self.mostrar_matriz(matriz_ejemplo, titulo)

    def mostrar_matriz(self, matriz, titulo):
        """
        Muestra una matriz dada en una ventana con el título proporcionado.
        """
        if self.matrices_window is None or not self.matrices_window.winfo_exists():
            self.matrices_window = tk.Toplevel(self.window)
            self.matrices_window.title(titulo)

        frame = ttk.Frame(self.matrices_window)
        frame.grid(row=0, column=0)

        # Crear Treeview para mostrar la matriz
        tree = ttk.Treeview(frame)

        # Encabezados de columna
        column_headers = [f'StateF {i}' for i in range(len(matriz[0]))]
        tree["columns"] = column_headers
        for header in column_headers:
            tree.heading(header, text=header)

        if not matriz.size:
            # Si la matriz está vacía, agregar una fila con valores vacíos
            tree.insert("", 0, text="No hay datos", values=[""] * len(column_headers))
        else:
            # Agregar filas
            for i, row in enumerate(matriz):
                tree.insert("", i, text=f'StateP {i}', values=tuple(round(val, 2) for val in row))

        tree.pack()

        # Crear tabla para mostrar la matriz
        table = PrettyTable()
        column_headers = [f'Future {i}' for i in range(matriz.shape[1])]
        table.field_names = ['StatesP'] + column_headers

        if not matriz.size:
            # Si la matriz está vacía, agregar una fila con valores vacíos
            table.add_row(["No hay datos"] + [""] * len(column_headers))
        else:
            for i, row in enumerate(matriz):
                table.add_row([f'Actual {i}'] + [f'{val:.2f}' for val in row])

        # Mostrar tabla
        print(table)

    def mostrar_matriz_datos(self, muestras):
        """
        Muestra una matriz de datos (muestras) en una ventana.
        """
        if self.datos_window is None or not self.datos_window.winfo_exists():
            self.datos_window = tk.Toplevel(self.window)
            self.datos_window.title("Matriz de Datos")

        frame = ttk.Frame(self.datos_window)
        frame.grid(row=0, column=0)

        # Crear Treeview para mostrar las muestras
        tree = ttk.Treeview(frame)

        # Encabezados de columna
        if muestras:
            column_headers = [f'Canal {i + 1}' for i in range(len(muestras[0]))]
        else:
            column_headers = ["No hay datos"]
        tree["columns"] = column_headers
        for header in column_headers:
            tree.heading(header, text=header)

        if not muestras:
            # Si la lista de muestras está vacía, agregar una fila con valores vacíos
            tree.insert("", 0, text="No hay datos", values=[""] * len(column_headers))
        else:
            # Agregar filas
            for i, row in enumerate(muestras):
                tree.insert("", i, text=f'Muestra {i + 1}', values=tuple(row))

        tree.pack()

        # Crear tabla para mostrar las muestras
        table = PrettyTable()
        if muestras:
            column_headers = [f'Canal {i + 1}' for i in range(len(muestras[0]))]
        else:
            column_headers = ["No hay datos"]
        table.field_names = ['Muestra'] + column_headers

        if not muestras:
            # Si la lista de muestras está vacía, agregar una fila con valores vacíos
            table.add_row(["No hay datos"] + [""] * len(column_headers))
        else:
            for i, row in enumerate(muestras):
                table.add_row([f'Muestra {i + 1}'] + [str(val) for val in row])

        # Mostrar tabla
        print(table)

    def mostrar_dataframe(self, df, titulo):
        """
        Muestra un DataFrame en una ventana interna.
        """
        if self.datos_window is None or not self.datos_window.winfo_exists():
            self.datos_window = tk.Toplevel(self.window)
            self.datos_window.title(titulo)

        frame = ttk.Frame(self.datos_window)
        frame.grid(row=0, column=0)

        # Crear Treeview para mostrar el DataFrame
        tree = ttk.Treeview(frame)

        # Encabezados de columna
        column_headers = list(df.columns)
        tree["columns"] = column_headers
        for header in column_headers:
            tree.heading(header, text=header)

        # Agregar filas
        for i, (_, row) in enumerate(df.iterrows()):
            tree.insert("", i, text=f'Row {i}', values=tuple(row))

        tree.pack()

    def run(self):
        """
        Ejecuta la interfaz gráfica.
        """
        self.window.mainloop()

if __name__ == "__main__":
    interfaz = InterfazGrafica()
    interfaz.run()