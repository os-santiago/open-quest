# Sitio de GitHub Pages

Este directorio encapsula todo el contenido y la configuración necesarios para
publicar el dashboard de Open Quest en el repositorio
[`os-santiago/os-santiago.github.io`](https://github.com/os-santiago/os-santiago.github.io).

## Estructura

- `Gemfile` / `Gemfile.lock`: dependencias administradas con Bundler.
- `_config.yml`: configuración de Jekyll y del tema Chirpy.
- `_includes/` y `_plugins/`: plantillas y plugins personalizados (incluye la
  carga de artefactos generados por los workflows).
- `assets/`: estilos específicos del dashboard.
- `index.md`: plantilla principal renderizada por Jekyll.

## Comandos útiles

```bash
bundle install
bundle exec jekyll serve
# o
bundle exec jekyll build
```

Los comandos se ejecutan desde este mismo directorio y utilizan los artefactos
publicados en `../docs/data/` y `../mission-merge-summary.md`.
