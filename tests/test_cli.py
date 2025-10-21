from pathlib import Path
from unittest.mock import Mock, patch

import pytest  # type: ignore
import responses  # type: ignore
from click.testing import CliRunner  # type: ignore

from t8_client import (
    BASE_URL,
    cli,
    compare_spectra,
    compute_spectrum,
    get_spectrum,
    get_wave,
    list_all_waves,
    list_spectra,
    list_waves,
    plot_spectrum,
    plot_wave,
)


@pytest.fixture
def runner() -> CliRunner:
    """Fixture that provides a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_env_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fixture that sets up mock environment credentials."""
    monkeypatch.setenv("T8_USER", "test_user")
    monkeypatch.setenv("T8_PASSWORD", "test_pass")


@pytest.fixture
def mock_env_no_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fixture that removes environment credentials."""
    monkeypatch.delenv("T8_USER", raising=False)
    monkeypatch.delenv("T8_PASSWORD", raising=False)


class TestListWaves:
    """Tests for list_waves CLI command."""

    @responses.activate
    def test_list_waves_success(
        self, runner: CliRunner, mock_env_credentials: None
    ) -> None:  # noqa: E501
        """Test successful wave listing."""
        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        # Mock list_waves API call
        responses.add(
            responses.GET,
            BASE_URL + "waves/test_machine/test_point/test_mode",
            json={
                "_items": [
                    {"_links": {"self": "http://example.com/waves/test/1234567890"}}
                ]
            },
            status=200,
        )

        result = runner.invoke(
            list_waves, ["-M", "test_machine", "-P", "test_point", "-m", "test_mode"]
        )

        assert result.exit_code == 0

    @responses.activate
    def test_list_waves_auth_failure(
        self, runner: CliRunner, mock_env_credentials: None
    ) -> None:  # noqa: E501
        """Test wave listing with authentication failure."""
        # Mock login failure
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            body="Invalid Username or Password",
            status=200,
        )

        result = runner.invoke(
            list_waves, ["-M", "test_machine", "-P", "test_point", "-m", "test_mode"]
        )

        assert result.exit_code == 0
        assert "No se pudo autenticar" in result.output

    def test_list_waves_no_credentials(
        self, runner: CliRunner, mock_env_no_credentials: None
    ) -> None:
        """Test wave listing without credentials."""
        result = runner.invoke(
            list_waves, ["-M", "test_machine", "-P", "test_point", "-m", "test_mode"]
        )

        assert result.exit_code == 0
        assert "No se encontraron credenciales" in result.output

    def test_list_waves_missing_required_options(self, runner: CliRunner) -> None:
        """Test wave listing with missing required options."""
        result = runner.invoke(list_waves, ["-M", "test_machine"])

        assert result.exit_code != 0
        assert "Error" in result.output or "Missing option" in result.output


class TestListSpectra:
    """Tests for list_spectra CLI command."""

    @responses.activate
    def test_list_spectra_success(
        self, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test successful spectra listing."""
        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        # Mock list_spectra API call
        responses.add(
            responses.GET,
            BASE_URL + "spectra/test_machine/test_point/test_mode",
            json={
                "_items": [
                    {"_links": {"self": "http://example.com/spectra/test/1234567890"}}
                ]
            },
            status=200,
        )

        result = runner.invoke(
            list_spectra, ["-M", "test_machine", "-P", "test_point", "-m", "test_mode"]
        )

        assert result.exit_code == 0

    @responses.activate
    def test_list_spectra_auth_failure(
        self, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test spectra listing with authentication failure."""
        # Mock login failure
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            body="Invalid Username or Password",
            status=200,
        )

        result = runner.invoke(
            list_spectra, ["-M", "test_machine", "-P", "test_point", "-m", "test_mode"]
        )

        assert result.exit_code == 0
        assert "No se pudo autenticar" in result.output

    def test_list_spectra_no_credentials(
        self, runner: CliRunner, mock_env_no_credentials: None
    ) -> None:
        """Test spectra listing without credentials."""
        result = runner.invoke(
            list_spectra, ["-M", "test_machine", "-P", "test_point", "-m", "test_mode"]
        )

        assert result.exit_code == 0
        assert "No se encontraron credenciales" in result.output


class TestGetWave:
    """Tests for get_wave CLI command."""

    @responses.activate
    def test_get_wave_success(
        self,
        runner: CliRunner,
        mock_env_credentials: None,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test successful wave retrieval."""
        monkeypatch.chdir(tmp_path)

        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        # Mock get_wave API call
        responses.add(
            responses.GET,
            BASE_URL + "waves/test_machine/test_point/test_mode/0",
            json={"data": "test_data", "factor": 1.0, "timestamp": 1234567890},
            status=200,
        )

        result = runner.invoke(
            get_wave, ["-M", "test_machine", "-P", "test_point", "-m", "test_mode"]
        )

        assert result.exit_code == 0

    @responses.activate
    def test_get_wave_with_date(
        self,
        runner: CliRunner,
        mock_env_credentials: None,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test wave retrieval with specific date."""
        monkeypatch.chdir(tmp_path)

        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        # Mock get_wave API call with specific timestamp
        responses.add(
            responses.GET,
            BASE_URL + "waves/test_machine/test_point/test_mode/1704110602",
            json={"data": "test_data", "factor": 1.0, "timestamp": 1704110602},
            status=200,
        )

        result = runner.invoke(
            get_wave,
            [
                "-M",
                "test_machine",
                "-P",
                "test_point",
                "-m",
                "test_mode",
                "-d",
                "2024-01-01T12:30:02",
            ],
        )

        assert result.exit_code == 0

    @responses.activate
    def test_get_wave_with_timestamp(
        self,
        runner: CliRunner,
        mock_env_credentials: None,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test wave retrieval with timestamp."""
        monkeypatch.chdir(tmp_path)

        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        # Mock get_wave API call
        responses.add(
            responses.GET,
            BASE_URL + "waves/test_machine/test_point/test_mode/1234567890",
            json={"data": "test_data", "factor": 1.0, "timestamp": 1234567890},
            status=200,
        )

        result = runner.invoke(
            get_wave,
            [
                "-M",
                "test_machine",
                "-P",
                "test_point",
                "-m",
                "test_mode",
                "-t",
                "1234567890",
            ],
        )

        assert result.exit_code == 0

    def test_get_wave_both_date_and_timestamp(
        self, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test that providing both date and timestamp fails."""
        result = runner.invoke(
            get_wave,
            [
                "-M",
                "test_machine",
                "-P",
                "test_point",
                "-m",
                "test_mode",
                "-d",
                "2024-01-01T12:00:00",
                "-t",
                "1234567890",
            ],
        )

        assert result.exit_code == 0
        assert "No se pueden especificar tanto --date como --timestamp" in result.output

    @responses.activate
    def test_get_wave_auth_failure(
        self, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test wave retrieval with authentication failure."""
        # Mock login failure
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            body="Invalid Username or Password",
            status=200,
        )

        result = runner.invoke(
            get_wave, ["-M", "test_machine", "-P", "test_point", "-m", "test_mode"]
        )

        assert result.exit_code == 0
        assert "No se pudo autenticar" in result.output


class TestGetSpectrum:
    """Tests for get_spectrum CLI command."""

    @responses.activate
    def test_get_spectrum_success(
        self,
        runner: CliRunner,
        mock_env_credentials: None,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test successful spectrum retrieval."""
        monkeypatch.chdir(tmp_path)

        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        # Mock get_spectrum API call
        responses.add(
            responses.GET,
            BASE_URL + "spectra/test_machine/test_point/test_mode/0",
            json={
                "data": "test_data",
                "factor": 0.5,
                "max_freq": 250,
                "min_freq": 0.625,
                "timestamp": 1234567890,
            },
            status=200,
        )

        result = runner.invoke(
            get_spectrum, ["-M", "test_machine", "-P", "test_point", "-m", "test_mode"]
        )

        assert result.exit_code == 0

    @responses.activate
    def test_get_spectrum_with_date(
        self,
        runner: CliRunner,
        mock_env_credentials: None,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test spectrum retrieval with specific date."""
        monkeypatch.chdir(tmp_path)

        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        # Mock get_spectrum API call
        responses.add(
            responses.GET,
            BASE_URL + "spectra/test_machine/test_point/test_mode/1704110602",
            json={
                "data": "test_data",
                "factor": 0.5,
                "max_freq": 250,
                "min_freq": 0.625,
                "timestamp": 1704110602,
            },
            status=200,
        )

        result = runner.invoke(
            get_spectrum,
            [
                "-M",
                "test_machine",
                "-P",
                "test_point",
                "-m",
                "test_mode",
                "-d",
                "2024-01-01T12:30:02",
            ],
        )

        assert result.exit_code == 0

    def test_get_spectrum_both_date_and_timestamp(
        self, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test that providing both date and timestamp fails."""
        result = runner.invoke(
            get_spectrum,
            [
                "-M",
                "test_machine",
                "-P",
                "test_point",
                "-m",
                "test_mode",
                "-d",
                "2024-01-01T12:00:00",
                "-t",
                "1234567890",
            ],
        )

        assert result.exit_code == 0
        assert "No se pueden especificar tanto --date como --timestamp" in result.output


class TestPlotWave:
    """Tests for plot_wave CLI command."""

    @responses.activate
    @patch("t8_client.cli.T8ApiClient.plot_wave")
    def test_plot_wave_success(
        self, mock_plot: Mock, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test successful wave plotting."""
        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        result = runner.invoke(
            plot_wave, ["-M", "test_machine", "-P", "test_point", "-m", "test_mode"]
        )

        assert result.exit_code == 0
        mock_plot.assert_called_once_with(
            "test_machine", "test_point", "test_mode", "0"
        )

    @responses.activate
    @patch("t8_client.cli.T8ApiClient.plot_wave")
    def test_plot_wave_with_timestamp(
        self, mock_plot: Mock, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test wave plotting with timestamp."""
        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        result = runner.invoke(
            plot_wave,
            [
                "-M",
                "test_machine",
                "-P",
                "test_point",
                "-m",
                "test_mode",
                "-t",
                "1234567890",
            ],
        )

        assert result.exit_code == 0
        mock_plot.assert_called_once_with(
            "test_machine", "test_point", "test_mode", "1234567890"
        )

    def test_plot_wave_both_date_and_timestamp(
        self, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test that providing both date and timestamp fails."""
        result = runner.invoke(
            plot_wave,
            [
                "-M",
                "test_machine",
                "-P",
                "test_point",
                "-m",
                "test_mode",
                "-d",
                "2024-01-01T12:00:00",
                "-t",
                "1234567890",
            ],
        )

        assert result.exit_code == 0
        assert "No se pueden especificar tanto --date como --timestamp" in result.output


class TestPlotSpectrum:
    """Tests for plot_spectrum CLI command."""

    @responses.activate
    @patch("t8_client.cli.T8ApiClient.plot_spectrum")
    def test_plot_spectrum_success(
        self, mock_plot: Mock, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test successful spectrum plotting."""
        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        result = runner.invoke(
            plot_spectrum, ["-M", "test_machine", "-P", "test_point", "-m", "test_mode"]
        )

        assert result.exit_code == 0
        mock_plot.assert_called_once_with(
            "test_machine", "test_point", "test_mode", "0"
        )

    @responses.activate
    @patch("t8_client.cli.T8ApiClient.plot_spectrum")
    def test_plot_spectrum_with_date(
        self, mock_plot: Mock, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test spectrum plotting with date."""
        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        result = runner.invoke(
            plot_spectrum,
            [
                "-M",
                "test_machine",
                "-P",
                "test_point",
                "-m",
                "test_mode",
                "-d",
                "2024-01-01T12:00:00",
            ],
        )

        assert result.exit_code == 0
        mock_plot.assert_called_once_with(
            "test_machine", "test_point", "test_mode", "2024-01-01T12:00:00"
        )


class TestListAllWaves:
    """Tests for list_all_waves CLI command."""

    @responses.activate
    def test_list_all_waves_success(
        self, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test successful listing of all waves."""
        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        # Mock list_available_waves API call
        responses.add(
            responses.GET,
            BASE_URL + "waves/",
            json={
                "_items": [
                    {"_links": {"self": "http://example.com/waves/m1/p1/mode1/"}},
                    {"_links": {"self": "http://example.com/waves/m2/p2/mode2/"}},
                ]
            },
            status=200,
        )

        result = runner.invoke(list_all_waves)

        assert result.exit_code == 0

    @responses.activate
    def test_list_all_waves_auth_failure(
        self, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test listing all waves with auth failure."""
        # Mock login failure
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            body="Invalid Username or Password",
            status=200,
        )

        result = runner.invoke(list_all_waves)

        assert result.exit_code == 0
        assert "No se pudo autenticar" in result.output

    def test_list_all_waves_no_credentials(
        self, runner: CliRunner, mock_env_no_credentials: None
    ) -> None:
        """Test listing all waves without credentials."""
        result = runner.invoke(list_all_waves)

        assert result.exit_code == 0
        assert "No se encontraron credenciales" in result.output


class TestComputeSpectrum:
    """Tests for compute_spectrum CLI command."""

    @responses.activate
    @patch("t8_client.cli.T8ApiClient.compute_spectrum_with_json")
    def test_compute_spectrum_success(
        self,
        mock_compute: Mock,
        runner: CliRunner,
        mock_env_credentials: None,
        tmp_path: Path,
    ) -> None:
        """Test successful spectrum computation from file."""
        # Mock login
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            json={"token": "test_token", "success": True},
            status=200,
        )

        # Create a temporary wave file
        wave_file = tmp_path / "test_wave.json"
        wave_file.write_text('{"data": "test", "factor": 1.0}')

        result = runner.invoke(compute_spectrum, [str(wave_file)])

        assert result.exit_code == 0
        mock_compute.assert_called_once_with(str(wave_file))

    @responses.activate
    def test_compute_spectrum_auth_failure(
        self, runner: CliRunner, mock_env_credentials: None, tmp_path: Path
    ) -> None:
        """Test spectrum computation with auth failure."""
        # Mock login failure
        responses.add(
            responses.POST,
            "https://lzfs45.mirror.twave.io/lzfs45/signin",
            body="Invalid Username or Password",
            status=200,
        )

        # Create a temporary wave file
        wave_file = tmp_path / "test_wave.json"
        wave_file.write_text('{"data": "test", "factor": 1.0}')

        result = runner.invoke(compute_spectrum, [str(wave_file)])

        assert result.exit_code == 0
        assert "No se pudo autenticar" in result.output

    def test_compute_spectrum_file_not_found(
        self, runner: CliRunner, mock_env_credentials: None
    ) -> None:
        """Test spectrum computation with non-existent file."""
        result = runner.invoke(compute_spectrum, ["nonexistent_file.json"])

        assert result.exit_code != 0
        # Click will show error about file not existing


class TestCompareSpectra:
    """Tests for compare_spectra CLI command."""

    @patch("subprocess.run")
    def test_compare_spectra_success(
        self, mock_run: Mock, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test successful spectra comparison."""
        # Create temporary files
        spectrum_file = tmp_path / "spectrum.json"
        wave_file = tmp_path / "wave.json"
        spectrum_file.write_text('{"data": "spectrum"}')
        wave_file.write_text('{"data": "wave"}')

        # Mock subprocess.run to simulate successful execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Comparison successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = runner.invoke(compare_spectra, [str(spectrum_file), str(wave_file)])

        assert result.exit_code == 0
        assert "Comparison successful" in result.output
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_compare_spectra_with_output(
        self, mock_run: Mock, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test spectra comparison with output file."""
        # Create temporary files
        spectrum_file = tmp_path / "spectrum.json"
        wave_file = tmp_path / "wave.json"
        output_file = tmp_path / "output.png"
        spectrum_file.write_text('{"data": "spectrum"}')
        wave_file.write_text('{"data": "wave"}')

        # Mock subprocess.run
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Saved to output.png"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = runner.invoke(
            compare_spectra,
            [str(spectrum_file), str(wave_file), "-o", str(output_file)],
        )

        assert result.exit_code == 0
        assert mock_run.called
        # Verify -o option was passed to subprocess
        call_args = mock_run.call_args[0][0]
        assert "-o" in call_args

    @patch("subprocess.run")
    def test_compare_spectra_script_failure(
        self, mock_run: Mock, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test spectra comparison when script fails."""
        # Create temporary files
        spectrum_file = tmp_path / "spectrum.json"
        wave_file = tmp_path / "wave.json"
        spectrum_file.write_text('{"data": "spectrum"}')
        wave_file.write_text('{"data": "wave"}')

        # Mock subprocess.run to simulate failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error in comparison"
        mock_run.return_value = mock_result

        result = runner.invoke(compare_spectra, [str(spectrum_file), str(wave_file)])

        assert result.exit_code == 0
        assert (
            "falló con código" in result.output
            or "Error in comparison" in result.output
        )

    @patch("subprocess.run")
    def test_compare_spectra_exception(
        self, mock_run: Mock, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test spectra comparison when subprocess raises exception."""
        # Create temporary files
        spectrum_file = tmp_path / "spectrum.json"
        wave_file = tmp_path / "wave.json"
        spectrum_file.write_text('{"data": "spectrum"}')
        wave_file.write_text('{"data": "wave"}')

        # Mock subprocess.run to raise exception
        mock_run.side_effect = Exception("Subprocess error")

        result = runner.invoke(compare_spectra, [str(spectrum_file), str(wave_file)])

        assert result.exit_code == 0
        assert "Error ejecutando script" in result.output


class TestCLIGroup:
    """Tests for the main CLI group."""

    def test_cli_help(self, runner: CliRunner) -> None:
        """Test that CLI help works."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "CLI para interactuar con la API T8" in result.output

    def test_cli_command_list(self, runner: CliRunner) -> None:
        """Test that all commands are listed."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        # Check that main commands are listed
        assert "list-waves" in result.output or "list_waves" in result.output
        assert "get-wave" in result.output or "get_wave" in result.output
        assert "get-spectrum" in result.output or "get_spectrum" in result.output
