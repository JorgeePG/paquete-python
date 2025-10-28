"""
Cliente LLM para interactuar con la API de Groq.
Implementación específica para análisis de configuraciones del sistema TWave T8.
"""

import json
import os
from collections.abc import Generator

from dotenv import load_dotenv  # type: ignore
from groq import Groq  # type: ignore

# Cargar variables de entorno desde .env
load_dotenv()

# Importar componentes de fragmentación (lazy import para evitar dependencias)
try:
    from llm_client.chunked_analyzer import ChunkedAnalyzer

    HAS_CHUNKED_ANALYZER = True
except ImportError:
    HAS_CHUNKED_ANALYZER = False


class GroqLLMClient:
    """Cliente para interactuar con modelos LLM de Groq."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Inicializa el cliente de Groq.

        Args:
            api_key: Clave API de Groq. Si no se proporciona, se busca en la variable
                    de entorno GROQ_API_KEY.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No se encontró la API key de Groq. "
                "Proporciona una clave o establece la variable GROQ_API_KEY."
            )

        self.client = Groq(api_key=self.api_key)
        # Usar llama-3.3-70b-versatile: rápido y con límites generosos
        # 30,000 RPM (requests per minute)
        # 14,400 RPD (requests per day)
        self.model = "llama-3.3-70b-versatile"

    def analyze_t8_configuration(
        self,
        config_data: str | dict,
        api_definitions: str | None = None,
        temperature: float = 0.6,
        max_tokens: int = 4096,
        stream: bool = False,
        use_chunking: bool = True,
        max_cache_age_hours: float = 24.0,
        verbose: bool = False,
    ) -> str | Generator[str]:
        """
        Analiza una configuración del sistema TWave T8 usando el modelo LLM.

        Args:
            config_data: Datos de configuración (JSON string o dict)
            api_definitions: Definiciones de la API (opcional)
            temperature: Temperatura para el modelo (0.0 - 1.0)
            max_tokens: Número máximo de tokens en la respuesta
            stream: Si True, retorna un generador para streaming
            use_chunking: Si True, usa estrategia de fragmentación (recomendado)
            max_cache_age_hours: Edad máxima del caché en horas (solo con chunking)
            verbose: Si True, muestra progreso del análisis (solo con chunking)

        Returns:
            Análisis de la configuración como string o generador
        """

        # Preparar los datos de configuración
        if isinstance(config_data, str):
            try:
                config_json = json.loads(config_data)
            except json.JSONDecodeError:
                config_json = config_data
        else:
            config_json = config_data

        # Usar estrategia de fragmentación si está disponible y habilitada
        if use_chunking and HAS_CHUNKED_ANALYZER and isinstance(config_json, dict):
            analyzer = ChunkedAnalyzer(self, api_definitions)
            return analyzer.analyze_config_chunked(
                config_data=config_json,
                temperature=temperature,
                max_cache_age_hours=max_cache_age_hours,
                stream=stream,
                verbose=verbose,
            )

        # Fallback: Análisis tradicional sin fragmentación
        prompt = self._build_t8_analysis_prompt(config_json, api_definitions)
        return self._generate_completion(
            prompt=prompt, temperature=temperature, max_tokens=max_tokens, stream=stream
        )

    def _build_t8_analysis_prompt(
        self, config_data: str | dict, api_definitions: str | None = None
    ) -> str:
        """
        Construye un prompt específico para análisis de configuraciones T8.

        Args:
            config_data: Datos de configuración
            api_definitions: Definiciones de la API

        Returns:
            Prompt formateado para el análisis
        """

        config_str = (
            json.dumps(config_data, indent=2)
            if isinstance(config_data, dict)
            else str(config_data)
        )

        # Intentar detectar las máquinas configuradas
        machine_info = ""
        if isinstance(config_data, dict) and "machines" in config_data:
            machines = config_data.get("machines", [])
            if machines:
                machine_tags = [m.get("tag", "desconocida") for m in machines]
                if len(machine_tags) == 1:
                    machine_info = (
                        f"\nDescribe la configuración de la máquina "
                        f"**{machine_tags[0]}**:"
                    )
                else:
                    machine_list = ", ".join(machine_tags)
                    machine_info = (
                        f"\nDescribe la configuración de las máquinas "
                        f"configuradas ({machine_list}):"
                    )
            else:
                machine_info = "\nDescribe la configuración del sistema:"
        else:
            machine_info = "\nDescribe la configuración del sistema:"

        prompt = (
            "Eres un asistente experto en analizar configuraciones del "
            "sistema TWave T8.\n\n"
            "**CONTEXTO:**\n"
            "Te proporciono un archivo de configuración (config.json) del "
            "sistema de monitoreo de vibración TWave T8."
        )

        if api_definitions:
            prompt += f"""
También tienes disponibles las siguientes definiciones clave de la API:
{api_definitions}
"""

        prompt += f"""

**ARCHIVO DE CONFIGURACIÓN:**
```json
{config_str}
```

**TAREA:**
Analiza el config.json usando las definiciones.{machine_info}
- Sus puntos de medición principales (menciona 2-3 ejemplos relevantes)
- Los modos de procesamiento asociados (AM1, AM2, AM3, etc.)
- Los parámetros más importantes calculados (Overall, 1x, DC_Gap, etc.)
- Los estados operativos
- Las estrategias de almacenamiento definidas

**FORMATO DE SALIDA:**
Estructura tu respuesta usando encabezados Markdown para cada sección:
- ## Máquina(s)
- ## Puntos de Medición  
- ## Modos de Procesamiento
- ## Parámetros Calculados
- ## Estados Operativos
- ## Estrategias de Almacenamiento

Proporciona información clara y concisa, enfocándote en los aspectos más 
relevantes para el monitoreo de vibración."""

        return prompt

    def ask_custom_question(
        self,
        question: str,
        context: str | None = None,
        temperature: float = 0.6,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> str | Generator[str]:
        """
        Hace una pregunta personalizada al modelo LLM.

        Args:
            question: Pregunta a realizar
            context: Contexto adicional (opcional)
            temperature: Temperatura para el modelo
            max_tokens: Número máximo de tokens
            stream: Si True, retorna un generador para streaming

        Returns:
            Respuesta como string o generador
        """

        prompt = question
        if context:
            prompt = f"**CONTEXTO:**\n{context}\n\n**PREGUNTA:**\n{question}"

        return self._generate_completion(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )

    def ask_about_config(
        self,
        question: str,
        config_data: dict,
        api_definitions: str | None = None,
        temperature: float = 0.6,
        stream: bool = False,
        use_chunking: bool = True,
        max_cache_age_hours: float = 24.0,
        verbose: bool = False,
    ) -> str | Generator[str]:
        """
        Hace una pregunta específica sobre una configuración T8.

        Usa fragmentación inteligente para manejar configuraciones grandes.

        Args:
            question: Pregunta sobre la configuración
            config_data: Datos de configuración
            api_definitions: Definiciones de la API (opcional)
            temperature: Temperatura del modelo
            stream: Si True, retorna generador para streaming
            use_chunking: Si True, usa estrategia de fragmentación
            max_cache_age_hours: Edad máxima del caché
            verbose: Mostrar progreso

        Returns:
            Respuesta como string o generador
        """
        if not use_chunking or not HAS_CHUNKED_ANALYZER:
            # Fallback: usar método simple (puede fallar con configs grandes)
            context = json.dumps(config_data, indent=2)
            if api_definitions:
                context = f"API Documentation:\n{api_definitions}\n\n{context}"
            return self.ask_custom_question(
                question=question,
                context=context,
                temperature=temperature,
                stream=stream,
            )

        # Usar estrategia de fragmentación con pregunta específica
        from llm_client.chunked_analyzer import ChunkedAnalyzer

        analyzer = ChunkedAnalyzer(self, api_definitions)

        # Fragmentar y analizar
        chunks = analyzer.chunker.chunk_config(config_data)
        config_uid = analyzer.chunker.get_config_uid(config_data)

        if verbose:
            print(f"📦 Procesando {len(chunks)} fragmentos...")

        # Analizar fragmentos relevantes (usar caché)
        partial_analyses = []
        for chunk in chunks:
            cached = analyzer.cache.get(
                chunk.chunk_id, max_age_hours=max_cache_age_hours
            )

            if cached:
                analysis = cached.analysis
            else:
                analysis = analyzer._analyze_chunk(chunk, temperature)
                analyzer.cache.set(
                    chunk_id=chunk.chunk_id,
                    chunk_type=chunk.chunk_type,
                    analysis=analysis,
                    config_uid=config_uid,
                    model=self.model,
                    temperature=temperature,
                )

            partial_analyses.append(
                {
                    "chunk_type": chunk.chunk_type,
                    "description": chunk.description,
                    "analysis": analysis,
                }
            )

        # Construir contexto agregado con la pregunta
        context = "**ANÁLISIS DE LA CONFIGURACIÓN T8:**\n\n"
        for idx, analysis in enumerate(partial_analyses, 1):
            context += f"### {idx}. {analysis['description']}\n"
            context += f"{analysis['analysis']}\n\n"

        # Hacer la pregunta con el contexto agregado
        final_prompt = f"""{context}

**PREGUNTA DEL USUARIO:**
{question}

**INSTRUCCIONES:**
Responde a la pregunta del usuario usando la información de los análisis anteriores.
Sé específico, claro y conciso. Si la pregunta es general como "explica todo",
proporciona un resumen estructurado y completo."""

        return self._generate_completion(
            prompt=final_prompt,
            temperature=temperature,
            max_tokens=4096,
            stream=stream,
        )

    def _generate_completion(
        self,
        prompt: str,
        temperature: float = 0.6,
        max_tokens: int = 4096,
        stream: bool = False,
        model: str | None = None,
    ) -> str | Generator[str]:
        """
        Genera una respuesta usando la API de Groq.

        Implementa estrategia de fallback inteligente:
        - Tier 1 (llama-3.1-8b-instant) → Tier 2 (Scout) → Tier 3 (70B) → Error
        - Evita modelos OpenAI que no corren en LPU de Groq

        Args:
            prompt: Prompt para el modelo
            temperature: Temperatura para el modelo
            max_tokens: Número máximo de tokens
            stream: Si True, retorna un generador para streaming
            model: Modelo a usar (si None, usa self.model)

        Returns:
            Respuesta como string o generador
        """

        # Usar modelo específico o el configurado por defecto
        selected_model = model if model is not None else self.model

        # Definir cadena de fallback basada en tiers
        # Solo modelos optimizados para Groq LPU (Meta)
        fallback_chain = [
            selected_model,
            "meta-llama/llama-4-scout-17b-16e-instruct",  # Tier 2: Scout MoE
            "llama-3.3-70b-versatile",  # Tier 3: Potente
            "llama-3.1-8b-instant",  # Tier 1: Ultrarrápido (último recurso)
        ]

        # Eliminar duplicados preservando orden
        seen = set()
        fallback_chain = [
            m for m in fallback_chain 
            if not (m in seen or seen.add(m))
        ]

        last_error = None

        for attempt_model in fallback_chain:
            try:
                completion = self.client.chat.completions.create(
                    model=attempt_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=1,
                    stream=stream,
                    stop=None,
                )

                if stream:
                    return self._stream_response(completion)
                else:
                    return completion.choices[0].message.content

            except Exception as e:
                last_error = e
                # Si no es el último modelo, intentar siguiente
                if attempt_model != fallback_chain[-1]:
                    continue
                # Si es el último, propagar error
                raise RuntimeError(
                    f"Todos los modelos fallaron. Último error con {attempt_model}: {str(e)}"
                ) from e

        # No debería llegar aquí, pero por seguridad
        raise RuntimeError(
            f"Error inesperado en fallback. Último error: {str(last_error)}"
        ) from last_error

    def _stream_response(self, completion: object) -> Generator[str]:
        """
        Procesa una respuesta en streaming.

        Args:
            completion: Objeto de respuesta de Groq

        Yields:
            Fragmentos de texto de la respuesta
        """
        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    def change_model(self, model_name: str) -> None:
        """
        Cambia el modelo LLM a usar.

        Args:
            model_name: Nombre del modelo (ej: "llama3-8b-8192", "mixtral-8x7b-32768")
        """
        self.model = model_name

    def get_available_models(self) -> list[str]:
        """
        Retorna una lista de modelos disponibles en Groq.
        Ordenados por recomendación (optimizados para Groq LPU).

        Returns:
            Lista de nombres de modelos
        """
        # Modelos Meta optimizados para Groq LPU (Oct 2025)
        return [
            "llama-3.3-70b-versatile",  # RECOMENDADO: Tier 3, máxima calidad
            "meta-llama/llama-4-scout-17b-16e-instruct",  # RECOMENDADO: Tier 2 MoE
            "llama-3.1-8b-instant",  # RECOMENDADO: Tier 1, ultrarrápido
            "llama-3.1-70b-versatile",  # Alternativa Tier 3
            "gemma2-9b-it",  # Fallback Google
            "gemma-7b-it",  # Fallback Google
        ]

    def clear_cache(self, config_uid: str | None = None) -> dict:
        """
        Limpia el caché de análisis de fragmentos.

        Args:
            config_uid: Si se proporciona, solo limpia esa configuración.
                       Si es None, limpia todo el caché.

        Returns:
            Diccionario con información de limpieza
        """
        if not HAS_CHUNKED_ANALYZER:
            return {
                "success": False,
                "message": "Chunked analyzer not available",
                "deleted": 0,
            }

        try:
            from llm_client.chunked_analyzer import ChunkedAnalyzer

            analyzer = ChunkedAnalyzer(self)
            deleted = analyzer.clear_cache(config_uid)
            return {
                "success": True,
                "message": f"Deleted {deleted} cache entries",
                "deleted": deleted,
            }
        except Exception as e:
            return {"success": False, "message": str(e), "deleted": 0}

    def get_cache_stats(self) -> dict:
        """
        Obtiene estadísticas del caché de análisis.

        Returns:
            Diccionario con estadísticas o mensaje de error
        """
        if not HAS_CHUNKED_ANALYZER:
            return {"available": False, "message": "Chunked analyzer not available"}

        try:
            from llm_client.chunked_analyzer import ChunkedAnalyzer

            analyzer = ChunkedAnalyzer(self)
            stats = analyzer.get_cache_stats()
            stats["available"] = True
            return stats
        except Exception as e:
            return {"available": False, "message": str(e)}
