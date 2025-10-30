# Hojas de vida del gremio Open Quest

Este directorio almacenará los perfiles generados automáticamente por los workflows de
GitHub Actions. Cada archivo YAML debe cumplir con el esquema descrito en
`../schemas/hoja-de-vida.schema.json`.

## Reglas generales

- El nombre del archivo corresponde al usuario de GitHub (`<usuario>.yml`).
- Las misiones se ordenan de la más reciente a la más antigua.
- Solo los workflows de automatización pueden editar estos archivos; los aprendices deben
  proponer cambios mediante misiones y PRs.

## Uso de la plantilla

1. Copia `TEMPLATE.yml` a un nuevo archivo con tu nombre de usuario.
2. Ajusta los campos básicos (`usuario`, `nombre`, `nivel`, `clase`, `rango_actual`).
3. No elimines la sección `resumen`; será recalculada por los workflows.

Ejemplo rápido:

```bash
cp docs/hojas-de-vida/TEMPLATE.yml docs/hojas-de-vida/octavius.yml
```
