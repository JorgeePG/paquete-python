"""
Sistema de caché para análisis de fragmentos de configuración.
Almacena análisis parciales para reutilización.
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class CachedAnalysis:
    """Representa un análisis cacheado de un fragmento."""

    chunk_id: str
    chunk_type: str
    analysis: str
    timestamp: float
    model: str
    temperature: float
    config_uid: str


class ChunkCache:
    """Gestiona el caché de análisis de fragmentos."""

    def __init__(self, cache_dir: str = ".cache/llm_chunks") -> None:
        """
        Inicializa el sistema de caché.

        Args:
            cache_dir: Directorio donde se almacena el caché
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, chunk_id: str) -> Path:
        """
        Obtiene la ruta del archivo de caché para un chunk_id.

        Args:
            chunk_id: ID del fragmento

        Returns:
            Path al archivo de caché
        """
        # Usar hash del chunk_id para evitar nombres demasiado largos
        cache_hash = hashlib.md5(chunk_id.encode()).hexdigest()
        return self.cache_dir / f"{cache_hash}.json"

    def get(self, chunk_id: str, max_age_hours: float = 24.0) -> CachedAnalysis | None:
        """
        Obtiene un análisis del caché si existe y no ha expirado.

        Args:
            chunk_id: ID del fragmento
            max_age_hours: Edad máxima del caché en horas (24h por defecto)

        Returns:
            CachedAnalysis si existe y es válido, None en caso contrario
        """
        cache_path = self._get_cache_path(chunk_id)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, encoding="utf-8") as f:
                data = json.load(f)

            cached = CachedAnalysis(**data)

            # Verificar si ha expirado
            age_hours = (time.time() - cached.timestamp) / 3600
            if age_hours > max_age_hours:
                # Eliminar caché expirado
                cache_path.unlink()
                return None

            return cached

        except (json.JSONDecodeError, KeyError, TypeError):
            # Caché corrupto, eliminarlo
            if cache_path.exists():
                cache_path.unlink()
            return None

    def set(
        self,
        chunk_id: str,
        chunk_type: str,
        analysis: str,
        config_uid: str,
        model: str = "groq/compound",
        temperature: float = 0.6,
    ) -> None:
        """
        Guarda un análisis en el caché.

        Args:
            chunk_id: ID del fragmento
            chunk_type: Tipo de fragmento
            analysis: Análisis generado por el LLM
            config_uid: UID de la configuración
            model: Modelo usado
            temperature: Temperatura usada
        """
        cached = CachedAnalysis(
            chunk_id=chunk_id,
            chunk_type=chunk_type,
            analysis=analysis,
            timestamp=time.time(),
            model=model,
            temperature=temperature,
            config_uid=config_uid,
        )

        cache_path = self._get_cache_path(chunk_id)

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(asdict(cached), f, indent=2)
        except OSError as e:
            # No fallar si no se puede escribir el caché
            print(f"⚠️  Warning: Could not write cache: {e}")

    def clear_config(self, config_uid: str) -> int:
        """
        Elimina todos los análisis cacheados de una configuración específica.

        Args:
            config_uid: UID de la configuración

        Returns:
            Número de archivos eliminados
        """
        deleted = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("config_uid") == config_uid:
                    cache_file.unlink()
                    deleted += 1
            except (json.JSONDecodeError, KeyError, OSError):
                pass
        return deleted

    def clear_all(self) -> int:
        """
        Elimina todo el caché.

        Returns:
            Número de archivos eliminados
        """
        deleted = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                deleted += 1
            except OSError:
                pass
        return deleted

    def get_stats(self) -> dict:
        """
        Obtiene estadísticas del caché.

        Returns:
            Diccionario con estadísticas
        """
        stats = {
            "total_entries": 0,
            "total_size_bytes": 0,
            "oldest_timestamp": None,
            "newest_timestamp": None,
            "configs": set(),
            "chunk_types": {},
        }

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                stats["total_entries"] += 1
                stats["total_size_bytes"] += cache_file.stat().st_size

                with open(cache_file, encoding="utf-8") as f:
                    data = json.load(f)

                timestamp = data.get("timestamp", 0)
                if (
                    stats["oldest_timestamp"] is None
                    or timestamp < stats["oldest_timestamp"]
                ):
                    stats["oldest_timestamp"] = timestamp
                if (
                    stats["newest_timestamp"] is None
                    or timestamp > stats["newest_timestamp"]
                ):
                    stats["newest_timestamp"] = timestamp

                config_uid = data.get("config_uid")
                if config_uid:
                    stats["configs"].add(config_uid)

                chunk_type = data.get("chunk_type", "unknown")
                stats["chunk_types"][chunk_type] = (
                    stats["chunk_types"].get(chunk_type, 0) + 1
                )

            except (json.JSONDecodeError, KeyError, OSError):
                pass

        stats["configs"] = list(stats["configs"])
        return stats

    def get_size_mb(self) -> float:
        """
        Calcula el tamaño total del caché en MB.

        Returns:
            Tamaño en MB
        """
        stats = self.get_stats()
        return stats["total_size_bytes"] / (1024 * 1024)
