import json
import os
from pathlib import Path
from typing import Never

import numpy as np  # type: ignore
import pytest  # type: ignore
import responses  # type: ignore

from t8_client import BASE_URL, T8ApiClient, ensure_plots_directory, get_plot_filename


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_ensure_plots_directory(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that plots directory is created."""
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)

        plots_dir = ensure_plots_directory()

        assert os.path.exists(plots_dir)
        assert plots_dir.endswith(os.path.join("data", "plots"))

    def test_get_plot_filename(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that plot filename is generated correctly."""
        monkeypatch.chdir(tmp_path)

        filename = get_plot_filename("test_plot.png")

        assert filename.endswith(os.path.join("data", "plots", "test_plot.png"))
        assert os.path.exists(os.path.dirname(filename))


class TestT8ApiClient:
    """Tests for T8ApiClient class."""

    def test_client_initialization(self) -> None:
        """Test that client initializes correctly."""
        client = T8ApiClient()

        assert client.session is not None
        assert client.token is None

    def test_parse_date_to_timestamp_with_iso_format(self) -> None:
        """Test date parsing with ISO 8601 format."""
        client = T8ApiClient()

        # Test with ISO format
        timestamp = client._parse_date_to_timestamp("2025-01-01T12:00:00")

        assert isinstance(timestamp, int)
        assert timestamp > 0

    def test_parse_date_to_timestamp_with_integer(self) -> None:
        """Test date parsing with integer timestamp."""
        client = T8ApiClient()

        timestamp = client._parse_date_to_timestamp("1234567890")

        assert timestamp == 1234567890

    def test_parse_date_to_timestamp_with_zero(self) -> None:
        """Test date parsing with zero (most recent)."""
        client = T8ApiClient()

        timestamp = client._parse_date_to_timestamp("0")

        assert timestamp == 0

    def test_parse_date_to_timestamp_invalid_format(self) -> None:
        """Test date parsing with invalid format raises ValueError."""
        client = T8ApiClient()

        with pytest.raises(ValueError) as excinfo:
            client._parse_date_to_timestamp("invalid-date")

        assert "Error de formato" in str(excinfo.value)

    def test_check_ok_response_success(self) -> None:
        """Test check_ok_response with successful response."""
        client = T8ApiClient()

        # Mock response
        class MockResponse:
            status_code = 200

            def json(self):  # noqa: ANN202
                return {"success": True, "data": "test"}

        result = client.check_ok_response(MockResponse())

        assert result == {"success": True, "data": "test"}

    def test_check_ok_response_failure(self, capsys: pytest.CaptureFixture) -> None:
        """Test check_ok_response with failed response."""
        client = T8ApiClient()

        # Mock response
        class MockResponse:
            status_code = 404
            text = "Not Found"

        result = client.check_ok_response(MockResponse())

        assert result is None
        captured = capsys.readouterr()
        assert "404" in captured.out

    def test_check_ok_response_invalid_json(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Test check_ok_response with invalid JSON."""
        client = T8ApiClient()

        # Mock response
        class MockResponse:
            status_code = 200
            text = "Invalid JSON"

            def json(self) -> Never:
                raise ValueError("Invalid JSON")

        result = client.check_ok_response(MockResponse())

        assert result is None
        captured = capsys.readouterr()
        assert "Error parsing JSON" in captured.out

    def test_decode_data_success(self) -> None:
        """Test successful data decoding."""
        client = T8ApiClient()

        # Sample encoded data (simple test)
        import base64
        import struct
        import zlib

        # Create sample data
        original_data = [100, 200, 300, 400, 500]
        packed = struct.pack(f"<{len(original_data)}h", *original_data)
        compressed = zlib.compress(packed)
        encoded = base64.b64encode(compressed).decode("utf-8")

        # Decode
        result = client.decode_data(encoded, factor=1.0)

        assert len(result) == len(original_data)
        assert result == original_data

    def test_decode_data_with_factor(self) -> None:
        """Test data decoding with scaling factor."""
        client = T8ApiClient()

        import base64
        import struct
        import zlib

        # Create sample data
        original_data = [100, 200, 300]
        factor = 0.5
        packed = struct.pack(f"<{len(original_data)}h", *original_data)
        compressed = zlib.compress(packed)
        encoded = base64.b64encode(compressed).decode("utf-8")

        # Decode
        result = client.decode_data(encoded, factor=factor)

        assert len(result) == len(original_data)
        assert result == [x * factor for x in original_data]

    def test_decode_data_invalid(self) -> None:
        """Test decode_data with invalid data."""
        client = T8ApiClient()

        result = client.decode_data("invalid_base64_data")

        assert result == []

    def test_save_to_file_wave(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test saving wave data to file."""
        monkeypatch.chdir(tmp_path)
        client = T8ApiClient()

        data = {"data": "test_data", "factor": 1.0, "timestamp": 1234567890}

        client.save_to_file(data, "machine1", "point1", "mode1", 1234567890, True)

        # Check file exists
        expected_file = os.path.join(
            "data", "waves", "wave_machine1_point1_mode1_1234567890.json"
        )
        assert os.path.exists(expected_file)

        # Check content
        with open(expected_file) as f:
            saved_data = json.load(f)
        assert saved_data == data

    def test_save_to_file_spectrum(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test saving spectrum data to file."""
        monkeypatch.chdir(tmp_path)
        client = T8ApiClient()

        data = {
            "data": "test_spectrum",
            "factor": 0.5,
            "max_freq": 250,
            "min_freq": 0.625,
        }

        client.save_to_file(data, "machine2", "point2", "mode2", 9876543210, False)

        # Check file exists
        expected_file = os.path.join(
            "data", "spectra", "spectrum_machine2_point2_mode2_9876543210.json"
        )
        assert os.path.exists(expected_file)

        # Check content
        with open(expected_file) as f:
            saved_data = json.load(f)
        assert saved_data == data

    def test_get_timestamp_and_formatted_wave_date(self) -> None:
        """Test timestamp extraction and formatting."""
        client = T8ApiClient()

        wave_data = {
            "_links": {"self": "http://example.com/waves/machine/point/mode/1234567890"}
        }

        result = client.get_timestamp_and_formatted_wave_date(wave_data)

        assert "1234567890" in result
        assert "=>" in result
        # Check that a formatted date is included
        assert "T" in result or ":" in result

    def test_get_timestamp_and_formatted_wave_date_invalid(self) -> None:
        """Test timestamp formatting with invalid timestamp."""
        client = T8ApiClient()

        wave_data = {
            "_links": {"self": "http://example.com/waves/machine/point/mode/invalid"}
        }

        result = client.get_timestamp_and_formatted_wave_date(wave_data)

        assert "invalid" in result

    def test_parse_machine_path(self) -> None:
        """Test parsing machine path."""
        client = T8ApiClient()

        machine, point, proc_mode = client._parse_machine_path(
            "test_machine:test_point:test_proc_mode"
        )

        assert machine == "test_machine"
        assert point == "test_point"
        assert proc_mode == "test_proc_mode"

    def test_parse_machine_path_incomplete(self) -> None:
        """Test parsing incomplete machine path."""
        client = T8ApiClient()

        machine, point, proc_mode = client._parse_machine_path("test_machine")

        assert machine == "test_machine"
        assert point == "Unknown"
        assert proc_mode == "Unknown"

    @responses.activate
    def test_list_available_waves_success(self, capsys: pytest.CaptureFixture) -> None:
        """Test listing available waves."""
        client = T8ApiClient()

        responses.add(
            responses.GET,
            BASE_URL + "waves/",
            json={
                "_items": [
                    {
                        "_links": {
                            "self": "http://example.com/waves/machine1/point1/mode1/"
                        }
                    },
                    {
                        "_links": {
                            "self": "http://example.com/waves/machine2/point2/mode2/"
                        }
                    },
                ]
            },
            status=200,
        )

        client.list_available_waves()

        captured = capsys.readouterr()
        assert "machine1" in captured.out
        assert "point1" in captured.out
        assert "machine2" in captured.out

    @responses.activate
    def test_list_available_waves_failure(self) -> None:
        """Test listing available waves with error."""
        client = T8ApiClient()

        responses.add(responses.GET, BASE_URL + "waves/", body="Not Found", status=404)

        # Should not raise exception
        client.list_available_waves()

    @responses.activate
    def test_get_machine_config_success(self) -> None:
        """Test getting machine configuration."""
        client = T8ApiClient()

        responses.add(
            responses.GET,
            BASE_URL + "confs/0",
            json={
                "machines": [
                    {
                        "name": "test_machine",
                        "points": [
                            {
                                "name": "test_point",
                                "proc_modes": [
                                    {
                                        "name": "test_mode",
                                        "sample_rate": 1000,
                                        "min_freq": 0,
                                        "max_freq": 500,
                                    }
                                ],
                            }
                        ],
                    }
                ]
            },
            status=200,
        )

        config = client._get_machine_config("test_machine", "test_point", "test_mode")

        assert config is not None
        assert config["sample_rate"] == 1000
        assert config["min_freq"] == 0
        assert config["max_freq"] == 500

    @responses.activate
    def test_get_machine_config_not_found(self) -> None:
        """Test getting machine configuration when not found."""
        client = T8ApiClient()

        responses.add(
            responses.GET, BASE_URL + "confs/0", json={"machines": []}, status=200
        )

        config = client._get_machine_config("nonexistent", "point", "mode")

        assert config is None

    @responses.activate
    def test_get_machine_config_error(self) -> None:
        """Test getting machine configuration with error."""
        client = T8ApiClient()

        responses.add(
            responses.GET, BASE_URL + "confs/0", body="Server Error", status=500
        )

        config = client._get_machine_config("test_machine", "test_point", "test_mode")

        assert config is None


class TestSpectrumComputation:
    """Tests for spectrum computation methods."""

    def test_compute_spectrum_basic(self) -> None:
        """Test basic spectrum computation."""
        # Create a simple sine wave
        sample_rate = 1000  # Hz
        duration = 1.0  # seconds
        freq = 10  # Hz

        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        waveform = np.sin(2 * np.pi * freq * t)

        frequencies, amplitudes = T8ApiClient.compute_spectrum(
            waveform, sample_rate, 0, sample_rate / 2
        )

        assert len(frequencies) > 0
        assert len(amplitudes) > 0
        assert len(frequencies) == len(amplitudes)
        assert np.max(frequencies) <= sample_rate / 2

    def test_compute_spectrum_with_frequency_range(self) -> None:
        """Test spectrum computation with specific frequency range."""
        sample_rate = 1000
        waveform = np.random.randn(1000)

        fmin = 10
        fmax = 100

        frequencies, amplitudes = T8ApiClient.compute_spectrum(
            waveform, sample_rate, fmin, fmax
        )

        assert np.min(frequencies) >= fmin
        assert np.max(frequencies) <= fmax

    def test_compute_spectrum_with_list_input(self) -> None:
        """Test spectrum computation with list input."""
        sample_rate = 1000
        waveform = [1.0, 2.0, 3.0, 4.0, 5.0] * 100  # Simple list

        frequencies, amplitudes = T8ApiClient.compute_spectrum(
            waveform, sample_rate, 0, 500
        )

        assert len(frequencies) > 0
        assert len(amplitudes) > 0

    def test_compute_spectrum_from_wave_data(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test computing spectrum from wave file data."""
        monkeypatch.chdir(tmp_path)
        client = T8ApiClient()

        # Create a test wave file
        import base64
        import struct
        import zlib

        # Create sample waveform
        waveform_data = [int(100 * np.sin(2 * np.pi * 0.1 * i)) for i in range(100)]
        packed = struct.pack(f"<{len(waveform_data)}h", *waveform_data)
        compressed = zlib.compress(packed)
        encoded = base64.b64encode(compressed).decode("utf-8")

        wave_file_data = {
            "data": encoded,
            "factor": 1.0,
            "sample_rate": 1000,
            "path": "test_machine:test_point:test_mode",
            "timestamp": 1234567890,
        }

        # Save to file
        os.makedirs("test_waves", exist_ok=True)
        wave_filepath = os.path.join("test_waves", "test_wave.json")
        with open(wave_filepath, "w") as f:
            json.dump(wave_file_data, f)

        # Compute spectrum
        frequencies, amplitudes, metadata = client.compute_spectrum_from_wave_data(
            wave_filepath
        )

        assert len(frequencies) > 0
        assert len(amplitudes) > 0
        assert metadata["machine"] == "test_machine"
        assert metadata["point"] == "test_point"
        assert metadata["proc_mode"] == "test_mode"
        assert metadata["min_freq"] == 0
        assert metadata["max_freq"] == 500


class TestDataValidation:
    """Tests for data validation and edge cases."""

    def test_decode_empty_data(self) -> None:
        """Test decoding empty data."""
        client = T8ApiClient()

        result = client.decode_data("", factor=1.0)

        assert result == []

    def test_parse_date_negative_timestamp(self) -> None:
        """Test parsing negative timestamp."""
        client = T8ApiClient()

        timestamp = client._parse_date_to_timestamp("-1")

        assert timestamp == -1

    def test_save_to_file_creates_directories(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that save_to_file creates necessary directories."""
        monkeypatch.chdir(tmp_path)
        client = T8ApiClient()

        data = {"test": "data"}

        # Ensure directories don't exist yet
        assert not os.path.exists("data")

        client.save_to_file(data, "m", "p", "mode", 0, True)

        # Check directories were created
        assert os.path.exists(os.path.join("data", "waves"))
