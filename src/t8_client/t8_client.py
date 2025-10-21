import base64
import json
import os
import struct
import zlib
from datetime import datetime  # type: ignore

# Configurar matplotlib para entornos sin GUI
import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import requests  # type: ignore
from dotenv import load_dotenv  # type: ignore

matplotlib.use("Agg")  # Backend sin GUI por defecto

# Cargar variables de entorno
load_dotenv()

# Configurar BASE_URL con fallback
T8_HOST = os.getenv("T8_HOST", "https://lzfs45.mirror.twave.io/lzfs45")
BASE_URL = T8_HOST + "/rest/"


def ensure_plots_directory() -> str:
    """
    Crea el directorio data/plots si no existe y devuelve la ruta.

    Returns:
        str: Ruta al directorio data/plots
    """
    plots_dir = os.path.join("data", "plots")
    os.makedirs(plots_dir, exist_ok=True)
    return plots_dir


def get_plot_filename(filename: str) -> str:
    """
    Genera una ruta completa para un archivo de gráfico en data/plots/

    Args:
        filename: Nombre del archivo (ej: "wave_machine_plot.png")

    Returns:
        str: Ruta completa al archivo (ej: "data/plots/wave_machine_plot.png")
    """
    plots_dir = ensure_plots_directory()
    return os.path.join(plots_dir, filename)


class T8ApiClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.token = None

    def _parse_date_to_timestamp(self, date: str) -> int:
        """
        Convierte una fecha en formato ISO 8601 o timestamp a entero timestamp.

        Args:
            date: Fecha en formato ISO 8601 (en hora local), timestamp,
                  o None para la más reciente

        Returns:
            int: Timestamp como entero

        Raises:
            ValueError: Si el formato de fecha es inválido
        """
        try:
            if "T" in str(date):
                dt = datetime.fromisoformat(str(date))
                # Si no tiene timezone, se trata como hora local
                # y se convierte directamente a timestamp
                return int(dt.timestamp())
            else:
                return int(date)
        except ValueError as e:
            raise ValueError(
                "Error de formato: No es ISO 8601 (YYYY-MM-DDTHH:MM:SS) "
                "o timestamp entero."
            ) from e

    def _setup_matplotlib_interactive(self) -> None:
        """Configura matplotlib para mostrar gráficos interactivos."""
        matplotlib.use("WebAgg")

    def _save_and_show_plot(
        self,
        machine: str,
        point: str,
        procMode: str,
        plot_type: str,
        save_file: str | None = None,
        suffix: str = "",
    ) -> None:
        """
        Guarda y muestra un gráfico de matplotlib.

        Args:
            machine: ID de la máquina
            point: Punto de medida
            procMode: Modo de procesamiento
            plot_type: Tipo de gráfico ('wave', 'spectrum')
            save_file: Ruta personalizada para guardar (opcional)
            suffix: Sufijo adicional para el nombre del archivo
        """
        plt.tight_layout()

        # Guardar el gráfico
        if save_file:
            plt.savefig(save_file, dpi=300, bbox_inches="tight")
            print(f"✓ Gráfico guardado en: {save_file}")
        else:
            # Guardar automáticamente en data/plots/
            filename = f"{plot_type}_{machine}_{point}_{procMode}{suffix}_plot.png"
            auto_save = get_plot_filename(filename)
            plt.savefig(auto_save, dpi=300, bbox_inches="tight")
            print(f"✓ Gráfico guardado en: {auto_save}")

        # Mostrar el gráfico interactivo
        try:
            print("📊 Mostrando gráfico interactivo...")
            print("   (Cierra la ventana para continuar)")
            plt.show()
        except Exception as e:
            print(f"⚠️  No se pudo mostrar gráfico interactivo: {e}")
            print("   Gráfico guardado correctamente en archivo.")

    def _parse_machine_path(self, path: str) -> tuple[str, str, str]:
        """
        Parsea un path de máquina y extrae machine, point y proc_mode.

        Args:
            path: Path en formato "machine:point:proc_mode"

        Returns:
            tuple: (machine, point, proc_mode)
        """
        parts = path.split(":")
        machine = parts[0] if len(parts) > 0 else "Unknown"
        point = parts[1] if len(parts) > 1 else "Unknown"
        proc_mode = parts[2] if len(parts) > 2 else "Unknown"
        return machine, point, proc_mode

    def _get_machine_config(
        self, machine_name: str, point: str, proc_mode: str
    ) -> dict | None:
        """
        Obtiene la configuración de una máquina específica desde la API.

        Args:
            machine_name: Nombre de la máquina
            point: Punto de medida
            proc_mode: Modo de procesamiento

        Returns:
            dict | None: Configuración de la máquina o None si no se encuentra
        """
        try:
            url = BASE_URL + "confs/0"
            response = self.session.get(url)
            conf_data = self.check_ok_response(response)

            if not conf_data:
                return None

            machines = conf_data.get("machines", [])
            for machine in machines:
                if machine.get("name") == machine_name:
                    points = machine.get("points", [])
                    for p in points:
                        if p.get("name") == point:
                            proc_modes = p.get("proc_modes", [])
                            for mode in proc_modes:
                                if mode.get("name") == proc_mode:
                                    return mode
            return None
        except Exception:
            return None

    def login_with_credentials(self, username: str, password: str) -> bool:
        # Primero obtenemos la página de login para obtener cualquier token CSRF
        login_page_url = "https://lzfs45.mirror.twave.io/lzfs45/signin"

        # Hacemos login usando form data como el navegador
        payload = {"username": username, "password": password, "signin": "Sign In"}

        try:
            response = self.session.post(login_page_url, data=payload)
            # Si el login es exitoso, probablemente nos redirige o nos da una cookie
            if (
                response.status_code == 200
                and "Invalid Username or Password" not in response.text
            ):
                return True
            elif "Invalid Username or Password" in response.text:
                print("Error: Credenciales inválidas")
                return False
            else:
                print(f"Error de login: {response.status_code} - {response.text[:100]}")
                return False
        except Exception as e:
            print(f"Error en la petición de login: {e}")
            return False

    def check_ok_response(self, response: requests.Response) -> dict | None:
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as e:
                print(f"Error parsing JSON: {e}")
                print(f"Full response: {response.text}")
                return None
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def list_available_waves(self) -> None:
        url = BASE_URL + "waves/"
        response = self.session.get(url)
        data = self.check_ok_response(response)
        if not data:
            return

        # Saco los url de las máquinas con sus puntos y modos de procesamiento
        waves = data.get("_items", [])
        print(f"\nEncontradas {len(waves)} ondas disponibles:\n")

        for i, wave in enumerate(waves, 1):
            # Extraer información del URL
            wave_url = wave.get("_links", {}).get("self", "")
            if wave_url:
                # Extraer machine, point, mode del URL
                # Formato esperado: .../waves/MACHINE/POINT/MODE/
                parts = wave_url.rstrip("/").split("/")
                if len(parts) >= 3:
                    machine = parts[-3]
                    point = parts[-2]
                    mode = parts[-1]
                    print(f"{i:2d}. Machine: {machine}, Point: {point}, Mode: {mode}")
                    print(f"    URL: {wave_url}")
                else:
                    print(f"{i:2d}. URL: {wave_url}")

    def _get_timestamp_from_item(self, item: dict) -> int:
        """
        Extrae el timestamp de un item (wave o spectrum) desde su URL.

        Args:
            item: Diccionario con la información del item

        Returns:
            int: Timestamp extraído del URL, o -1 si no se puede extraer
        """
        item_url = item.get("_links", {}).get("self", "")
        try:
            return int(item_url.split("/")[-1]) if item_url else -1
        except ValueError:
            return -1

    def list_waves(self, machine: str, point: str, procMode: str) -> bool:
        url = BASE_URL + "waves/" + machine + "/" + point + "/" + procMode
        response = self.session.get(url)
        data = self.check_ok_response(response)
        if not data:
            return False
        for wave in data.get("_items", []):
            # Filtrar los que tienen timestamp = 0
            if self._get_timestamp_from_item(wave) != 0:
                print(self.get_timestamp_and_formatted_wave_date(wave))
        return True

    def list_spectra(self, machine: str, point: str, procMode: str) -> bool:
        url = BASE_URL + "spectra/" + machine + "/" + point + "/" + procMode
        response = self.session.get(url)
        data = self.check_ok_response(response)
        if not data:
            return False
        for spectrum in data.get("_items", []):
            # Filtrar los que tienen timestamp = 0
            if self._get_timestamp_from_item(spectrum) != 0:
                print(self.get_timestamp_and_formatted_wave_date(spectrum))
        return True

    def get_wave(
        self, machine: str, point: str, procMode: str, date: str | int = 0
    ) -> dict | None:
        """
        Obtiene una onda específica o la más reciente si no se especifica fecha.
        Guarda la onda en un archivo JSON y devuelve los datos de la onda.

        Args:
            machine: ID de la máquina
            point: Punto de medida
            procMode: Modo de procesamiento
            date: Fecha en formato ISO 8601, timestamp, o None para la más reciente

        Returns:
            dict | None: Datos de la onda o None si hay error
        """
        try:
            timestamp = self._parse_date_to_timestamp(date)
        except ValueError as e:
            print(str(e))
            return None

        try:
            # Construir URL para obtener la onda específica
            url = (
                BASE_URL
                + "waves/"
                + machine
                + "/"
                + point
                + "/"
                + procMode
                + "/"
                + str(timestamp)
            )
            response = self.session.get(url)
            data = self.check_ok_response(response)

            if not data:
                return None

            # Guardar en archivo JSON
            self.save_to_file(data, machine, point, procMode, timestamp, is_wave=True)

            # Mostrar información básica
            formatted_date = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            print("Onda descargada exitosamente:")
            print(f"   Machine: {machine}")
            print(f"   Point: {point}")
            print(f"   Mode: {procMode}")
            print(f"   Timestamp: {timestamp}")
            print(f"   Fecha: {formatted_date}")

            # Devolver los datos de la onda
            return data

        except Exception as e:
            print(f"Error al obtener la onda: {e}")
            return None

    def decode_data(self, encoded_data: str, factor: float = 1.0) -> list[float]:
        """
        Decodifica los datos de onda comprimidos en base64 + zlib.
        Usa int16 little-endian que es el formato que mejor funciona.

        Args:
            encoded_data: Datos codificados en base64
            factor: Factor de escala a aplicar a los datos

        Returns:
            list[float]: Array de muestras decodificadas
        """
        try:
            # Decodificar base64
            compressed_data = base64.b64decode(encoded_data)

            # Descomprimir con zlib
            decompressed_data = zlib.decompress(compressed_data)

            # Convertir a valores int16 little-endian
            sample_count = len(decompressed_data) // 2
            samples = struct.unpack(f"<{sample_count}h", decompressed_data)

            # Aplicar factor de escala
            scaled_samples = [sample * factor for sample in samples]

            print(f"Decodificados {len(scaled_samples)} muestras (int16 little-endian)")
            print(f"Rango: {min(scaled_samples):.2f} a {max(scaled_samples):.2f}")

            return scaled_samples

        except Exception as e:
            print(f"Error decodificando datos de onda: {e}")
            return []

    def get_spectrum(
        self, machine: str, point: str, procMode: str, date: str | int = 0
    ) -> dict | None:
        """
        Obtiene un espectro específico o el más reciente si no se especifica fecha.
        Guarda el espectro en un archivo JSON y devuelve los datos del espectro.

        Args:
            machine: ID de la máquina
            point: Punto de medida
            procMode: Modo de procesamiento
            date: Fecha en formato ISO 8601, timestamp, o None para la más reciente

        Returns:
            dict | None: Datos del espectro o None si hay error
        """
        try:
            timestamp = self._parse_date_to_timestamp(date)
        except ValueError as e:
            print(str(e))
            return None

        try:
            # Construir URL para obtener la onda específica
            url = (
                BASE_URL
                + "spectra/"
                + machine
                + "/"
                + point
                + "/"
                + procMode
                + "/"
                + str(timestamp)
            )
            response = self.session.get(url)
            data = self.check_ok_response(response)

            if not data:
                return None

            # Guardar en archivo JSON
            self.save_to_file(data, machine, point, procMode, timestamp, is_wave=False)

            # Mostrar información básica
            formatted_date = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            print("Espectro descargado exitosamente:")
            print(f"   Machine: {machine}")
            print(f"   Point: {point}")
            print(f"   Mode: {procMode}")
            print(f"   Timestamp: {timestamp}")
            print(f"   Fecha: {formatted_date}")

            return data

        except Exception as e:
            print(f"Error al obtener el espectro: {e}")
            return None

    def save_to_file(
        self,
        data: dict,
        machine: str,
        point: str,
        procMode: str,
        timestamp: int,
        is_wave: bool,
    ) -> None:
        """Guarda los datos en un archivo JSON."""
        import os

        # Crear directorio data/waves si no existe
        if is_wave:
            os.makedirs("data/waves", exist_ok=True)
            # Crear nombre del archivo:
            # wave_<MACHINE>_<POINT>_<PROC_MODE>_<TIMESTAMP>.json
            filename = f"wave_{machine}_{point}_{procMode}_{timestamp}.json"
            filepath = os.path.join("data/waves", filename)
        else:
            os.makedirs("data/spectra", exist_ok=True)
            # Crear nombre del archivo:
            # spectrum_<MACHINE>_<POINT>_<PROC_MODE>_<TIMESTAMP>.json
            filename = f"spectrum_{machine}_{point}_{procMode}_{timestamp}.json"
            filepath = os.path.join("data/spectra", filename)

        # Guardar datos en archivo JSON
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"   Archivo guardado: {filepath}")
        except Exception as e:
            print(f"Error al guardar el archivo: {e}")

    def get_timestamp_and_formatted_wave_date(self, wave: dict) -> str | None:
        url = wave.get("_links", {}).get("self")
        # ahora parseo el url y saco la fecha
        url_parts = url.split("/")
        fecha = url_parts[-1]  # Sabiendo que la fecha es el timestamp del final
        # Ahora se le da un formato ISO 8601 al timestamp
        # como esta de ejemplo: 2025-01-01T12:00:00
        try:
            # Convertir timestamp a entero y luego a datetime
            timestamp = int(fecha)
            fecha_formateada = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
        except (ValueError, OSError):
            # Si hay error en la conversión, retornar el timestamp original
            fecha_formateada = fecha
        return fecha + " => " + fecha_formateada

    def plot_wave(
        self,
        machine: str,
        point: str,
        procMode: str,
        date: str | None = "0",
        save_file: str | None = None,
    ) -> None:
        """Genera un gráfico de la onda usando matplotlib.

        Args:
            machine: ID de la máquina
            point: Punto de medida
            procMode: Modo de procesamiento
            unit: Unidad de medida (ej: 'mm/s', 'g', 'm/s²')
            date: Fecha/timestamp de la onda
            save_file: Ruta para guardar el gráfico (opcional)
        """
        self._setup_matplotlib_interactive()
        print(f"Obteniendo onda para {machine}:{point}:{procMode}...")
        wave_data = self.get_wave(machine, point, procMode, date)
        if not wave_data:
            print("No se pudo obtener la onda.")
            return

        # Extraer datos de la respuesta
        encoded_data = wave_data.get("data", "")
        factor = wave_data.get("factor", 1.0)
        sample_rate = wave_data.get("sample_rate", 1)  # En Hz

        if not encoded_data:
            print("No hay datos de onda para decodificar.")
            return

        print(f"Decodificando datos (factor: {factor}, fs: {sample_rate} Hz)...")

        # Decodificar los datos comprimidos
        samples = self.decode_data(encoded_data, factor)
        if not samples:
            print("No se pudieron decodificar los datos de la onda.")
            return

        # Crear array de tiempo
        duration = len(samples) / sample_rate
        times = [i / sample_rate for i in range(len(samples))]

        unit = self.getUnits(machine, point, procMode)
        print("Generando gráfico...")

        # Crear el gráfico
        plt.figure(figsize=(14, 8))
        plt.plot(times, samples, "b-", linewidth=0.8)
        plt.title(
            f"Señal de Vibración - {machine}:{point}:{procMode}",
            fontsize=14,
            fontweight="bold",
        )
        plt.xlabel("Tiempo (s)", fontsize=12)
        plt.ylabel(f"Amplitud ({unit})", fontsize=12)
        plt.grid(True, alpha=0.3)

        # Añadir información en el gráfico
        info_text = (
            f"Muestras: {len(samples)}\nFs: {sample_rate} Hz\nDuración: {duration:.2f}s"
        )
        plt.text(
            0.02,
            0.98,
            info_text,
            transform=plt.gca().transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        # Guardar y mostrar el gráfico
        self._save_and_show_plot(machine, point, procMode, "wave", save_file)

        print("✓ Gráfico generado exitosamente")
        print(f"  - {len(samples)} muestras a {sample_rate} Hz")
        print(f"  - Duración: {duration:.2f} segundos")
        print(f"  - Rango: {min(samples):.2f} a {max(samples):.2f}")

    def getUnits(self, machine: str, point: str, procMode: str) -> str:
        """
        Lo primero que tengo que hacer es entrar a la configuración, luego
        tengo que ir a la máquina, después al punto y ahí vamos al punto con
        el nombre que estoy buscando y entro en input, luego en sensor, saco
        unit_id.
        Una vez tengo unit_id, voy a  ir en la configuración a sacar units y
        busco la que tenga ese id que sacamos antes.
        """
        try:
            url = BASE_URL + "confs/0"
            response = self.session.get(url)
            conf_data = self.check_ok_response(response)

            if not conf_data:
                return None

            unit_id = None
            machines = conf_data.get("machines", [])
            for m in machines:
                if m.get("name") == machine:
                    points = m.get("points", [])
                    for p in points:
                        if p.get("name") == point:
                            unit_id = (
                                p.get("input", {}).get("sensor", {}).get("unit_id")
                            )
            if unit_id is not None:
                units = conf_data.get("units", [])
                for unit in units:
                    if unit.get("id") == unit_id:
                        return unit.get("label", "Unknown Unit")
            return None
        except Exception:
            return None

    def plot_spectrum(
        self,
        machine: str,
        point: str,
        procMode: str,
        date: str | None = "0",
        save_file: str | None = None,
    ) -> None:
        """Genera un gráfico del espectro usando matplotlib.

        Args:
            machine: ID de la máquina
            point: Punto de medida
            procMode: Modo de procesamiento
            date: Fecha/timestamp del espectro
            save_file: Ruta para guardar el gráfico (opcional)
        """
        self._setup_matplotlib_interactive()
        print(f"Obteniendo espectro para {machine}:{point}:{procMode}...")
        spec_data = self.get_spectrum(machine, point, procMode, date)
        if not spec_data:
            print("No se pudo obtener el espectro.")
            return

        # Extraer datos de la respuesta del espectro
        encoded_data = spec_data.get("data", "")
        factor = spec_data.get("factor", 1.0)
        max_freq = spec_data.get("max_freq", 250)  # Hz
        min_freq = spec_data.get("min_freq", 0.625)  # Hz

        if not encoded_data:
            print("No hay datos de espectro para decodificar.")
            return

        print(
            f"Decodificando datos (factor: {factor}, freq: {min_freq}-{max_freq} Hz)"
            + "..."
        )

        # Decodificar los datos comprimidos (usar el mismo método que las ondas)
        samples = self.decode_data(encoded_data, factor)
        if not samples:
            print("No se pudieron decodificar los datos del espectro.")
            return

        # Crear array de frecuencias
        num_samples = len(samples)
        frequencies = [
            min_freq + i * (max_freq - min_freq) / (num_samples - 1)
            for i in range(num_samples)
        ]

        # Obtener unidades automáticamente
        unit = self.getUnits(machine, point, procMode)
        if not unit:
            unit = "Unknown Unit"

        print("Generando gráfico...")

        # Crear el gráfico del espectro
        plt.figure(figsize=(14, 8))
        plt.plot(frequencies, samples, "b-", linewidth=0.8)
        plt.title(
            f"Espectro - {machine}:{point}:{procMode}", fontsize=14, fontweight="bold"
        )
        plt.xlabel("Frecuencia (Hz)", fontsize=12)
        plt.ylabel(f"Amplitud ({unit})", fontsize=12)
        plt.grid(True, alpha=0.3)

        # Añadir información en el gráfico
        info_text = (
            f"Muestras: {num_samples}\n"
            f"Rango freq: {min_freq}-{max_freq} Hz\n"
            f"Resolución: {(max_freq - min_freq) / (num_samples - 1):.3f} Hz"
        )
        plt.text(
            0.02,
            0.98,
            info_text,
            transform=plt.gca().transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        # Guardar y mostrar el gráfico
        self._save_and_show_plot(machine, point, procMode, "spectrum", save_file)

        print("✓ Gráfico generado exitosamente")
        print(f"  - {num_samples} muestras")
        print(f"  - Frecuencia: {min_freq:.3f} - {max_freq:.1f} Hz")
        print(f"  - Rango: {min(samples):.6f} a {max(samples):.6f}")

    def compute_spectrum_from_wave_data(
        self, wave_filepath: str
    ) -> tuple[np.ndarray, np.ndarray, dict]:
        """
        Calcula un espectro a partir de un archivo de onda JSON.

        Args:
            wave_filepath: Ruta al archivo JSON de la onda
            fmin: Frecuencia mínima opcional (si no se proporciona, usa API)
            fmax: Frecuencia máxima opcional (si no se proporciona, usa API)

        Returns:
            Tuple con (frecuencias, amplitudes, metadata)
        """
        with open(wave_filepath) as f:
            data = json.load(f)

        # Extraer datos de la onda
        waveform = data.get("data")
        waveform = self.decode_data(waveform, data.get("factor", 1.0))

        # Extraer información del path usando la función auxiliar
        path = data.get("path", "Unknown:Unknown:Unknown")
        machine_name, point, proc_mode = self._parse_machine_path(path)

        fmin = None
        fmax = None
        mode_config = self._get_machine_config(machine_name, point, proc_mode)
        if mode_config:
            sample_rate = mode_config.get("sample_rate", 1)
            fmin = mode_config.get("min_freq", 0)
            fmax = mode_config.get("max_freq", sample_rate / 2)

        # Valores por defecto si no se pudieron obtener de la API
        sample_rate = data.get("sample_rate", 1)
        if fmin is None:
            fmin = 0
        if fmax is None:
            fmax = sample_rate / 2

        # Calcular espectro
        frequencies, amplitudes = T8ApiClient.compute_spectrum(
            np.array(waveform), sample_rate, fmin, fmax
        )

        # Metadata
        metadata = {
            "min_freq": fmin,
            "max_freq": fmax,
            "num_samples": len(amplitudes),
            "sample_rate": sample_rate,
            "path": data.get("path", "Unknown"),
            "timestamp": data.get("timestamp", 0),
            "machine": machine_name,
            "point": point,
            "proc_mode": proc_mode,
        }

        return frequencies, amplitudes, metadata

    def compute_spectrum_with_json(self, wave_filepath: str) -> None:
        """
        Calcula y muestra un espectro a partir de un archivo de onda JSON.

        Args:
            wave_filepath: Ruta al archivo JSON de la onda
        """
        # Usar la función refactorizada para obtener datos del espectro
        frequencies, amplitudes, metadata = self.compute_spectrum_from_wave_data(
            wave_filepath
        )

        machine_name = metadata["machine"]
        point = metadata["point"]
        proc_mode = metadata["proc_mode"]
        min_freq = metadata["min_freq"]
        max_freq = metadata["max_freq"]
        sample_rate = metadata["sample_rate"]

        print(f"Calculando espectro para {machine_name}:{point}:{proc_mode}...")
        print(f"  - Sample rate: {sample_rate} Hz")
        print(f"  - Fmin: {min_freq} Hz")
        print(f"  - Fmax: {max_freq} Hz")

        # Obtener unidades automáticamente
        unit = self.getUnits(machine_name, point, proc_mode)
        if not unit:
            unit = "Unknown Unit"

        # Configurar matplotlib y crear gráfico
        self._setup_matplotlib_interactive()
        plt.figure(figsize=(14, 8))
        plt.plot(frequencies, amplitudes, "b-", linewidth=0.8)
        plt.title(
            f"Espectro Computado - {machine_name}:{point}:{proc_mode}",
            fontsize=14,
            fontweight="bold",
        )
        plt.xlabel("Frecuencia (Hz)", fontsize=12)
        plt.ylabel(f"Amplitud ({unit})", fontsize=12)
        plt.grid(True, alpha=0.3)

        # Añadir información en el gráfico
        info_text = (
            f"Muestras: {len(amplitudes)}\n"
            f"Rango freq: {min_freq}-{max_freq} Hz\n"
            f"Sample rate: {sample_rate} Hz"
        )
        plt.text(
            0.02,
            0.98,
            info_text,
            transform=plt.gca().transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        # Guardar y mostrar el gráfico
        self._save_and_show_plot(
            machine_name, point, proc_mode, "spectrum", suffix="_computed"
        )

        print("✓ Espectro computado exitosamente")
        print(f"  - {len(amplitudes)} puntos freq")
        print(f"  - Frecuencia: {min_freq:.1f} - {max_freq:.1f} Hz")
        min_val = min(amplitudes)
        max_val = max(amplitudes)
        print(f"  - Rango: {min_val:.6f} a {max_val:.6f}")

    @staticmethod
    def compute_spectrum(
        waveform: np.ndarray, sample_rate: int, fmin: float, fmax: float
    ) -> tuple[np.ndarray, np.ndarray]:
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
        # Convertir lista a numpy array si es necesario
        if not isinstance(waveform, np.ndarray):
            waveform = np.array(waveform)

        # Remover componente DC (valor medio)
        waveform = waveform - np.mean(waveform)

        # Aplicar ventana Hanning para reducir efectos de borde
        # window = np.hanning(len(waveform))
        # waveform_windowed = waveform * window
        waveform_windowed = waveform.copy()

        # Calcular FFT
        spectrum = np.fft.fft(waveform_windowed)
        magnitude = np.abs(spectrum) / len(spectrum)
        freqs = np.fft.fftfreq(len(waveform), 1 / sample_rate)

        # Solo usar frecuencias positivas (primera mitad del espectro)
        n = len(waveform) // 2
        freqs_positive = freqs[:n]
        magnitude_positive = magnitude[:n] * 2  # Factor 2 para energía

        # Excluir la frecuencia 0 Hz (DC) del filtrado si fmin es 0
        if fmin == 0:
            fmin = freqs_positive[1] if len(freqs_positive) > 1 else 0

        # Filtrar por rango de frecuencias
        mask = (freqs_positive >= fmin) & (freqs_positive <= fmax)
        filtered_freqs = freqs_positive[mask]
        filtered_spectrum = magnitude_positive[mask]

        return filtered_freqs, filtered_spectrum
