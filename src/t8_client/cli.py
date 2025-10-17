import os

import click # type: ignore
from dotenv import load_dotenv # type: ignore

from t8_client import T8ApiClient

# Cargar variables de entorno
load_dotenv()

@click.group()
def cli()-> None:
    """CLI para interactuar con la API T8."""
    pass

@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
def list_waves(machine: str, point: str, mode: str) -> None:
    """Lista las ondas según los parámetros especificados."""
    client = T8ApiClient()
    
    # Obtener credenciales del archivo .env
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")
    
    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: No se pudo autenticar", err=True)
            return
    else:
        click.echo("Error: No se encontraron credenciales en el archivo .env", err=True)
        return
    
    # Llamar al método corregido
    client.list_waves(machine, point, mode)

@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
def list_spectra(machine: str, point: str, mode: str) -> None:
    """Lista los espectros según los parámetros especificados."""
    client = T8ApiClient()
    
    # Obtener credenciales del archivo .env
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")
    
    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: No se pudo autenticar", err=True)
            return
    else:
        click.echo("Error: No se encontraron credenciales en el archivo .env", err=True)
        return
    
    # Llamar al método correcto
    client.list_spectra(machine, point, mode)

@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
@click.option(
    "-d",
    "--date",
    required=False,
    help="Date in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
)
@click.option(
    "-t",
    "--timestamp", 
    required=False,
    help="Unix timestamp"
)
def get_wave(
    machine: str, point: str, mode: str, 
    date: str | None = None, timestamp: str | None = None
) -> None:
    """Obtiene una onda específica según los parámetros especificados.
    
    Si no se especifica -d (fecha) o -t (timestamp), se descarga la 
    onda más reciente.
    La fecha debe estar en formato ISO 8601 (2019-04-11T16:43:22).
    El timestamp debe ser un valor Unix timestamp entero."""
    
    # Validar que no se especifiquen ambas opciones
    if date and timestamp:
        click.echo(
            "Error: No se pueden especificar tanto --date como --timestamp " +
            "al mismo tiempo", 
            err=True
        )
        return
    
    # Determinar el valor a usar
    date_value = "0"  # Valor por defecto para obtener la más reciente
    if date:
        date_value = date
    elif timestamp:
        date_value = timestamp
    
    client = T8ApiClient()

    # Obtener credenciales del archivo .env
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: No se pudo autenticar", err=True)
            return
    else:
        click.echo("Error: No se encontraron credenciales en el archivo .env", err=True)
        return

    client.get_wave(machine, point, mode, date_value)

@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
@click.option(
    "-d",
    "--date",
    required=False,
    help="Date in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
)
@click.option(
    "-t",
    "--timestamp", 
    required=False,
    help="Unix timestamp"
)
def get_spectrum(
    machine: str, point: str, mode: str, 
    date: str | None = None, timestamp: str | None = None
) -> None:
    """Obtiene un espectro específico según los parámetros especificados.

    Si no se especifica -d (fecha) o -t (timestamp), se descarga el 
    espectro más reciente.
    La fecha debe estar en formato ISO 8601 (2019-04-11T16:43:22).
    El timestamp debe ser un valor Unix timestamp entero."""
    
    # Validar que no se especifiquen ambas opciones
    if date and timestamp:
        click.echo(
            "Error: No se pueden especificar tanto --date como --timestamp " +
            "al mismo tiempo", 
            err=True
        )
        return
    
    # Determinar el valor a usar
    date_value = "0"  # Valor por defecto para obtener la más reciente
    if date:
        date_value = date
    elif timestamp:
        date_value = timestamp
    
    client = T8ApiClient()

    # Obtener credenciales del archivo .env
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: No se pudo autenticar", err=True)
            return
    else:
        click.echo("Error: No se encontraron credenciales en el archivo .env", err=True)
        return

    client.get_spectrum(machine, point, mode, date_value)

@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
@click.option(
    "-d",
    "--date",
    required=False,
    help="Date in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
)
@click.option(
    "-t",
    "--timestamp", 
    required=False,
    help="Unix timestamp"
)
def plot_wave(
    machine: str, point: str, mode: str, 
    date: str | None = None, timestamp: str | None = None
) -> None:
    """Genera un gráfico de la onda especificada.
    
    Si no se especifica -d (fecha) o -t (timestamp), se graficará la 
    onda más reciente.
    La fecha debe estar en formato ISO 8601 (2019-04-11T16:43:22).
    El timestamp debe ser un valor Unix timestamp entero."""
    
    # Validar que no se especifiquen ambas opciones
    if date and timestamp:
        click.echo(
            "Error: No se pueden especificar tanto --date como --timestamp " +
            "al mismo tiempo", 
            err=True
        )
        return
    
    # Determinar el valor a usar
    date_value = "0"  # Valor por defecto para obtener la más reciente
    if date:
        date_value = date
    elif timestamp:
        date_value = timestamp
    
    client = T8ApiClient()

    # Obtener credenciales del archivo .env
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: No se pudo autenticar", err=True)
            return
    else:
        click.echo("Error: No se encontraron credenciales en el archivo .env", err=True)
        return

    client.plot_wave(machine, point, mode, date_value)

@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
@click.option(
    "-d",
    "--date",
    required=False,
    help="Date in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
)
@click.option(
    "-t",
    "--timestamp", 
    required=False,
    help="Unix timestamp"
)
def plot_spectrum(
    machine: str, point: str, mode: str, 
    date: str | None = None, timestamp: str | None = None
) -> None:
    """Genera un gráfico de  espectro especificado.
    
    Si no se especifica -d (fecha) o -t (timestamp), se graficará la 
    onda más reciente.
    La fecha debe estar en formato ISO 8601 (2019-04-11T16:43:22).
    El timestamp debe ser un valor Unix timestamp entero."""
    
    # Validar que no se especifiquen ambas opciones
    if date and timestamp:
        click.echo(
            "Error: No se pueden especificar tanto --date como --timestamp " +
            "al mismo tiempo", 
            err=True
        )
        return
    
    # Determinar el valor a usar
    date_value = "0"  # Valor por defecto para obtener la más reciente
    if date:
        date_value = date
    elif timestamp:
        date_value = timestamp
    
    client = T8ApiClient()

    # Obtener credenciales del archivo .env
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: No se pudo autenticar", err=True)
            return
    else:
        click.echo("Error: No se encontraron credenciales en el archivo .env", err=True)
        return

    client.plot_spectrum(machine, point, mode, date_value)

@cli.command()
def list_all_waves() -> None:
    """Lista todas las ondas disponibles."""
    client = T8ApiClient()
    
    # Obtener credenciales del archivo .env
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")
    
    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: No se pudo autenticar", err=True)
            return
    else:
        click.echo("Error: No se encontraron credenciales en el archivo .env", err=True)
        return
    
    client.list_available_waves()

@cli.command()
@click.argument("filename", type=click.Path(exists=True))
def compute_spectrum(filename: str) -> None:
    """Computa el espectro a partir de un archivo JSON local."""
    client = T8ApiClient()
    
    # Obtener credenciales del archivo .env 
    # (necesario para obtener configuración de la API)
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")
    
    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: No se pudo autenticar", err=True)
            return
    else:
        click.echo("Error: No se encontraron credenciales en el archivo .env", err=True)
        return
    
    client.compute_spectrum_with_json(filename)

@cli.command()
@click.argument("spectrum_file", type=click.Path(exists=True))
@click.argument("wave_file", type=click.Path(exists=True))
@click.option("-o", "--output", help="Archivo de salida para el gráfico")
def compare_spectra(
    spectrum_file: str, wave_file: str, output: str | None = None
) -> None:
    """Compara un espectro de la API con un espectro calculado desde una onda.
    
    SPECTRUM_FILE: Archivo JSON del espectro descargado de la API
    WAVE_FILE: Archivo JSON de la onda para calcular el espectro
    """
    import sys
    import subprocess
    from pathlib import Path
    
    # Ruta al script de comparación
    script_path = Path(__file__).parent.parent.parent / "scripts" / "compare_spectra.py"
    
    if not script_path.exists():
        click.echo(
            f"Error: Script de comparación no encontrado en {script_path}", 
            err=True
        )
        return
    
    # Construir comando para ejecutar el script
    cmd = [sys.executable, str(script_path), spectrum_file, wave_file]
    if output:
        cmd.extend(["-o", output])
    
    try:
        # Ejecutar el script de comparación
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Mostrar la salida
        if result.stdout:
            click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)
        
        # Verificar el código de salida
        if result.returncode != 0:
            click.echo(
                f"Error: El script de comparación falló con código "
                f"{result.returncode}", 
                err=True
            )
        
    except Exception as e:
        click.echo(f"Error ejecutando script de comparación: {e}", err=True)

if __name__ == "__main__":
    cli()
