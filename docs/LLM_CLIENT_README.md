# Cliente LLM para Análisis de Configuraciones TWave T8

Este módulo proporciona una interfaz para usar modelos LLM de Groq para analizar configuraciones del sistema TWave T8.

## 🚀 Instalación

1. **Instalar dependencias**:

```bash
uv pip install groq
# o sincronizar todas las dependencias del proyecto
uv sync
```

2. **Configurar la API Key de Groq**:

Edita el archivo `.env` en la raíz del proyecto y añade tu API key:

```bash
# .env
GROQ_API_KEY=tu_api_key_de_groq_aqui
```

Para obtener tu API key:

1. Ve a https://console.groq.com/
2. Crea una cuenta o inicia sesión
3. Ve a la sección "API Keys"
4. Crea una nueva API key y cópiala

## 📖 Uso Básico

### Análisis de Configuración T8

```python
from llm_client import GroqLLMClient
import json

# Inicializar el cliente (carga automáticamente desde .env)
client = GroqLLMClient()

# Cargar configuración
with open("llm/config.json") as f:
    config_data = json.load(f)

# Analizar configuración
resultado = client.analyze_t8_configuration(
    config_data=config_data,
    temperature=0.6,
    max_tokens=4096
)

print(resultado)
```

### Modo Streaming

Para respuestas largas, usa el modo streaming:

```python
# Análisis con streaming
for chunk in client.analyze_t8_configuration(
    config_data=config_data,
    stream=True
):
    print(chunk, end="", flush=True)
```

### Preguntas Personalizadas

```python
# Hacer una pregunta específica sobre la configuración
respuesta = client.ask_custom_question(
    question="¿Cuáles son los puntos de medición más críticos?",
    context=json.dumps(config_data, indent=2),
    temperature=0.7
)

print(respuesta)
```

### Cambiar de Modelo

```python
# Ver modelos disponibles
print(client.get_available_models())

# Cambiar a otro modelo
client.change_model("llama3-8b-8192")

# Usar el nuevo modelo
respuesta = client.ask_custom_question(
    "Explica qué es TWave T8",
    temperature=0.5
)
```

## 🎯 Modelos Disponibles

- `moonshotai/kimi-k2-instruct` (predeterminado) - Recomendado para análisis técnicos
- `llama3-8b-8192` - Rápido y eficiente
- `llama3-70b-8192` - Más capacidad de razonamiento
- `mixtral-8x7b-32768` - Buen balance entre velocidad y calidad
- `gemma-7b-it` - Alternativa ligera

## ⚙️ Parámetros de Configuración

### `analyze_t8_configuration()`

- **config_data**: Datos de configuración (str o dict)
- **api_definitions**: Definiciones de la API (opcional)
- **temperature**: 0.0-1.0, controla la creatividad (default: 0.6)
  - 0.0-0.3: Respuestas más determinísticas
  - 0.4-0.7: Balance entre creatividad y precisión
  - 0.8-1.0: Respuestas más creativas
- **max_tokens**: Número máximo de tokens en la respuesta (default: 4096)
- **stream**: True para streaming, False para respuesta completa (default: False)

### `ask_custom_question()`

- **question**: Pregunta a realizar
- **context**: Contexto adicional (opcional)
- **temperature**: Mismos valores que arriba
- **max_tokens**: Mismos valores que arriba
- **stream**: Mismos valores que arriba

## 📝 Ejemplos Completos

Ejecuta el script de ejemplos:

```bash
python examples/llm_groq_example.py
```

Este script incluye:

- ✅ Análisis completo de configuración T8
- ✅ Ejemplo de streaming
- ✅ Preguntas personalizadas
- ✅ Cambio de modelos

## 🔧 Solución de Problemas

### Error: "No se encontró la API key de Groq"

**Solución**: Verifica que el archivo `.env` existe y contiene:

```bash
GROQ_API_KEY=tu_api_key_aqui
```

### Error: "Import 'groq' could not be resolved"

**Solución**: Instala la librería de Groq:

```bash
uv pip install groq
```

### Error de conexión

**Solución**:

1. Verifica tu conexión a internet
2. Verifica que tu API key es válida
3. Revisa los límites de uso en https://console.groq.com/

## 💡 Mejores Prácticas

1. **Para análisis técnicos**: Usa `temperature=0.6`
2. **Para respuestas creativas**: Usa `temperature=0.8`
3. **Para respuestas largas**: Usa `stream=True`
4. **Para velocidad**: Usa `llama3-8b-8192`
5. **Para calidad**: Usa `mixtral-8x7b-32768` o el modelo predeterminado

## 🔐 Seguridad

- **NUNCA** compartas tu API key
- **NUNCA** subas el archivo `.env` al repositorio (ya está en `.gitignore`)
- Rota tu API key regularmente
- Usa variables de entorno en producción

## 📚 Estructura del Código

```
src/llm_client/
├── __init__.py          # Exporta GroqLLMClient
└── groq_client.py       # Implementación principal

examples/
└── llm_groq_example.py  # Ejemplos de uso

.env                      # Configuración (API keys)
```

## 🤝 Contribuir

Si encuentras bugs o tienes sugerencias, abre un issue en el repositorio.

## 📄 Licencia

Este código es parte del proyecto paquete-python.
