Definiciones Clave API TWave T8 (Simplificado)
Endpoint Principal: GET /confs/:id
Descripción: Obtiene una configuración guardada específica por su ID. Soporta formato JSON (por defecto) y Protobuf.

Parámetro de Ruta:

id (string, requerido): Identificador de la configuración.

Parámetro de Query:

format (string, opcional): Formato de respuesta ('application/json' o 'application/x-protobuf'). Por defecto es JSON.

Estructura de la Respuesta JSON de Configuración
El objeto JSON principal contiene las siguientes claves:

_links:

home (uri): URL base de la API.

self (uri): URL del recurso de configuración actual.

t (number): Timestamp Unix de cuándo se guardó/generó la configuración.

uid (string): Identificador único de la configuración.

machines (array de objetos): Lista de máquinas configuradas en el sistema.

mb_servers (array de objetos): Definiciones de los servidores Modbus a los que el T8 puede conectarse.

mb_slave_regs (array de objetos): Mapeo de registros Modbus específicos a valores internos del T8.

properties (array de objetos): Definiciones de las propiedades físicas medibles (ej: Desplazamiento, Velocidad).

units (array de objetos): Definiciones de las unidades de medida (ej: µm, mm/s, Hz).

Detalles del Objeto machines
Cada objeto dentro del array machines representa una máquina y contiene:

id (integer): ID numérico único de la máquina.

tag (string): Identificador corto y único de la máquina (ej: "LP_Turbine").

name (string): Nombre descriptivo.

image (string): Nombre del archivo de imagen asociado.

speed (number): Velocidad nominal de la máquina.

load (number): Carga nominal de la máquina.

load_unit_id (integer): ID de la unidad para la carga.

period (number): Intervalo (en segundos) entre adquisiciones de datos/snapshots.

components (array de objetos): Partes físicas de la máquina (ej: rodamientos).

id (integer): ID del componente.

name (string): Nombre del componente.

desc (string): Descripción.

states (array de objetos): Estados operativos definidos.

id (integer): ID del estado.

name (string): Nombre del estado (ej: "Stopped", "Full_Speed").

condition (string): Expresión lógica que determina si el estado está activo (basada en velocidad, parámetros, etc.).

strategies (array de objetos): Reglas para decidir cuándo almacenar datos.

id (integer): ID de la estrategia.

name (string): Nombre de la estrategia.

type (integer): Tipo de disparador (0: Tiempo/Cron, 1: Ciclos de monitorización, 2: Cambio de estado, 3: Nivel de alarma, 5: Manual/Usuario).

condition (string): Condición adicional para activar la estrategia.

cron_line (string): Expresión Cron para estrategias tipo 0.

mon_period (integer): Período para estrategias tipo 1.

state1_id, state2_id (integer): IDs de estado inicial y final para estrategias tipo 2.

alarm (integer): Nivel de alarma para estrategias tipo 3.

points (array de objetos): Puntos de medición en la máquina.

Detalles del Objeto points
Cada objeto dentro del array points representa un punto de medición y contiene:

id (integer): ID del punto.

tag (string): Identificador corto y único del punto (ej: "MAD31CY005").

name (string): Nombre descriptivo.

desc (string): Descripción detallada.

path (string): Ruta completa del punto (ej: "LP_Turbine:MAD31CY005").

type (integer): Tipo de origen del dato (0: Entrada física, 1: Modbus, 3: Fórmula).

mode (integer): Modo de medición (0: Dinámico/Vibración, 1: Estático/Proceso, 2: Tacómetro).

component_id (integer): ID del componente asociado (si existe).

input (objeto): Configuración detallada si type es 0 (entrada física). Incluye:

number (integer): Número del canal físico.

sensor (objeto): Detalles del sensor conectado (ID, ganancia, unidades, límites DC, etc.).

exp (string): Expresión si type es 3 (fórmula).

mb_register (objeto): Configuración si type es 1 (Modbus).

proc_modes (array de objetos): Modos de procesamiento definidos para este punto.

Detalles del Objeto proc_modes
Cada objeto dentro del array proc_modes define cómo se procesa la señal de un punto:

id (integer): ID del modo de procesamiento.

tag (string): Identificador corto del modo (ej: "AM1").

name (string): Nombre descriptivo (ej: "AM1").

type (integer): Tipo de procesamiento (0: Solo Forma de Onda, 1: Forma de Onda + Espectro, 2: Demodulación, 5: Tacómetro, 6: Forma de Onda Larga, 9: Espectro Completo).

sample_rate (integer): Frecuencia de muestreo (Hz) usada para la forma de onda.

samples (integer): Número de muestras en la forma de onda.

max_freq (number): Frecuencia máxima (Hz u Órdenes) del espectro calculado.

min_freq (number): Frecuencia mínima (Hz u Órdenes) del espectro.

bins (integer): Número de líneas (resolución) del espectro.

averages (integer): Número de promedios para el espectro.

overlap (number): Porcentaje de solapamiento para los promedios (0 a 1).

window (integer): Tipo de ventana aplicada (0: Rectangular, 1: Hann, 2: Hamming, 3: Blackman).

integrate_sp (integer): Nivel de integración aplicado al espectro (0: Ninguno, 1: Una vez, 2: Dos veces).

save_sp (boolean): Indica si el espectro calculado se guarda por defecto.

save_wf (boolean): Indica si la forma de onda se guarda por defecto.

selectors (array de objetos): Definen si se guarda (save_sp, save_wf) para una strategy_id específica, sobreescribiendo los valores por defecto.

params (array de objetos): Parámetros calculados a partir de este modo de procesamiento.

Detalles del Objeto params
Cada objeto dentro del array params define un valor numérico calculado:

id (integer): ID del parámetro.

tag (string): Identificador corto (ej: "Overall", "1x", "DC_Gap").

name (string): Nombre descriptivo.

path (string): Ruta completa del parámetro (ej: "LP_Turbine:MAD31CY005:Overall").

type (integer): Tipo de cálculo (0: Media, 1: RMS, 2: Pico Real, 3: Pico-Pico, 4: Factor de Cresta, 6: RMS Espectral, 9: Pico-Pico calculado de bandas, 10: Frecuencia, 12: Amplitud de Pico/Fase, 13: Fase de Pico/Fase).

integrate (integer): Nivel de integración aplicado antes del cálculo (0: Ninguno, 1: Una vez, 2: Dos veces).

detector (integer): Detector de amplitud aplicado después del cálculo (0: Ninguno, 1: RMS, 2: Pico, 3: Pico-Pico). Usado principalmente en parámetros tipo 9 (bandas espectrales).

spectral_bands (array de objetos): Definición de bandas si el type es 6 o 9. Define freq1 y freq2 (frecuencias límite, pueden ser expresiones con "speed").

alarms (array de objetos): Límites de alarma (Warning1/2, Alert1/2, Danger1/2) asociados a diferentes state_id.

unit_id (integer): ID de la unidad del valor resultante (puede sobreescribirse con custom_unit_id).

Detalles de properties y units
properties: Lista de IDs y nombres para magnitudes físicas (ej: ID 4 = Displacement, ID 5 = Velocity, ID 17 = Speed).

units: Lista de IDs, etiquetas (label), property_id asociada, y factores/offsets de conversión. Define las unidades concretas (ej: ID 14 = µm (propiedad 4), ID 17 = mm/s (propiedad 5), ID 48 = RPM (propiedad 17)). Incluye definiciones para dB si decibel es true.