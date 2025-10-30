#!/usr/bin/env python3
"""Generate aggregated mission metrics and update player profiles.

This script is executed by the `mission-merge.yml` workflow. It scans the
`docs/hojas-de-vida` directory for player profiles, updates derived fields
(`xp_total`, `arcanum_actual`, `resumen`) and produces consolidated artifacts
inside `docs/data`.

Outputs:
* docs/data/leaderboard.json: leaderboard artifact consumed by future stages.
* mission-merge-summary.md: human readable summary for workflow logs/artifacts.
"""
from __future__ import annotations

import json
import sys
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = ROOT / "docs" / "hojas-de-vida"
DATA_DIR = ROOT / "docs" / "data"
LEADERBOARD_PATH = DATA_DIR / "leaderboard.json"
SUMMARY_PATH = ROOT / "mission-merge-summary.md"
SEASON_METADATA_PATH = DATA_DIR / "season.json"

RANK_ORDER = ["E", "D", "C", "B", "A", "S", "SS"]


@dataclass
class ProfileMetrics:
    usuario: str
    nombre: Optional[str]
    clase: Optional[str]
    nivel: Optional[str]
    rango: Optional[str]
    xp: int
    arcanum: int
    misiones: int
    ultima_mision: Optional[str]
    xp_por_clase: Dict[str, int]
    misiones_por_rango: Dict[str, int]
    source_path: Path


class MetricsError(RuntimeError):
    """Custom error raised when the script cannot complete."""


def load_yaml(path: Path) -> Dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - defensive guard
        raise MetricsError(f"No se pudo analizar '{path}': {exc}") from exc


def dump_yaml(data: Dict, path: Path) -> None:
    path.write_text(
        yaml.safe_dump(
            data,
            sort_keys=False,
            allow_unicode=True,
            width=120,
            default_flow_style=False,
        ),
        encoding="utf-8",
    )


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def format_date(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.date().isoformat()


def update_profile(path: Path) -> Optional[ProfileMetrics]:
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise MetricsError(f"El archivo '{path}' no contiene un objeto YAML válido.")

    missions: List[Dict] = list(data.get("misiones") or [])
    xp_total = 0
    arcanum_total = 0
    xp_por_clase: Dict[str, int] = defaultdict(int)
    misiones_por_rango: Dict[str, int] = defaultdict(int)
    ultima_mision_dt: Optional[datetime] = None

    for mission in missions:
        xp_mission = int(mission.get("xp", 0) or 0)
        xp_total += xp_mission
        arcanum_total += int(mission.get("arcanum", 0) or 0)

        mission_clase = mission.get("clase")
        if mission_clase:
            xp_por_clase[mission_clase] += xp_mission

        mission_rango = mission.get("rango")
        if mission_rango:
            misiones_por_rango[mission_rango] += 1

        fecha = parse_date(mission.get("fecha"))
        if fecha and (ultima_mision_dt is None or fecha > ultima_mision_dt):
            ultima_mision_dt = fecha

    xp_por_clase = dict(sorted(xp_por_clase.items()))
    misiones_por_rango = {
        rango: misiones_por_rango[rango]
        for rango in RANK_ORDER
        if misiones_por_rango.get(rango)
    }

    niveles_desbloqueados = list(misiones_por_rango.keys())

    resumen: Dict[str, object] = OrderedDict()
    resumen["total_misiones"] = len(missions)
    if ultima_mision_dt:
        resumen["ultima_mision"] = format_date(ultima_mision_dt)
    resumen["xp_por_clase"] = xp_por_clase
    if niveles_desbloqueados:
        resumen["niveles_desbloqueados"] = niveles_desbloqueados

    ordered = OrderedDict()
    for key in (
        "usuario",
        "nombre",
        "nivel",
        "clase",
        "rango_actual",
        "xp_total",
        "arcanum_actual",
        "insignias",
        "misiones",
        "resumen",
    ):
        if key == "xp_total":
            ordered[key] = xp_total
        elif key == "arcanum_actual":
            if arcanum_total or "arcanum_actual" in data:
                ordered[key] = arcanum_total
        elif key == "insignias":
            ordered[key] = data.get(key) or []
        elif key == "misiones":
            ordered[key] = missions
        elif key == "resumen":
            ordered[key] = resumen
        else:
            if key in data:
                ordered[key] = data[key]

    dump_yaml(ordered, path)

    return ProfileMetrics(
        usuario=ordered.get("usuario"),
        nombre=ordered.get("nombre"),
        clase=ordered.get("clase"),
        nivel=ordered.get("nivel"),
        rango=ordered.get("rango_actual"),
        xp=xp_total,
        arcanum=ordered.get("arcanum_actual", 0),
        misiones=len(missions),
        ultima_mision=resumen.get("ultima_mision"),
        xp_por_clase=xp_por_clase,
        misiones_por_rango=misiones_por_rango,
        source_path=path,
    )


def load_season_metadata() -> Dict[str, object]:
    if not SEASON_METADATA_PATH.exists():
        return {
            "id": "0000Q0",
            "titulo": "Temporada por definir",
            "descripcion": "Configura docs/data/season.json para personalizar este valor.",
        }
    try:
        return json.loads(SEASON_METADATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MetricsError(
            f"El archivo de temporada '{SEASON_METADATA_PATH}' no es JSON válido: {exc}"
        ) from exc


def build_leaderboard(profiles: List[ProfileMetrics]) -> Dict[str, object]:
    temporada = load_season_metadata()

    sorted_profiles = sorted(
        profiles,
        key=lambda p: (p.xp, parse_date(p.ultima_mision) or datetime.min),
        reverse=True,
    )

    jugadores = []
    total_xp = 0
    total_misiones = 0
    clases_activas = set()

    for idx, profile in enumerate(sorted_profiles, start=1):
        total_xp += profile.xp
        total_misiones += profile.misiones
        if profile.clase:
            clases_activas.add(profile.clase)
        jugador = {
            "posicion": idx,
            "usuario": profile.usuario,
            "nivel": profile.nivel,
            "xp": profile.xp,
            "misiones": profile.misiones,
            "arcanum": profile.arcanum,
            "estadisticas": {
                "xp_por_clase": profile.xp_por_clase,
                "misiones_por_rango": profile.misiones_por_rango,
            },
        }

        if profile.nombre is not None:
            jugador["nombre"] = profile.nombre
        if profile.clase is not None:
            jugador["clase"] = profile.clase
        if profile.rango is not None:
            jugador["rango"] = profile.rango
        if profile.ultima_mision is not None:
            jugador["ultima_mision"] = profile.ultima_mision

        jugadores.append(jugador)

    participantes = len(jugadores)
    xp_promedio = float(total_xp) / participantes if participantes else 0.0

    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    return {
        "generated_at": generated_at,
        "temporada": temporada,
        "jugadores": jugadores,
        "resumen_global": {
            "total_participantes": participantes,
            "xp_promedio": round(xp_promedio, 2),
            "misiones_completadas": total_misiones,
            "clases_activas": sorted(clases_activas),
        },
    }


def write_leaderboard(leaderboard: Dict[str, object]) -> None:
    ensure_data_dir()
    LEADERBOARD_PATH.write_text(
        json.dumps(leaderboard, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_summary(profiles: List[ProfileMetrics], leaderboard: Dict[str, object]) -> None:
    lines = ["### Resumen de Mission Merge"]
    lines.append(f"Generado en: {leaderboard['generated_at']}")
    lines.append("")
    lines.append(f"Participantes procesados: {len(profiles)}")
    lines.append(
        "XP total acumulada: "
        f"{sum(profile.xp for profile in profiles)}"
    )
    lines.append(
        "Misiones registradas: "
        f"{sum(profile.misiones for profile in profiles)}"
    )
    if profiles:
        lines.append("")
        lines.append("Top 3 jugadores:")
        for jugador in leaderboard["jugadores"][:3]:
            lines.append(
                f"- {jugador['posicion']}. {jugador['usuario']} – {jugador['xp']} XP"
            )
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_data_dir()

    if not PROFILES_DIR.exists():
        raise MetricsError(
            "No se encontró el directorio de hojas de vida. Ejecuta la etapa 1 del plan."
        )

    profiles: List[ProfileMetrics] = []

    profile_paths = [
        path
        for path in PROFILES_DIR.iterdir()
        if path.suffix.lower() in {".yml", ".yaml"}
    ]

    for path in sorted(profile_paths):
        if path.name.upper() in {"TEMPLATE.YML", "TEMPLATE.YAML"}:
            continue
        profile_metrics = update_profile(path)
        if profile_metrics and profile_metrics.usuario:
            profiles.append(profile_metrics)

    leaderboard = build_leaderboard(profiles)
    write_leaderboard(leaderboard)
    write_summary(profiles, leaderboard)

    print(f"Perfiles procesados: {len(profiles)}")
    print(f"Leaderboard generado en: {LEADERBOARD_PATH}")


if __name__ == "__main__":
    try:
        main()
    except MetricsError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
