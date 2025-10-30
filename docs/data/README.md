# Artefactos de datos consolidados

Los workflows de Open Quest publicarán en este directorio los artefactos derivados que se
consumirán desde GitHub Pages y otros tableros comunitarios.

## Archivos esperados

- `leaderboard.json`: snapshot ordenado de participantes, validado con
  `../schemas/leaderboard.schema.json`.
- `missions.json`: catálogo derivado de `mission-registry.schema.json` con información de
  disponibilidad y conteos en tiempo real.
- Archivos adicionales (`*.csv`, `*.parquet`) podrán generarse en etapas futuras para
  análisis avanzado.

> Durante la etapa 1 del plan, solo se versionan los esquemas y la plantilla de hoja de
> vida; los artefactos finales serán generados por los workflows en etapas posteriores.
