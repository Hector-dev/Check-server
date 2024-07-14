# Check Server 2.0

## Descripción
Check Server 2.0 es una aplicación de escritorio desarrollada en Python que permite monitorear la conectividad y el rendimiento de múltiples servidores. La aplicación ofrece una interfaz gráfica intuitiva para gestionar una lista de servidores y realizar pruebas de ping, latencia y velocidad de conexión.

## Características
- Interfaz gráfica de usuario construida con Tkinter
- Almacenamiento de datos de servidores en SQLite
- Monitoreo en tiempo real de estado de conexión, latencia, velocidad de descarga y subida
- Operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para gestionar servidores
- Actualización automática de estados cada 5 minutos
- Visualización de resultados en una tabla interactiva

## Requisitos del sistema
- Python 3.7 o superior
- Bibliotecas Python: tkinter, sqlite3, threading, subprocess, speedtest-cli, ping3, psutil, PIL

## Instalación

1. Clone este repositorio:

git clone (https://github.com/Hector-dev/Check-server.git)

2. Navegue al directorio del proyecto:

cd check-server-2.0

3. Instale las dependencias:

pip install speedtest-cli ping3 psutil Pillow

## Uso
Para iniciar la aplicación, ejecute:

### Funciones principales:
- **Crear Registro**: Añade un nuevo servidor a la base de datos.
- **Modificar Registro**: Actualiza la información de un servidor existente.
- **Mostrar Lista**: Actualiza y muestra el estado de todos los servidores.
- **Eliminar Registro**: Elimina un servidor de la base de datos.

### Interfaz de usuario:
- La ventana principal muestra una tabla con la lista de servidores y su estado.
- Use los campos de entrada en la parte superior para añadir o modificar servidores.
- Haga doble clic en una fila de la tabla para cargar los datos de un servidor en los campos de entrada.

## Estructura del proyecto

check-server-2.0/
│
├── check_server.py         # Script principal
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Este archivo
├── active.ico              # Icono para servidores activos
├── inactivo.ico            # Icono para servidores inactivos
└── BD                      # Base de datos SQLite (se crea automáticamente)

## Funcionamiento interno
1. Al iniciar, la aplicación se conecta a la base de datos SQLite.
2. La interfaz gráfica se construye utilizando Tkinter y ttk.
3. Los servidores se muestran en un Treeview, que se actualiza periódicamente.
4. Las comprobaciones de conectividad se realizan en hilos separados para no bloquear la interfaz.
5. Los resultados se actualizan en tiempo real en la interfaz gráfica.

## Resolución de problemas
- Si la aplicación no inicia, verifique que todas las dependencias estén instaladas correctamente.
- En caso de errores, revise el archivo `error_log.txt` que se genera en el directorio de la aplicación.

## Contribuir
Las contribuciones son bienvenidas. Por favor, abra un issue para discutir cambios importantes antes de crear un pull request.

## Licencia
[MIT License](https://opensource.org/licenses/MIT)

## Contacto
Héctor Rodríguez - [hectorrdev@gmail.com]

Enlace del proyecto: [https://github.com/Hector-dev/Check-server](https://github.com/Hector-dev/Check-server)
