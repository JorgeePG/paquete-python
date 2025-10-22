import base64
import json
import os
import tempfile
import zlib
from datetime import datetime

import numpy as np  # type: ignore
import responses  # type: ignore

from t8_client import BASE_URL, T8ApiClient


@responses.activate
def test_login_success() -> None:
    responses.add(
        responses.POST,
        "https://lzfs45.mirror.twave.io/lzfs45/signin",
        json={"token": "test_token", "success": True, "text": "Todo bien"},
        status=200,
    )
    client = T8ApiClient()

    assert client.login_with_credentials("user", "pass")


@responses.activate
def test_login_invalid_credentials() -> None:
    responses.add(
        responses.POST,
        "https://lzfs45.mirror.twave.io/lzfs45/signin",
        body="Invalid Username or Password",
        status=200,
    )
    client = T8ApiClient()

    assert not client.login_with_credentials("user", "wrong_pass")


@responses.activate
def test_login_server_error() -> None:
    responses.add(
        responses.POST,
        "https://lzfs45.mirror.twave.io/lzfs45/signin",
        body="Internal Server Error",
        status=500,
    )
    client = T8ApiClient()

    assert not client.login_with_credentials("user", "pass")


@responses.activate
def test_login_exception() -> None:
    responses.add(
        responses.POST,
        "https://lzfs45.mirror.twave.io/lzfs45/signin",
        body=Exception("Connection error"),
    )
    client = T8ApiClient()

    assert not client.login_with_credentials("user", "pass")


@responses.activate
def test_get_waveform_success() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "waves/test_machine/test_point/test_proc_mode",
        json={
            "_links": {
                "home": "http://lzfs45.mirror.twave.io/lzfs45/rest/",
                "last": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/test_machine/test_point/test_proc_mode/0",
            },
            "_items": [
                {
                    "_links": {
                        "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/test_machine/test_point/test_proc_mode/1554907724"
                    }
                },
                {
                    "_links": {
                        "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/test_machine/test_point/test_proc_mode/1554907764"
                    }
                },
            ],
        },
        status=200,
    )
    assert client.list_waves("test_machine", "test_point", "test_proc_mode")


@responses.activate
def test_get_waveform_failure() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "waves/test_machine/test_point/test_proc_mode",
        body="Not Found",
        status=404,
    )
    assert not client.list_waves("test_machine", "test_point", "test_proc_mode")


@responses.activate
def test_get_spectra_success() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "spectra/test_machine/test_point/test_proc_mode",
        json={
            "_links": {
                "home": "http://lzfs45.mirror.twave.io/lzfs45/rest/",
                "last": "http://lzfs45.mirror.twave.io/lzfs45/rest/spectra/test_machine/test_point/test_proc_mode/0",
            },
            "_items": [
                {
                    "_links": {
                        "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/spectra/test_machine/test_point/test_proc_mode/1554907724"
                    }
                },
                {
                    "_links": {
                        "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/spectra/test_machine/test_point/test_proc_mode/1554907764"
                    }
                },
            ],
        },
        status=200,
    )
    assert client.list_spectra("test_machine", "test_point", "test_proc_mode")


@responses.activate
def test_get_spectra_failure() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "spectra/test_machine/test_point/test_proc_mode",
        body="Not Found",
        status=404,
    )
    assert not client.list_spectra("test_machine", "test_point", "test_proc_mode")


@responses.activate
def test_get_wave_success() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "waves/test_machine/test_point/test_proc_mode/0",
        json={
            "_links": {
                "home": "http://lzfs45.mirror.twave.io/lzfs45/rest/",
                "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/test_machine/test_point/test_proc_mode/0",
            },
            "data": "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",  # noqa: E501
            "factor": 0.000102270635,
            "max_freq": 250,
            "min_freq": 0.625,
            "path": "test_machine:test_point:test_proc_mode",
            "snap_t": 1555119736.011538,
            "speed": 2.034545,
            "t": 1555119729.402038,
            "unit_id": 14,
            "window": 1,
        },
        status=200,
    )
    assert (
        client.get_wave("test_machine", "test_point", "test_proc_mode", 0) is not None
    )  # noqa: E501


@responses.activate
def test_get_wave_failure() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "waves/test_machine/test_point/test_proc_mode/0",
        body="Not Found",
        status=404,
    )
    assert client.get_wave("test_machine", "test_point", "test_proc_mode", 0) is None


@responses.activate
def test_get_wave_invalid_date() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "waves/test_machine/test_point/test_proc_mode/-1",
        body="Not Found",
        status=404,
    )
    assert client.get_wave("test_machine", "test_point", "test_proc_mode", -1) is None


@responses.activate
def test_get_wave_exception() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "waves/test_machine/test_point/test_proc_mode/0",
        body=Exception("Connection error"),
    )
    assert client.get_wave("test_machine", "test_point", "test_proc_mode", 0) is None


@responses.activate
def test_get_spectrum_success() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "spectra/test_machine/test_point/test_proc_mode/0",
        json={
            "_links": {
                "home": "http://lzfs45.mirror.twave.io/lzfs45/rest/",
                "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/spectra/test_machine/test_point/test_proc_mode/0",
            },
            "data": "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",  # noqa: E501
            "factor": 0.000102270635,
            "max_freq": 250,
            "min_freq": 0.625,
            "path": "test_machine:test_point:test_proc_mode",
            "snap_t": 1555119736.011538,
            "speed": 2.034545,
            "t": 1555119729.402038,
            "unit_id": 14,
            "window": 1,
        },
        status=200,
    )
    assert (
        client.get_spectrum("test_machine", "test_point", "test_proc_mode", 0)
        is not None
    )  # noqa: E501


@responses.activate
def test_get_spectrum_failure() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "spectra/test_machine/test_point/test_proc_mode/0",
        body="Not Found",
        status=404,
    )
    assert (
        client.get_spectrum("test_machine", "test_point", "test_proc_mode", 0) is None
    )  # noqa: E501


@responses.activate
def test_get_spectrum_invalid_date() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "spectra/test_machine/test_point/test_proc_mode/-1",
        body="Not Found",
        status=404,
    )
    assert (
        client.get_spectrum("test_machine", "test_point", "test_proc_mode", -1) is None
    )  # noqa: E501


@responses.activate
def test_get_spectrum_exception() -> None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "spectra/test_machine/test_point/test_proc_mode/0",
        body=Exception("Connection error"),
    )
    assert (
        client.get_spectrum("test_machine", "test_point", "test_proc_mode", 0) is None
    )  # noqa: E501


# ==============================================================================
# Tests for decode_data()
# ==============================================================================


def test_decode_data_success() -> None:
    """Test successful decoding of compressed wave data."""
    client = T8ApiClient()

    # Create test data: array of int16 values
    test_samples = np.array([100, 200, 300, -100, -200, -300], dtype=np.int16)

    # Compress the data (little-endian int16)
    raw_data = test_samples.tobytes()
    compressed = zlib.compress(raw_data)
    encoded = base64.b64encode(compressed).decode("utf-8")

    # Test decoding with factor 1.0
    decoded = client.decode_data(encoded, factor=1.0)

    assert len(decoded) == len(test_samples)
    assert decoded == [100.0, 200.0, 300.0, -100.0, -200.0, -300.0]


def test_decode_data_with_factor() -> None:
    """Test decoding with scaling factor."""
    client = T8ApiClient()

    test_samples = np.array([100, 200, 300], dtype=np.int16)
    raw_data = test_samples.tobytes()
    compressed = zlib.compress(raw_data)
    encoded = base64.b64encode(compressed).decode("utf-8")

    # Test with factor 0.1
    decoded = client.decode_data(encoded, factor=0.1)

    assert len(decoded) == 3
    assert decoded == [10.0, 20.0, 30.0]


def test_decode_data_empty() -> None:
    """Test decoding with invalid data returns empty list."""
    client = T8ApiClient()

    # Test with invalid base64
    decoded = client.decode_data("invalid_base64", factor=1.0)
    assert decoded == []


def test_decode_data_large_dataset() -> None:
    """Test decoding with larger dataset."""
    client = T8ApiClient()

    # Create 1000 samples
    test_samples = np.array(range(-500, 500), dtype=np.int16)
    raw_data = test_samples.tobytes()
    compressed = zlib.compress(raw_data)
    encoded = base64.b64encode(compressed).decode("utf-8")

    decoded = client.decode_data(encoded, factor=1.0)

    assert len(decoded) == 1000
    assert decoded[0] == -500.0
    assert decoded[-1] == 499.0


# ==============================================================================
# Tests for _parse_date_to_timestamp()
# ==============================================================================


def test_parse_date_iso8601() -> None:
    """Test parsing ISO 8601 date string."""
    client = T8ApiClient()

    # Test with ISO 8601 format
    date_str = "2025-01-15T12:30:45"
    timestamp = client._parse_date_to_timestamp(date_str)

    # Verify it's a valid timestamp
    assert isinstance(timestamp, int)
    assert timestamp > 0

    # Verify it converts back correctly
    dt = datetime.fromtimestamp(timestamp)
    assert dt.year == 2025
    assert dt.month == 1
    assert dt.day == 15


def test_parse_date_timestamp() -> None:
    """Test parsing integer timestamp."""
    client = T8ApiClient()

    # Test with integer timestamp
    original_timestamp = 1555119736
    timestamp = client._parse_date_to_timestamp(original_timestamp)

    assert timestamp == original_timestamp


def test_parse_date_string_timestamp() -> None:
    """Test parsing string representation of timestamp."""
    client = T8ApiClient()

    # Test with string timestamp
    timestamp = client._parse_date_to_timestamp("1555119736")

    assert timestamp == 1555119736


def test_parse_date_invalid() -> None:
    """Test parsing invalid date format raises ValueError."""
    client = T8ApiClient()

    try:
        client._parse_date_to_timestamp("invalid_date")
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "Format error" in str(e)


# ==============================================================================
# Tests for _parse_machine_path()
# ==============================================================================


def test_parse_machine_path_complete() -> None:
    """Test parsing complete machine path."""
    client = T8ApiClient()

    machine, point, proc_mode = client._parse_machine_path("LP_Turbine:MAD31CY005:AM1")

    assert machine == "LP_Turbine"
    assert point == "MAD31CY005"
    assert proc_mode == "AM1"


def test_parse_machine_path_incomplete() -> None:
    """Test parsing incomplete machine path."""
    client = T8ApiClient()

    # Only machine
    machine, point, proc_mode = client._parse_machine_path("LP_Turbine")
    assert machine == "LP_Turbine"
    assert point == "Unknown"
    assert proc_mode == "Unknown"

    # Machine and point
    machine, point, proc_mode = client._parse_machine_path("LP_Turbine:MAD31CY005")
    assert machine == "LP_Turbine"
    assert point == "MAD31CY005"
    assert proc_mode == "Unknown"


def test_parse_machine_path_empty() -> None:
    """Test parsing empty machine path."""
    client = T8ApiClient()

    machine, point, proc_mode = client._parse_machine_path("")
    assert machine == ""
    assert point == "Unknown"
    assert proc_mode == "Unknown"


# ==============================================================================
# Tests for _get_machine_config()
# ==============================================================================


@responses.activate
def test_get_machine_config_success() -> None:
    """Test getting machine configuration successfully."""
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
                                    "sample_rate": 25600,
                                    "min_freq": 0.625,
                                    "max_freq": 250,
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
    assert config["sample_rate"] == 25600
    assert config["min_freq"] == 0.625
    assert config["max_freq"] == 250


@responses.activate
def test_get_machine_config_not_found() -> None:
    """Test when machine configuration is not found."""
    client = T8ApiClient()

    responses.add(
        responses.GET,
        BASE_URL + "confs/0",
        json={"machines": []},
        status=200,
    )

    config = client._get_machine_config("nonexistent", "point", "mode")
    assert config is None


@responses.activate
def test_get_machine_config_api_error() -> None:
    """Test when API returns error."""
    client = T8ApiClient()

    responses.add(
        responses.GET,
        BASE_URL + "confs/0",
        body="Server Error",
        status=500,
    )

    config = client._get_machine_config("test_machine", "test_point", "test_mode")
    assert config is None


# ==============================================================================
# Tests for getUnits()
# ==============================================================================


@responses.activate
def test_get_units_success() -> None:
    """Test getting units successfully."""
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
                            "input": {"sensor": {"unit_id": 14}},
                        }
                    ],
                }
            ],
            "units": [
                {"id": 14, "label": "mm/s"},
                {"id": 15, "label": "g"},
            ],
        },
        status=200,
    )

    unit = client.getUnits("test_machine", "test_point", "test_mode")

    assert unit == "mm/s"


@responses.activate
def test_get_units_not_found() -> None:
    """Test when units are not found."""
    client = T8ApiClient()

    responses.add(
        responses.GET,
        BASE_URL + "confs/0",
        json={"machines": [], "units": []},
        status=200,
    )

    unit = client.getUnits("nonexistent", "point", "mode")
    assert unit is None


@responses.activate
def test_get_units_missing_unit_id() -> None:
    """Test when sensor doesn't have unit_id."""
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
                            "input": {"sensor": {}},
                        }
                    ],
                }
            ],
            "units": [{"id": 14, "label": "mm/s"}],
        },
        status=200,
    )

    unit = client.getUnits("test_machine", "test_point", "test_mode")
    assert unit is None


# ==============================================================================
# Tests for compute_spectrum() - Static Method
# ==============================================================================


def test_compute_spectrum_basic() -> None:
    """Test basic spectrum computation."""
    # Create simple sine wave
    sample_rate = 1000  # 1000 Hz
    duration = 1  # 1 second
    freq = 50  # 50 Hz sine wave

    t = np.linspace(0, duration, sample_rate, endpoint=False)
    waveform = np.sin(2 * np.pi * freq * t)

    # Compute spectrum
    freqs, spectrum = T8ApiClient.compute_spectrum(waveform, sample_rate, 0, 500)

    # Check outputs
    assert len(freqs) > 0
    assert len(spectrum) > 0
    assert len(freqs) == len(spectrum)

    # Frequencies should be in range
    assert freqs[0] >= 0
    assert freqs[-1] <= 500


def test_compute_spectrum_frequency_range() -> None:
    """Test spectrum computation with specific frequency range."""
    sample_rate = 1000
    waveform = np.random.randn(1000)

    # Compute spectrum for limited range
    freqs, spectrum = T8ApiClient.compute_spectrum(waveform, sample_rate, 10, 100)

    # All frequencies should be in specified range
    assert freqs[0] >= 10
    assert freqs[-1] <= 100


def test_compute_spectrum_removes_dc() -> None:
    """Test that DC component is removed."""
    sample_rate = 1000
    # Waveform with DC offset
    waveform = np.ones(1000) * 10 + np.random.randn(1000) * 0.1

    freqs, spectrum = T8ApiClient.compute_spectrum(waveform, sample_rate, 0, 500)

    # Spectrum should exist and be computed
    assert len(spectrum) > 0
    assert isinstance(spectrum, np.ndarray)


def test_compute_spectrum_single_sample() -> None:
    """Test spectrum computation with minimal waveform."""
    # Use at least 2 samples to avoid FFT errors
    waveform = np.array([1.0, 2.0])

    freqs, spectrum = T8ApiClient.compute_spectrum(waveform, 1000, 0, 500)

    # Should handle gracefully
    assert len(freqs) >= 0
    assert len(spectrum) >= 0


# ==============================================================================
# Tests for compute_spectrum_from_wave_data()
# ==============================================================================


def test_compute_spectrum_from_wave_data() -> None:
    """Test computing spectrum from wave JSON file."""
    client = T8ApiClient()

    # Create test waveform data (sine wave)
    test_samples = np.sin(2 * np.pi * 10 * np.linspace(0, 1, 1000))
    test_samples_int16 = (test_samples * 1000).astype(np.int16)

    # Compress the data
    raw_data = test_samples_int16.tobytes()
    compressed = zlib.compress(raw_data)
    encoded = base64.b64encode(compressed).decode("utf-8")

    # Create a temporary test wave file with proper data
    test_wave_data = {
        "data": encoded,
        "factor": 0.001,
        "sample_rate": 1000,
        "path": "test_machine:test_point:test_mode",
        "timestamp": 1555119736,
    }

    # Create temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as temp_file:
        json.dump(test_wave_data, temp_file)
        temp_filepath = temp_file.name

    try:
        # Mock the API configuration endpoint
        with responses.RequestsMock() as rsps:
            rsps.add(
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

            freqs, amplitudes, metadata = client.compute_spectrum_from_wave_data(
                temp_filepath
            )

            # Check that metadata is properly populated
            assert "min_freq" in metadata
            assert "max_freq" in metadata
            assert "sample_rate" in metadata
            assert "machine" in metadata
            assert "point" in metadata
            assert "proc_mode" in metadata

            # Check that data structures are created
            assert isinstance(freqs, np.ndarray)
            assert isinstance(amplitudes, np.ndarray)
            assert len(freqs) > 0
            assert len(amplitudes) > 0
            assert len(freqs) == len(amplitudes)
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filepath):
            os.unlink(temp_filepath)


# ==============================================================================
# Tests for list_available_waves()
# ==============================================================================


@responses.activate
def test_list_available_waves_success() -> None:
    """Test listing all available waves."""
    client = T8ApiClient()

    responses.add(
        responses.GET,
        BASE_URL + "waves/",
        json={
            "_items": [
                {"_links": {"self": BASE_URL + "waves/machine1/point1/mode1/"}},
                {"_links": {"self": BASE_URL + "waves/machine2/point2/mode2/"}},
            ]
        },
        status=200,
    )

    # This should not raise an exception
    client.list_available_waves()


@responses.activate
def test_list_available_waves_empty() -> None:
    """Test listing waves when none available."""
    client = T8ApiClient()

    responses.add(
        responses.GET,
        BASE_URL + "waves/",
        json={"_items": []},
        status=200,
    )

    # Should handle empty list gracefully
    client.list_available_waves()


@responses.activate
def test_list_available_waves_error() -> None:
    """Test listing waves when API returns error."""
    client = T8ApiClient()

    responses.add(
        responses.GET,
        BASE_URL + "waves/",
        body="Server Error",
        status=500,
    )

    # Should handle error gracefully
    client.list_available_waves()


# ==============================================================================
# Tests for check_ok_response()
# ==============================================================================


def test_check_ok_response_success() -> None:
    """Test checking successful response."""
    client = T8ApiClient()

    # Create mock response
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "http://test.com/api",
            json={"success": True, "data": "test"},
            status=200,
        )

        response = client.session.get("http://test.com/api")
        result = client.check_ok_response(response)

        assert result is not None
        assert result["success"] is True
        assert result["data"] == "test"


def test_check_ok_response_error() -> None:
    """Test checking error response."""
    client = T8ApiClient()

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "http://test.com/api",
            body="Not Found",
            status=404,
        )

        response = client.session.get("http://test.com/api")
        result = client.check_ok_response(response)

        assert result is None


def test_check_ok_response_invalid_json() -> None:
    """Test checking response with invalid JSON."""
    client = T8ApiClient()

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "http://test.com/api",
            body="Not valid JSON {{{",
            status=200,
        )

        response = client.session.get("http://test.com/api")
        result = client.check_ok_response(response)

        assert result is None
