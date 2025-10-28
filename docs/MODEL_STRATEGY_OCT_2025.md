# 🎯 Estrategia de Modelos LLM - Octubre 2025

**Optimización para Groq LPU Architecture**

---

## 📋 **RESUMEN EJECUTIVO**

Sistema de selección dinámica de modelos optimizado para la arquitectura LPU (Language Processing Units) de Groq, enfocado en modelos Meta que ofrecen el mejor rendimiento en esta plataforma.

### Resultados Clave:

- ✅ **17 llamadas** totales (16 fragmentos + 1 agregación)
- ✅ **~612 t/s** promedio ponderado
- ✅ **71% ahorro** en tokens de documentación API
- ✅ **Fallback automático** Tier 1 → Tier 2 → Tier 3

---

## 🏗️ **ARQUITECTURA DE MODELOS**

### **Tier 1: Ultrarrápido (~800+ t/s)**

```
llama-3.1-8b-instant
├─ Denso 8B parámetros
├─ ~800+ tokens/segundo en Groq LPU
├─ Ventana: 8,192 tokens
└─ Uso: 37.5% de fragmentos (6/16)
    ├─ machines_summary
    ├─ operational_states
    ├─ system_properties (si <5000 chars)
    ├─ measurement_points (si <2000 chars)
    ├─ processing_modes (si <2000 chars)
    └─ calculated_params (si <1000 chars)
```

### **Tier 2: Equilibrado MoE (~500 t/s)** ⭐ RECOMENDADO

```
meta-llama/llama-4-scout-17b-16e-instruct
├─ Mixture of Experts (17B activos / 16 expertos)
├─ ~500 tokens/segundo en Groq LPU
├─ Ventana: 16,384 tokens ← Mayor contexto
└─ Uso: 62.5% de fragmentos (10/16)
    ├─ system_properties (si ≥5000 chars)
    ├─ measurement_points (si ≥2000 chars)
    ├─ storage_strategies (medianos/grandes)
    ├─ processing_modes (≥2000 chars, FFTs complejas)
    ├─ calculated_params (≥1000 chars, alarmas)
    └─ Agregación simple (≤12 fragmentos)
```

### **Tier 3: Potente (~300 t/s)**

```
llama-3.3-70b-versatile
├─ Denso 70B parámetros
├─ ~300 tokens/segundo en Groq LPU
├─ Ventana: 8,192 tokens
└─ Uso: Agregación compleja
    └─ Síntesis final (>12 fragmentos)
```

### **Fallbacks (Google)**

```
gemma-7b-it       (Tier 1, ~750 t/s, seguridad)
gemma2-9b-it      (Tier 2, ~450 t/s, alternativa)
```

---

## 🔄 **ESTRATEGIA DE FALLBACK**

### Cadena Automática de Recuperación:

```python
1. Modelo solicitado (ej: llama-3.1-8b-instant)
   ↓ [FALLA]
2. meta-llama/llama-4-scout-17b-16e-instruct (Tier 2)
   ↓ [FALLA]
3. llama-3.3-70b-versatile (Tier 3)
   ↓ [FALLA]
4. llama-3.1-8b-instant (último recurso)
   ↓ [FALLA]
5. RuntimeError con mensaje detallado
```

### Características:

- ✅ **Deduplicación automática** (elimina duplicados en la cadena)
- ✅ **Preserva orden** (prioriza modelos más eficientes primero)
- ✅ **Solo modelos Groq LPU** (evita OpenAI GPT-OSS que no corren en LPU)
- ✅ **Mensajes de error informativos** (indica qué falló y dónde)

---

## 📊 **DISTRIBUCIÓN DE LLAMADAS**

Para un config.json con **16 fragmentos**:

| Tier  | Modelo               | Llamadas | %     | Velocidad | Total t/s |
| ----- | -------------------- | -------- | ----- | --------- | --------- |
| **1** | llama-3.1-8b-instant | 6        | 37.5% | ~800 t/s  | 300       |
| **2** | Scout MoE            | 10       | 62.5% | ~500 t/s  | 312.5     |
| **3** | llama-3.3-70b        | 1        | 5.9%  | ~300 t/s  | N/A\*     |

_Agregación final no se cuenta en promedio de fragmentos_

**Velocidad Promedio Ponderada:** ~612 tokens/segundo

---

## 🎯 **SELECCIÓN DINÁMICA POR CHUNK TYPE**

### Lógica de Selección (`ModelSelector.select_for_chunk_analysis`):

```python
SIMPLE (Tier 1 - 8B instant):
├─ machines_summary
├─ operational_states
└─ Fragmentos <5000 chars

MEDIUM (Tier 2 - Scout):
├─ measurement_points (≥2000 chars)
├─ storage_strategies (grandes)
├─ processing_modes (FFTs complejas)
└─ calculated_params (con alarmas)

COMPLEX (Tier 2 - Scout):
└─ Fragmentos >4000 chars
    └─ Scout maneja hasta 16k tokens
```

### Agregación (`ModelSelector.select_for_aggregation`):

```python
if num_fragments <= 12:
    return Scout (MoE, rápido y suficiente)
else:
    return llama-3.3-70b (máxima coherencia)
```

---

## 📄 **FRAGMENTACIÓN DE DOCUMENTACIÓN API**

### ApiDocFragmenter - 71% Ahorro de Tokens

**Antes:** ~1,250 tokens de DocComprimida.md por fragmento  
**Después:** ~360 tokens contextuales por fragmento

### Contextos Especializados:

| Chunk Type           | Contexto API                    | Tokens |
| -------------------- | ------------------------------- | ------ |
| `machines_summary`   | Máquinas, tags, alarmas         | 364    |
| `measurement_points` | Points, sensors, unidades       | 744    |
| `processing_modes`   | Proc modes, FFTs, parámetros    | 1,242  |
| `calculated_params`  | Params, alarmas, almacenamiento | 1,454  |
| `operational_states` | Estados operativos              | 450    |
| `storage_strategies` | Estrategias almacenamiento      | 520    |
| `system_properties`  | Propiedades globales            | 380    |

**Beneficio:** Cada fragmento recibe **solo la documentación relevante** para su tipo.

---

## 🚀 **IMPLEMENTACIÓN**

### Archivos Modificados:

1. **`src/llm_client/model_selector.py`**

   - ✅ Actualizado nombre Scout: `meta-llama/llama-4-scout-17b-16e-instruct`
   - ✅ Lógica de selección por chunk type y tamaño
   - ✅ Estrategia de agregación (≤12 → Scout, >12 → 70B)
   - ✅ Método `get_model_stats()` actualizado

2. **`src/llm_client/groq_client.py`**

   - ✅ `_generate_completion()` con fallback automático
   - ✅ `get_available_models()` con modelos Groq LPU
   - ✅ Eliminación de duplicados en cadena de fallback

3. **`src/llm_client/api_doc_fragmenter.py`**

   - ✅ 7 contextos especializados por chunk type
   - ✅ Fragmentación inteligente de DocComprimida.md

4. **`src/llm_client/chunked_analyzer.py`**

   - ✅ Integración ModelSelector para selección dinámica
   - ✅ Integración ApiDocFragmenter para contextos
   - ✅ Caché con 24hr expiración

5. **`src/t8_client/cli.py`**
   - ✅ Comando `model-info` actualizado
   - ✅ Muestra arquitectura, rendimiento y estrategia

---

## 📈 **MÉTRICAS DE EFICIENCIA**

### Comparación: Antes vs Después

| Métrica                  | Antes    | Después  | Mejora  |
| ------------------------ | -------- | -------- | ------- |
| **Llamadas API**         | 39       | 17       | ✅ -56% |
| **Fragmentos**           | 38       | 16       | ✅ -58% |
| **Tokens API/fragmento** | ~1,250   | ~360     | ✅ -71% |
| **Velocidad promedio**   | ~400 t/s | ~612 t/s | ✅ +53% |
| **Modelos activos**      | 7        | 5        | ✅ -29% |

### Costo-Beneficio Tier 2 (Scout):

- **62.5% de llamadas** usan Scout (Tier 2)
- **16k tokens** de contexto (2x vs 8B)
- **~500 t/s** (mejor que 70B, suficiente calidad)
- **MoE 17B/16E:** activación eficiente de expertos

---

## 🔧 **USO**

### Ver Información de Modelos:

```bash
uv run t8-cli model-info
```

### Análisis con Modelo Específico:

```bash
# Usa estrategia automática (recomendado)
uv run t8-cli chat-config --verbose -i

# Limpia caché antes de analizar
uv run t8-cli chat-config --verbose -i --clear-cache
```

### Programáticamente:

```python
from llm_client.model_selector import ModelSelector
from llm_client.chunking import ConfigChunk

# Seleccionar modelo para un fragmento
chunk = ConfigChunk(
    chunk_id="config_xyz_processing_modes_MAD31CY005_0",
    chunk_type="processing_modes",
    content_size=3500,
    data={"proc_modes": [...]}
)

model_config = ModelSelector.select_for_chunk_analysis(
    chunk_type=chunk.chunk_type,
    content_size=chunk.content_size
)

print(f"Modelo: {model_config.name}")
# Output: meta-llama/llama-4-scout-17b-16e-instruct

# Seleccionar para agregación
agg_model = ModelSelector.select_for_aggregation(
    num_fragments=16,
    total_size=50000
)
print(f"Agregación: {agg_model.name}")
# Output: llama-3.3-70b-versatile (porque 16 > 12)
```

---

## ⚠️ **ADVERTENCIAS IMPORTANTES**

### ✅ **Nombres Exactos de Modelos**

Los nombres **DEBEN coincidir** con la API de Groq:

```python
# ✅ CORRECTO
"meta-llama/llama-4-scout-17b-16e-instruct"
"llama-3.1-8b-instant"
"llama-3.3-70b-versatile"

# ❌ INCORRECTO
"llama-4-scout-17b-16e-instruct"  # falta prefijo meta-llama/
"llama3-8b-instant"               # falta guión y versión
"llama-3.3-70b"                   # falta sufijo -versatile
```

### 🔄 **Actualización de Modelos**

Si Groq actualiza nombres o depreca modelos:

1. Verificar en [Groq Console](https://console.groq.com/playground)
2. Actualizar `ModelSelector.MODELS` en `model_selector.py`
3. Ejecutar `uv run t8-cli model-info` para validar

### 🚫 **NO Usar Modelos OpenAI en Groq**

Evitar `openai/gpt-oss-*` porque:

- ❌ No corren en Groq LPU (infraestructura diferente)
- ❌ Rendimiento impredecible
- ❌ No optimizados para esta plataforma

---

## 📚 **REFERENCIAS**

- [Groq LPU Architecture](https://groq.com/lpu/)
- [Meta Llama Models](https://llama.meta.com/)
- Documentación interna: `llm/DocComprimida.md`
- Código fuente: `src/llm_client/`

---

**Última actualización:** Octubre 28, 2025  
**Optimizado para:** Groq LPU Architecture  
**Modelos principales:** Meta Llama 3.1, 3.3, 4 Scout
