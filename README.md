# t8-client

Cliente Python para interactuar con la API T8. Permite descargar, listar y graficar ondas y espectros de mediciones de máquinas.

## Descripción

t8-client es un paquete Python que proporciona una interfaz de línea de comandos (CLI) para interactuar con la API T8. Permite gestionar datos de ondas y espectros de diferentes máquinas y puntos de medición, incluyendo funcionalidades de descarga, listado, graficación y comparación de datos.

## Requisitos

- Python 3.13 o superior
- uv (gestor de paquetes)

## Instalación

### Instalación del entorno de desarrollo

```bash
# Clonar el repositorio
git clone <repository-url>
cd paquete-python

# Crear el entorno virtual e instalar dependencias
uv sync
```

### Configuración

Crear un archivo `.env` en la raíz del proyecto con las credenciales de acceso a la API:

```
T8_USER=tu_usuario
T8_PASSWORD=tu_contraseña
```

## Uso

### Comandos disponibles

#### Listar ondas

```bash
uv run t8-cli list-waves -M <machine> -P <point> -m <mode>
```

#### Listar espectros

```bash
uv run t8-cli list-spectra -M <machine> -P <point> -m <mode>
```

#### Obtener una onda específica

```bash
# Onda más reciente
uv run t8-cli get-wave -M <machine> -P <point> -m <mode>

# Onda por fecha (formato ISO 8601)
uv run t8-cli get-wave -M <machine> -P <point> -m <mode> -d "2019-04-11T16:43:22"

# Onda por timestamp Unix
uv run t8-cli get-wave -M <machine> -P <point> -m <mode> -t 1555119736
```

#### Obtener un espectro específico

```bash
# Espectro más reciente
uv run t8-cli get-spectrum -M <machine> -P <point> -m <mode>

# Espectro por fecha o timestamp
uv run t8-cli get-spectrum -M <machine> -P <point> -m <mode> -d "2019-04-11T16:43:22"
```

#### Graficar onda

```bash
uv run t8-cli plot-wave -M <machine> -P <point> -m <mode>
```

#### Graficar espectro

```bash
uv run t8-cli plot-spectrum -M <machine> -P <point> -m <mode>
```

#### Listar todas las ondas disponibles

```bash
uv run t8-cli list-all-waves
```

#### Calcular espectro desde archivo local

```bash
uv run t8-cli compute-spectrum <ruta_archivo.json>
```

#### Comparar espectros

```bash
uv run t8-cli compare-spectra <archivo_espectro.json> <archivo_onda.json>
uv run t8-cli compare-spectra <archivo_espectro.json> <archivo_onda.json> -o <salida.png>
```

### Parámetros

- `-M, --machine`: ID de la máquina
- `-P, --point`: Punto de medición de la máquina
- `-m, --mode`: Modo de procesamiento
- `-d, --date`: Fecha en formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)
- `-t, --timestamp`: Timestamp Unix
- `-o, --output`: Archivo de salida (para comparación de espectros)

### Ejemplos

```bash
# Listar ondas de una máquina específica
uv run t8-cli list-waves -M "LP_Turbine" -P "MAD31CY005" -m "AM1"

# Descargar onda más reciente
uv run t8-cli get-wave -M "LP_Turbine" -P "MAD31CY005" -m "AM1"

# Graficar espectro de una fecha específica
uv run t8-cli plot-spectrum -M "LP_Turbine" -P "MAD31CY005" -m "AM1" -t 1555119736
```

## Estructura del proyecto

```
src/t8_client/
  ├── __init__.py
  ├── cli.py           # Interfaz de línea de comandos
  ├── models.py        # Modelos de datos
  └── t8_client.py     # Cliente API principal
tests/                 # Tests unitarios
data/                  # Datos descargados (ondas, espectros, gráficos)
scripts/               # Scripts auxiliares
```

## Desarrollo

### Ejecutar tests

```bash
uv run pytest
```

### Ejecutar tests con cobertura

```bash
uv run pytest --cov
```

### Linting

```bash
uv run ruff check .
```