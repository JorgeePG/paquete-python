# Guía de Uso: Comando `chat-config`

El comando `chat-config` te permite conversar con un LLM sobre las configuraciones del sistema TWave T8.

## 🚀 Requisitos Previos

1. **Configurar API Key de Groq** en `.env`:

```bash
GROQ_API_KEY=tu_api_key_aqui
```

2. **Credenciales de T8** (ya configuradas):

```bash
T8_USER=practicas
T8_PASSWORD=Practicas2025
```

3. **Instalar dependencia**:

```bash
uv pip install groq
# o sincronizar todas las dependencias
uv sync
```

## 📖 Modos de Uso

### 1. Pregunta Simple

Haz una pregunta específica sobre la configuración:

```bash
# Pregunta sobre la configuración de la API
t8-cli chat-config -q "¿Cuáles son los principales puntos de medición?"

# Pregunta sobre un archivo local
t8-cli chat-config -c llm/config.json -q "¿Qué tasas de muestreo se usan?"
```

### 2. Modo Interactivo

Inicia una conversación continua:

```bash
# Modo interactivo con configuración de la API
t8-cli chat-config -i

# Modo interactivo con archivo local
t8-cli chat-config -c llm/config.json -i

# Modo interactivo con streaming
t8-cli chat-config -i -s
```

En modo interactivo puedes:

- Escribir preguntas libremente
- Escribir `analyze` para análisis completo
- Escribir `help` para sugerencias
- Escribir `exit` o `quit` para salir

### 3. Análisis Completo

Sin especificar pregunta, realiza un análisis completo:

```bash
# Análisis de la configuración de la API
t8-cli chat-config

# Análisis de archivo local
t8-cli chat-config -c llm/config.json

# Análisis con streaming
t8-cli chat-config -s
```

## ⚙️ Opciones Disponibles

| Opción              | Descripción                      | Valor por Defecto |
| ------------------- | -------------------------------- | ----------------- |
| `-c, --config-file` | Ruta al archivo de configuración | Usa config de API |
| `-q, --question`    | Pregunta específica              | -                 |
| `-i, --interactive` | Modo interactivo                 | False             |
| `-s, --stream`      | Streaming en tiempo real         | False             |
| `-t, --temperature` | Temperatura del modelo (0.0-1.0) | 0.6               |

## 📝 Ejemplos Prácticos

### Ejemplo 1: Preguntas Técnicas

```bash
# Información sobre sensores
t8-cli chat-config -q "¿Qué tipos de sensores están configurados?"

# Información sobre alarmas
t8-cli chat-config -q "¿Cuáles son los umbrales de alarma para MAD31CY005?"

# Información sobre modos de procesamiento
t8-cli chat-config -q "Explica los diferentes modos de procesamiento (AM1, AM2, AM3)"
```

### Ejemplo 2: Sesión Interactiva

```bash
$ t8-cli chat-config -i -s

============================================================
🤖 T8 Configuration Chat (Interactive Mode)
============================================================
📋 Configuration source: API configuration
🌡️  Temperature: 0.6
📡 Streaming: Enabled

Commands:
  - Type your question and press Enter
  - Type 'analyze' for full configuration analysis
  - Type 'help' for suggestions
  - Type 'exit' or 'quit' to exit
============================================================

You> What machines are configured?

LLM> Based on the configuration, there is one machine configured:
**LP_Turbine** (Low Pressure Turbine)

This machine has:
- 8 measurement points distributed across two bearings
- Bearing Outlet End and Bearing Inlet End components
- Multiple vibration and casing sensors
...

You> Tell me about the sampling rates

LLM> The system uses different sampling rates depending on the
processing mode:
- **AM1 (High Frequency)**: 12,800 Hz sample rate...

You> exit

👋 Goodbye!
```

### Ejemplo 3: Análisis con Streaming

```bash
# Ver el análisis en tiempo real
t8-cli chat-config -c llm/config.json -s

✅ Loaded configuration from: llm/config.json

💭 Analyzing T8 configuration...

📝 Analysis:

## Máquina
The configuration contains one main machine: **LP_Turbine**
(Low Pressure Turbine). This machine...
[análisis continúa en tiempo real]
```

### Ejemplo 4: Ajustar Creatividad

```bash
# Respuesta más determinística (temperatura baja)
t8-cli chat-config -q "List the measurement points" -t 0.2

# Respuesta más creativa (temperatura alta)
t8-cli chat-config -q "Explain the monitoring strategy" -t 0.8
```

## 💡 Preguntas Sugeridas

Escribe `help` en modo interactivo, o prueba estas:

- "What machines are configured in this system?"
- "What are the main measurement points?"
- "What processing modes are available?"
- "What parameters are being monitored?"
- "What are the alarm thresholds for MAD31CY005?"
- "Explain the storage strategies"
- "What sampling rates are used?"
- "Describe the sensor configuration"
- "What are the operational states?"
- "How is vibration data processed?"

## 🔧 Solución de Problemas

### Error: "LLM client not available"

```bash
uv pip install groq
```

### Error: "No se encontró la API key de Groq"

Edita `.env` y añade:

```bash
GROQ_API_KEY=tu_api_key_aqui
```

### Error: "Could not authenticate with T8 API"

Verifica las credenciales en `.env`:

```bash
T8_USER=practicas
T8_PASSWORD=Practicas2025
T8_HOST=https://lzfs45.mirror.twave.io/lzfs45
```

## 🎯 Consejos de Uso

1. **Para análisis técnicos precisos**: usa `-t 0.3` a `-t 0.6`
2. **Para explicaciones detalladas**: usa `-t 0.6` a `-t 0.8`
3. **Para respuestas largas**: activa streaming con `-s`
4. **Para sesiones exploratorias**: usa modo interactivo `-i`
5. **Para análisis de archivos locales**: usa `-c ruta/archivo.json`

## 🔄 Flujo de Trabajo Recomendado

1. **Primera vez**: Análisis general

   ```bash
   t8-cli chat-config
   ```

2. **Exploración**: Modo interactivo

   ```bash
   t8-cli chat-config -i -s
   ```

3. **Preguntas específicas**: Consultas directas

   ```bash
   t8-cli chat-config -q "tu pregunta específica"
   ```

4. **Análisis de archivos guardados**: Usar archivos locales
   ```bash
   t8-cli chat-config -c data/config_backup.json -i
   ```
