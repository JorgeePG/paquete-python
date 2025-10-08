# Ejercicio - Desarrollo de Paquete Python

## Descripción del proyecto

Se busca desarrollar un paquete de Python que obtenga datos desde un T8 mediante la API REST y realice tareas básicas con los datos.

### Objetivos

- Crear y gestionar un paquete de Python usando `uv`.
- Organizar el código en módulos y paquetes, usando clases y funciones según las necesidades.
- Obtener datos desde un T8 realizando llamadas a una API REST.
- Calcular el espectro a partir de una onda, usando la Transformada Rápida de Fourier (FFT).
- Representar gráficamente los datos obtenidos.
- Realizar tests para comprobar que el código funciona correctamente, utilizando `pytest`.
- Crear una interfaz de línea de comandos (CLI) para interactuar con el paquete, usando `Click`.
- Gestionar el código mediante Git y GitHub.
- Documentar el código para facilitar su comprensión y mantenimiento.

### Desarrollo del ejercicio

Para desarrollar este ejercicio se proponen los siguientes pasos:

#### 1. Configuración del proyecto y pruebas iniciales

1. Crear un repositorio en GitHub para gestionar el código del proyecto. Configurar correctamente el archivo `.gitignore`.
1. Configurar el entorno de desarrollo y las dependencias del proyecto usando `uv`. Estructura básica del proyecto. Añadir a `pyproject.toml` las configuraciones necesarias para `pytest`, `ruff`, etc.
1. Descargar una forma de onda desde la API REST del T8, usando `curl` o una herramienta similar.
1. Implementar la clase `T8ApiClient` para gestionar las llamadas a la API REST del T8. Comprobar que se conecta correctamente a la API, comprobando el valor del código de estado HTTP devuelto.

#### 2. Listado y obtención de formas de onda y representación gráfica

1. Crear un método en `T8ApiClient` para listar las ondas disponibles en la API.
1. Crear un método en `T8ApiClient` para obtener una onda desde la API y guardarla en un archivo JSON.
1. Crear un método en `T8ApiClient` para crear un plot de una onda desde un archivo JSON.

#### 3. Uso de la CLI para obtener y representar formas de onda

1. Crear la CLI el comando `t8-client`. Añadir el subcomando `list-waves` en la CLI para listar las ondas disponibles en la API.
1. Añadir a la CLI el subcomando `get-wave` en la CLI para descargar una onda.
1. Añadir a la CLI el subcomando `plot-wave` en la CLI para representar gráficamente una onda.

#### 4. Obtención y representación de espectros

1. Crear un método en `T8ApiClient` para listar los espectros disponibles en la API.
1. Crear un método en `T8ApiClient` para obtener un espectro desde la API y guardarlo en un archivo JSON.
1. Crear un método en `T8ApiClient` para crear un plot de un espectro desde un archivo JSON.

#### 5. Cálculo de espectros y comparación de resultados

1. Crear un método en `T8ApiClient` para calcular el espectro a partir de una onda descargada previamente.
1. Crear un script para comparar el espectro calculado con el espectro descargado de la API, representándolos gráficamente.

## Ejecución del código

### Obtención de datos de la API

El código se ejecuta mediante la línea de comandos (CLI), que incluirá los comandos siguientes:

- `list-waves`: lista las ondas capturadas en el equipo para una máquina, punto de medida y modo de procesamiento específicos, como una lista de fechas y horas en formato ISO 8601.

    ```txt
    $ t8-client list-waves -M MACHINE -p POINT -m PROC_MODE
    2025-01-01T12:00:00
    2025-01-01T12:05:00
    ...
    ```

- `list-spectra`: lista los espectros capturados en el equipo para una máquina, punto de medida y modo de procesamiento específicos, como una lista de fechas y horas en formato ISO 8601.

    ```txt
    $ t8-client list-spectra -M MACHINE -p POINT -m PROC_MODE
    2025-01-01T12:00:00
    2025-01-01T12:05:00
    ...
    ```

- `get-wave`: obtiene una onda correspondiente a una máquina, punto de medida, modo de procesamiento y fecha/hora específicos. La fecha y hora de la onda se podrá introducir en formato ISO 8601 (`-d`) o como timestamp de Linux (`-t`). La onda se descargará y guardará en un archivo JSON `data/waves/wave_<MACHINE>_<POINT>_<PROC_MODE>_<TIMESTAMP>.json`. Si no se especifica una onda mediante `-d` o `-t`, se descargará la onda más reciente.

    ```txt
    t8-client get-wave -M MACHINE -p POINT -m PROC_MODE [-d DATETIME | -t TIMESTAMP]
    ```

- `get-spectrum`: obtiene un espectro específico correspondiente a una máquina, punto de medida, modo de procesamiento y fecha/hora específicos. La fecha y hora de la onda se podrá introducir en formato ISO 8601 (`-d`) o como timestamp de Linux (`-t`). El espectro se descargará y guardará en un archivo JSON `data/spectra/spectrum_<MACHINE>_<POINT>_<PROC_MODE>_<TIMESTAMP>.json`. Si no se especifica un espectro mediante `-d` o `-t`, se descargará el espectro más reciente.

    ```txt
    t8-client get-spectrum -M MACHINE -p POINT -m PROC_MODE [-d DATETIME | -t TIMESTAMP]
    ```

- `plot-wave`: representa gráficamente una onda.

    ```txt
    t8-client plot-wave -M MACHINE -p POINT -m PROC_MODE [-d DATETIME | -t TIMESTAMP]
    ```

- `plot-spectrum`: representa gráficamente un espectro.

    ```txt
    t8-client plot-spectrum -M MACHINE -p POINT -m PROC_MODE [-d DATETIME | -t TIMESTAMP]
    ```

- `compute-spectrum`: calcula el espectro a partir de una onda descargada previamente en `data/waves/` y lo guarda en un archivo JSON `data/spectra/spectrum_<MACHINE>_<POINT>_<PROC_MODE>_<TIMESTAMP>_computed.json`.

    ```txt
    t8-client compute-spectrum -w WAVE_FILE
    ```

    El cálculo se realizará mediante la Transformada Rápida de Fourier (FFT) del paquete `numpy`. El espectro se calculará en un rango de frecuencias determinado por los parámetros `fmin` y `fmax`.

    ```python
    def compute_spectrum(waveform, sample_rate, fmin, fmax):
        """
        Compute the frequency spectrum of a given waveform within a specified frequency
        range.

        Parameters:
        waveform: The input signal waveform.
        sample_rate: The sampling rate of the waveform in Hz.
        fmin: The minimum frequency of interest in Hz.
        fmax: The maximum frequency of interest in Hz.

        Returns:
        A tuple containing:
            - filtered_freqs: The corresponding frequencies within the
                specified range.
            - filtered_spectrum: The magnitude of the frequency spectrum within
                the specified range, with an RMS AC detector.
        """
        spectrum = fft(waveform) * 2 * np.sqrt(2)
        magintude = np.abs(spectrum) / len(spectrum)
        freqs = fftfreq(len(waveform), 1 / sample_rate)
        filtered_spectrum = magintude[(freqs >= fmin) & (freqs <= fmax)]
        filtered_freqs = freqs[(freqs >= fmin) & (freqs <= fmax)]
        return filtered_freqs, filtered_spectrum
    ```

La comprobación de que el código funciona correctamente se realizará mediante la ejecución de estos comandos.

Los parámetros necesarios para calcular el espectro se obtendrán de la web del T8 para ese espectro.

Para crear los plots se utilizará `matplotlib`. Cada gráfica tendrá un título en el que se indique el tipo de dato, la máquina, el punto de medida, el modo de procesamiento y la fecha/hora del dato. También incluirán nombres de los ejes y sus unidades.

- Click: <https://click.palletsprojects.com/>
- NumPy FFT: <https://numpy.org/doc/stable/reference/generated/numpy.fft.fft.html>

### Comparación de espectros descargado y calculado

El espectro calculado se comparará con el espectro descargado de la API para comprobar que ambos coinciden, mediante un script `scripts/compare_spectra.py`, que creará un plot con dos subpltots, uno con el espectro descargado y otro con el espectro calculado.

### Implementación inicial

Puede ser recomendable comenzar con una máquina, punto, modo de procesamiento y fecha/hora específicos, sin usar parámetros en los comandos, y luego generalizar el código para que funcione con cualquier valor de los parámetros.

Por ejemplo, se puede implementar el código y la CLI para la onda: `MACHINE=LP_Turbine`, `POINT=MAD31CY005`, `PROC_MODE=AM1`, `DATETIME=2019-04-11T18:25:54` (UTC).

Del mismo modo, se puede calcular el espectro a partir de los parámetros definidos en la web del T8 para ese espectro.

Posteriormente se generalizará el código para que funcione con cualquier máquina, punto, modo de procesamiento y fecha/hora. Para el cálculo del espectro, se obtendrán desde la API los parámetros necesarios de la última configuración del equipo para el modo de procesamiento.

## Acceso a la API REST del T8

Para descargar los datos es necesario conectarse a un T8 virtual que sirve una API REST. En ella están disponibles diversos tipos de datos del T8: ondas, espectros, configuraciones, alarmas, etc.

La API de este equipo de demostración está accesible en la dirección `<HOST>/rest`; para el equipo de demostración, el host es <https://lzfs45.mirror.twave.io/lzfs45>. Para conectarse a este equipo, y a la API, se necesitan usuario y contraseña.

La API está documentada en <https://apidoc.twave.io/>. Aquí se pueden consultar las rutas a las que hay que hacer peticiones para el dato se quiere descargar. Por ejemplo, en el caso de las formas de onda, se obtienen desde la ruta `/waves`.

**Nota:** las llamadas a la API REST del T8 se realizarán mediante HTTP o HTTPS indistintamente, por lo que el código debe soportar ambos protocolos.

### Credenciales y variables de entorno

Los datos de acceso a la API REST del T8 se almacenarán como variables de entorno, ya sea exportandolas en el sistema o en un archivo `.env` (que no se subirá al repositorio). Estas variables tendrán los nombres siguientes:

- `T8_HOST`: URL de la API REST del T8.
- `T8_USER`: Nombre de usuario para acceder a la API REST del T8.
- `T8_PASSWORD`: Contraseña para acceder a la API REST del T8.

## Estructura del proyecto

### Organización del código

El código se organizará en paquetes y módulos, según las necesidades, siguiendo las mejores prácticas para proyectos de Python.

Se utilizarán clases para organizar el código.

El proyecto tendrá una estructura similar a la siguiente:

```txt
t8-client/
|-- src/
|   |-- t8_client/               # Paquete principal
|   |   |-- __init__.py          
|   |   |-- api.py               # Módulo para gestionar la API REST del T8
|   |   |-- cli.py               # Módulo para la CLI usando Click
|   |   |-- waveform.py          # Definición de la clase Waveform 
|   |   \-- ...
|-- tests/                       # Tests del proyecto, organizados por módulos
|   |-- __init__.py
|   |-- test_api.py
|   |-- test_cli.py
|   |-- test_waveform.py
|   \-- ...
|-- data/                        # Datos descargados para pruebas
|   |-- waves/                   # Datos de ondas descargados
|   |-- spectra/                 # Datos de espectros descargados
|   |-- plots/                   # Plots generados
|   |-- api_data/                # Archivos descargados de la API
|   \-- ...
|-- scripts/                     # Scripts de utilidad
|   \-- ...
|-- .env                         # Archivo con variables de entorno
|-- .gitignore                   # Archivos y directorios a ignorar en Git
|-- README.md                    # Descripción del proyecto
|-- pyproject.toml               # Configuración del proyecto y dependencias
|-- uv.lock                      # Archivo de bloqueo de dependencias de uv
\-- ...
```

La estructura puede variar para adaptarse a las necesidades del proyecto, pero debe seguir las mejores prácticas para proyectos de Python.

### Gestión del proyecto y dependencias

Se utilizará `uv` para gestionar el proyecto y las dependencias. El archivo `pyproject.toml` se utilizará para definir las dependencias del proyecto, así como la configuración del paquete.

- Getting Started with uv: <https://docs.astral.sh/uv/getting-started/first-steps/>

### Organización de datos

El directorio `data/` se utiliza para almacenar los datos descargados de la API del T8 durante el desarrollo y las pruebas:

- `data/waves/`: Archivos JSON con datos de ondas individuales descargados.
- `data/spectra/`: Archivos JSON con datos de espectros individuales descargados.
- `data/plots/`: Plots generados.
- `data/api_data/`: Archivos descargados de la API que no sean ondas o espectros.

**Importante:** Los archivos de datos se excluyen del control de versiones (están en `.gitignore`) para evitar subir archivos grandes al repositorio.

### Nombres de archivos de datos por defecto

Los scripts deben utilizar los siguientes nombres de archivos por defecto:

- Datos de ondas: `data/waves/wave_MACHINE_POINT_MODE_TIMESTAMP.json`
- Datos de espectros: `data/spectra/spectrum_MACHINE_POINT_MODE_TIMESTAMP.json`

### Repositorio GitHub

Se creará un repositorio en GitHub para gestionar el código del proyecto. El repositorio tendrá acceso público.

En este repositorio se incluirá un archivo `README.md` con la descripción del proyecto. Debe explicar cómo instalar el paquete y ejecutar el código y los comandos disponibles en la CLI.

Los cambios en el código se añadirán al repositorio usando commits bien organizados y definidos, con mensajes claros y descriptivos de los cambios realizados.

**Importante:** No se debe subir al repositorio información sensible, como credenciales, tokens de acceso, etc. Se añadirán al archivo `.gitignore` los archivos que contengan este tipo de información, especialmente archivos `.env` o similares.

También se incluirán en `.gitignore` los archivos de configuración del entorno de desarrollo, así como los archivos generados automáticamente por el entorno de desarrollo o el sistema operativo.

- Tutorial Git: <https://learngitbranching.js.org/?locale=es_ES>
- GitHub Gist - Git Tips and Commit Best Practices: <https://gist.github.com/luismts/495d982e8c5b1a0ced4a57cf3d93cf60>
- GitHub Docs - Set up Git: <https://docs.github.com/en/get-started/getting-started-with-git/set-up-git>
- GitHub Docs - Git Basics: <https://docs.github.com/en/get-started/git-basics>

### Comentarios y docstrings

Se escribirán comentarios en el código para explicar las partes más complejas o importantes. Los comentarios explicarán POR QUÉ se hace algo, no CÓMO se hace. Serán claros y concisos.

Las clases y funciones se documentarán mediante docstrings, siguiendo las recomendaciones para la documentación de código en Python.

- Formatos de Docstrings: <https://www.datacamp.com/tutorial/docstrings-python>

### Tests

Se escribirán tests para comprobar que el código funciona correctamente y los diferentes elementos devuelven los resultados esperados. Los tests se organizarán en un directorio `tests/`, separando los tests por módulos o funcionalidades.

Se utilizará `pytest` para la realización de tests:

```bash
uv add --dev pytest 
uv run pytest
```

Se crearán `mocks` para simular las respuestas de la API REST del T8, evitando realizar llamadas reales, de forma que los tests no dependan de la disponibilidad del equipo, así como de cualquier otro componente que resulte necesario.

- Effective Python Testing with Pytest: <https://realpython.com/pytest-python-testing/>
- Comprehensive Mocking Guide: <https://pytest-with-eric.com/mocking/pytest-mocking/>
- `pytest-mock` Documentation: <https://pytest-mock.readthedocs.io>
- `unittest.mock` Examples: <https://docs.python.org/3/library/unittest.mock-examples.html>

### Estilo de código y linting

Se utilizará `Ruff` para el linting del código, siguiendo las mejores prácticas recomendadas para proyectos de Python.

```bash
uv add --dev ruff
uv run ruff check .
```

Las reglas de linting a aplicar se definirán en el archivo `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
lint.select = ["ANN", "Q", "E", "F", "UP", "B", "I", "Q"]
lint.ignore = []
lint.exclude = []
```

**Importante:** Cada commit que se realice deberá pasar tanto los tests como el linting sin ningún error.

- Ruff: <https://docs.astral.sh/ruff/>

## Bonus

Se pueden implementar otras funcionalidades adicionales para complementar las anteriores, por ejemplo:

- Obtener la configuración del espectro: en el caso anterior se calculó el espectro mediante parámetros definidos en el código; en este caso se propone descargar la configuración desde la API y extraer de ella los parámetros.
- Obtener las unidades de los datos descargados desde la API y mostrarlas en los plots.
- Creación de otros comandos como:
  - Listar las máquinas o modos de procesamiento existentes en el equipo.
  - Listar todas las ondas y espectros disponibles junto con sus metadatos y almacenarlos en un archivo CSV.
