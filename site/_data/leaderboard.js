const { readFile } = require("node:fs/promises");
const path = require("node:path");

const DEFAULT_LEADERBOARD = {
  generated_at: null,
  temporada: {
    id: "0000Q0",
    titulo: "Temporada no disponible",
    descripcion: "Aún no se ha generado un leaderboard con metadatos de temporada."
  },
  jugadores: [],
  resumen_global: {
    total_participantes: 0,
    xp_promedio: 0,
    misiones_completadas: 0,
    clases_activas: []
  }
};

module.exports = async function () {
  const leaderboardPath = path.resolve("docs/data/leaderboard.json");

  try {
    const fileContents = await readFile(leaderboardPath, "utf-8");
    const parsed = JSON.parse(fileContents);
    return parsed;
  } catch (error) {
    if (error.code === "ENOENT") {
      return { ...DEFAULT_LEADERBOARD, missing: true };
    }

    if (error.name === "SyntaxError") {
      return {
        ...DEFAULT_LEADERBOARD,
        missing: false,
        parseError: error.message
      };
    }

    throw error;
  }
};
