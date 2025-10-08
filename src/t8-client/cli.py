import os

import click
from dotenv import load_dotenv

from .t8_client import T8ApiClient

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
    
    # Llamar al método corregido
    client.list_waves(machine, point, mode)

@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
@click.option("-d", "--date", required=False, 
              help="Date in ISO 8601 format(YYYY-MM-DDTHH:MM:SS) or Unix timestamp")
def get_wave(machine: str, point: str, mode: str, date: int | None = 0) -> None:
    """Obtiene una onda específica según los parámetros especificados.
    
    La fecha puede ser en formato ISO 8601 (2019-04-11T16:43:22) o timestamp Unix.
    Si no se especifica fecha, se descarga la onda más reciente."""
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

    client.getWave(machine, point, mode, date)

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

if __name__ == "__main__":
    cli()


