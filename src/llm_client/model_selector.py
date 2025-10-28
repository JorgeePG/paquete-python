"""
Selector inteligente de modelos LLM basado en complejidad de la tarea.
Optimiza costos usando modelos apropiados para cada tipo de análisis.
"""

from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configuración de un modelo LLM."""

    name: str
    max_tokens: int
    speed: str  # "fast", "medium", "slow"
    quality: str  # "basic", "good", "excellent"
    cost_tier: int  # 1 (más barato) a 5 (más caro)
    rpm_limit: int  # Requests per minute
    description: str


class ModelSelector:
    """Selecciona el modelo óptimo según el tipo y tamaño de la tarea."""

    # Catálogo de modelos disponibles en Groq (actualizados Oct 2025)
    # Enfoque en modelos Meta optimizados para LPU de Groq
    MODELS = {
        # Tier 1: Ultra-rápido (~800+ t/s) - El sprinter más optimizado
        "llama-3.1-8b-instant": ModelConfig(
            name="llama-3.1-8b-instant",
            max_tokens=8192,
            speed="fast",
            quality="good",
            cost_tier=1,
            rpm_limit=30000,
            description="Más rápido y optimizado. Fragmentos pequeños y baja latencia",
        ),
        # Tier 2: Equilibrado MoE (~500 t/s) - El intermedio inteligente
        "meta-llama/llama-4-scout-17b-16e-instruct": ModelConfig(
            name="meta-llama/llama-4-scout-17b-16e-instruct",
            max_tokens=16384,  # Scout tiene ventana extendida
            speed="medium",
            quality="excellent",
            cost_tier=2,
            rpm_limit=30000,
            description="MoE 17B/16E. Balance perfecto: fragmentos grandes y agregaciones simples",
        ),
        # Tier 3: Potente versatil (~300 t/s) - El razonador definitivo
        "llama-3.3-70b-versatile": ModelConfig(
            name="llama-3.3-70b-versatile",
            max_tokens=8192,
            speed="medium",
            quality="excellent",
            cost_tier=3,
            rpm_limit=30000,
            description="Máxima calidad. Agregación final compleja y razonamiento profundo",
        ),
        # Tier 1: Fallback ligero (Google, para diversificación)
        "gemma-7b-it": ModelConfig(
            name="gemma-7b-it",
            max_tokens=8192,
            speed="fast",
            quality="good",
            cost_tier=1,
            rpm_limit=30000,
            description="Fallback fiable. Énfasis en seguridad (Google)",
        ),
        # Tier 2: Alternativa balanceada (Google)
        "gemma2-9b-it": ModelConfig(
            name="gemma2-9b-it",
            max_tokens=8192,
            speed="fast",
            quality="good",
            cost_tier=2,
            rpm_limit=30000,
            description="Alternativa balanceada si Scout no disponible",
        ),
    }

    @classmethod
    def select_for_chunk_analysis(
        cls, chunk_type: str, content_size: int
    ) -> ModelConfig:
        """
        Selecciona el modelo óptimo para analizar un fragmento.
        Estrategia actualizada Oct 2025: Enfoque en modelos Meta optimizados para Groq LPU.

        Args:
            chunk_type: Tipo de fragmento (machines_summary, calculated_params, etc.)
            content_size: Tamaño aproximado del contenido en caracteres

        Returns:
            Configuración del modelo seleccionado
        """
        # REGLA 1: Por defecto - llama-3.1-8b-instant (el más rápido)
        # Para fragmentos pequeños y tareas simples
        
        # Fragmentos muy simples -> modelo ultra-rápido
        if chunk_type in [
            "machines_summary",
            "operational_states",
        ]:
            return cls.MODELS["llama-3.1-8b-instant"]

        # System properties: depende del tamaño
        if chunk_type == "system_properties":
            if content_size < 5000:
                # Pequeño -> ultrarrápido
                return cls.MODELS["llama-3.1-8b-instant"]
            else:
                # Extenso -> Scout MoE (mejor para contextos grandes)
                return cls.MODELS["meta-llama/llama-4-scout-17b-16e-instruct"]

        # Measurement points y storage strategies
        if chunk_type in ["measurement_points", "storage_strategies"]:
            if content_size < 2000:
                # Pequeños -> ultrarrápido
                return cls.MODELS["llama-3.1-8b-instant"]
            else:
                # Medianos/Grandes -> Scout MoE (ventana 16k)
                return cls.MODELS["meta-llama/llama-4-scout-17b-16e-instruct"]

        # Processing modes: técnico y potencialmente complejo
        if chunk_type == "processing_modes":
            if content_size < 2000:
                # Configuración simple -> rápido
                return cls.MODELS["llama-3.1-8b-instant"]
            elif content_size < 4000:
                # Configuración media -> Scout (MoE eficiente)
                return cls.MODELS["meta-llama/llama-4-scout-17b-16e-instruct"]
            else:
                # FFT complejas múltiples -> Scout (mejor razonamiento)
                return cls.MODELS["meta-llama/llama-4-scout-17b-16e-instruct"]

        # Calculated params: el más variable en complejidad
        if chunk_type == "calculated_params":
            if content_size < 1000:
                # Parámetros muy simples -> ultrarrápido
                return cls.MODELS["llama-3.1-8b-instant"]
            elif content_size < 3000:
                # Parámetros medianos -> Scout (MoE balanceado)
                return cls.MODELS["meta-llama/llama-4-scout-17b-16e-instruct"]
            else:
                # Parámetros complejos con alarmas -> Scout (mejor comprensión)
                return cls.MODELS["meta-llama/llama-4-scout-17b-16e-instruct"]

        # Fallback: Scout (modelo equilibrado)
        return cls.MODELS["meta-llama/llama-4-scout-17b-16e-instruct"]

    @classmethod
    def select_for_aggregation(cls, num_fragments: int, total_size: int) -> ModelConfig:
        """
        Selecciona el modelo óptimo para agregar análisis parciales.
        Estrategia Oct 2025: Scout para agregaciones simples, 70B para complejas.

        Args:
            num_fragments: Número de fragmentos a agregar
            total_size: Tamaño total aproximado en caracteres

        Returns:
            Configuración del modelo seleccionado
        """
        # Agregaciones muy pequeñas (≤5 fragmentos) -> Scout (rápido y suficiente)
        if num_fragments <= 5:
            return cls.MODELS["meta-llama/llama-4-scout-17b-16e-instruct"]

        # Agregaciones medianas (6-12 fragmentos) -> Scout (MoE eficiente)
        # Scout 17B/16E es perfecto para este rango: buena calidad, velocidad decente
        if num_fragments <= 12:
            return cls.MODELS["meta-llama/llama-4-scout-17b-16e-instruct"]

        # Agregaciones grandes y complejas (>12 fragmentos) -> 70B (máxima calidad)
        # El 70B es necesario para mantener coherencia en síntesis muy complejas
        if num_fragments > 12:
            return cls.MODELS["llama-3.3-70b-versatile"]

        # Fallback: Scout (equilibrado)
        return cls.MODELS["meta-llama/llama-4-scout-17b-16e-instruct"]

    @classmethod
    def select_for_question(
        cls, question_complexity: str = "medium"
    ) -> ModelConfig:
        """
        Selecciona el modelo óptimo para responder una pregunta.

        Args:
            question_complexity: "simple", "medium", "complex"

        Returns:
            Configuración del modelo seleccionado
        """
        if question_complexity == "simple":
            return cls.MODELS["llama-3.1-8b-instant"]
        elif question_complexity == "complex":
            return cls.MODELS["llama-3.3-70b-versatile"]
        else:  # medium
            return cls.MODELS["meta-llama/llama-4-scout-17b-16e-instruct"]

    @classmethod
    def get_model_stats(cls) -> dict:
        """
        Retorna estadísticas de los modelos disponibles.

        Returns:
            Diccionario con información de modelos
        """
        return {
            "total_models": len(cls.MODELS),
            "models": {
                name: {
                    "speed": config.speed,
                    "quality": config.quality,
                    "cost_tier": config.cost_tier,
                    "max_tokens": config.max_tokens,
                    "description": config.description,
                }
                for name, config in cls.MODELS.items()
            },
            "recommendations": {
                "fastest": "llama-3.1-8b-instant",
                "balanced": "meta-llama/llama-4-scout-17b-16e-instruct",
                "best_quality": "llama-3.3-70b-versatile",
                "fallback_safe": "gemma-7b-it",
            },
            "architecture_notes": {
                "llama-3.1-8b-instant": "Denso 8B. ~800+ t/s. Optimizado Groq LPU.",
                "meta-llama/llama-4-scout-17b-16e-instruct": "MoE 17B/16E. ~500 t/s. Ventana 16k. El equilibrado perfecto.",
                "llama-3.3-70b-versatile": "Denso 70B. ~300 t/s. Razonamiento profundo.",
                "gemma-7b-it": "Denso 7B. ~750 t/s. Google, énfasis seguridad.",
                "gemma2-9b-it": "Denso 9B. ~450 t/s. Alternativa si Scout no disponible.",
            },
            "strategy": {
                "fragments_small": "llama-3.1-8b-instant",
                "fragments_large": "meta-llama/llama-4-scout-17b-16e-instruct",
                "aggregation_simple": "meta-llama/llama-4-scout-17b-16e-instruct",
                "aggregation_complex": "llama-3.3-70b-versatile",
            },
        }
