#!/usr/bin/env python3
"""
Script para comparar espectros calculados localmente vs espectros descargados de la API T8.

Este script carga un espectro descargado de la API y un espectro calculado localmente
a partir de una onda, y los compara gráficamente usando dos subplots.

Uso:
    python scripts/compare_spectra.py <espectro_api> <onda_para_calcular>
    python scripts/compare_spectra.py data/spectra/spectrum_*.json data/waves/wave_*.json

Ejemplo:
    python scripts/compare_spectra.py \
        data/spectra/spectrum_LP_Turbine_MAD32CY005_AM2_1554993802.json \
        data/waves/wave_LP_Turbine_MAD32CY005_AM2_1554993802.json
"""  # noqa: E501

import sys
import json
import argparse
from pathlib import Path
import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
import matplotlib # type: ignore
from typing import Any

# Añadir el directorio src al path para importar nuestros módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import ajustado para la estructura real del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "t8-client"))
from t8_client import T8ApiClient # type: ignore


def load_api_spectrum(spectrum_file: str) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:  # noqa: E501
    """
    Carga un espectro descargado de la API desde un archivo JSON.
    
    Args:
        spectrum_file: Ruta al archivo JSON del espectro
        
    Returns:
        Tuple con (frecuencias, amplitudes, metadata)
    """
    with open(spectrum_file) as f:
        data = json.load(f)
    
    # Extraer datos del espectro
    encoded_data = data.get("data", "")
    factor = data.get("factor", 1.0)
    max_freq = data.get("max_freq", 250)  # Hz
    min_freq = data.get("min_freq", 0.625)  # Hz
    
    if not encoded_data:
        raise ValueError("No se encontraron datos de espectro en el archivo")
    
    # Decodificar los datos usando el método del cliente T8
    client = T8ApiClient()
    samples = client.decode_data(encoded_data, factor)
    
    if not samples:
        raise ValueError("No se pudieron decodificar los datos del espectro")
    
    # Crear array de frecuencias
    num_samples = len(samples)
    frequencies = np.linspace(min_freq, max_freq, num_samples)
    amplitudes = np.array(samples)
    
    # Metadata para información del gráfico
    metadata = {
        "min_freq": min_freq,
        "max_freq": max_freq,
        "num_samples": num_samples,
        "path": data.get("path", "Unknown"),
        "timestamp": data.get("timestamp", 0)
    }
    
    return frequencies, amplitudes, metadata


def compute_spectrum_from_wave(
    wave_file: str, api_metadata: dict[str, Any] = None
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """
    Calcula un espectro a partir de un archivo de onda usando FFT.
    Usa el método existente en T8ApiClient para evitar duplicación.
    
    Args:
        wave_file: Ruta al archivo JSON de la onda
        api_metadata: Metadata del espectro API para usar los mismos rangos
        
    Returns:
        Tuple con (frecuencias, amplitudes, metadata)
    """
    # Crear cliente T8
    client = T8ApiClient()
    
    # Usar el mismo rango de frecuencias que el espectro API si está disponible
    fmin = None
    fmax = None
    if api_metadata:
        fmin = api_metadata["min_freq"]
        fmax = api_metadata["max_freq"]
        print(f"  Usando rango del espectro API: {fmin:.1f} - {fmax:.1f} Hz")
    
    # Usar el método existente del cliente
    frequencies, amplitudes, metadata = client.compute_spectrum_from_wave_data(
        wave_file, fmin, fmax
    )
    
    return frequencies, amplitudes, metadata


def compare_spectra(spectrum_file: str, wave_file: str, output_file: str = None) ->None:
    """
    Compara un espectro de la API con un espectro calculado y genera un gráfico.
    
    Args:
        spectrum_file: Archivo JSON del espectro de la API
        wave_file: Archivo JSON de la onda para calcular espectro
        output_file: Archivo opcional para guardar el gráfico
    """
    print("🔄 Cargando espectro de la API...")
    try:
        api_freqs, api_amplitudes, api_metadata = load_api_spectrum(spectrum_file)
        print(f"✓ Espectro API cargado: {api_metadata['num_samples']} puntos")
        print(f"  Rango: {api_metadata['min_freq']:.1f} - {api_metadata['max_freq']:.1f} Hz")  # noqa: E501
    except Exception as e:
        print(f"❌ Error cargando espectro de la API: {e}")
        return
    
    print("\n🧮 Calculando espectro desde onda...")
    try:
        # Pasar metadata de API para usar mismo rango de frecuencias
        calc_freqs, calc_amplitudes, calc_metadata = compute_spectrum_from_wave(
            wave_file, api_metadata
        )
        print(f"✓ Espectro calculado: {calc_metadata['num_samples']} puntos")
        print(f"  Rango: {calc_metadata['min_freq']:.1f} - {calc_metadata['max_freq']:.1f} Hz")  # noqa: E501
    except Exception as e:
        print(f"❌ Error calculando espectro: {e}")
        return
    
    print("\n📊 Generando gráfico de comparación...")
    
    # Configurar matplotlib
    matplotlib.use("Agg")  # Backend para guardar archivos
    
    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle("Comparación de Espectros: API vs Calculado", fontsize=16, fontweight="bold")  # noqa: E501
    
    # Subplot 1: Espectro de la API
    ax1.plot(api_freqs, api_amplitudes, "b-", linewidth=0.8, label="Espectro API")
    ax1.set_title(f"Espectro descargado de la API\n{api_metadata['path']}", fontsize=12)
    ax1.set_xlabel("Frecuencia (Hz)")
    ax1.set_ylabel("Amplitud")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Información del espectro API
    api_info = (
        f"Puntos: {api_metadata['num_samples']}\n"
        f"Rango: {api_metadata['min_freq']:.1f}-{api_metadata['max_freq']:.1f} Hz\n"
        f"Max: {np.max(api_amplitudes):.6f}"
    )
    ax1.text(0.02, 0.98, api_info, transform=ax1.transAxes, 
             verticalalignment="top", bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8))  # noqa: E501
    
    # Subplot 2: Espectro calculado
    ax2.plot(calc_freqs, calc_amplitudes, "r-", linewidth=0.8, label="Espectro Calculado")  # noqa: E501
    ax2.set_title(f"Espectro calculado con FFT\n{calc_metadata['path']}", fontsize=12)
    ax2.set_xlabel("Frecuencia (Hz)")
    ax2.set_ylabel("Amplitud")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Información del espectro calculado
    calc_info = (
        f"Puntos: {calc_metadata['num_samples']}\n"
        f"Rango: {calc_metadata['min_freq']:.1f}-{calc_metadata['max_freq']:.1f} Hz\n"
        f"Fs: {calc_metadata['sample_rate']} Hz\n"
        f"Max: {np.max(calc_amplitudes):.6f}"
    )
    ax2.text(0.02, 0.98, calc_info, transform=ax2.transAxes, 
             verticalalignment="top", bbox=dict(boxstyle="round", facecolor="lightcoral", alpha=0.8))  # noqa: E501
    
    plt.tight_layout()
    
    # Guardar el gráfico
    if output_file is None:
        # Generar nombre automático basado en los archivos de entrada
        spectrum_name = Path(spectrum_file).stem
        wave_name = Path(wave_file).stem
        filename = f"comparison_{spectrum_name}_vs_{wave_name}.png"
        
        # Crear directorio data/plots si no existe
        plots_dir = Path("data/plots")
        plots_dir.mkdir(parents=True, exist_ok=True)
        output_file = str(plots_dir / filename)
    
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"✓ Gráfico guardado en: {output_file}")
    
    # Estadísticas de comparación
    print("\n📈 Estadísticas de comparación:")
    print(f"  API    - Puntos: {len(api_amplitudes):,}, Max: {np.max(api_amplitudes):.6f}, RMS: {np.sqrt(np.mean(api_amplitudes**2)):.6f}")  # noqa: E501
    print(f"  Calc   - Puntos: {len(calc_amplitudes):,}, Max: {np.max(calc_amplitudes):.6f}, RMS: {np.sqrt(np.mean(calc_amplitudes**2)):.6f}")  # noqa: E501
    
    # Intentar calcular correlación si los rangos son compatibles
    try:
        if len(api_freqs) > 10 and len(calc_freqs) > 10:
            # Interpolar para comparar en las mismas frecuencias
            common_freqs = np.linspace(
                max(np.min(api_freqs), np.min(calc_freqs)),
                min(np.max(api_freqs), np.max(calc_freqs)),
                min(len(api_freqs), len(calc_freqs))
            )
            
            api_interp = np.interp(common_freqs, api_freqs, api_amplitudes)
            calc_interp = np.interp(common_freqs, calc_freqs, calc_amplitudes)
            
            correlation = np.corrcoef(api_interp, calc_interp)[0, 1]
            print(f"  Correlación: {correlation:.4f}")
    except Exception:
        print("  Correlación: No se pudo calcular")
    
    print("\n✅ Comparación completada exitosamente")


def main() -> None:
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Compara espectros de la API con espectros calculados localmente",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("spectrum_file", 
                       help="Archivo JSON del espectro descargado de la API")
    parser.add_argument("wave_file", 
                       help="Archivo JSON de la onda para calcular el espectro")
    parser.add_argument("-o", "--output", 
                       help="Archivo de salida para el gráfico (opcional)")
    
    args = parser.parse_args()
    
    # Verificar que los archivos existen
    if not Path(args.spectrum_file).exists():
        print(f"❌ Error: El archivo de espectro no existe: {args.spectrum_file}")
        sys.exit(1)
        
    if not Path(args.wave_file).exists():
        print(f"❌ Error: El archivo de onda no existe: {args.wave_file}")
        sys.exit(1)
    
    # Ejecutar la comparación
    try:
        compare_spectra(args.spectrum_file, args.wave_file, args.output)
    except KeyboardInterrupt:
        print("\n⚠️ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()