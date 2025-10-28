"""
Sistema de fragmentación y procesamiento por chunks para configuraciones T8.
Implementa estrategia "Divide y Vencerás" para manejar configs grandes.
"""

import hashlib
import json
from dataclasses import dataclass


@dataclass
class ConfigChunk:
    """Representa un fragmento de la configuración."""

    chunk_id: str
    chunk_type: str  # 'machines', 'points', 'proc_modes', 'states', etc.
    content: dict | list
    description: str
    config_uid: str  # UID de la configuración original


class ConfigChunker:
    """Divide configuraciones T8 en fragmentos lógicos manejables."""

    @staticmethod
    def get_config_uid(config_data: dict) -> str:
        """
        Obtiene o genera un UID único para la configuración.

        Args:
            config_data: Datos de configuración

        Returns:
            UID de la configuración
        """
        # Intentar usar UID del config si existe
        if isinstance(config_data, dict) and "uid" in config_data:
            return config_data["uid"]

        # Generar hash del contenido
        config_str = json.dumps(config_data, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()

    @staticmethod
    def chunk_config(config_data: dict) -> list[ConfigChunk]:
        """
        Divide la configuración en fragmentos lógicos.

        Args:
            config_data: Diccionario con la configuración completa

        Returns:
            Lista de fragmentos (ConfigChunk)
        """
        chunks = []
        config_uid = ConfigChunker.get_config_uid(config_data)

        # Fragmento 1: Información general de máquinas (sin detalles)
        if "machines" in config_data:
            machines_summary = []
            for machine in config_data["machines"]:
                summary = {
                    "id": machine.get("id"),
                    "tag": machine.get("tag"),
                    "name": machine.get("name"),
                    "speed": machine.get("speed"),
                    "speed_factor": machine.get("speed_factor"),
                    "num_points": len(machine.get("points", [])),
                    "num_states": len(machine.get("states", [])),
                    "num_strategies": len(machine.get("strategies", [])),
                }
                machines_summary.append(summary)

            chunks.append(
                ConfigChunk(
                    chunk_id=f"{config_uid}:machines_summary",
                    chunk_type="machines_summary",
                    content=machines_summary,
                    description="Información general de las máquinas configuradas",
                    config_uid=config_uid,
                )
            )

        # Fragmento 2: Puntos de medición (agrupados por máquina)
        if "machines" in config_data:
            for machine in config_data["machines"]:
                machine_tag = machine.get("tag", "unknown")
                points = machine.get("points", [])

                if points:
                    # Agrupar puntos en grupos de 5 para no sobrecargar
                    point_groups = [points[i : i + 5] for i in range(0, len(points), 5)]

                    for idx, point_group in enumerate(point_groups):
                        # Simplificar puntos (sin proc_modes detallados)
                        simplified_points = []
                        for point in point_group:
                            simplified = {
                                "id": point.get("id"),
                                "tag": point.get("tag"),
                                "name": point.get("name"),
                                "desc": point.get("desc"),
                                "type": point.get("type"),
                                "unit_id": point.get("unit_id"),
                                "input_number": point.get("input", {}).get("number"),
                                "sensor": point.get("input", {}).get("sensor", {}),  # AÑADIDO: Info completa del sensor
                                "num_proc_modes": len(point.get("proc_modes", [])),
                                "proc_mode_tags": [
                                    pm.get("tag") for pm in point.get("proc_modes", [])
                                ],
                            }
                            simplified_points.append(simplified)

                        chunks.append(
                            ConfigChunk(
                                chunk_id=f"{config_uid}:points_{machine_tag}_group{idx}",
                                chunk_type="measurement_points",
                                content={
                                    "machine": machine_tag,
                                    "points": simplified_points,
                                },
                                description=(
                                    f"Puntos de medición de {machine_tag} "
                                    f"(grupo {idx + 1})"
                                ),
                                config_uid=config_uid,
                            )
                        )

        # Fragmento 3: Modos de procesamiento (CONSOLIDADO por máquina)
        if "machines" in config_data:
            for machine in config_data["machines"]:
                machine_tag = machine.get("tag", "unknown")
                
                # Consolidar todos los modos de todos los puntos de esta máquina
                all_modes = []
                for point in machine.get("points", []):
                    point_tag = point.get("tag", "unknown")
                    proc_modes = point.get("proc_modes", [])

                    for mode in proc_modes:
                        # Incluir TODOS los campos relevantes según DocComprimida.md
                        mode_complete = {
                            "id": mode.get("id"),
                            "tag": mode.get("tag"),
                            "name": mode.get("name"),
                            "type": mode.get("type"),
                            "sample_rate": mode.get("sample_rate"),
                            "samples": mode.get("samples"),  # AÑADIDO
                            "max_freq": mode.get("max_freq"),
                            "min_freq": mode.get("min_freq"),
                            "bins": mode.get("bins"),
                            "averages": mode.get("averages"),  # AÑADIDO
                            "overlap": mode.get("overlap"),  # AÑADIDO
                            "window": mode.get("window"),  # AÑADIDO
                            "integrate_sp": mode.get("integrate_sp"),  # AÑADIDO
                            "save_sp": mode.get("save_sp"),  # AÑADIDO
                            "save_wf": mode.get("save_wf"),  # AÑADIDO
                            "selectors": mode.get("selectors", []),  # AÑADIDO
                            "num_params": len(mode.get("params", [])),
                            "point": point_tag,  # Identificar a qué punto pertenece
                        }
                        all_modes.append(mode_complete)

                if all_modes:
                    chunks.append(
                        ConfigChunk(
                            chunk_id=f"{config_uid}:proc_modes_{machine_tag}",
                            chunk_type="processing_modes",
                            content={
                                "machine": machine_tag,
                                "proc_modes": all_modes,
                            },
                            description=f"Modos de procesamiento de {machine_tag}",
                            config_uid=config_uid,
                        )
                    )

        # Fragmento 4: Parámetros calculados (OPTIMIZADO - por punto, con batching)
        if "machines" in config_data:
            for machine in config_data["machines"]:
                machine_tag = machine.get("tag", "unknown")
                
                # Consolidar todos los puntos de esta máquina
                all_points_params = []
                
                for point in machine.get("points", []):
                    point_tag = point.get("tag", "unknown")
                    
                    # Capturar información del sensor para determinar unidades correctas
                    sensor_info = point.get("input", {}).get("sensor", {})
                    point_unit_id = point.get("unit_id")
                    
                    # Consolidar parámetros de este punto
                    point_params = []
                    for mode in point.get("proc_modes", []):
                        mode_tag = mode.get("tag", "unknown")
                        mode_integrate_sp = mode.get("integrate_sp", 0)
                        params = mode.get("params", [])
                        
                        for param in params:
                            # Incluir campos esenciales de forma compacta
                            param_compact = {
                                "id": param.get("id"),
                                "tag": param.get("tag"),
                                "name": param.get("name"),
                                "path": param.get("path"),
                                "type": param.get("type"),
                                "integrate": param.get("integrate"),
                                "detector": param.get("detector"),
                                "spectral_bands": param.get("spectral_bands", []),
                                "alarms": param.get("alarms", []),
                                "unit_id": param.get("unit_id"),
                                "custom_unit_id": param.get("custom_unit_id"),
                                "proc_mode": mode_tag,
                                "proc_mode_integrate_sp": mode_integrate_sp,
                            }
                            point_params.append(param_compact)
                    
                    if point_params:
                        all_points_params.append({
                            "point": point_tag,
                            "point_unit_id": point_unit_id,
                            "sensor": sensor_info,
                            "params": point_params,
                        })
                
                # Dividir en grupos de máximo 3 puntos para no sobrecargar
                if all_points_params:
                    batch_size = 3
                    for batch_idx in range(0, len(all_points_params), batch_size):
                        batch = all_points_params[batch_idx:batch_idx + batch_size]
                        point_tags = [p["point"] for p in batch]
                        
                        chunks.append(
                            ConfigChunk(
                                chunk_id=f"{config_uid}:params_{machine_tag}_batch{batch_idx // batch_size}",
                                chunk_type="calculated_params",
                                content={
                                    "machine": machine_tag,
                                    "points_data": batch,
                                },
                                description=(
                                    f"Parámetros de {machine_tag}: "
                                    f"{', '.join(point_tags[:2])}"
                                    f"{' y más' if len(point_tags) > 2 else ''}"
                                ),
                                config_uid=config_uid,
                            )
                        )

        # Fragmento 5: Estados operativos
        if "machines" in config_data:
            for machine in config_data["machines"]:
                machine_tag = machine.get("tag", "unknown")
                states = machine.get("states", [])

                if states:
                    chunks.append(
                        ConfigChunk(
                            chunk_id=f"{config_uid}:states_{machine_tag}",
                            chunk_type="operational_states",
                            content={"machine": machine_tag, "states": states},
                            description=f"Estados operativos de {machine_tag}",
                            config_uid=config_uid,
                        )
                    )

        # Fragmento 6: Estrategias de almacenamiento
        if "machines" in config_data:
            for machine in config_data["machines"]:
                machine_tag = machine.get("tag", "unknown")
                strategies = machine.get("strategies", [])

                if strategies:
                    chunks.append(
                        ConfigChunk(
                            chunk_id=f"{config_uid}:strategies_{machine_tag}",
                            chunk_type="storage_strategies",
                            content={"machine": machine_tag, "strategies": strategies},
                            description=(
                                f"Estrategias de almacenamiento de {machine_tag}"
                            ),
                            config_uid=config_uid,
                        )
                    )

        # Fragmento 7: Propiedades y unidades (sistema)
        system_info = {}
        if "properties" in config_data:
            system_info["properties"] = config_data["properties"]
        if "units" in config_data:
            system_info["units"] = config_data["units"]

        if system_info:
            chunks.append(
                ConfigChunk(
                    chunk_id=f"{config_uid}:system_info",
                    chunk_type="system_properties",
                    content=system_info,
                    description="Propiedades y unidades del sistema",
                    config_uid=config_uid,
                )
            )

        return chunks

    @staticmethod
    def get_chunk_summary(chunk: ConfigChunk) -> str:
        """
        Genera un resumen textual del fragmento.

        Args:
            chunk: Fragmento a resumir

        Returns:
            Resumen en texto
        """
        summary = f"**{chunk.description}**\n"
        summary += f"Tipo: {chunk.chunk_type}\n"

        if chunk.chunk_type == "machines_summary":
            machines = chunk.content
            summary += f"Total de máquinas: {len(machines)}\n"
            for m in machines:
                summary += (
                    f"  - {m['tag']}: {m['num_points']} puntos, "
                    f"{m['num_states']} estados, {m['num_strategies']} estrategias\n"
                )

        elif chunk.chunk_type == "measurement_points":
            points = chunk.content.get("points", [])
            summary += f"Total de puntos: {len(points)}\n"
            for p in points:
                summary += (
                    f"  - {p['tag']}: {p.get('desc', 'N/A')} "
                    f"({len(p.get('proc_mode_tags', []))} modos)\n"
                )

        elif chunk.chunk_type == "processing_modes":
            modes = chunk.content.get("proc_modes", [])
            summary += f"Total de modos: {len(modes)}\n"
            for m in modes:
                summary += (
                    f"  - {m['tag']}: {m.get('min_freq', 0)}-"
                    f"{m.get('max_freq', 0)} Hz "
                    f"({m.get('num_params', 0)} parámetros)\n"
                )

        elif chunk.chunk_type == "calculated_params":
            # Resumen compacto de parámetros por puntos
            points_data = chunk.content.get("points_data", [])
            summary += f"Puntos: {len(points_data)}\n"
            
            for point_data in points_data:
                point = point_data.get("point", "N/A")
                params = point_data.get("params", [])
                sensor = point_data.get("sensor", {})
                sensor_unit = sensor.get("unit_id", "N/A")
                
                summary += f"  - {point} (sensor unit={sensor_unit}): {len(params)} parámetros"
                
                # Contar alarmas totales
                total_alarms = sum(len(p.get('alarms', [])) for p in params)
                if total_alarms > 0:
                    summary += f", {total_alarms} alarmas"
                summary += "\n"

        elif chunk.chunk_type == "operational_states":
            states = chunk.content.get("states", [])
            summary += f"Total de estados: {len(states)}\n"
            for s in states:
                summary += f"  - {s.get('name', 'N/A')}: {s.get('condition', 'N/A')}\n"

        elif chunk.chunk_type == "storage_strategies":
            strategies = chunk.content.get("strategies", [])
            summary += f"Total de estrategias: {len(strategies)}\n"
            for s in strategies:
                summary += f"  - {s.get('name', 'N/A')}: {s.get('cron_line', 'N/A')}\n"

        elif chunk.chunk_type == "system_properties":
            props = chunk.content.get("properties", [])
            units = chunk.content.get("units", [])
            summary += f"Propiedades: {len(props)}, Unidades: {len(units)}\n"

        return summary
