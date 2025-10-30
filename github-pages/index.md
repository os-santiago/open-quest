---
layout: page
title: Panel Open Quest
permalink: /
toc: false
comments: false
---
{% assign open_quest = site.data.open_quest %}
{% assign leaderboard = open_quest.leaderboard %}
{% assign analytics = open_quest.analytics %}
{% assign missionSummary = open_quest.missionSummary %}

<section class="card">
  <header>
    <div class="badge">Temporada {{ leaderboard.temporada.id }}</div>
    <h2>{{ leaderboard.temporada.titulo }}</h2>
    {% if leaderboard.temporada.descripcion %}
      <p>{{ leaderboard.temporada.descripcion }}</p>
    {% endif %}
    {% if leaderboard.generated_at %}
      <small>Última generación del leaderboard: {{ leaderboard.generated_at }}</small>
    {% elsif leaderboard.missing %}
      <small>No se encontró <code>docs/data/leaderboard.json</code>. Se mostrará un estado base.</small>
    {% elsif leaderboard.parseError %}
      <small>Error al procesar el leaderboard: {{ leaderboard.parseError }}</small>
    {% endif %}
  </header>

  <div class="summary-grid">
    <div class="summary-card">
      <h3>Participantes</h3>
      <p>{{ analytics.totalJugadores | format_number }}</p>
    </div>
    <div class="summary-card">
      <h3>XP total</h3>
      <p>{{ missionSummary.xpTotalAcumulada | format_number }}</p>
    </div>
    <div class="summary-card">
      <h3>Misiones completadas</h3>
      <p>{{ leaderboard.resumen_global.misiones_completadas | default: analytics.totalMisiones | format_number }}</p>
    </div>
    <div class="summary-card">
      <h3>XP promedio</h3>
      <p>{{ leaderboard.resumen_global.xp_promedio | default: 0 | format_decimal: 1 }}</p>
    </div>
  </div>

  {% assign clases_activas = leaderboard.resumen_global.clases_activas %}
  {% if clases_activas and clases_activas.size > 0 %}
    <div class="badge">Clases activas</div>
    <ul class="list-inline">
      {% for clase in clases_activas %}
        <li>{{ clase }}</li>
      {% endfor %}
    </ul>
  {% endif %}
</section>

{% if analytics.hasData %}
  <section class="card">
    <h2>Indicadores avanzados</h2>
    <div class="highlight-grid">
      <div class="highlight-card">
        <h3>XP promedio por jugador</h3>
        <strong>{{ analytics.xpPromedioPorJugador | format_decimal: 1 }}</strong>
        <small>Basado en {{ analytics.totalJugadores | format_number }} participantes activos.</small>
      </div>
      <div class="highlight-card">
        <h3>XP por misión</h3>
        <strong>{{ analytics.xpPromedioPorMision | format_decimal: 1 }}</strong>
        <small>Relación entre {{ analytics.totalMisiones | format_number }} misiones y la XP total.</small>
      </div>
      <div class="highlight-card">
        <h3>Nivel promedio</h3>
        {% if analytics.levelStats.jugadoresConNivel %}
          <strong>{{ analytics.levelStats.promedio | format_decimal: 1 }}</strong>
          <small>Niveles registrados: {{ analytics.levelStats.jugadoresConNivel | format_number }}.<br>Máximo {{ analytics.levelStats.maximo | format_number }}, mínimo {{ analytics.levelStats.minimo | format_number }}.</small>
        {% else %}
          <strong>—</strong>
          <small>Todavía no hay niveles registrados.</small>
        {% endif %}
      </div>
    </div>
  </section>

  <section class="card">
    <h2>Jugadores destacados</h2>
    <div class="grid grid-2">
      <div>
        <h3>Mayor XP acumulada</h3>
        {% if analytics.topXp.size > 0 %}
          <ol class="metric-list">
            {% for jugador in analytics.topXp %}
              <li class="metric-item">
                <div class="metric-header">
                  <span class="metric-rank">#{{ forloop.index }}</span>
                  <div>
                    <strong>{{ jugador.usuario }}</strong>
                    {% if jugador.nombre %}<br><small>{{ jugador.nombre }}</small>{% endif %}
                  </div>
                  <span class="metric-value">{{ jugador.xp | format_number }} XP</span>
                </div>
                <div class="metric-subtext">
                  <span>{{ jugador.clase }}</span>
                  {% if jugador.nivel %}<span>Nivel {{ jugador.nivel | format_number }}</span>{% endif %}
                  <span>{{ jugador.misiones | format_number }} misiones</span>
                </div>
              </li>
            {% endfor %}
          </ol>
        {% else %}
          <div class="empty-state">Todavía no hay XP registrada en el leaderboard.</div>
        {% endif %}
      </div>
      <div>
        <h3>Más misiones completadas</h3>
        {% if analytics.topMisiones.size > 0 %}
          <ol class="metric-list">
            {% for jugador in analytics.topMisiones %}
              <li class="metric-item">
                <div class="metric-header">
                  <span class="metric-rank">#{{ forloop.index }}</span>
                  <div>
                    <strong>{{ jugador.usuario }}</strong>
                    {% if jugador.nombre %}<br><small>{{ jugador.nombre }}</small>{% endif %}
                  </div>
                  <span class="metric-value">{{ jugador.misiones | format_number }} misiones</span>
                </div>
                <div class="metric-subtext">
                  <span>{{ jugador.clase }}</span>
                  {% if jugador.nivel %}<span>Nivel {{ jugador.nivel | format_number }}</span>{% endif %}
                  <span>{{ jugador.xp | format_number }} XP</span>
                </div>
              </li>
            {% endfor %}
          </ol>
        {% else %}
          <div class="empty-state">Todavía no se han registrado misiones.</div>
        {% endif %}
      </div>
    </div>
  </section>

  <section class="card">
    <h2>Rendimiento por clase</h2>
    {% if analytics.classBreakdown.size > 0 %}
      <ul class="progress-list">
        {% for clase in analytics.classBreakdown %}
          <li>
            <div class="progress-item-header">
              <span><strong>{{ clase.nombre }}</strong></span>
              <span>{{ clase.totalXp | format_number }} XP</span>
            </div>
            <div class="progress-bar">
              <span style="width: {{ clase.participacionXp | percent_value: 1 }}%"></span>
            </div>
            <div class="progress-footer">
              <span>{{ clase.participantes | format_number }} participantes</span>
              <span>XP promedio: {{ clase.xpPromedio | format_decimal: 1 }}</span>
              <span>Misiones promedio: {{ clase.misionesPromedio | format_decimal: 1 }}</span>
            </div>
          </li>
        {% endfor %}
      </ul>
    {% else %}
      <div class="empty-state">No hay clases registradas en el leaderboard.</div>
    {% endif %}
  </section>

  <section class="card">
    <h2>Distribución de rangos</h2>
    {% if analytics.rankDistribution.size > 0 %}
      <ul class="rank-chips">
        {% for rank in analytics.rankDistribution %}
          <li>
            <strong>{{ rank.nombre }}</strong>
            <span>{{ rank.participantes | format_number }}</span>
          </li>
        {% endfor %}
      </ul>
    {% else %}
      <div class="empty-state">Los rangos aparecerán cuando se registren participantes.</div>
    {% endif %}
  </section>

  <section class="card">
    <h2>Misiones más recientes</h2>
    {% if analytics.latestMissions.size > 0 %}
      <ol class="timeline">
        {% for item in analytics.latestMissions %}
          <li class="timeline-item">
            <div>
              <strong>{{ item.usuario }}</strong>
              {% if item.nombre %}<br><small>{{ item.nombre }}</small>{% endif %}
            </div>
            <div class="timeline-meta">
              <span>{{ item.clase }}</span>
              <span>{{ item.misiones | format_number }} misiones</span>
              <span>{{ item.xp | format_number }} XP</span>
              <time datetime="{{ item.ultimaMisionISO }}">{{ item.ultimaMisionLabel }}</time>
            </div>
          </li>
        {% endfor %}
      </ol>
    {% else %}
      <div class="empty-state">Cuando haya actividad reciente, la veremos aquí en forma de línea de tiempo.</div>
    {% endif %}
  </section>
{% endif %}

<section class="card">
  <h2>Actividad reciente</h2>
  {% if missionSummary.generatedAt %}
    <p><strong>mission-merge</strong> generó los artefactos el <time datetime="{{ missionSummary.generatedAt }}">{{ missionSummary.generatedAt | format_spanish_datetime }}</time>.</p>
  {% elsif missionSummary.missing %}
    <p class="empty-state">Todavía no se ha ejecutado <code>mission-merge</code> en este repositorio.</p>
  {% else %}
    <p>Resumen no disponible.</p>
  {% endif %}

  <dl>
    <div>
      <dt>Participantes procesados</dt>
      <dd>{{ missionSummary.participantesProcesados | format_number }}</dd>
    </div>
    <div>
      <dt>XP total acumulada</dt>
      <dd>{{ missionSummary.xpTotalAcumulada | format_number }}</dd>
    </div>
    <div>
      <dt>Misiones registradas</dt>
      <dd>{{ missionSummary.misionesRegistradas | format_number }}</dd>
    </div>
  </dl>
</section>

<section class="card">
  <h2>Leaderboard del gremio</h2>
  {% assign jugadores = leaderboard.jugadores %}
  {% if jugadores and jugadores.size > 0 %}
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th scope="col">Pos</th>
            <th scope="col">Usuario</th>
            <th scope="col">Clase</th>
            <th scope="col">Nivel</th>
            <th scope="col">Rango</th>
            <th scope="col">XP</th>
            <th scope="col">Misiones</th>
            <th scope="col">Última misión</th>
          </tr>
        </thead>
        <tbody>
          {% for jugador in jugadores %}
            <tr>
              <td>{{ jugador.posicion }}</td>
              <td>
                <strong>{{ jugador.usuario }}</strong>
                {% if jugador.nombre %}<br><small>{{ jugador.nombre }}</small>{% endif %}
              </td>
              <td>{{ jugador.clase | default: "-" }}</td>
              <td>
                {% if jugador.nivel %}
                  {{ jugador.nivel | format_number }}
                {% else %}
                  —
                {% endif %}
              </td>
              <td>{{ jugador.rango | default: "-" }}</td>
              <td>{{ jugador.xp | format_number }}</td>
              <td>{{ jugador.misiones | format_number }}</td>
              <td>
                {% if jugador.ultima_mision %}
                  <time datetime="{{ jugador.ultima_mision }}">{{ jugador.ultima_mision | format_spanish_datetime }}</time>
                {% else %}
                  —
                {% endif %}
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  {% else %}
    <div class="empty-state">
      <p>Cuando se registren misiones y participantes, aparecerán aquí sus posiciones.</p>
    </div>
  {% endif %}
</section>
