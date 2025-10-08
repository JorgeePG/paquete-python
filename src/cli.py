import click
import os
from dotenv import load_dotenv
from .t8_client import T8ApiClient

# Cargar variables de entorno
load_dotenv()

@click.group()
def cli():
    """CLI para interactuar con la API T8."""
    pass

@cli.command()
@click.option('-M', '--machine', required=True, help='Machine ID')
@click.option('-P', '--point', required=True, help='Point of the machine')
@click.option('-m', '--mode', required=True, help='Processing mode')
def list_waves(machine, point, mode):
    """Lista las ondas según los parámetros especificados."""
    client = T8ApiClient()
    
    # Obtener credenciales del archivo .env
    username = os.getenv('T8_USER')
    password = os.getenv('T8_PASSWORD')
    
    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: No se pudo autenticar", err=True)
            return
    else:
        click.echo("Error: No se encontraron credenciales en el archivo .env", err=True)
        return
    
    # Llamar al método corregido
    client.listWaves(machine, point, mode)

@cli.command()
def list_all_waves():
    """Lista todas las ondas disponibles."""
    client = T8ApiClient()
    
    # Obtener credenciales del archivo .env
    username = os.getenv('T8_USER')
    password = os.getenv('T8_PASSWORD')
    
    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: No se pudo autenticar", err=True)
            return
    else:
        click.echo("Error: No se encontraron credenciales en el archivo .env", err=True)
        return
    
    client.list_available_waves()

if __name__ == '__main__':
    cli()


