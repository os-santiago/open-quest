# Sistema de Revisión y Publicación Automatizada

Este documento detalla el diseño del sistema que centraliza la revisión de misiones,
la validación de repositorios y _pull requests_, y la publicación de resultados en GitHub
Pages para el gremio Open Quest y la comunidad de os-santiago.

## Objetivos del sistema

- Estandarizar el flujo de revisión de misiones enviadas mediante repositorios Git.
- Automatizar la verificación de calidad, el cálculo de experiencia y las métricas
de desempeño.
- Mantener actualizado el historial individual de cada integrante a través del mismo
  repositorio Git.
- Publicar los tableros de resultados y el _leaderboard_ comunitario en GitHub Pages
  sin intervención manual.

## Componentes principales

| Componente | Descripción |
|------------|-------------|
| Repositorios de misión | Cada misión vive en un repositorio dentro de la organización `open-quest`. Las ramas `main` alojan entregas aceptadas; las ramas de características contienen el trabajo en curso. |
| GitHub Actions | Conjunto de _workflows_ que validan el código, calculan experiencia, generan artefactos (hojas de vida) y publican los datos consolidados. |
| GitHub Pages (os-santiago) | Sitio que muestra los tableros del gremio y la comunidad, alojado en el repositorio [`os-santiago/os-santiago.github.io`](https://github.com/os-santiago/os-santiago.github.io) y alimentado por artefactos generados por los _workflows_. |
| Almacenamiento de metadatos | Directorio `docs/hojas-de-vida/` en el repositorio central con archivos YAML/JSON por usuario, gestionado automáticamente. |

## Flujo de revisión de misiones

1. **Creación de rama de misión**: el aprendiz clona el repositorio base de la misión
y crea una rama `mission/<id>/<usuario>`.
2. **Trabajo y _commit_**: los cambios se guardan de forma incremental; los mensajes de
   _commit_ incluyen referencias a la misión.
3. **Pull request (PR)**: al abrir el PR se ejecutan _workflows_ de validación estática,
   pruebas automatizadas y verificación de convenciones (linters, pruebas unitarias,
   escaneo de seguridad cuando aplique).
4. **Revisión del gremio**: revisores designados comentan y aprueban los PR. Una vez
   aprobado, se invoca un _workflow_ de _merge_ que actualiza métricas y experiencia.
5. **Actualización de historial**: tras el _merge_, el sistema registra la misión en la
   hoja de vida del aprendiz dentro del directorio de metadatos y recalcula sus
   estadísticas acumuladas.

## Workflows de GitHub Actions

### 1. `mission-review.yml`
- **Eventos**: `pull_request`, `pull_request_target`.
- **Tareas**:
  - Instalar dependencias del lenguaje correspondiente.
  - Ejecutar validaciones (`lint`, `test`, `security`).
  - Publicar resultados en comentarios del PR.
  - Emitir una puntuación preliminar de misión.

### 2. `mission-merge.yml`
- **Eventos**: `workflow_call`, `push` en `main`.
- **Tareas**:
  - Confirmar que el PR se fusionó con aprobación mínima requerida.
  - Actualizar el archivo YAML/JSON del aprendiz con la misión completada (puntos,
    recompensas, fecha, enlace al PR).
  - Recalcular métricas globales (XP acumulada, nivel, contribuciones por categoría).
  - Generar un resumen estático (`docs/data/leaderboard.json`) con todos los puntajes.

### 3. `pages-build.yml`
- **Eventos**: `workflow_run` (en éxito de `mission-merge.yml`) y ejecución manual vía
  `workflow_dispatch`.
- **Tareas**:
  - Instalar Node.js 20 y dependencias de Eleventy (`npm ci`).
  - Construir el sitio estático a partir de los artefactos ubicados en `docs/data/`.
  - Publicar el contenido generado en `_site/` dentro del repositorio `os-santiago/os-santiago.github.io`
    utilizando el secreto `OS_SANTIAGO_PAGES_TOKEN`.
  - Actualizar el entorno `os-santiago-pages` con la URL final (`https://os-santiago.github.io/open-quest/`).

## Hojas de vida en Open Quest

- Cada usuario posee un archivo `docs/hojas-de-vida/<usuario>.yml` con la siguiente
  estructura:
  ```yaml
  usuario: <github-username>
  nombre: <nombre completo>
  nivel: <nivel actual>
  xp_total: <experiencia acumulada>
  misiones:
    - id: <mission-id>
      titulo: <título de la misión>
      pr: <url-pr>
      xp: <xp adjudicada>
      recompensas:
        - <recompensa>
      fecha: <ISO8601>
  ```
- Estos archivos se versionan en el mismo repositorio, proporcionando trazabilidad.
- Los _workflows_ son los únicos autorizados para modificar estos archivos; los PR
  provenientes de aprendices no pueden editarlos directamente.

## Leaderboard para os-santiago

- El sitio de GitHub Pages incluirá:
  - **Leaderboard general** con posición, usuario, XP, nivel y cantidad de misiones.
  - **Ranking por gremio**: filtros para comparar subgrupos (backend, frontend, data, etc.).
  - **Historial de misiones recientes** mostrando los PR aprobados más recientes.
- El _frontend_ consumirá `leaderboard.json` y los perfiles individuales para renderizar
  componentes con datos actualizados.
- Se habilitarán _webhooks_ o `workflow_run` para refrescar la caché del sitio cuando
  se publique una nueva versión.

## Seguridad y cumplimiento

- Uso de _secrets_ cifrados en GitHub Actions para tokens de acceso cuando sea necesario
  (por ejemplo, si se consumen APIs externas).
- Activación de protecciones de rama (`required_status_checks`, `required_reviews`).
- Registro de auditoría mediante comentarios automáticos y etiquetas en los PR.
- Copias de seguridad periódicas exportando `docs/data/*.json` al repositorio `open-quest-archive`.

## Plan de implementación incremental

1. Definir esquemas de datos y crear plantillas de hojas de vida.
2. Configurar `mission-review.yml` con validaciones básicas y publicación de resultados.
3. Implementar `mission-merge.yml` con generación de métricas y artefactos.
4. Crear el sitio estático (por ejemplo, con Eleventy) y adaptarlo para consumir los
   artefactos generados.
5. Desplegar `pages-build.yml` y conectar el repositorio de GitHub Pages de os-santiago.
6. Iterar agregando paneles adicionales, métricas avanzadas y visualizaciones.

Con este diseño se garantiza un flujo consistente, auditable y automatizado que impulsa
la colaboración y el seguimiento de progreso dentro de Open Quest.
