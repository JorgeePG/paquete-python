"""
Procesador de fragmentos con análisis LLM y agregación.
Implementa la estrategia "Divide y Vencerás" completa.
"""

from collections.abc import Generator
from typing import TYPE_CHECKING

from llm_client.api_doc_fragmenter import ApiDocFragmenter
from llm_client.cache import ChunkCache
from llm_client.chunking import ConfigChunk, ConfigChunker
from llm_client.model_selector import ModelSelector

if TYPE_CHECKING:
    from llm_client.groq_client import GroqLLMClient


class ChunkedAnalyzer:
    """Analiza configuraciones por fragmentos con caché y agregación."""

    def __init__(
        self, llm_client: "GroqLLMClient", api_definitions: str | None = None
    ) -> None:
        """
        Inicializa el analizador de fragmentos.

        Args:
            llm_client: Cliente LLM (GroqLLMClient)
            api_definitions: Definiciones de la API
        """
        self.llm_client = llm_client
        self.api_definitions = api_definitions
        self.cache = ChunkCache()
        self.chunker = ConfigChunker()
        self.verbose = False  # Por defecto no verboso

    def analyze_config_chunked(
        self,
        config_data: dict,
        temperature: float = 0.6,
        max_cache_age_hours: float = 24.0,
        stream: bool = False,
        verbose: bool = True,
    ) -> str | Generator[str]:
        """
        Analiza una configuración usando la estrategia de fragmentación.

        Proceso:
        1. Fragmenta el config.json en partes lógicas
        2. Analiza cada fragmento (usa caché si está disponible)
        3. Agrega todos los análisis parciales en uno final

        Args:
            config_data: Diccionario con la configuración
            temperature: Temperatura del modelo
            max_cache_age_hours: Edad máxima del caché en horas
            stream: Si True, retorna generador para streaming
            verbose: Si True, muestra progreso

        Returns:
            Análisis completo como string o generador
        """
        # Configurar verbosidad para este análisis
        self.verbose = verbose
        
        # 1. Fragmentar configuración
        if verbose:
            print("📦 Fragmentando configuración...")

        chunks = self.chunker.chunk_config(config_data)
        config_uid = self.chunker.get_config_uid(config_data)

        if verbose:
            print(f"   ✅ {len(chunks)} fragmentos creados")

        # 2. Analizar cada fragmento (con caché)
        partial_analyses = []
        cache_hits = 0
        cache_misses = 0

        for idx, chunk in enumerate(chunks, 1):
            if verbose:
                print(
                    f"\n🔍 Analizando fragmento {idx}/{len(chunks)}: {chunk.chunk_type}"
                )

            # Intentar obtener del caché
            cached = self.cache.get(chunk.chunk_id, max_age_hours=max_cache_age_hours)

            if cached:
                # Usar análisis cacheado
                if verbose:
                    print("   ⚡ Usando análisis cacheado")
                partial_analyses.append(
                    {
                        "chunk_type": chunk.chunk_type,
                        "description": chunk.description,
                        "analysis": cached.analysis,
                    }
                )
                cache_hits += 1
            else:
                # Generar nuevo análisis
                if verbose:
                    print("   🤖 Generando nuevo análisis...")

                analysis = self._analyze_chunk(chunk, temperature)

                # Guardar en caché
                self.cache.set(
                    chunk_id=chunk.chunk_id,
                    chunk_type=chunk.chunk_type,
                    analysis=analysis,
                    config_uid=config_uid,
                    model=self.llm_client.model,
                    temperature=temperature,
                )

                partial_analyses.append(
                    {
                        "chunk_type": chunk.chunk_type,
                        "description": chunk.description,
                        "analysis": analysis,
                    }
                )
                cache_misses += 1

        if verbose:
            print(f"\n📊 Caché: {cache_hits} hits, {cache_misses} misses")
            print(f"💾 Tamaño del caché: {self.cache.get_size_mb():.2f} MB")

        # 3. Agregar análisis parciales
        if verbose:
            print("\n🔄 Agregando análisis parciales...")

        final_analysis = self._aggregate_analyses(
            partial_analyses, config_data, temperature, stream
        )

        if verbose and not stream:
            print("   ✅ Análisis completo generado\n")

        return final_analysis

    def _analyze_chunk(self, chunk: ConfigChunk, temperature: float) -> str:
        """
        Analiza un fragmento específico usando el LLM.

        Args:
            chunk: Fragmento a analizar
            temperature: Temperatura del modelo

        Returns:
            Análisis del fragmento
        """

        # Seleccionar modelo óptimo para este fragmento
        content_size = len(str(chunk.content))
        model_config = ModelSelector.select_for_chunk_analysis(
            chunk.chunk_type, content_size
        )

        if self.verbose:
            print(
                f"  🤖 Modelo: {model_config.name} "
                f"(tier {model_config.cost_tier}, {content_size} chars)"
            )

        # Construir prompt específico para el fragmento
        prompt = self._build_chunk_prompt(chunk)

        # Generar análisis (sin streaming) usando el modelo seleccionado
        response = self.llm_client._generate_completion(
            prompt=prompt,
            temperature=temperature,
            max_tokens=min(1500, model_config.max_tokens),  # Reducido de 2048 a 1500
            stream=False,
            model=model_config.name,  # Modelo dinámico
        )

        return response

    def _build_chunk_prompt(self, chunk: ConfigChunk) -> str:
        """
        Construye un prompt específico para analizar un fragmento.
        Incluye solo la documentación API relevante para ese tipo de fragmento.

        Args:
            chunk: Fragmento a analizar

        Returns:
            Prompt formateado con contexto API optimizado
        """
        import json as json_module

        chunk_json = json_module.dumps(chunk.content, indent=2)

        # Obtener contexto API relevante para este tipo de fragmento
        api_context = ApiDocFragmenter.get_relevant_context(chunk.chunk_type)

        # Prompts base con contexto API específico
        prompts = {
            "machines_summary": f"""
Analiza este resumen de máquinas T8:

{api_context}

**DATOS:**
```json
{chunk_json}
```

Lista brevemente: máquinas, puntos por máquina, estados y estrategias.
Máximo 300 palabras.""",
            "measurement_points": f"""
Analiza puntos de medición T8:

{api_context}

**DATOS:**
```json
{chunk_json}
```

Resume: tipos de sensores (type/mode), ubicaciones (path), configuración física.
Formato tabla compacta. Máximo 400 palabras.""",
            "processing_modes": f"""
Analiza modos de procesamiento T8:

{api_context}

**DATOS:**
```json
{chunk_json}
```

Indica: FFT config (sample_rate, max_freq, bins), averages, overlap, window, 
integrate_sp (afecta unidades), save_sp/save_wf.
Formato tabla. Máximo 500 palabras.""",
            "calculated_params": f"""
Eres experto en TWave T8. Analiza estos parámetros calculados:

{api_context}

**DATOS:**
```json
{chunk_json}
```

Para cada punto, indica de forma COMPACTA:
- Parámetros principales (tag, type, integrate)
- Unidades resultantes (considerando sensor.unit_id e integrate)
- Bandas espectrales si aplica (type 6/9)
- Alarmas configuradas (solo si existen, indicar state_id y valores)

**REGLAS UNIDADES CRÍTICAS:**
- Si sensor.unit_id=14 (µm) y integrate=0 → resultado en µm
- Si sensor.unit_id=14 (µm) y integrate=1 → resultado en mm/s
- Si sensor.unit_id=14 (µm) y integrate=2 → resultado en g

Formato: Lista concisa, evita repetir estructura JSON. Máximo 500 palabras.""",
            "operational_states": f"""
Analiza estados operativos T8:

{api_context}

**DATOS:**
```json
{chunk_json}
```

Lista: nombres, condiciones (expresiones con speed/params), propósito.
Máximo 300 palabras.""",
            "storage_strategies": f"""
Analiza estrategias de almacenamiento T8:

{api_context}

**DATOS:**
```json
{chunk_json}
```

Por cada estrategia indica:
- Tipo (type) y qué lo dispara:
  * type 0: Tiempo/Cron (cron_line)
  * type 1: Ciclos de monitorización (mon_period)
  * type 2: Cambio de estado (de state1_id a state2_id)
  * type 3: Nivel de alarma de parámetros (alarm level)
  * type 5: Manual
- Condición adicional (condition) si existe
- **CRÍTICO:** Menciona qué estados o parámetros están involucrados

Formato tabla. Máximo 400 palabras.""",
            "system_properties": f"""
Analiza propiedades del sistema T8:

{api_context}

**DATOS:**
```json
{chunk_json}
```

Resume: propiedades físicas (properties), unidades (units) con factores de conversión,
relaciones property_id.
Formato tabla. Máximo 300 palabras.""",
        }

        # Fallback con contexto genérico
        return prompts.get(
            chunk.chunk_type,
            f"""
Analiza este fragmento de configuración T8:

{api_context}

**Fragmento:** {chunk.chunk_type}
**Descripción:** {chunk.description}

```json
{chunk_json}
```

Análisis breve basado en contexto API. Máximo 300 palabras.""",
        )

    def _aggregate_analyses(
        self,
        partial_analyses: list[dict],
        config_data: dict,
        temperature: float,
        stream: bool,
    ) -> str | Generator[str]:
        """
        Agrega todos los análisis parciales en uno final y coherente.
        Optimizado para reducir tokens usando resúmenes estructurados.

        Args:
            partial_analyses: Lista de análisis parciales
            config_data: Configuración original (para contexto)
            temperature: Temperatura del modelo
            stream: Si True, retorna generador

        Returns:
            Análisis final agregado
        """
        # Agrupar análisis por tipo para resumen más compacto
        grouped = {}
        for analysis in partial_analyses:
            chunk_type = analysis['chunk_type']
            if chunk_type not in grouped:
                grouped[chunk_type] = []
            grouped[chunk_type].append(analysis)
        
        # Construir contexto COMPACTO con análisis agrupados
        context = "**ANÁLISIS DE CONFIGURACIÓN T8 (Resumen Estructurado):**\n\n"
        
        # Orden lógico de presentación
        type_order = [
            "machines_summary",
            "system_properties", 
            "measurement_points",
            "processing_modes",
            "calculated_params",
            "operational_states",
            "storage_strategies"
        ]
        
        for chunk_type in type_order:
            if chunk_type in grouped:
                analyses = grouped[chunk_type]
                context += f"### {chunk_type.replace('_', ' ').title()}\n"
                
                # Si hay múltiples análisis del mismo tipo, condensarlos
                if len(analyses) > 1:
                    context += f"*({len(analyses)} fragmentos consolidados)*\n\n"
                    # Solo incluir los primeros 2 completos, resumir el resto
                    for analysis in analyses[:2]:
                        context += f"{analysis['analysis']}\n\n"
                    if len(analyses) > 2:
                        context += f"*... y {len(analyses) - 2} fragmentos adicionales del mismo tipo*\n\n"
                else:
                    context += f"{analyses[0]['analysis']}\n\n"
                
                context += "---\n\n"
        
        # Agregar información básica de la config
        machines = config_data.get("machines", [])
        machine_names = [m.get("tag", "Unknown") for m in machines]
        context += f"**Máquinas:** {', '.join(machine_names)}\n"
        context += f"**Total de fragmentos analizados:** {len(partial_analyses)}\n\n"

        # Prompt OPTIMIZADO para agregación final con RELACIONES explícitas
        aggregation_prompt = f"""
Eres un experto en TWave T8. Sintetiza los siguientes análisis parciales en un 
reporte coherente y profesional.

{context}

**RELACIONES CLAVE DEL SISTEMA T8:**

1. **Estados Operativos** → definen condiciones de la máquina (basados en speed, parámetros)
2. **Estrategias de Almacenamiento** → SE ACTIVAN según:
   - Estados operativos (type 2: cambios de estado entre state1_id y state2_id)
   - Niveles de alarma de parámetros (type 3: según nivel alarm)
   - Tiempo/Cron (type 0: cron_line)
   - Ciclos de monitorización (type 1: cada mon_period ciclos)
3. **Parámetros Calculados** → generan alarmas que pueden activar estrategias
4. **Modos de Procesamiento** → definen cómo se calculan los parámetros (FFT, integración)

**INSTRUCCIONES:**

Al generar el reporte, EXPLICA EXPLÍCITAMENTE estas relaciones:
- Qué estados están definidos y cómo se detectan
- Qué estrategias se disparan con cada estado o alarma
- Cómo las alarmas de parámetros activan estrategias de almacenamiento

Usa formato Markdown:

## 📊 Resumen General
## 🏭 Máquinas y Puntos de Medición
## ⚙️ Procesamiento y Parámetros Calculados
## 🔄 Estados Operativos y sus Condiciones
## 💾 Estrategias de Almacenamiento (y qué las activa)
## 🎯 Observaciones Clave

**Límite:** Máximo 2500 palabras. Sé técnico y explica las RELACIONES."""

        # Seleccionar modelo potente para agregación
        total_size = sum(len(a["analysis"]) for a in partial_analyses)
        model_config = ModelSelector.select_for_aggregation(
            num_fragments=len(partial_analyses), total_size=total_size
        )

        if self.verbose:
            print(
                f"\n🔄 Agregando {len(partial_analyses)} análisis parciales..."
            )
            print(
                f"🤖 Modelo de agregación: {model_config.name} "
                f"(tier {model_config.cost_tier}, {total_size} chars)"
            )

        # Generar agregación final usando modelo potente
        return self.llm_client._generate_completion(
            prompt=aggregation_prompt,
            temperature=temperature,
            max_tokens=min(3000, model_config.max_tokens),  # Reducido de 4096 a 3000
            stream=stream,
            model=model_config.name,  # Modelo dinámico para agregación
        )

    def clear_cache(self, config_uid: str | None = None) -> int:
        """
        Limpia el caché.

        Args:
            config_uid: Si se proporciona, solo limpia esa configuración.
                       Si es None, limpia todo el caché.

        Returns:
            Número de entradas eliminadas
        """
        if config_uid:
            return self.cache.clear_config(config_uid)
        else:
            return self.cache.clear_all()

    def get_cache_stats(self) -> dict:
        """
        Obtiene estadísticas del caché.

        Returns:
            Diccionario con estadísticas
        """
        return self.cache.get_stats()
