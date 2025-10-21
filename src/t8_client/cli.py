import os

import click  # type: ignore
from dotenv import load_dotenv  # type: ignore

from t8_client.t8_client import T8ApiClient

# Load environment variables
load_dotenv()


@click.group()
def cli() -> None:
    """CLI to interact with the T8 API."""
    pass


@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
def list_waves(machine: str, point: str, mode: str) -> None:
    """Lists waves according to the specified parameters."""
    client = T8ApiClient()

    # Get credentials from .env file
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: Could not authenticate", err=True)
            return
    else:
        click.echo("Error: Credentials not found in .env file", err=True)
        return

    # Call the corrected method
    client.list_waves(machine, point, mode)


@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
def list_spectra(machine: str, point: str, mode: str) -> None:
    """Lists spectra according to the specified parameters."""
    client = T8ApiClient()

    # Get credentials from .env file
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: Could not authenticate", err=True)
            return
    else:
        click.echo("Error: Credentials not found in .env file", err=True)
        return

    # Call the correct method
    client.list_spectra(machine, point, mode)


@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
@click.option(
    "-d", "--date", required=False, help="Date in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
)
@click.option("-t", "--timestamp", required=False, help="Unix timestamp")
def get_wave(
    machine: str,
    point: str,
    mode: str,
    date: str | None = None,
    timestamp: str | None = None,
) -> None:
    """Gets a specific wave according to the specified parameters.

    If -d (date) or -t (timestamp) are not specified, the most
    recent wave is downloaded.
    The date must be in ISO 8601 format (2019-04-11T16:43:22).
    The timestamp must be a Unix timestamp integer value."""

    # Validate that both options are not specified
    if date and timestamp:
        click.echo(
            "Error: Cannot specify both --date and --timestamp " + "at the same time",
            err=True,
        )
        return

    # Determine the value to use
    date_value = "0"  # Default value to get the most recent
    if date:
        date_value = date
    elif timestamp:
        date_value = timestamp

    client = T8ApiClient()

    # Get credentials from .env file
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: Could not authenticate", err=True)
            return
    else:
        click.echo("Error: Credentials not found in .env file", err=True)
        return

    client.get_wave(machine, point, mode, date_value)


@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
@click.option(
    "-d", "--date", required=False, help="Date in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
)
@click.option("-t", "--timestamp", required=False, help="Unix timestamp")
def get_spectrum(
    machine: str,
    point: str,
    mode: str,
    date: str | None = None,
    timestamp: str | None = None,
) -> None:
    """Gets a specific spectrum according to the specified parameters.

    If -d (date) or -t (timestamp) are not specified, the most
    recent spectrum is downloaded.
    The date must be in ISO 8601 format (2019-04-11T16:43:22).
    The timestamp must be a Unix timestamp integer value."""

    # Validate that both options are not specified
    if date and timestamp:
        click.echo(
            "Error: Cannot specify both --date and --timestamp " + "at the same time",
            err=True,
        )
        return

    # Determine the value to use
    date_value = "0"  # Default value to get the most recent
    if date:
        date_value = date
    elif timestamp:
        date_value = timestamp

    client = T8ApiClient()

    # Get credentials from .env file
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: Could not authenticate", err=True)
            return
    else:
        click.echo("Error: Credentials not found in .env file", err=True)
        return

    client.get_spectrum(machine, point, mode, date_value)


@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
@click.option(
    "-d", "--date", required=False, help="Date in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
)
@click.option("-t", "--timestamp", required=False, help="Unix timestamp")
def plot_wave(
    machine: str,
    point: str,
    mode: str,
    date: str | None = None,
    timestamp: str | None = None,
) -> None:
    """Generates a plot of the specified wave.

    If -d (date) or -t (timestamp) are not specified, the most
    recent wave will be plotted.
    The date must be in ISO 8601 format (2019-04-11T16:43:22).
    The timestamp must be a Unix timestamp integer value."""

    # Validate that both options are not specified
    if date and timestamp:
        click.echo(
            "Error: Cannot specify both --date and --timestamp " + "at the same time",
            err=True,
        )
        return

    # Determine the value to use
    date_value = "0"  # Default value to get the most recent
    if date:
        date_value = date
    elif timestamp:
        date_value = timestamp

    client = T8ApiClient()

    # Get credentials from .env file
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: Could not authenticate", err=True)
            return
    else:
        click.echo("Error: Credentials not found in .env file", err=True)
        return

    client.plot_wave(machine, point, mode, date_value)


@cli.command()
@click.option("-M", "--machine", required=True, help="Machine ID")
@click.option("-P", "--point", required=True, help="Point of the machine")
@click.option("-m", "--mode", required=True, help="Processing mode")
@click.option(
    "-d", "--date", required=False, help="Date in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
)
@click.option("-t", "--timestamp", required=False, help="Unix timestamp")
def plot_spectrum(
    machine: str,
    point: str,
    mode: str,
    date: str | None = None,
    timestamp: str | None = None,
) -> None:
    """Generates a plot of the specified spectrum.

    If -d (date) or -t (timestamp) are not specified, the most
    recent wave will be plotted.
    The date must be in ISO 8601 format (2019-04-11T16:43:22).
    The timestamp must be a Unix timestamp integer value."""

    # Validate that both options are not specified
    if date and timestamp:
        click.echo(
            "Error: Cannot specify both --date and --timestamp " + "at the same time",
            err=True,
        )
        return

    # Determine the value to use
    date_value = "0"  # Default value to get the most recent
    if date:
        date_value = date
    elif timestamp:
        date_value = timestamp

    client = T8ApiClient()

    # Get credentials from .env file
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: Could not authenticate", err=True)
            return
    else:
        click.echo("Error: Credentials not found in .env file", err=True)
        return

    client.plot_spectrum(machine, point, mode, date_value)


@cli.command()
def list_all_waves() -> None:
    """Lists all available waves."""
    client = T8ApiClient()

    # Get credentials from .env file
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: Could not authenticate", err=True)
            return
    else:
        click.echo("Error: Credentials not found in .env file", err=True)
        return

    client.list_available_waves()


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
def compute_spectrum(filename: str) -> None:
    """Computes the spectrum from a local JSON file."""
    client = T8ApiClient()

    # Get credentials from .env file
    # (necessary to obtain API configuration)
    username = os.getenv("T8_USER")
    password = os.getenv("T8_PASSWORD")

    if username and password:
        if not client.login_with_credentials(username, password):
            click.echo("Error: Could not authenticate", err=True)
            return
    else:
        click.echo("Error: Credentials not found in .env file", err=True)
        return

    client.compute_spectrum_with_json(filename)


@cli.command()
@click.argument("spectrum_file", type=click.Path(exists=True))
@click.argument("wave_file", type=click.Path(exists=True))
@click.option("-o", "--output", help="Output file for the plot")
def compare_spectra(
    spectrum_file: str, wave_file: str, output: str | None = None
) -> None:
    """Compares an API spectrum with a spectrum calculated from a wave.

    SPECTRUM_FILE: JSON file of the spectrum downloaded from the API
    WAVE_FILE: JSON file of the wave to calculate the spectrum
    """
    import subprocess
    import sys
    from pathlib import Path

    # Path to comparison script
    script_path = Path(__file__).parent.parent.parent / "scripts" / "compare_spectra.py"

    if not script_path.exists():
        click.echo(f"Error: Comparison script not found at {script_path}", err=True)
        return

    # Build command to execute the script
    cmd = [sys.executable, str(script_path), spectrum_file, wave_file]
    if output:
        cmd.extend(["-o", output])

    try:
        # Execute comparison script
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Show output
        if result.stdout:
            click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)

        # Check exit code
        if result.returncode != 0:
            click.echo(
                f"Error: Comparison script failed with code {result.returncode}",
                err=True,
            )

    except Exception as e:
        click.echo(f"Error executing comparison script: {e}", err=True)


if __name__ == "__main__":
    cli()
