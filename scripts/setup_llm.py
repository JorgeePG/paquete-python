#!/usr/bin/env python3
"""
Script de configuración para el cliente LLM de Groq.
"""

import os
from pathlib import Path


def setup_groq_api_key() -> None:
    """Configura la API key de Groq."""
    print("🔧 Configuración del Cliente LLM Groq")
    print("=" * 40)

    current_key = os.getenv("GROQ_API_KEY")

    if current_key:
        print(f"✅ API Key actual encontrada: {current_key[:10]}...")
        update = input("¿Quieres actualizarla? (y/N): ").lower()
        if update != "y":
            print("Manteniendo la API key actual.")
            return

    print("\n📝 Para obtener tu API key de Groq:")
    print("1. Ve a https://console.groq.com/")
    print("2. Crea una cuenta o inicia sesión")
    print("3. Ve a la sección 'API Keys'")
    print("4. Crea una nueva API key")

    api_key = input("\n🔑 Ingresa tu API key de Groq: ").strip()

    if not api_key:
        print("❌ No se ingresó ninguna API key.")
        return

    # Intentar crear archivo .env en el directorio del proyecto
    env_file = Path(".env")

    try:
        # Leer contenido existente si existe
        existing_content = ""
        if env_file.exists():
            with open(env_file, encoding="utf-8") as f:
                lines = f.readlines()

            # Filtrar líneas que no sean GROQ_API_KEY
            existing_content = "".join(
                line for line in lines if not line.startswith("GROQ_API_KEY")
            )

        # Escribir el archivo con la nueva API key
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(existing_content)
            if existing_content and not existing_content.endswith("\n"):
                f.write("\n")
            f.write(f"GROQ_API_KEY={api_key}\n")

        print(f"✅ API key guardada en {env_file.absolute()}")
        print("\n💡 Para usar la API key, ejecuta:")
        print("   source .env")
        print("   # o")
        print(f"   export GROQ_API_KEY={api_key}")

    except Exception as e:
        print(f"❌ Error al guardar el archivo .env: {e}")
        print("\n💡 Puedes establecer manualmente la variable de entorno:")
        print(f"   export GROQ_API_KEY={api_key}")


def test_connection() -> None:
    """Prueba la conexión con Groq."""
    print("\n🔬 Probando conexión con Groq...")

    try:
        from llm_client import GroqLLMClient

        client = GroqLLMClient()

        # Hacer una pregunta simple de prueba
        respuesta = client.ask_custom_question(
            "Di 'Hola' si puedes comunicarte conmigo.", temperature=0.1, max_tokens=50
        )

        print("✅ Conexión exitosa!")
        print(f"📝 Respuesta del modelo: {respuesta}")

    except Exception as e:
        print(f"❌ Error en la conexión: {e}")
        print("\n💡 Verifica:")
        print("  1. Tu API key es correcta")
        print("  2. Tienes conexión a internet")
        print("  3. La variable GROQ_API_KEY está establecida")


def main() -> None:
    """Función principal."""
    setup_groq_api_key()

    # Preguntar si quiere probar la conexión
    if os.getenv("GROQ_API_KEY"):
        test_now = input("\n🧪 ¿Quieres probar la conexión ahora? (Y/n): ").lower()
        if test_now != "n":
            test_connection()

    print("\n🎉 ¡Configuración completada!")
    print("\n📚 Próximos pasos:")
    print("  1. Ejecuta: python examples/llm_groq_example.py")
    print("  2. Lee la documentación en src/llm_client/groq_client.py")


if __name__ == "__main__":
    main()
