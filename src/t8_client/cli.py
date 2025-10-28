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


@cli.command()
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True),
    help="Path to configuration file (default: uses API config)",
)
@click.option(
    "-q",
    "--question",
    help="Single question to ask about the configuration",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Start interactive conversation mode",
)
@click.option(
    "-s",
    "--stream",
    is_flag=True,
    help="Stream responses in real-time",
)
@click.option(
    "-t",
    "--temperature",
    type=float,
    default=0.6,
    help="Model temperature (0.0-1.0, default: 0.6)",
)
@click.option(
    "--no-chunking",
    is_flag=True,
    help="Disable chunked analysis strategy (process config as a whole)",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed progress during chunked analysis",
)
@click.option(
    "--cache-max-age",
    type=float,
    default=24.0,
    help="Max age of cache in hours (default: 24)",
)
@click.option(
    "--clear-cache",
    is_flag=True,
    help="Clear the analysis cache and exit",
)
@click.option(
    "--cache-stats",
    is_flag=True,
    help="Show cache statistics and exit",
)
def chat_config(
    config_file: str | None = None,
    question: str | None = None,
    interactive: bool = False,
    stream: bool = False,
    temperature: float = 0.6,
    no_chunking: bool = False,
    verbose: bool = False,
    cache_max_age: float = 24.0,
    clear_cache: bool = False,
    cache_stats: bool = False,
) -> None:
    """Chat with LLM about T8 configuration files.

    Uses "Divide and Conquer" strategy with caching for efficient analysis
    of large configuration files.

    Examples:

        # Ask a single question about API config
        t8-cli chat-config -q "What are the main measurement points?"

        # Ask about a local config file with verbose output
        t8-cli chat-config -c llm/config.json -q "What sampling rates?" --verbose

        # Interactive mode with streaming
        t8-cli chat-config -i -s

        # Interactive mode with a specific file (no chunking)
        t8-cli chat-config -c llm/config.json -i --no-chunking

        # Clear the analysis cache
        t8-cli chat-config --clear-cache

        # Show cache statistics
        t8-cli chat-config --cache-stats
    """
    import json

    try:
        from llm_client import GroqLLMClient
    except ImportError:
        click.echo(
            "❌ Error: LLM client not available. Make sure 'groq' is installed.",
            err=True,
        )
        click.echo("   Run: pip install groq", err=True)
        return

    # Initialize LLM client
    try:
        llm_client = GroqLLMClient()
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        click.echo(
            "   Make sure GROQ_API_KEY is set in your .env file or environment.",
            err=True,
        )
        return

    # Handle cache management commands
    if clear_cache:
        click.echo("🧹 Clearing analysis cache...")
        result = llm_client.clear_cache()
        if result["success"]:
            click.echo(f"   ✅ {result['message']}")
        else:
            click.echo(f"   ❌ {result['message']}", err=True)
        return

    if cache_stats:
        click.echo("📊 Cache Statistics:\n")
        stats = llm_client.get_cache_stats()
        if stats.get("available"):
            click.echo(f"   Total entries: {stats.get('total_entries', 0)}")
            click.echo(
                f"   Total size: {stats.get('total_size_bytes', 0) / 1024:.2f} KB"
            )
            click.echo(f"   Configurations: {len(stats.get('configs', []))}")
            click.echo("\n   Chunk types:")
            for chunk_type, count in stats.get("chunk_types", {}).items():
                click.echo(f"      - {chunk_type}: {count}")
        else:
            click.echo(f"   ❌ {stats.get('message', 'Not available')}")
        return

    # Load configuration
    config_data = None
    config_source = "API configuration"

    # Load API definitions from DocComprimida.md if available
    api_definitions = None
    doc_file = "llm/DocComprimida.md"
    try:
        with open(doc_file, encoding="utf-8") as f:
            api_definitions = f.read()
        click.echo(f"✅ Loaded API documentation from: {doc_file}")
    except FileNotFoundError:
        click.echo(f"⚠️  API documentation not found at: {doc_file}")
    except Exception as e:
        click.echo(f"⚠️  Could not load API documentation: {e}")

    if config_file:
        # Load from file
        try:
            with open(config_file, encoding="utf-8") as f:
                config_data = json.load(f)
            config_source = config_file
            click.echo(f"✅ Loaded configuration from: {config_file}")
        except Exception as e:
            click.echo(f"❌ Error loading config file: {e}", err=True)
            return
    else:
        # Get configuration from API
        client = T8ApiClient()
        username = os.getenv("T8_USER")
        password = os.getenv("T8_PASSWORD")

        if not (username and password):
            click.echo("❌ Error: T8 credentials not found in .env file", err=True)
            return

        if not client.login_with_credentials(username, password):
            click.echo("❌ Error: Could not authenticate with T8 API", err=True)
            return

        # Try to get configuration from the API
        try:
            config_data = client.get_configuration()
            if not config_data:
                click.echo(
                    "⚠️  Warning: Could not retrieve configuration from API",
                    err=True,
                )
                click.echo("   Use -c to specify a local configuration file", err=True)
                return
            click.echo("✅ Loaded configuration from T8 API")
        except Exception as e:
            click.echo(f"❌ Error getting API configuration: {e}", err=True)
            click.echo("   Use -c to specify a local configuration file", err=True)
            return

    # Single question mode
    if question and not interactive:
        click.echo(f"\n🤔 Question: {question}")
        if not no_chunking:
            click.echo("🧩 Using chunked analysis strategy with cache...")
        click.echo("💭 Thinking...\n")

        try:
            if stream:
                click.echo("📝 Answer:\n")
                for chunk in llm_client.ask_about_config(
                    question=question,
                    config_data=config_data,
                    api_definitions=api_definitions,
                    temperature=temperature,
                    stream=True,
                    use_chunking=not no_chunking,
                    max_cache_age_hours=cache_max_age,
                    verbose=verbose,
                ):
                    click.echo(chunk, nl=False)
                click.echo("\n")
            else:
                answer = llm_client.ask_about_config(
                    question=question,
                    config_data=config_data,
                    api_definitions=api_definitions,
                    temperature=temperature,
                    use_chunking=not no_chunking,
                    max_cache_age_hours=cache_max_age,
                    verbose=verbose,
                )
                click.echo(f"📝 Answer:\n{answer}\n")
        except Exception as e:
            click.echo(f"\n❌ Error: {e}", err=True)
        return

    # Interactive mode
    if interactive or not question:
        click.echo("\n" + "=" * 60)
        click.echo("🤖 T8 Configuration Chat (Interactive Mode)")
        click.echo("=" * 60)
        click.echo(f"📋 Configuration source: {config_source}")
        click.echo(f"🌡️  Temperature: {temperature}")
        click.echo(f"📡 Streaming: {'Enabled' if stream else 'Disabled'}")
        chunking_status = "Disabled" if no_chunking else "Enabled (with cache)"
        click.echo(f"🧩 Chunking: {chunking_status}")
        if not no_chunking:
            click.echo(f"⏰ Cache max age: {cache_max_age} hours")
        click.echo("\nCommands:")
        click.echo("  - Type your question and press Enter")
        click.echo("  - Type 'analyze' for full configuration analysis")
        click.echo("  - Type 'help' for suggestions")
        click.echo("  - Type 'cache-stats' to see cache statistics")
        click.echo("  - Type 'clear-cache' to clear the cache")
        click.echo("  - Type 'exit' or 'quit' to exit")
        click.echo("=" * 60 + "\n")

        while True:
            try:
                user_input = click.prompt("You", type=str, prompt_suffix="> ")

                if not user_input.strip():
                    continue

                # Check for exit commands
                if user_input.lower() in ["exit", "quit", "q"]:
                    click.echo("\n👋 Goodbye!")
                    break

                # Special commands
                if user_input.lower() == "help":
                    click.echo("\n💡 Suggested questions:")
                    click.echo("  - What machines are configured in this system?")
                    click.echo("  - What are the main measurement points?")
                    click.echo("  - What processing modes are available?")
                    click.echo("  - What parameters are being monitored?")
                    click.echo("  - What are the alarm thresholds for MAD31CY005?")
                    click.echo("  - Explain the storage strategies")
                    click.echo("  - What sampling rates are used?\n")
                    continue

                if user_input.lower() == "cache-stats":
                    click.echo("\n📊 Cache Statistics:")
                    stats = llm_client.get_cache_stats()
                    if stats.get("available"):
                        click.echo(f"   Total entries: {stats.get('total_entries', 0)}")
                        size_kb = stats.get("total_size_bytes", 0) / 1024
                        click.echo(f"   Total size: {size_kb:.2f} KB")
                        configs = stats.get("configs", [])
                        click.echo(f"   Configurations: {len(configs)}")
                        click.echo("   Chunk types:")
                        for chunk_type, count in stats.get("chunk_types", {}).items():
                            click.echo(f"      - {chunk_type}: {count}")
                    else:
                        click.echo(f"   ❌ {stats.get('message', 'Not available')}")
                    click.echo()
                    continue

                if user_input.lower() == "clear-cache":
                    click.echo("\n🧹 Clearing analysis cache...")
                    result = llm_client.clear_cache()
                    if result["success"]:
                        click.echo(f"   ✅ {result['message']}\n")
                    else:
                        click.echo(f"   ❌ {result['message']}\n", err=True)
                    continue

                if user_input.lower() == "analyze":
                    click.echo("\n💭 Analyzing configuration...\n")
                    try:
                        if stream:
                            click.echo("LLM", nl=False)
                            click.echo("> ", nl=False)
                            for chunk in llm_client.analyze_t8_configuration(
                                config_data=config_data,
                                api_definitions=api_definitions,
                                temperature=temperature,
                                stream=True,
                                use_chunking=not no_chunking,
                                max_cache_age_hours=cache_max_age,
                                verbose=verbose,
                            ):
                                click.echo(chunk, nl=False)
                            click.echo("\n")
                        else:
                            answer = llm_client.analyze_t8_configuration(
                                config_data=config_data,
                                api_definitions=api_definitions,
                                temperature=temperature,
                                use_chunking=not no_chunking,
                                max_cache_age_hours=cache_max_age,
                                verbose=verbose,
                            )
                            click.echo(f"LLM> {answer}\n")
                    except Exception as e:
                        click.echo(f"❌ Error: {e}\n", err=True)
                    continue

                # Regular question
                click.echo()
                try:
                    if stream:
                        click.echo("LLM", nl=False)
                        click.echo("> ", nl=False)
                        for chunk in llm_client.ask_about_config(
                            question=user_input,
                            config_data=config_data,
                            api_definitions=api_definitions,
                            temperature=temperature,
                            stream=True,
                            use_chunking=not no_chunking,
                            max_cache_age_hours=cache_max_age,
                            verbose=verbose,
                        ):
                            click.echo(chunk, nl=False)
                        click.echo("\n")
                    else:
                        answer = llm_client.ask_about_config(
                            question=user_input,
                            config_data=config_data,
                            api_definitions=api_definitions,
                            temperature=temperature,
                            use_chunking=not no_chunking,
                            max_cache_age_hours=cache_max_age,
                            verbose=verbose,
                        )
                        click.echo(f"LLM> {answer}\n")
                except Exception as e:
                    click.echo(f"❌ Error: {e}\n", err=True)

            except (KeyboardInterrupt, EOFError):
                click.echo("\n\n👋 Goodbye!")
                break

    # If no question and not interactive, show default analysis
    elif not question:
        click.echo("\n💭 Analyzing T8 configuration...\n")
        if not no_chunking:
            click.echo("🧩 Using chunked analysis strategy with cache...\n")

        try:
            if stream:
                click.echo("📝 Analysis:\n")
                for chunk in llm_client.analyze_t8_configuration(
                    config_data=config_data,
                    temperature=temperature,
                    stream=True,
                    use_chunking=not no_chunking,
                    max_cache_age_hours=cache_max_age,
                    verbose=verbose,
                ):
                    click.echo(chunk, nl=False)
                click.echo("\n")
            else:
                answer = llm_client.analyze_t8_configuration(
                    config_data=config_data,
                    temperature=temperature,
                    use_chunking=not no_chunking,
                    max_cache_age_hours=cache_max_age,
                    verbose=verbose,
                )
                click.echo(f"📝 Analysis:\n{answer}\n")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)


@cli.command()
def model_info() -> None:
    """Muestra información sobre los modelos LLM disponibles y su estrategia de uso."""
    try:
        from llm_client.model_selector import ModelSelector

        stats = ModelSelector.get_model_stats()

        click.echo("🤖 **MODELOS LLM DISPONIBLES**\n")
        click.echo(f"Total de modelos configurados: {stats['total_models']}\n")

        click.echo("📊 **CATÁLOGO DE MODELOS:**\n")
        for name, info in stats["models"].items():
            tier_emoji = "💰" * info["cost_tier"]
            speed_emoji = {"fast": "⚡", "medium": "🔄", "slow": "🐢"}.get(
                info["speed"], "❓"
            )
            quality_emoji = {
                "basic": "⭐",
                "good": "⭐⭐",
                "excellent": "⭐⭐⭐",
            }.get(info["quality"], "❓")

            click.echo(f"  • {name}")
            click.echo(f"    Velocidad: {speed_emoji} {info['speed']}")
            click.echo(f"    Calidad: {quality_emoji} {info['quality']}")
            click.echo(f"    Costo: {tier_emoji} Tier {info['cost_tier']}")
            click.echo(f"    Uso: {info['description']}")
            click.echo()

        click.echo("🎯 **RECOMENDACIONES:**\n")
        recs = stats["recommendations"]
        click.echo(f"  ⚡ Más rápido: {recs['fastest']}")
        click.echo(f"  ⚖️  Balanceado: {recs['balanced']}")
        click.echo(f"  ⭐ Mejor calidad: {recs['best_quality']}")
        click.echo(f"  �️  Fallback seguro: {recs['fallback_safe']}")

        click.echo("\n🏗️ **ARQUITECTURA Y RENDIMIENTO:**\n")
        arch_notes = stats.get("architecture_notes", {})
        for model_name, note in arch_notes.items():
            click.echo(f"  • {model_name}")
            click.echo(f"    {note}")

        click.echo("\n💡 **ESTRATEGIA DE FRAGMENTACIÓN (Oct 2025):**\n")
        strategy = stats.get("strategy", {})
        click.echo(
            f"  📦 Fragmentos pequeños → {strategy.get('fragments_small', 'N/A')}"
        )
        click.echo(
            f"  📦 Fragmentos grandes → {strategy.get('fragments_large', 'N/A')}"
        )
        click.echo(
            f"  🔗 Agregación simple → {strategy.get('aggregation_simple', 'N/A')}"
        )
        click.echo(
            f"  🔗 Agregación compleja → {strategy.get('aggregation_complex', 'N/A')}"
        )

        click.echo("\n📈 **EFICIENCIA ESPERADA (16 fragmentos):**")
        click.echo("    • 37.5% llamadas Tier 1 (llama-3.1-8b-instant ~800 t/s)")
        click.echo("    • 62.5% llamadas Tier 2 (Scout MoE ~500 t/s)")
        click.echo("    • 1 llamada agregación final (70B si >12 fragmentos)")
        click.echo("    • Promedio ponderado: ~612 t/s")
        click.echo("    • Fallback automático: Tier 1 → Tier 2 → Tier 3")

    except ImportError:
        click.echo(
            "❌ Error: ModelSelector no disponible. "
            "Instala las dependencias necesarias.",
            err=True,
        )
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


if __name__ == "__main__":
    cli()
