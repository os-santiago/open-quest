# Esquemas de datos de Open Quest

Este directorio centraliza los contratos de datos que utilizarán los workflows de
GitHub Actions y el sitio estático del gremio. Los esquemas están definidos en formato
[JSON Schema](https://json-schema.org/) (versión 2020-12) y describen los artefactos que
se almacenarán en el repositorio `open-quest`.

## Archivos disponibles

- `hoja-de-vida.schema.json`: valida el estado individual de cada aprendiz almacenado en
  `docs/hojas-de-vida/<usuario>.yml`.
- `leaderboard.schema.json`: define la estructura del resumen publicado en
  `docs/data/leaderboard.json` tras cada ciclo de merge.
- `mission-registry.schema.json`: describe el catálogo fuente de misiones para las
  organizaciones `open-quest` y `os-santiago`.

## Uso recomendado

1. Los workflows de revisión y merge deben ejecutar una validación de esquema antes de
   aceptar cambios en los artefactos correspondientes.
2. El sitio estático puede apoyarse en estos archivos para generar tipos o modelos en el
   _frontend_.
3. Cualquier cambio al modelo de datos debe reflejarse primero en estos esquemas para
   mantener sincronizados los pipelines.

## Validación local

Puedes validar un archivo contra su esquema ejecutando:

```bash
npm exec -- jsonschema -i docs/hojas-de-vida/<usuario>.yml docs/schemas/hoja-de-vida.schema.json
```

> _Nota:_ usa `yq -o=json` o `yaml2json` si prefieres validar archivos YAML.
