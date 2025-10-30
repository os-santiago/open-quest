const loadLeaderboard = require("./leaderboard");

function toNumber(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : 0;
}

function toDate(value) {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? null : date;
}

module.exports = async function () {
  const leaderboard = await loadLeaderboard();
  const jugadores = Array.isArray(leaderboard.jugadores)
    ? leaderboard.jugadores
    : [];

  const totalJugadores = jugadores.length;
  const totalXp = jugadores.reduce((acc, jugador) => acc + toNumber(jugador.xp), 0);
  const totalMisiones = jugadores.reduce(
    (acc, jugador) => acc + toNumber(jugador.misiones),
    0
  );

  const topXp = [...jugadores]
    .filter((jugador) => toNumber(jugador.xp) > 0)
    .sort((a, b) => toNumber(b.xp) - toNumber(a.xp))
    .slice(0, 5)
    .map((jugador) => ({
      usuario: jugador.usuario,
      nombre: jugador.nombre,
      clase: jugador.clase || "Sin clase",
      nivel: toNumber(jugador.nivel) || null,
      misiones: toNumber(jugador.misiones),
      xp: toNumber(jugador.xp)
    }));

  const topMisiones = [...jugadores]
    .filter((jugador) => toNumber(jugador.misiones) > 0)
    .sort((a, b) => toNumber(b.misiones) - toNumber(a.misiones))
    .slice(0, 5)
    .map((jugador) => ({
      usuario: jugador.usuario,
      nombre: jugador.nombre,
      clase: jugador.clase || "Sin clase",
      nivel: toNumber(jugador.nivel) || null,
      misiones: toNumber(jugador.misiones),
      xp: toNumber(jugador.xp)
    }));

  const classMap = new Map();
  for (const jugador of jugadores) {
    const clase = jugador.clase || "Sin clase";
    const stats = classMap.get(clase) || {
      nombre: clase,
      participantes: 0,
      totalXp: 0,
      totalMisiones: 0
    };

    stats.participantes += 1;
    stats.totalXp += toNumber(jugador.xp);
    stats.totalMisiones += toNumber(jugador.misiones);
    classMap.set(clase, stats);
  }

  const classBreakdown = Array.from(classMap.values())
    .map((claseStats) => ({
      ...claseStats,
      xpPromedio:
        claseStats.participantes > 0
          ? claseStats.totalXp / claseStats.participantes
          : 0,
      misionesPromedio:
        claseStats.participantes > 0
          ? claseStats.totalMisiones / claseStats.participantes
          : 0
    }))
    .sort((a, b) => b.totalXp - a.totalXp);

  const totalXpClases = classBreakdown.reduce(
    (acc, claseStats) => acc + claseStats.totalXp,
    0
  );

  for (const claseStats of classBreakdown) {
    claseStats.participacionXp = totalXpClases
      ? (claseStats.totalXp / totalXpClases) * 100
      : 0;
  }

  const rankMap = new Map();
  for (const jugador of jugadores) {
    const rank = jugador.rango || "Sin rango";
    const stats = rankMap.get(rank) || { nombre: rank, participantes: 0 };
    stats.participantes += 1;
    rankMap.set(rank, stats);
  }

  const rankDistribution = Array.from(rankMap.values()).sort(
    (a, b) => b.participantes - a.participantes
  );

  const latestMissions = [];
  for (const jugador of jugadores) {
    const ultimaMisionDate = toDate(jugador.ultima_mision);
    if (!ultimaMisionDate) {
      continue;
    }

    latestMissions.push({
      usuario: jugador.usuario,
      nombre: jugador.nombre,
      clase: jugador.clase || "Sin clase",
      ultimaMisionISO: ultimaMisionDate.toISOString(),
      ultimaMisionLabel: new Intl.DateTimeFormat("es-CL", {
        dateStyle: "long",
        timeStyle: "short"
      }).format(ultimaMisionDate),
      xp: toNumber(jugador.xp),
      misiones: toNumber(jugador.misiones)
    });
  }

  latestMissions.sort(
    (a, b) => new Date(b.ultimaMisionISO) - new Date(a.ultimaMisionISO)
  );

  latestMissions.splice(6);

  const niveles = jugadores
    .map((jugador) => toNumber(jugador.nivel))
    .filter((nivel) => nivel > 0);

  let nivelMinimo = null;
  let nivelMaximo = null;
  let nivelPromedio = 0;

  if (niveles.length > 0) {
    nivelMinimo = Math.min(...niveles);
    nivelMaximo = Math.max(...niveles);
    nivelPromedio = niveles.reduce((acc, nivel) => acc + nivel, 0) / niveles.length;
  }

  const xpPromedioPorJugador = totalJugadores > 0 ? totalXp / totalJugadores : 0;
  const xpPromedioPorMision = totalMisiones > 0 ? totalXp / totalMisiones : 0;

  return {
    hasData: totalJugadores > 0,
    totalJugadores,
    totalXp,
    totalMisiones,
    xpPromedioPorJugador,
    xpPromedioPorMision,
    topXp,
    topMisiones,
    classBreakdown,
    rankDistribution,
    latestMissions,
    levelStats: {
      promedio: nivelPromedio,
      maximo: nivelMaximo,
      minimo: nivelMinimo,
      jugadoresConNivel: niveles.length
    }
  };
};
