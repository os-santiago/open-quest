const { readFile } = require("node:fs/promises");
const path = require("node:path");

const DEFAULT_SUMMARY = {
  generatedAt: null,
  participantesProcesados: 0,
  xpTotalAcumulada: 0,
  misionesRegistradas: 0
};

const SUMMARY_KEYS = {
  "Generado en": "generatedAt",
  "Participantes procesados": "participantesProcesados",
  "XP total acumulada": "xpTotalAcumulada",
  "Misiones registradas": "misionesRegistradas"
};

const NUMERIC_FIELDS = new Set([
  "participantesProcesados",
  "xpTotalAcumulada",
  "misionesRegistradas"
]);

module.exports = async function () {
  const summaryPath = path.resolve("mission-merge-summary.md");

  try {
    const raw = await readFile(summaryPath, "utf-8");
    const lines = raw.split(/\r?\n/);
    const summary = { ...DEFAULT_SUMMARY };

    for (const line of lines) {
      const [label, ...rest] = line.split(":");
      if (!label || rest.length === 0) {
        continue;
      }

      const key = SUMMARY_KEYS[label.trim()];
      if (!key) {
        continue;
      }

      const value = rest.join(":").trim();
      if (key === "generatedAt") {
        summary[key] = value || DEFAULT_SUMMARY[key];
        continue;
      }

      if (NUMERIC_FIELDS.has(key)) {
        const numericValue = Number(value);
        summary[key] = Number.isFinite(numericValue)
          ? numericValue
          : DEFAULT_SUMMARY[key];
        continue;
      }

      summary[key] = value;
    }

    return summary;
  } catch (error) {
    if (error.code === "ENOENT") {
      return { ...DEFAULT_SUMMARY, missing: true };
    }

    throw error;
  }
};
