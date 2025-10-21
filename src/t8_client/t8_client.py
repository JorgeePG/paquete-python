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

matplotlib.use("Agg")  # Non-GUI backend by default

# Load environment variables
load_dotenv()

# Configure BASE_URL with fallback
T8_HOST = os.getenv("T8_HOST", "https://lzfs45.mirror.twave.io/lzfs45")
BASE_URL = T8_HOST + "/rest/"


def ensure_plots_directory() -> str:
    """
    Creates the data/plots directory if it doesn't exist and returns the path.

    Returns:
        str: Path to the data/plots directory
    """
    plots_dir = os.path.join("data", "plots")
    os.makedirs(plots_dir, exist_ok=True)
    return plots_dir


def get_plot_filename(filename: str) -> str:
    """
    Generates a complete path for a plot file in data/plots/

    Args:
        filename: File name (e.g.: "wave_machine_plot.png")

    Returns:
        str: Complete path to the file (e.g.: "data/plots/wave_machine_plot.png")
    """
    plots_dir = ensure_plots_directory()
    return os.path.join(plots_dir, filename)


class T8ApiClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.token = None

    def _parse_date_to_timestamp(self, date: str) -> int:
        """
        Converts a date in ISO 8601 format or timestamp to an integer timestamp.

        Args:
            date: Date in ISO 8601 format (in local time), timestamp,
                  or None for the most recent

        Returns:
            int: Timestamp as an integer

        Raises:
            ValueError: If the date format is invalid
        """
        try:
            if "T" in str(date):
                dt = datetime.fromisoformat(str(date))
                # If no timezone, treat as local time
                # and convert directly to timestamp
                return int(dt.timestamp())
            else:
                return int(date)
        except ValueError as e:
            raise ValueError(
                "Format error: Not ISO 8601 (YYYY-MM-DDTHH:MM:SS) or integer timestamp."
            ) from e

    def _setup_matplotlib_interactive(self) -> None:
        """Configures matplotlib to display interactive plots."""
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
        Saves and displays a matplotlib plot.

        Args:
            machine: Machine ID
            point: Measurement point
            procMode: Processing mode
            plot_type: Plot type ('wave', 'spectrum')
            save_file: Custom path to save (optional)
            suffix: Additional suffix for the filename
        """
        plt.tight_layout()

        # Save the plot
        if save_file:
            plt.savefig(save_file, dpi=300, bbox_inches="tight")
            print(f"✓ Plot saved to: {save_file}")
        else:
            # Automatically save to data/plots/
            filename = f"{plot_type}_{machine}_{point}_{procMode}{suffix}_plot.png"
            auto_save = get_plot_filename(filename)
            plt.savefig(auto_save, dpi=300, bbox_inches="tight")
            print(f"✓ Plot saved to: {auto_save}")

        # Show interactive plot
        try:
            print("📊 Displaying interactive plot...")
            print("   (Close the window to continue)")
            plt.show()
        except Exception as e:
            print(f"⚠️  Could not display interactive plot: {e}")
            print("   Plot saved correctly to file.")

    def _parse_machine_path(self, path: str) -> tuple[str, str, str]:
        """
        Parses a machine path and extracts machine, point and proc_mode.

        Args:
            path: Path in format "machine:point:proc_mode"

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
        Gets the configuration of a specific machine from the API.

        Args:
            machine_name: Machine name
            point: Measurement point
            proc_mode: Processing mode

        Returns:
            dict | None: Machine configuration or None if not found
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
        # First get the login page to obtain any CSRF token
        login_page_url = "https://lzfs45.mirror.twave.io/lzfs45/signin"

        # Login using form data like a browser
        payload = {"username": username, "password": password, "signin": "Sign In"}

        try:
            response = self.session.post(login_page_url, data=payload)
            # If login is successful, it probably redirects us or gives us a cookie
            if (
                response.status_code == 200
                and "Invalid Username or Password" not in response.text
            ):
                return True
            elif "Invalid Username or Password" in response.text:
                print("Error: Invalid credentials")
                return False
            else:
                print(f"Login error: {response.status_code} - {response.text[:100]}")
                return False
        except Exception as e:
            print(f"Error in login request: {e}")
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

        # Extract URLs of machines with their points and processing modes
        waves = data.get("_items", [])
        print(f"\nFound {len(waves)} available waves:\n")

        for i, wave in enumerate(waves, 1):
            # Extract information from URL
            wave_url = wave.get("_links", {}).get("self", "")
            if wave_url:
                # Extract machine, point, mode from URL
                # Expected format: .../waves/MACHINE/POINT/MODE/
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
        Extracts the timestamp from an item (wave or spectrum) from its URL.

        Args:
            item: Dictionary with item information

        Returns:
            int: Timestamp extracted from URL, or -1 if it cannot be extracted
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
            # Filter those with timestamp = 0
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
            # Filter those with timestamp = 0
            if self._get_timestamp_from_item(spectrum) != 0:
                print(self.get_timestamp_and_formatted_wave_date(spectrum))
        return True

    def get_wave(
        self, machine: str, point: str, procMode: str, date: str | int = 0
    ) -> dict | None:
        """
        Gets a specific wave or the most recent one if no date is specified.
        Saves the wave to a JSON file and returns the wave data.

        Args:
            machine: Machine ID
            point: Measurement point
            procMode: Processing mode
            date: Date in ISO 8601 format, timestamp, or None for the most recent

        Returns:
            dict | None: Wave data or None if there's an error
        """
        try:
            timestamp = self._parse_date_to_timestamp(date)
        except ValueError as e:
            print(str(e))
            return None

        try:
            # Build URL to get specific wave
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

            # Save to JSON file
            self.save_to_file(data, machine, point, procMode, timestamp, is_wave=True)

            # Display basic information
            formatted_date = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            print("Wave downloaded successfully:")
            print(f"   Machine: {machine}")
            print(f"   Point: {point}")
            print(f"   Mode: {procMode}")
            print(f"   Timestamp: {timestamp}")
            print(f"   Date: {formatted_date}")

            # Return wave data
            return data

        except Exception as e:
            print(f"Error getting wave: {e}")
            return None

    def decode_data(self, encoded_data: str, factor: float = 1.0) -> list[float]:
        """
        Decodes compressed wave data in base64 + zlib.
        Uses int16 little-endian which is the format that works best.

        Args:
            encoded_data: Data encoded in base64
            factor: Scaling factor to apply to data

        Returns:
            list[float]: Array of decoded samples
        """
        try:
            # Decode base64
            compressed_data = base64.b64decode(encoded_data)

            # Decompress with zlib
            decompressed_data = zlib.decompress(compressed_data)

            # Convert to int16 little-endian values
            sample_count = len(decompressed_data) // 2
            samples = struct.unpack(f"<{sample_count}h", decompressed_data)

            # Apply scaling factor
            scaled_samples = [sample * factor for sample in samples]

            print(f"Decoded {len(scaled_samples)} samples (int16 little-endian)")
            print(f"Range: {min(scaled_samples):.2f} to {max(scaled_samples):.2f}")

            return scaled_samples

        except Exception as e:
            print(f"Error decoding wave data: {e}")
            return []

    def get_spectrum(
        self, machine: str, point: str, procMode: str, date: str | int = 0
    ) -> dict | None:
        """
        Gets a specific spectrum or the most recent one if no date is specified.
        Saves the spectrum to a JSON file and returns the spectrum data.

        Args:
            machine: Machine ID
            point: Measurement point
            procMode: Processing mode
            date: Date in ISO 8601 format, timestamp, or None for the most recent

        Returns:
            dict | None: Spectrum data or None if there's an error
        """
        try:
            timestamp = self._parse_date_to_timestamp(date)
        except ValueError as e:
            print(str(e))
            return None

        try:
            # Build URL to get specific wave
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

            # Save to JSON file
            self.save_to_file(data, machine, point, procMode, timestamp, is_wave=False)

            # Display basic information
            formatted_date = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            print("Spectrum downloaded successfully:")
            print(f"   Machine: {machine}")
            print(f"   Point: {point}")
            print(f"   Mode: {procMode}")
            print(f"   Timestamp: {timestamp}")
            print(f"   Date: {formatted_date}")

            return data

        except Exception as e:
            print(f"Error getting spectrum: {e}")
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
        """Saves data to a JSON file."""
        import os

        # Create data/waves directory if it doesn't exist
        if is_wave:
            os.makedirs("data/waves", exist_ok=True)
            # Create filename:
            # wave_<MACHINE>_<POINT>_<PROC_MODE>_<TIMESTAMP>.json
            filename = f"wave_{machine}_{point}_{procMode}_{timestamp}.json"
            filepath = os.path.join("data/waves", filename)
        else:
            os.makedirs("data/spectra", exist_ok=True)
            # Create filename:
            # spectrum_<MACHINE>_<POINT>_<PROC_MODE>_<TIMESTAMP>.json
            filename = f"spectrum_{machine}_{point}_{procMode}_{timestamp}.json"
            filepath = os.path.join("data/spectra", filename)

        # Save data to JSON file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"   File saved: {filepath}")
        except Exception as e:
            print(f"Error saving file: {e}")

    def get_timestamp_and_formatted_wave_date(self, wave: dict) -> str | None:
        url = wave.get("_links", {}).get("self")
        # now parse the url and extract the date
        url_parts = url.split("/")
        fecha = url_parts[-1]  # Knowing that the date is the timestamp at the end
        # Now give ISO 8601 format to the timestamp
        # like this example: 2025-01-01T12:00:00
        try:
            # Convert timestamp to integer and then to datetime
            timestamp = int(fecha)
            fecha_formateada = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
        except (ValueError, OSError):
            # If there's a conversion error, return the original timestamp
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
        """Generates a wave plot using matplotlib.

        Args:
            machine: Machine ID
            point: Measurement point
            procMode: Processing mode
            unit: Unit of measurement (e.g.: 'mm/s', 'g', 'm/s²')
            date: Date/timestamp of the wave
            save_file: Path to save the plot (optional)
        """
        self._setup_matplotlib_interactive()
        print(f"Getting wave for {machine}:{point}:{procMode}...")
        wave_data = self.get_wave(machine, point, procMode, date)
        if not wave_data:
            print("Could not get wave.")
            return

        # Extract data from response
        encoded_data = wave_data.get("data", "")
        factor = wave_data.get("factor", 1.0)
        sample_rate = wave_data.get("sample_rate", 1)  # In Hz

        if not encoded_data:
            print("No wave data to decode.")
            return

        print(f"Decoding data (factor: {factor}, fs: {sample_rate} Hz)...")

        # Decode compressed data
        samples = self.decode_data(encoded_data, factor)
        if not samples:
            print("Could not decode wave data.")
            return

        # Create time array
        duration = len(samples) / sample_rate
        times = [i / sample_rate for i in range(len(samples))]

        unit = self.getUnits(machine, point, procMode)
        print("Generating plot...")

        # Create plot
        plt.figure(figsize=(14, 8))
        plt.plot(times, samples, "b-", linewidth=0.8)
        plt.title(
            f"Vibration Signal - {machine}:{point}:{procMode}",
            fontsize=14,
            fontweight="bold",
        )
        plt.xlabel("Time (s)", fontsize=12)
        plt.ylabel(f"Amplitude ({unit})", fontsize=12)
        plt.grid(True, alpha=0.3)

        # Add information to the plot
        info_text = (
            f"Samples: {len(samples)}\nFs: {sample_rate} Hz\nDuration: {duration:.2f}s"
        )
        plt.text(
            0.02,
            0.98,
            info_text,
            transform=plt.gca().transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        # Save and display plot
        self._save_and_show_plot(machine, point, procMode, "wave", save_file)

        print("✓ Plot generated successfully")
        print(f"  - {len(samples)} samples at {sample_rate} Hz")
        print(f"  - Duration: {duration:.2f} seconds")
        print(f"  - Range: {min(samples):.2f} to {max(samples):.2f}")

    def getUnits(self, machine: str, point: str, procMode: str) -> str:
        """
        First I need to enter the configuration, then
        I need to go to the machine, then to the point and there we go to the point with
        the name I'm looking for and enter input, then sensor, get
        unit_id.
        Once we have unit_id, I will go to the configuration to get units and
        look for the one with that id we got before.
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
        """Generates a spectrum plot using matplotlib.

        Args:
            machine: Machine ID
            point: Measurement point
            procMode: Processing mode
            date: Date/timestamp of the spectrum
            save_file: Path to save the plot (optional)
        """
        self._setup_matplotlib_interactive()
        print(f"Getting spectrum for {machine}:{point}:{procMode}...")
        spec_data = self.get_spectrum(machine, point, procMode, date)
        if not spec_data:
            print("Could not get spectrum.")
            return

        # Extract data from spectrum response
        encoded_data = spec_data.get("data", "")
        factor = spec_data.get("factor", 1.0)
        max_freq = spec_data.get("max_freq", 250)  # Hz
        min_freq = spec_data.get("min_freq", 0.625)  # Hz

        if not encoded_data:
            print("No spectrum data to decode.")
            return

        print(
            f"Decoding data (factor: {factor}, freq: {min_freq}-{max_freq} Hz)" + "..."
        )

        # Decode compressed data (use the same method as waves)
        samples = self.decode_data(encoded_data, factor)
        if not samples:
            print("Could not decode spectrum data.")
            return

        # Create frequency array
        num_samples = len(samples)
        frequencies = [
            min_freq + i * (max_freq - min_freq) / (num_samples - 1)
            for i in range(num_samples)
        ]

        # Get units automatically
        unit = self.getUnits(machine, point, procMode)
        if not unit:
            unit = "Unknown Unit"

        print("Generating plot...")

        # Create spectrum plot
        plt.figure(figsize=(14, 8))
        plt.plot(frequencies, samples, "b-", linewidth=0.8)
        plt.title(
            f"Spectrum - {machine}:{point}:{procMode}", fontsize=14, fontweight="bold"
        )
        plt.xlabel("Frequency (Hz)", fontsize=12)
        plt.ylabel(f"Amplitude ({unit})", fontsize=12)
        plt.grid(True, alpha=0.3)

        # Add information to the plot
        info_text = (
            f"Samples: {num_samples}\n"
            f"Freq range: {min_freq}-{max_freq} Hz\n"
            f"Resolution: {(max_freq - min_freq) / (num_samples - 1):.3f} Hz"
        )
        plt.text(
            0.02,
            0.98,
            info_text,
            transform=plt.gca().transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        # Save and display plot
        self._save_and_show_plot(machine, point, procMode, "spectrum", save_file)

        print("✓ Plot generated successfully")
        print(f"  - {num_samples} samples")
        print(f"  - Frequency: {min_freq:.3f} - {max_freq:.1f} Hz")
        print(f"  - Range: {min(samples):.6f} to {max(samples):.6f}")

    def compute_spectrum_from_wave_data(
        self, wave_filepath: str
    ) -> tuple[np.ndarray, np.ndarray, dict]:
        """
        Calculates a spectrum from a wave JSON file.

        Args:
            wave_filepath: Path to the wave JSON file
            fmin: Optional minimum frequency (if not provided, uses API)
            fmax: Optional maximum frequency (if not provided, uses API)

        Returns:
            Tuple with (frequencies, amplitudes, metadata)
        """
        with open(wave_filepath) as f:
            data = json.load(f)

        # Extract wave data
        waveform = data.get("data")
        waveform = self.decode_data(waveform, data.get("factor", 1.0))

        # Extract information from path using helper function
        path = data.get("path", "Unknown:Unknown:Unknown")
        machine_name, point, proc_mode = self._parse_machine_path(path)

        fmin = None
        fmax = None
        mode_config = self._get_machine_config(machine_name, point, proc_mode)
        if mode_config:
            sample_rate = mode_config.get("sample_rate", 1)
            fmin = mode_config.get("min_freq", 0)
            fmax = mode_config.get("max_freq", sample_rate / 2)

        # Default values if they couldn't be obtained from the API
        sample_rate = data.get("sample_rate", 1)
        if fmin is None:
            fmin = 0
        if fmax is None:
            fmax = sample_rate / 2

        # Calculate spectrum
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
        Calculates and displays a spectrum from a wave JSON file.

        Args:
            wave_filepath: Path to the wave JSON file
        """
        # Use refactored function to get spectrum data
        frequencies, amplitudes, metadata = self.compute_spectrum_from_wave_data(
            wave_filepath
        )

        machine_name = metadata["machine"]
        point = metadata["point"]
        proc_mode = metadata["proc_mode"]
        min_freq = metadata["min_freq"]
        max_freq = metadata["max_freq"]
        sample_rate = metadata["sample_rate"]

        print(f"Calculating spectrum for {machine_name}:{point}:{proc_mode}...")
        print(f"  - Sample rate: {sample_rate} Hz")
        print(f"  - Fmin: {min_freq} Hz")
        print(f"  - Fmax: {max_freq} Hz")

        # Get units automatically
        unit = self.getUnits(machine_name, point, proc_mode)
        if not unit:
            unit = "Unknown Unit"

        # Configure matplotlib and create plot
        self._setup_matplotlib_interactive()
        plt.figure(figsize=(14, 8))
        plt.plot(frequencies, amplitudes, "b-", linewidth=0.8)
        plt.title(
            f"Computed Spectrum - {machine_name}:{point}:{proc_mode}",
            fontsize=14,
            fontweight="bold",
        )
        plt.xlabel("Frequency (Hz)", fontsize=12)
        plt.ylabel(f"Amplitude ({unit})", fontsize=12)
        plt.grid(True, alpha=0.3)

        # Add information to the plot
        info_text = (
            f"Samples: {len(amplitudes)}\n"
            f"Freq range: {min_freq}-{max_freq} Hz\n"
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

        # Save and display plot
        self._save_and_show_plot(
            machine_name, point, proc_mode, "spectrum", suffix="_computed"
        )

        print("✓ Spectrum computed successfully")
        print(f"  - {len(amplitudes)} freq points")
        print(f"  - Frequency: {min_freq:.1f} - {max_freq:.1f} Hz")
        min_val = min(amplitudes)
        max_val = max(amplitudes)
        print(f"  - Range: {min_val:.6f} to {max_val:.6f}")

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
        # Convert list to numpy array if necessary
        if not isinstance(waveform, np.ndarray):
            waveform = np.array(waveform)

        # Remove DC component (mean value)
        waveform = waveform - np.mean(waveform)

        # Apply Hanning window to reduce edge effects
        # window = np.hanning(len(waveform))
        # waveform_windowed = waveform * window
        waveform_windowed = waveform.copy()

        # Calculate FFT
        spectrum = np.fft.fft(waveform_windowed)
        magnitude = np.abs(spectrum) / len(spectrum)
        freqs = np.fft.fftfreq(len(waveform), 1 / sample_rate)

        # Only use positive frequencies (first half of spectrum)
        n = len(waveform) // 2
        freqs_positive = freqs[:n]
        magnitude_positive = magnitude[:n] * 2  # Factor 2 for energy

        # Exclude 0 Hz frequency (DC) from filtering if fmin is 0
        if fmin == 0:
            fmin = freqs_positive[1] if len(freqs_positive) > 1 else 0

        # Filter by frequency range
        mask = (freqs_positive >= fmin) & (freqs_positive <= fmax)
        filtered_freqs = freqs_positive[mask]
        filtered_spectrum = magnitude_positive[mask]

        return filtered_freqs, filtered_spectrum
