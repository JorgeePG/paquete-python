"""
Fragmentador de documentación API para análisis optimizado por tipo de chunk.
Solo pasa la documentación relevante a cada análisis de fragmento.
"""


class ApiDocFragmenter:
    """Fragmenta la documentación de la API según el tipo de análisis."""

    # Definiciones relevantes para cada tipo de fragmento
    RELEVANT_SECTIONS = {
        "machines_summary": """
**CONTEXTO API - Estructura de Máquinas:**

machines (array): Lista de máquinas configuradas.
  - id (integer): ID único de la máquina
  - tag (string): Identificador corto (ej: "LP_Turbine")
  - name (string): Nombre descriptivo
  - speed (number): Velocidad nominal
  - load (number): Carga nominal
  - period (number): Intervalo entre adquisiciones (segundos)
""",
        "measurement_points": """
**CONTEXTO API - Puntos de Medición:**

points (array): Puntos de medición en la máquina.
  - id (integer): ID del punto
  - tag (string): Identificador único (ej: "MAD31CY005")
  - name (string): Nombre descriptivo
  - path (string): Ruta completa (ej: "LP_Turbine:MAD31CY005")
  - type (integer): Origen del dato
    * 0: Entrada física (sensor conectado)
    * 1: Modbus (valor remoto)
    * 3: Fórmula calculada
  - mode (integer): Modo de medición
    * 0: Dinámico/Vibración
    * 1: Estático/Proceso
    * 2: Tacómetro
  - component_id (integer): ID del componente asociado
  - input (object): Configuración del sensor físico
    * number (integer): Canal físico
    * sensor (object): Detalles del sensor (ganancia, unidades, límites)
""",
        "processing_modes": """
**CONTEXTO API - Modos de Procesamiento (proc_modes):**

proc_modes (array): Configuración de procesamiento de señales.
  - id (integer): ID del modo
  - tag (string): Identificador (ej: "AM1", "AM2")
  - name (string): Nombre descriptivo
  - type (integer): Tipo de procesamiento
    * 0: Solo Forma de Onda
    * 1: Forma de Onda + Espectro FFT
    * 2: Demodulación de envolvente
    * 5: Tacómetro
    * 6: Forma de Onda Larga
    * 9: Espectro Completo
  - sample_rate (integer): Frecuencia de muestreo en Hz
  - samples (integer): Número de muestras de la forma de onda
  - max_freq (number): Frecuencia máxima del espectro (Hz u Órdenes)
  - min_freq (number): Frecuencia mínima del espectro
  - bins (integer): Líneas de resolución del espectro
  - averages (integer): Número de promedios para reducir ruido
  - overlap (number): Solapamiento entre promedios (0 a 1)
  - window (integer): Tipo de ventana
    * 0: Rectangular
    * 1: Hann
    * 2: Hamming
    * 3: Blackman
  - integrate_sp (integer): Integración del espectro
    * 0: Ninguno (Aceleración)
    * 1: Una vez (Velocidad)
    * 2: Dos veces (Desplazamiento)
  - save_sp (boolean): Guardar espectro por defecto
  - save_wf (boolean): Guardar forma de onda por defecto
""",
        "calculated_params": """
**CONTEXTO API - Parámetros Calculados (params):**

params (array): Valores numéricos calculados desde las señales.
  - id (integer): ID del parámetro
  - tag (string): Identificador (ej: "Overall", "1x", "DC_Gap")
  - name (string): Nombre descriptivo
  - path (string): Ruta completa (ej: "LP_Turbine:MAD31CY005:Overall")
  - type (integer): Tipo de cálculo
    * 0: Media (promedio aritmético)
    * 1: RMS (valor eficaz)
    * 2: Pico Real (máximo absoluto)
    * 3: Pico-Pico (rango total)
    * 4: Factor de Cresta (Pico/RMS)
    * 6: RMS Espectral (energía en banda)
    * 9: Pico-Pico de bandas espectrales
    * 10: Frecuencia dominante
    * 12: Amplitud de componente armónico
    * 13: Fase de componente armónico
  - integrate (integer): Integración antes del cálculo
    * 0: Ninguno
    * 1: Una vez
    * 2: Dos veces
  - detector (integer): Detector de amplitud (para bandas)
    * 0: Ninguno
    * 1: RMS
    * 2: Pico
    * 3: Pico-Pico
  - spectral_bands (array): Bandas de frecuencia si type es 6 o 9
    * freq1 (number/string): Frecuencia inferior (puede usar "speed")
    * freq2 (number/string): Frecuencia superior
  - alarms (array): Límites de alarma por estado
    * state_id (integer): Estado operativo asociado
    * warning1, warning2 (number): Límites de precaución
    * alert1, alert2 (number): Límites de alerta
    * danger1, danger2 (number): Límites de peligro
  - unit_id (integer): ID de la unidad del resultado
""",
        "operational_states": """
**CONTEXTO API - Estados Operativos (states):**

states (array): Estados operativos definidos para la máquina.
  - id (integer): ID del estado
  - name (string): Nombre (ej: "Stopped", "Full_Speed", "Starting")
  - condition (string): Expresión lógica que determina si el estado está activo
    * Basada en velocidad, parámetros calculados, entradas digitales
    * Ejemplos: "speed > 2900", "DC_Gap < 500"
    
**Nota:** Los estados se usan para:
1. Aplicar diferentes límites de alarma según el estado operativo
2. Activar estrategias de almacenamiento en transiciones
3. Filtrar análisis de tendencias por estado
""",
        "storage_strategies": """
**CONTEXTO API - Estrategias de Almacenamiento (strategies):**

strategies (array): Reglas para decidir cuándo almacenar datos.
  - id (integer): ID de la estrategia
  - name (string): Nombre descriptivo
  - type (integer): Tipo de disparador
    * 0: Tiempo/Cron (almacenar periódicamente)
    * 1: Ciclos de monitorización (cada N ciclos)
    * 2: Cambio de estado operativo
    * 3: Nivel de alarma alcanzado
    * 5: Manual/Usuario
  - condition (string): Condición adicional para activar
  - cron_line (string): Expresión Cron para type=0 (ej: "0 */6 * * *")
  - mon_period (integer): Período para type=1 (número de ciclos)
  - state1_id, state2_id (integer): Estados para type=2 (transición)
  - alarm (integer): Nivel de alarma para type=3
    * 0: Normal
    * 1: Warning
    * 2: Alert
    * 3: Danger

**Interacción con proc_modes:**
Los proc_modes pueden tener "selectors" que sobrescriben save_sp/save_wf
para una strategy_id específica.
""",
        "system_properties": """
**CONTEXTO API - Propiedades y Unidades del Sistema:**

properties (array): Magnitudes físicas medibles.
  - id (integer): ID de la propiedad
  - name (string): Nombre de la magnitud física
  
Ejemplos comunes:
  - ID 4: Displacement (Desplazamiento)
  - ID 5: Velocity (Velocidad)
  - ID 6: Acceleration (Aceleración)
  - ID 17: Speed (Velocidad de rotación)

units (array): Unidades de medida concretas.
  - id (integer): ID de la unidad
  - label (string): Etiqueta (ej: "µm", "mm/s", "RPM")
  - property_id (integer): Propiedad asociada
  - factor (number): Factor de conversión a unidad base
  - offset (number): Offset de conversión
  - decibel (boolean): Si es una escala logarítmica
  
Ejemplos comunes:
  - ID 14: µm (Displacement)
  - ID 17: mm/s (Velocity)
  - ID 20: g (Acceleration)
  - ID 48: RPM (Speed)

**Conversiones:**
valor_base = (valor_medido * factor) + offset
Para dB: valor_dB = 20 * log10(valor / referencia)
""",
    }

    @classmethod
    def get_relevant_context(cls, chunk_type: str) -> str:
        """
        Obtiene el contexto API relevante para un tipo de fragmento.

        Args:
            chunk_type: Tipo de fragmento (machines_summary, calculated_params, etc.)

        Returns:
            Documentación API relevante para ese tipo de fragmento
        """
        return cls.RELEVANT_SECTIONS.get(
            chunk_type,
            """
**CONTEXTO API - Sistema TWave T8:**

Sistema de monitoreo de vibración y condición de maquinaria rotativa.
El archivo de configuración (config.json) define máquinas, puntos de medición,
modos de procesamiento de señales, y parámetros calculados para análisis.
""",
        )

    @classmethod
    def should_include_api_context(cls, chunk_type: str) -> bool:
        """
        Determina si se debe incluir contexto API para un tipo de fragmento.

        Args:
            chunk_type: Tipo de fragmento

        Returns:
            True si se debe incluir contexto API
        """
        # Siempre incluir contexto excepto para el resumen general
        return chunk_type != "machines_summary"
