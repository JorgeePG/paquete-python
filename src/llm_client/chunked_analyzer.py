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
            max_tokens=min(2048, model_config.max_tokens),
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
Eres un experto en sistemas TWave T8. Analiza el siguiente resumen de máquinas:

{api_context}

**DATOS A ANALIZAR:**
```json
{chunk_json}
```

Proporciona una descripción concisa de:
- Número de máquinas configuradas
- Nombres y tags de las máquinas
- Cantidad de puntos de medición por máquina
- Estados y estrategias configuradas

Sé breve y directo.""",
            "measurement_points": f"""
Eres un experto en sistemas TWave T8. Analiza los siguientes puntos de medición:

{api_context}

**DATOS A ANALIZAR:**
```json
{chunk_json}
```

Describe brevemente:
- Tipos de sensores y su configuración (según el campo `type` y `mode`)
- Ubicaciones de medición principales (según `path` y `component_id`)
- Configuración de entrada física (si aplica)

Sé conciso y técnico.""",
            "processing_modes": f"""
Eres un experto en sistemas TWave T8. Analiza los siguientes modos de procesamiento:

{api_context}

**DATOS A ANALIZAR:**
```json
{chunk_json}
```

Explica brevemente (usando el contexto API):
- Configuraciones FFT: sample_rate, max_freq, bins, averages
- Tipo de procesamiento (type) y su significado
- Niveles de integración aplicados (integrate_sp)
- Configuración de guardado (save_sp, save_wf)

Sé técnico y preciso.""",
            "calculated_params": f"""
Eres un experto en sistemas TWave T8. Analiza los siguientes parámetros calculados:

{api_context}

**DATOS A ANALIZAR:**
```json
{chunk_json}
```

Describe (interpretando según el contexto API):
- Tipo de cálculo (type) y su significado exacto
- Configuración de alarmas por estado (si existen)
- Bandas espectrales (spectral_bands) si aplican
- Niveles de integración y detección aplicados

Sé preciso y técnico.""",
            "operational_states": f"""
Eres un experto en sistemas TWave T8. Analiza los siguientes estados operativos:

{api_context}

**DATOS A ANALIZAR:**
```json
{chunk_json}
```

Explica (usando el contexto API):
- Nombres y condiciones de cada estado
- Lógica de las condiciones (expresiones con speed, params)
- Propósito de cada estado en el monitoreo

Sé conciso.""",
            "storage_strategies": f"""
Eres un experto en sistemas TWave T8. Analiza las siguientes estrategias de
almacenamiento:

{api_context}

**DATOS A ANALIZAR:**
```json
{chunk_json}
```

Describe (interpretando el campo `type` según contexto API):
- Tipo de disparador de cada estrategia
- Configuración específica (cron_line, mon_period, state transitions, alarm levels)
- Cuándo y por qué se almacenan datos

Sé técnico.""",
            "system_properties": f"""
Eres un experto en sistemas TWave T8. Analiza las siguientes propiedades del sistema:

{api_context}

**DATOS A ANALIZAR:**
```json
{chunk_json}
```

Resume (usando el contexto API):
- Propiedades físicas (properties) y sus IDs
- Unidades de medida (units) con factores de conversión
- Relaciones entre properties y units (property_id)

Sé directo y técnico.""",
        }

        # Fallback con contexto genérico
        return prompts.get(
            chunk.chunk_type,
            f"""
Eres un experto en sistemas TWave T8.

{api_context}

**FRAGMENTO A ANALIZAR:**
Tipo: {chunk.chunk_type}
Descripción: {chunk.description}

```json
{chunk_json}
```

Proporciona un análisis breve y conciso basándote en el contexto API proporcionado.""",
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

        Args:
            partial_analyses: Lista de análisis parciales
            config_data: Configuración original (para contexto)
            temperature: Temperatura del modelo
            stream: Si True, retorna generador

        Returns:
            Análisis final agregado
        """
        # Construir contexto con todos los análisis parciales
        context = "**ANÁLISIS PARCIALES DE LA CONFIGURACIÓN T8:**\n\n"

        for idx, analysis in enumerate(partial_analyses, 1):
            context += f"## {idx}. {analysis['description']}\n"
            context += f"Tipo: {analysis['chunk_type']}\n\n"
            context += f"{analysis['analysis']}\n\n"
            context += "---\n\n"

        # Agregar información básica de la config
        machines = config_data.get("machines", [])
        machine_names = [m.get("tag", "Unknown") for m in machines]
        context += f"**Máquinas en la configuración:** {', '.join(machine_names)}\n\n"

        # Prompt para agregación final
        aggregation_prompt = f"""
Eres un experto en el sistema de monitoreo de vibración TWave T8.

A continuación, te proporciono análisis parciales de diferentes secciones de un
archivo de configuración. Tu tarea es **sintetizar estos análisis en una única
explicación coherente y completa** para el usuario.

{context}

**TAREA:**

Genera un análisis completo y bien estructurado de la configuración, integrando
toda la información de los análisis parciales.

**FORMATO DE SALIDA:**

Estructura tu respuesta usando encabezados Markdown:

## 📊 Resumen General

## 🏭 Máquinas Configuradas

## 📍 Puntos de Medición Principales

## ⚙️ Modos de Procesamiento

## 📈 Parámetros Monitoreados

## 🔄 Estados Operativos

## 💾 Estrategias de Almacenamiento

## 🎯 Conclusiones

Proporciona información clara, concisa y profesional. Evita repetir información
innecesariamente. Enfócate en los aspectos más relevantes para el monitoreo de
vibración y la operación del sistema.
"""

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
            max_tokens=min(4096, model_config.max_tokens),
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
