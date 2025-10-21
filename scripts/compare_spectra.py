#!/usr/bin/env python3
"""
Script to compare locally calculated spectra vs spectra downloaded from the T8 API.

This script loads a spectrum downloaded from the API and a spectrum calculated locally
from a wave, and compares them graphically using two subplots.

Usage:
    python scripts/compare_spectra.py <api_spectrum> <wave_to_calculate>
    python scripts/compare_spectra.py data/spectra/spectrum_*.json data/waves/wave_*.json

Example:
    python scripts/compare_spectra.py \
        data/spectra/spectrum_LP_Turbine_MAD32CY005_AM2_1554993802.json \
        data/waves/wave_LP_Turbine_MAD32CY005_AM2_1554993802.json
"""  # noqa: E501

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore

# Add src directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Adjusted import for the real project structure
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "t8-client"))
from t8_client import T8ApiClient  # type: ignore


def load_api_spectrum(
    spectrum_file: str,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:  # noqa: E501
    """
    Loads a spectrum downloaded from the API from a JSON file.

    Args:
        spectrum_file: Path to the spectrum JSON file

    Returns:
        Tuple with (frequencies, amplitudes, metadata)
    """
    with open(spectrum_file) as f:
        data = json.load(f)

    # Extract spectrum data
    encoded_data = data.get("data", "")
    factor = data.get("factor", 1.0)
    max_freq = data.get("max_freq", 250)  # Hz
    min_freq = data.get("min_freq", 0.625)  # Hz

    if not encoded_data:
        raise ValueError("No spectrum data found in file")

    # Decode data using T8 client method
    client = T8ApiClient()
    samples = client.decode_data(encoded_data, factor)

    if not samples:
        raise ValueError("Could not decode spectrum data")

    # Create frequency array
    num_samples = len(samples)
    frequencies = np.linspace(min_freq, max_freq, num_samples)
    amplitudes = np.array(samples)

    # Metadata for plot information
    metadata = {
        "min_freq": min_freq,
        "max_freq": max_freq,
        "num_samples": num_samples,
        "path": data.get("path", "Unknown"),
        "timestamp": data.get("timestamp", 0),
    }

    return frequencies, amplitudes, metadata


def compute_spectrum_from_wave(
    wave_file: str, api_metadata: dict[str, Any] = None
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """
    Calculates a spectrum from a wave file using FFT.
    Uses the existing method in T8ApiClient to avoid duplication.

    Args:
        wave_file: Path to the wave JSON file
        api_metadata: API spectrum metadata to use the same ranges

    Returns:
        Tuple with (frequencies, amplitudes, metadata)
    """
    # Create T8 client
    client = T8ApiClient()

    # Use the same frequency range as the API spectrum if available
    fmin = None
    fmax = None
    if api_metadata:
        fmin = api_metadata["min_freq"]
        fmax = api_metadata["max_freq"]
        print(f"  Using API spectrum range: {fmin:.1f} - {fmax:.1f} Hz")

    # Use the existing client method
    frequencies, amplitudes, metadata = client.compute_spectrum_from_wave_data(
        wave_file
    )

    return frequencies, amplitudes, metadata


def compare_spectra(
    spectrum_file: str, wave_file: str, output_file: str = None
) -> None:
    """
    Compares an API spectrum with a calculated spectrum and generates a plot.

    Args:
        spectrum_file: API spectrum JSON file
        wave_file: Wave JSON file to calculate spectrum
        output_file: Optional file to save the plot
    """
    print("🔄 Loading API spectrum...")
    try:
        api_freqs, api_amplitudes, api_metadata = load_api_spectrum(spectrum_file)
        print(f"✓ API spectrum loaded: {api_metadata['num_samples']} points")
        print(
            f"  Range: {api_metadata['min_freq']:.1f} - {api_metadata['max_freq']:.1f} Hz"
        )  # noqa: E501
    except Exception as e:
        print(f"❌ Error loading API spectrum: {e}")
        return

    print("\n🧮 Calculating spectrum from wave...")
    try:
        # Pass API metadata to use same frequency range
        calc_freqs, calc_amplitudes, calc_metadata = compute_spectrum_from_wave(
            wave_file, api_metadata
        )
        print(f"✓ Spectrum calculated: {calc_metadata['num_samples']} points")
        print(
            f"  Range: {calc_metadata['min_freq']:.1f} - {calc_metadata['max_freq']:.1f} Hz"
        )  # noqa: E501
    except Exception as e:
        print(f"❌ Error calculating spectrum: {e}")
        return

    print("\n📊 Generating comparison plot...")

    # Configure matplotlib
    matplotlib.use("Agg")  # Backend to save files

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle(
        "Spectrum Comparison: API vs Calculated", fontsize=16, fontweight="bold"
    )  # noqa: E501

    # Subplot 1: API spectrum
    ax1.plot(api_freqs, api_amplitudes, "b-", linewidth=0.8, label="API Spectrum")
    ax1.set_title(f"Spectrum downloaded from API\n{api_metadata['path']}", fontsize=12)
    ax1.set_xlabel("Frequency (Hz)")
    ax1.set_ylabel("Amplitude")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # API spectrum information
    api_info = (
        f"Points: {api_metadata['num_samples']}\n"
        f"Range: {api_metadata['min_freq']:.1f}-{api_metadata['max_freq']:.1f} Hz\n"
        f"Max: {np.max(api_amplitudes):.6f}"
    )
    ax1.text(
        0.02,
        0.98,
        api_info,
        transform=ax1.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8),
    )  # noqa: E501

    # Subplot 2: Calculated spectrum
    ax2.plot(
        calc_freqs, calc_amplitudes, "r-", linewidth=0.8, label="Calculated Spectrum"
    )  # noqa: E501
    ax2.set_title(f"Spectrum calculated with FFT\n{calc_metadata['path']}", fontsize=12)
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Amplitude")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    # Calculated spectrum information
    calc_info = (
        f"Points: {calc_metadata['num_samples']}\n"
        f"Range: {calc_metadata['min_freq']:.1f}-{calc_metadata['max_freq']:.1f} Hz\n"
        f"Fs: {calc_metadata['sample_rate']} Hz\n"
        f"Max: {np.max(calc_amplitudes):.6f}"
    )
    ax2.text(
        0.02,
        0.98,
        calc_info,
        transform=ax2.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="lightcoral", alpha=0.8),
    )  # noqa: E501

    plt.tight_layout()

    # Save the plot
    if output_file is None:
        # Generate automatic name based on input files
        spectrum_name = Path(spectrum_file).stem
        wave_name = Path(wave_file).stem
        filename = f"comparison_{spectrum_name}_vs_{wave_name}.png"

        # Create data/plots directory if it doesn't exist
        plots_dir = Path("data/plots")
        plots_dir.mkdir(parents=True, exist_ok=True)
        output_file = str(plots_dir / filename)

    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"✓ Plot saved to: {output_file}")

    # Comparison statistics
    print("\n📈 Comparison statistics:")
    print(
        f"  API    - Points: {len(api_amplitudes):,}, Max: {np.max(api_amplitudes):.6f}, RMS: {np.sqrt(np.mean(api_amplitudes**2)):.6f}"
    )  # noqa: E501
    print(
        f"  Calc   - Points: {len(calc_amplitudes):,}, Max: {np.max(calc_amplitudes):.6f}, RMS: {np.sqrt(np.mean(calc_amplitudes**2)):.6f}"
    )  # noqa: E501

    # Try to calculate correlation if ranges are compatible
    try:
        if len(api_freqs) > 10 and len(calc_freqs) > 10:
            # Interpolate to compare at the same frequencies
            common_freqs = np.linspace(
                max(np.min(api_freqs), np.min(calc_freqs)),
                min(np.max(api_freqs), np.max(calc_freqs)),
                min(len(api_freqs), len(calc_freqs)),
            )

            api_interp = np.interp(common_freqs, api_freqs, api_amplitudes)
            calc_interp = np.interp(common_freqs, calc_freqs, calc_amplitudes)

            correlation = np.corrcoef(api_interp, calc_interp)[0, 1]
            print(f"  Correlation: {correlation:.4f}")
    except Exception:
        print("  Correlation: Could not calculate")

    print("\n✅ Comparison completed successfully")


def main() -> None:
    """Main script function."""
    parser = argparse.ArgumentParser(
        description="Compares API spectra with locally calculated spectra",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("spectrum_file", help="API spectrum JSON file")
    parser.add_argument("wave_file", help="Wave JSON file to calculate spectrum")
    parser.add_argument("-o", "--output", help="Output file for plot (optional)")

    args = parser.parse_args()

    # Verify files exist
    if not Path(args.spectrum_file).exists():
        print(f"❌ Error: Spectrum file does not exist: {args.spectrum_file}")
        sys.exit(1)

    if not Path(args.wave_file).exists():
        print(f"❌ Error: Wave file does not exist: {args.wave_file}")
        sys.exit(1)

    # Execute comparison
    try:
        compare_spectra(args.spectrum_file, args.wave_file, args.output)
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
