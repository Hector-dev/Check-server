"""
Check Server 2.0

Este script implementa una aplicación de interfaz gráfica para monitorear servidores
y realizar pruebas de conectividad y rendimiento.

Autor: Hector Rodriguez
Versión: 2.0.0
"""

# Importar Bibliotecas
from tkinter import *
from tkinter import messagebox
from tkinter import ttk 
import tkinter as tk
import sqlite3
import threading
from tkinter import PhotoImage
import subprocess
import speedtest_cli
from ping3 import ping
import psutil
import queue
import concurrent.futures
import os
import sys
import numpy as np
import pkg_resources
from PIL import Image, ImageTk
import traceback

import platform
if platform.system() != 'Windows':
    import termios
    



# Desarrollo de la Interfaz grafica
root=Tk()
root.title("Check Server")
root.geometry("600x350")

ruta_icono = r"active.ico"
root.iconbitmap(ruta_icono)

main_frame = ttk.Frame(root, padding="20 20 20 20")
main_frame.pack(fill=BOTH, expand=True)



# Carga y redimensiona las imágenes
active_img = Image.open(r"active.ico").resize((16, 16), Image.LANCZOS)
inactive_img = Image.open(r"inactivo.ico").resize((16, 16), Image.LANCZOS)

# Convierte las imágenes a formato PhotoImage de Tkinter
active_icon = ImageTk.PhotoImage(active_img)
inactive_icon = ImageTk.PhotoImage(inactive_img)

# Variables globales
miservidor = StringVar()
miurl = StringVar()
miestado = StringVar()
miid = StringVar()


def conexionBBDD():

    """
    Establece la conexión con la base de datos SQLite.
    Si la base de datos no existe, la crea y añade datos de ejemplo.
    """
    
    try:
        # Conexión a la base de datos (o creación si no existe)
        conexion = sqlite3.connect("BD")  # Cambia el nombre del archivo de la base de datos
        miCursor = conexion.cursor()

        # Verificar si la tabla ya existe
        miCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='BBDD'")
        tabla_existe = miCursor.fetchone()

        if tabla_existe:
            print("Conectado.")
        else:
            # Crear la tabla si no existe
            miCursor.execute("CREATE TABLE IF NOT EXISTS BBDD (ID INTEGER PRIMARY KEY AUTOINCREMENT, SERVIDOR TEXT, IP TEXT)")

            # Insertar datos de ejemplo
            miCursor.execute("INSERT INTO BBDD (SERVIDOR, IP) VALUES (?, ?)", ("google", "8.8.8.8"))

        # Guardar cambios y cerrar la conexión
        conexion.commit()
        conexion.close()

    except sqlite3.Error as e:
        print(f"Error en la conexión: {e}")

def eliminarBBDD():

    """
    Elimina la tabla BBDD de la base de datos tras confirmación del usuario.
    """    
    miConexion=sqlite3.connect("BD")
    miCursor=miConexion.cursor()
    if messagebox.askyesno(message="¿Los Datos se perderan definitivamente, Desea continuar?", title="ADVERTENCIA"):
        miCursor.execute("DROP TABLE BBDD")
    else:
        pass
    limpiarCampos()
    mostrar()

def salirAplicacion():
    
    """
    Cierra la aplicación tras confirmación del usuario.
    """
    
    valor=messagebox.askquestion("Salir","¿Está seguro que desea salir de la Aplicación?")
    if valor=="yes":
        root.destroy()

def limpiarCampos():
    
    """
    Limpia todos los campos de entrada en la interfaz.
    """
    
    miid.set("")
    miservidor.set("")
    miurl.set("")
    miestado.set("")

def mensaje():
    
    """
    Muestra un cuadro de diálogo con información sobre la aplicación.
    """
    
    acerca='''
	Check server Version 2.0.0
                by: Hector Rodriguez
	'''
    messagebox.showinfo(title="INFORMACION", message=acerca)

#crud

def crear():
    
    """
    Crea un nuevo registro en la base de datos con la información ingresada por el usuario.
    """
    
    with sqlite3.connect("BD") as miConexion:
        miCursor = miConexion.cursor()
        try:
            servidor = miservidor.get()
            url = miurl.get()
            datos = (servidor, url)
            miCursor.execute("INSERT INTO BBDD (SERVIDOR, IP) VALUES (?, ?)", datos)
            messagebox.showinfo("ÉXITO", "Registro creado correctamente.")
        except sqlite3.Error as e:
            messagebox.showerror("ERROR", f"Error al crear el registro: {e}")
    limpiarCampos()
    mostrar()

def mostrar():
    
    """
    Muestra los registros de la base de datos en el Treeview y realiza comprobaciones de conectividad.
    """
    
    popup = mostrar_pantalla_carga()
    threading.Thread(target=realizar_comprobaciones, args=(popup,)).start()

def actualizar():
    
    """
    Actualiza un registro existente en la base de datos con la información ingresada por el usuario.
    """
    
    miConexion = sqlite3.connect("BD")
    miCursor = miConexion.cursor()
    try:
        id = miid.get()
        servidor = miservidor.get()
        url = miurl.get()
        
        if not id:
            messagebox.showwarning("ADVERTENCIA", "Por favor, seleccione un registro para actualizar.")
            return

        miCursor.execute("SELECT * FROM BBDD WHERE ID=?", (id,))
        if not miCursor.fetchone():
            messagebox.showwarning("ADVERTENCIA", "El registro seleccionado no existe.")
            return

        miCursor.execute("UPDATE BBDD SET SERVIDOR=?, IP=? WHERE ID=?", (servidor, url, id))
        miConexion.commit()
        
        if miCursor.rowcount > 0:
            messagebox.showinfo("ÉXITO", "Registro actualizado correctamente.")
        else:
            messagebox.showinfo("INFORMACIÓN", "No se realizaron cambios en el registro.")
    except sqlite3.Error as error:
        messagebox.showwarning("ADVERTENCIA", f"Error al actualizar el registro: {error}")
    finally:
        miConexion.close()
    limpiarCampos()
    mostrar()

def borrar():
    
    """
    Elimina un registro seleccionado de la base de datos tras confirmación del usuario.
    """
    
    miConexion = sqlite3.connect("BD")
    miCursor = miConexion.cursor()
    try:
        if messagebox.askyesno(message="¿Realmente desea eliminar el registro?", title="ADVERTENCIA"):
            id_a_borrar = miid.get()
            if not id_a_borrar:
                messagebox.showwarning("ADVERTENCIA", "Por favor, seleccione un registro para eliminar.")
                return
            miCursor.execute("DELETE FROM BBDD WHERE ID=?", (id_a_borrar,))
            miConexion.commit()
            if miCursor.rowcount > 0:
                messagebox.showinfo("ÉXITO", "Registro eliminado correctamente.")
            else:
                messagebox.showinfo("INFORMACIÓN", "No se encontró un registro con ese ID.")
    except sqlite3.Error as error:
        messagebox.showwarning("ADVERTENCIA", f"Ocurrió un error al tratar de eliminar el registro: {error}")
    finally:
        miConexion.close()
    limpiarCampos()
    mostrar()
#Prueba de servidores

def ping_host(host):
    
    """
    Realiza un ping al host especificado.

    Args:
    host (str): La dirección IP o nombre de dominio a hacer ping.

    Returns:
    bool: True si el ping fue exitoso, False en caso contrario.
    """
    
    try:
        result = subprocess.run(['ping', '-n', '1', '-w', '1000', host],
                                capture_output=True, text=True, timeout=2, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False   

def medir_ancho_banda(ip_list):
    
    """
    Mide el ancho de banda (velocidad de descarga y subida) para una lista de IPs.

    Args:
    ip_list (list): Lista de direcciones IP a medir.

    Returns:
    dict: Un diccionario con las IPs como claves y tuplas (descarga, subida) como valores.
    """
    
    results = {}
    threads = []

    def medir_ip(ip):
        try:
            st = speedtest_cli.Speedtest()
            st.get_best_server()
            descarga = st.download() / 1_000_000  # Velocidad de descarga en Mbps
            subida = st.upload() / 1_000_000  # Velocidad de subida en Mbps
            results[ip] = (descarga, subida)
        except Exception as e:
            print(f"Error al medir el ancho de banda para la IP {ip}: {e}")
            results[ip] = (None, None)

    for ip in ip_list:
        thread = threading.Thread(target=medir_ip, args=(ip,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results

def obtener_latencia(host):
    
    """
    Obtiene la latencia para un host específico.

    Args:
    host (str): La dirección IP o nombre de dominio a medir.

    Returns:
    float: La latencia en milisegundos, o None si no se pudo medir.
    """
    
    try:
        latencia = ping(host, timeout=1)
        return latencia * 1000 if latencia is not None else None  # Convertir a ms
    except Exception as e:
        print(f"Error al obtener la latencia: {e}")
        return None

def obtener_estadisticas_red():
    
    """
    Obtiene estadísticas de red del sistema.

    Returns:
    dict: Un diccionario con estadísticas de red por interfaz.
    """
    
    return psutil.net_io_counters(pernic=True)

def obtener_ips_desde_bbdd():
    
    """
    Obtiene todas las direcciones IP almacenadas en la base de datos.

    Returns:
    list: Una lista de direcciones IP.
    """
    
    try:
        with sqlite3.connect("BD") as miConexion:
            miCursor = miConexion.cursor()
            miCursor.execute("SELECT IP FROM BBDD")
            ips = [row[0] for row in miCursor.fetchall()]
            return ips
    except sqlite3.Error as e:
        print(f"Error al obtener IPs desde la base de datos: {e}")
        return []

ips_a_medir = root.after(5000,obtener_ips_desde_bbdd)

def obtener_ids_desde_bbdd():
    
    """
    Obtiene todos los IDs y direcciones IP almacenados en la base de datos.

    Returns:
    list: Una lista de tuplas (ID, IP).
    """

    
    try:
        with sqlite3.connect("BD") as miConexion:
            miCursor = miConexion.cursor()
            miCursor.execute("SELECT ID, IP FROM BBDD")
            return miCursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al obtener IDs desde la base de datos: {e}")
        return []

def ejecutar_tareas(ip):
    
    """
    Ejecuta todas las tareas de comprobación para una IP específica.

    Args:
    ip (str): La dirección IP a comprobar.

    Returns:
    tuple: (estado, latencia, descarga, subida) con los resultados de las pruebas.
    """
    
    try:
        print(f"Iniciando pruebas para IP: {ip}")
        
        # Comprobar estado de conexión
        estado = ping(ip) is not None
        print(f"Estado de ping para {ip}: {'Activo' if estado else 'Inactivo'}")
        actualizar_treeview_estado(ip, estado)
        
        if estado:
            # Comprobar latencia
            latencia = obtener_latencia(ip)
            print(f"Latencia para {ip}: {latencia}")
            actualizar_treeview_latencia(ip, latencia)
            
            # Comprobar velocidades
            st = speedtest_cli.Speedtest()
            st.get_best_server()
            descarga = st.download() / 1_000_000
            actualizar_treeview_descarga(ip, descarga)
            subida = st.upload() / 1_000_000
            actualizar_treeview_subida(ip, subida)
            print(f"Velocidades para {ip}: Descarga: {descarga}, Subida: {subida}")
        else:
            actualizar_treeview_inactivo(ip)
        
        return estado, latencia if estado else None, descarga if estado else None, subida if estado else None
    except Exception as e:
        print(f"Error al ejecutar tareas para {ip}: {e}")
        return False, None, None, None
    except Exception as e:
        print(f"Error procesando IP {ip}: {e}")
        actualizar_treeview_error(ip)
        return False, None, None, None
        
        return estado, latencia, descarga, subida
    except Exception as e:
        print(f"Error procesando IP {ip}: {e}")
        return False, None, None, None


#pantalla de carga

def mostrar_pantalla_carga():
    
    """
    Muestra una pantalla de carga mientras se realizan las comprobaciones.

    Returns:
    ttk.Frame: El frame de la pantalla de carga.
    """
    
    frame = ttk.Frame(tree)
    frame.place(relx=0.5, rely=0.5, anchor='center')
    
    label = ttk.Label(frame, text="Comprobando conexiones...", background='white')
    label.pack(pady=10)
    
    progress_bar = ttk.Progressbar(frame, mode="indeterminate", length=200)
    progress_bar.pack(pady=10)
    progress_bar.start()
    
    return frame

def cerrar_pantalla_carga(frame):
    
    """
    Cierra la pantalla de carga.

    Args:
    frame (ttk.Frame): El frame de la pantalla de carga a cerrar.
    """
    
    frame.destroy()

# Funciones de actualización del Treeview
# (actualizar_treeview_inactivo, actualizar_treeview_error, etc.)
# Estas funciones actualizan las filas del Treeview con los resultados de las comprobaciones.

def actualizar_treeview_inactivo(ip):
    for item in tree.get_children():
        if tree.item(item)["values"][1] == ip:
            tree.item(item, values=(tree.item(item)["values"][0], ip, "inactivo", "N/A", "N/A", "N/A"), tags=('inactivo',))
            tree.update()
            break

def actualizar_treeview_error(ip):
    for item in tree.get_children():
        if tree.item(item)["values"][1] == ip:
            tree.item(item, values=(tree.item(item)["values"][0], ip, "Error", "Error", "Error", "Error"), tags=('inactivo',))
            tree.update()
            break

def actualizar_treeview_estado(ip, estado):
    estado_str = "activo" if estado else "inactivo"
    icon = active_icon if estado else inactive_icon
    for item in tree.get_children():
        if tree.item(item)["values"][1] == ip:
            tree.item(item, values=(tree.item(item)["values"][0], ip, estado_str, "Comprobando...", "Comprobando...", "Comprobando..."), image=icon, tags=(estado_str,))
            tree.update()
            break

def actualizar_treeview_latencia(ip, latencia):
    latencia_str = f"{latencia:.2f} ms" if latencia is not None else "N/A"
    for item in tree.get_children():
        if tree.item(item)["values"][1] == ip:
            valores = list(tree.item(item)["values"])
            valores[3] = latencia_str
            tree.item(item, values=tuple(valores))
            tree.update()
            break

def actualizar_treeview_descarga(ip, descarga):
    descarga_str = f"{descarga:.2f} Mbps" if descarga is not None else "N/A"
    for item in tree.get_children():
        if tree.item(item)["values"][1] == ip:
            valores = list(tree.item(item)["values"])
            valores[4] = descarga_str
            tree.item(item, values=tuple(valores))
            tree.update()
            break

def actualizar_treeview_subida(ip, subida):
    subida_str = f"{subida:.2f} Mbps" if subida is not None else "N/A"
    for item in tree.get_children():
        if tree.item(item)["values"][1] == ip:
            valores = list(tree.item(item)["values"])
            valores[5] = subida_str
            tree.item(item, values=tuple(valores))
            tree.update()
            break

def realizar_comprobaciones(frame_carga):
    
    """
    Realiza todas las comprobaciones de servidores y actualiza el Treeview.

    Args:
    frame_carga (ttk.Frame): El frame de la pantalla de carga.
    """
    
    # Paso 1: Poblar el Treeview con información básica
    poblar_treeview_basico()
    
    # Paso 2: Realizar comprobaciones y actualizar
    actualizar_treeview_con_comprobaciones()
    
    root.after(0, cerrar_pantalla_carga, frame_carga)
    root.after(300000, mostrar)  # Actualizar cada 60 segundos

def poblar_treeview_basico():
    
    """
    Puebla el Treeview con la información básica de los servidores desde la base de datos.
    """
    
    # Limpiar el Treeview
    for item in tree.get_children():
        tree.delete(item)
    
    # Obtener información básica de la base de datos
    with sqlite3.connect("BD") as miConexion:
        miCursor = miConexion.cursor()
        miCursor.execute("SELECT ROWID, SERVIDOR, IP FROM BBDD")
        for rowid, servidor, ip in miCursor.fetchall():
            tree.insert("", "end", text=str(rowid), values=(servidor, ip, "Comprobando...", "N/A", "N/A", "N/A"))

def actualizar_treeview_con_comprobaciones():
    
    """
    Actualiza el Treeview con los resultados de las comprobaciones de todos los servidores.
    """
    
    ips = obtener_ips_desde_bbdd()
    print(f"IPs a comprobar: {ips}")
    
    for ip in ips:
        threading.Thread(target=ejecutar_tareas, args=(ip,)).start()


# Tabla 

tree = ttk.Treeview(main_frame, columns=("Nombre", "IP", "Estado", "Latencia", "Descarga", "Subida"))
tree.heading("#0", text="ID")
tree.heading("Nombre", text="Nombre")
tree.heading("IP", text="IP")
tree.heading("Estado", text="Estado")
tree.heading("Latencia", text="Latencia")
tree.heading("Descarga", text="Descarga")
tree.heading("Subida", text="Subida")
tree.pack(fill=BOTH, expand=True)

# Configurar las proporciones de las columnas (ajusta estos valores según tus preferencias)
column_proportions = [0.05, 0.2, 0.2, 0.1, 0.15, 0.15, 0.15]
# Configura el estilo para incluir las imágenes
style = ttk.Style()
style.configure("Treeview", rowheight=25)  # Aumenta la altura de las filas para acomodar las imágenes
style.configure("Treeview.Cell", padding=(0, 0, 0, 0))

#funcionalidades extra

def seleccionarUsandoClick(event):
    
    """
    Maneja el evento de doble clic en una fila del Treeview.
    Carga los datos del servidor seleccionado en los campos de entrada.

    Args:
    event: El evento de clic.
    """
    
    item = tree.identify('item', event.x, event.y)
    miid.set(tree.item(item, "text"))
    miservidor.set(tree.item(item, "values")[0])
    miurl.set(tree.item(item, "values")[1])
    miestado.set(tree.item(item, "values")[2])

tree.bind("<Double-1>", seleccionarUsandoClick)
tree.pack(fill=BOTH, expand=True)

def adjust_treeview_column_widths(event):
    
    """
    Ajusta los anchos de las columnas del Treeview cuando se redimensiona la ventana.

    Args:
    event: El evento de redimensionamiento.
    """
    
    total_width = event.width - 20  # Restamos un poco para el scrollbar vertical
    for i, proportion in enumerate(column_proportions):
        col_id = '#' + str(i)
        tree.column(col_id, width=int(total_width * proportion))

# Vincular la función al evento de redimensionamiento del Treeview
tree.bind('<Configure>', adjust_treeview_column_widths)

#apartado grafico
# Configuración adicional de la interfaz gráfica
# (estilos, menús, botones, etc.)

style = ttk.Style()
style.theme_use('clam')

bg_color = "#f0f0f0"  # Un gris claro para el fondo
fg_color = "#333333"  # Un gris oscuro para el texto
accent_color = "#4a7abc"  # Un azul para acentos

root.configure(bg=bg_color)

style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Arial", 10))
style.configure("TEntry", background="white", font=("Arial", 10))
style.configure("TButton", background=accent_color, foreground="white", font=("Arial", 10, "bold"))
style.map("TButton", background=[('active', '#3a5a9c')])

style.configure("Treeview", background="white", foreground=fg_color, rowheight=25, fieldbackground="white")
style.configure("Treeview.Heading", background=accent_color, foreground="white", font=("Arial", 10, "bold"))
style.map("Treeview", background=[('selected', '#d3d3d3')], foreground=[('selected', fg_color)])

style.configure("Treeview", rowheight=25)  # Aumenta la altura de las filas para acomodar las imágenes
tree.tag_configure('activo', foreground='green')
tree.tag_configure('inactivo', foreground='red')

root.geometry("640x550")  # Ajusta según sea necesario
root.resizable(True, True)  # Hace que la ventana sea redimensionable

# Colocar widgets en la pantalla

# Interfaz gráfica
input_frame = ttk.Frame(root)
input_frame.pack(pady=10)

ttk.Label(input_frame, text="Nueva IP").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
ttk.Entry(input_frame, width=50, textvariable=miurl).grid(row=0, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Nombre").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
ttk.Entry(input_frame, width=50, textvariable=miservidor).grid(row=1, column=1, padx=5, pady=5)

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

ttk.Button(button_frame, text="Crear Registro", command=crear, width=15).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="Modificar Registro", command=actualizar, width=17).grid(row=0, column=1, padx=5)
ttk.Button(button_frame, text="Mostrar Lista", command=mostrar, width=15).grid(row=0, column=2, padx=5)
ttk.Button(button_frame, text="Eliminar Registro", command=borrar, width=17).grid(row=0, column=3, padx=5)

# Menú
menubar = tk.Menu(root)
menubasedat = tk.Menu(menubar, tearoff=0)
menubasedat.add_command(label="Crear/Conectar Base de Datos", command=conexionBBDD)
menubasedat.add_command(label="Eliminar Base de Datos", command=eliminarBBDD)
menubasedat.add_command(label="Salir", command=salirAplicacion)
menubar.add_cascade(label="Inicio", menu=menubasedat)

ayudamenu = tk.Menu(menubar, tearoff=0)
ayudamenu.add_command(label="Resetear Campos", command=limpiarCampos)
ayudamenu.add_command(label="Acerca", command=mensaje)
menubar.add_cascade(label="Ayuda", menu=ayudamenu)

root.config(menu=menubar)

# Iniciar la aplicación
# Punto de entrada principal

if __name__ == "__main__":
    try:
        conexionBBDD()
        mostrar()
        root.mainloop()
    except Exception as e:
        # Manejo de errores y registro en archivo
        with open("error_log.txt", "w") as f:
            f.write(f"An error occurred: {str(e)}\n")
            f.write(traceback.format_exc())
        print(f"An error occurred. Check error_log.txt for details.")
        sys.exit(1)