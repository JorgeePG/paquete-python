#!/usr/bin/env python3
"""
Ejemplo de uso del cliente LLM de Groq para análisis de configuraciones T8.
"""

import json
import os
from pathlib import Path

from llm_client import GroqLLMClient


def load_config_data(config_path: str = "llm/config.json") -> dict:
    """Carga los datos de configuración desde un archivo JSON."""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {config_path}")

    with open(config_file, encoding="utf-8") as f:
        return json.load(f)


def analyze_t8_configuration_example() -> None:
    """Ejemplo de análisis de configuración T8."""
    print("🔍 Ejemplo: Análisis de configuración TWave T8")
    print("=" * 50)

    try:
        # Inicializar el cliente (necesitas establecer GROQ_API_KEY)
        client = GroqLLMClient()

        # Cargar datos de configuración
        config_data = load_config_data()

        print("📋 Analizando configuración...")

        # Realizar análisis
        resultado = client.analyze_t8_configuration(
            config_data=config_data, temperature=0.6, max_tokens=4096
        )

        print("\n📊 RESULTADO DEL ANÁLISIS:")
        print("-" * 30)
        print(resultado)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Asegúrate de:")
        print("  1. Establecer la variable GROQ_API_KEY")
        print("  2. Tener el archivo de configuración en llm/config.json")


def streaming_example() -> None:
    """Ejemplo de uso en modo streaming."""
    print("\n🔄 Ejemplo: Análisis en modo streaming")
    print("=" * 50)

    try:
        client = GroqLLMClient()
        config_data = load_config_data()

        print("📋 Analizando configuración (streaming)...")
        print("\n📊 RESULTADO (streaming):")
        print("-" * 30)

        # Usar streaming para ver la respuesta en tiempo real
        for chunk in client.analyze_t8_configuration(
            config_data=config_data, stream=True, temperature=0.6
        ):
            print(chunk, end="", flush=True)

        print("\n" + "=" * 50)

    except Exception as e:
        print(f"❌ Error: {e}")


def custom_question_example() -> None:
    """Ejemplo de pregunta personalizada."""
    print("\n❓ Ejemplo: Pregunta personalizada")
    print("=" * 50)

    try:
        client = GroqLLMClient()
        config_data = load_config_data()

        # Convertir config a string para usar como contexto
        context = json.dumps(config_data, indent=2)

        pregunta = (
            "¿Cuáles son los puntos de medición más críticos en esta "
            "configuración y qué parámetros monitorizan?"
        )

        print(f"🤔 Pregunta: {pregunta}")
        print("\n📝 Respuesta:")
        print("-" * 30)

        respuesta = client.ask_custom_question(
            question=pregunta, context=f"Configuración T8:\n{context}", temperature=0.7
        )

        print(respuesta)

    except Exception as e:
        print(f"❌ Error: {e}")


def model_switching_example() -> None:
    """Ejemplo de cambio de modelo."""
    print("\n🔄 Ejemplo: Cambio de modelo")
    print("=" * 50)

    try:
        client = GroqLLMClient()

        print(f"📦 Modelo actual: {client.model}")
        print(f"📋 Modelos disponibles: {client.get_available_models()}")

        # Cambiar a un modelo diferente
        client.change_model("llama3-8b-8192")
        print(f"✅ Modelo cambiado a: {client.model}")

        # Hacer una pregunta simple con el nuevo modelo
        respuesta = client.ask_custom_question(
            "Explica brevemente qué es el sistema TWave T8.",
            temperature=0.5,
            max_tokens=500,
        )

        print("\n📝 Respuesta con nuevo modelo:")
        print("-" * 30)
        print(respuesta)

    except Exception as e:
        print(f"❌ Error: {e}")


def main() -> None:
    """Función principal que ejecuta todos los ejemplos."""
    print("🚀 Ejemplos de uso del Cliente LLM Groq para TWave T8")
    print("=" * 60)

    # Verificar API key
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  ADVERTENCIA: No se encontró GROQ_API_KEY")
        print("   Establece la variable de entorno antes de ejecutar:")
        print("   export GROQ_API_KEY='tu_api_key_aqui'")
        print()

    # Ejecutar ejemplos
    analyze_t8_configuration_example()
    streaming_example()
    custom_question_example()
    model_switching_example()

    print("\n✅ ¡Ejemplos completados!")
    print("\n💡 Consejos:")
    print("  - Usa temperature=0.6 para análisis técnicos")
    print("  - Usa streaming=True para respuestas largas")
    print("  - Prueba diferentes modelos según tus necesidades")


if __name__ == "__main__":
    main()
