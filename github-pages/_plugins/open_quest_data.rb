# frozen_string_literal: true

require "json"
require "time"

module OpenQuest
  DEFAULT_LEADERBOARD = {
    "generated_at" => nil,
    "temporada" => {
      "id" => "0000Q0",
      "titulo" => "Temporada no disponible",
      "descripcion" => "Aún no se ha generado un leaderboard con metadatos de temporada."
    },
    "jugadores" => [],
    "resumen_global" => {
      "total_participantes" => 0,
      "xp_promedio" => 0,
      "misiones_completadas" => 0,
      "clases_activas" => []
    }
  }.freeze

  DEFAULT_SUMMARY = {
    "generatedAt" => nil,
    "participantesProcesados" => 0,
    "xpTotalAcumulada" => 0,
    "misionesRegistradas" => 0
  }.freeze

  SUMMARY_KEYS = {
    "Generado en" => "generatedAt",
    "Participantes procesados" => "participantesProcesados",
    "XP total acumulada" => "xpTotalAcumulada",
    "Misiones registradas" => "misionesRegistradas"
  }.freeze

  module Formatting
    module_function

    MONTHS = %w[enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre].freeze

    def to_number(value)
      return nil if value.nil?

      number = Float(value)
      number.nan? ? nil : number
    rescue StandardError
      nil
    end

    def format_integer_part(number)
      digits = number.to_i.to_s
      digits.reverse.chars.each_slice(3).map(&:join).join(".").reverse
    end

    def format_number(value)
      number = to_number(value)
      return "0" if number.nil?

      sign = number.negative? ? "-" : ""
      sign + format_integer_part(number.abs.round)
    end

    def format_decimal(value, digits = 1)
      number = to_number(value)
      return "0" if number.nil?

      digits = digits.to_i
      sign = number.negative? ? "-" : ""
      absolute = number.abs
      if digits.zero?
        return sign + format_integer_part(absolute.round)
      end

      formatted = format("%.#{digits}f", absolute)
      integer_part, decimal_part = formatted.split(".", 2)
      sign + format_integer_part(integer_part.to_i) + "," + decimal_part
    end

    def percent_value(value, digits = 1)
      number = to_number(value)
      return "0" if number.nil?

      format("%.#{digits.to_i}f", number)
    end

    def spanish_datetime(value)
      return "" if value.nil? || value.to_s.strip.empty?

      time = value.is_a?(Time) ? value : Time.parse(value.to_s)
      time = time.getlocal

      month_name = MONTHS[time.month - 1]
      formatted_time = format("%02d:%02d", time.hour, time.min)
      "#{time.day} de #{month_name} de #{time.year}, #{formatted_time}"
    rescue StandardError
      value.to_s
    end
  end

  module Filters
    def format_number(value)
      Formatting.format_number(value)
    end

    def format_decimal(value, digits = 1)
      Formatting.format_decimal(value, digits)
    end

    def format_spanish_datetime(value)
      Formatting.spanish_datetime(value)
    end

    def percent_value(value, digits = 1)
      Formatting.percent_value(value, digits)
    end
  end

  Liquid::Template.register_filter(Filters)

  class DataGenerator < Jekyll::Generator
    safe true
    priority :high

    def generate(site)
      leaderboard = load_leaderboard(site)
      mission_summary = load_mission_summary(site)
      analytics = compute_analytics(leaderboard)

      site.data["open_quest"] = {
        "leaderboard" => leaderboard,
        "missionSummary" => mission_summary,
        "analytics" => analytics
      }
    end

    private

    def load_leaderboard(site)
      path = File.join(repository_root(site), "docs", "data", "leaderboard.json")
      data = read_json(path)

      return DEFAULT_LEADERBOARD.merge("missing" => true) if data.nil?

      deep_merge(DEFAULT_LEADERBOARD, data)
    rescue JSON::ParserError => e
      DEFAULT_LEADERBOARD.merge("parseError" => e.message)
    end

    def load_mission_summary(site)
      path = File.join(repository_root(site), "mission-merge-summary.md")
      return DEFAULT_SUMMARY.merge("missing" => true) unless File.exist?(path)

      summary = DEFAULT_SUMMARY.dup
      File.read(path).each_line do |line|
        label, value = line.split(":", 2)
        next unless value

        key = SUMMARY_KEYS[label&.strip]
        next unless key

        cleaned_value = value.strip
        if %w[participantesProcesados xpTotalAcumulada misionesRegistradas].include?(key)
          summary[key] = cleaned_value.empty? ? 0 : cleaned_value.to_i
        else
          summary[key] = cleaned_value.empty? ? nil : cleaned_value
        end
      end

      summary
    end

    def read_json(path)
      return nil unless File.exist?(path)

      content = File.read(path)
      return nil if content.strip.empty?

      JSON.parse(content)
    end

    def repository_root(site)
      File.expand_path("..", site.source)
    end

    def deep_merge(base, other)
      result = base.dup
      other.each do |key, value|
        if result.key?(key) && result[key].is_a?(Hash) && value.is_a?(Hash)
          result[key] = deep_merge(result[key], value)
        else
          result[key] = value
        end
      end
      result
    end

    def compute_analytics(leaderboard)
      jugadores = leaderboard.fetch("jugadores", [])
      jugadores = [] unless jugadores.is_a?(Array)

      total_jugadores = jugadores.length
      total_xp = jugadores.sum { |jugador| numeric_value(jugador["xp"]) }
      total_misiones = jugadores.sum { |jugador| numeric_value(jugador["misiones"]) }

      top_xp = jugadores
                .select { |jugador| numeric_value(jugador["xp"]) > 0 }
                .sort_by { |jugador| -numeric_value(jugador["xp"]) }
                .first(5)
                .map { |jugador| sanitize_player_summary(jugador) }

      top_misiones = jugadores
                      .select { |jugador| numeric_value(jugador["misiones"]) > 0 }
                      .sort_by { |jugador| -numeric_value(jugador["misiones"]) }
                      .first(5)
                      .map { |jugador| sanitize_player_summary(jugador) }

      class_map = Hash.new { |hash, key| hash[key] = { "nombre" => key, "participantes" => 0, "totalXp" => 0.0, "totalMisiones" => 0.0 } }

      jugadores.each do |jugador|
        clase = jugador["clase"].to_s.strip
        clase = "Sin clase" if clase.empty?
        stats = class_map[clase]
        stats["participantes"] += 1
        stats["totalXp"] += numeric_value(jugador["xp"])
        stats["totalMisiones"] += numeric_value(jugador["misiones"])
      end

      class_breakdown = class_map.values.map do |stats|
        participantes = stats["participantes"]
        xp_promedio = participantes.positive? ? stats["totalXp"] / participantes : 0
        misiones_promedio = participantes.positive? ? stats["totalMisiones"] / participantes : 0

        stats.merge(
          "xpPromedio" => xp_promedio,
          "misionesPromedio" => misiones_promedio
        )
      end.sort_by { |stats| -stats["totalXp"] }

      total_xp_clases = class_breakdown.sum { |stats| stats["totalXp"] }
      class_breakdown.each do |stats|
        stats["participacionXp"] = total_xp_clases.positive? ? (stats["totalXp"] / total_xp_clases) * 100 : 0
      end

      rank_map = Hash.new { |hash, key| hash[key] = { "nombre" => key, "participantes" => 0 } }
      jugadores.each do |jugador|
        rank = jugador["rango"].to_s.strip
        rank = "Sin rango" if rank.empty?
        rank_map[rank]["participantes"] += 1
      end
      rank_distribution = rank_map.values.sort_by { |stats| -stats["participantes"] }

      latest_missions = jugadores.filter_map do |jugador|
        timestamp = jugador["ultima_mision"] || jugador["ultimaMision"]
        time = parse_time(timestamp)
        next unless time

        {
          "usuario" => jugador["usuario"],
          "nombre" => jugador["nombre"],
          "clase" => jugador["clase"].to_s.empty? ? "Sin clase" : jugador["clase"],
          "ultimaMisionISO" => time.iso8601,
          "ultimaMisionLabel" => Formatting.spanish_datetime(time),
          "xp" => numeric_value(jugador["xp"]),
          "misiones" => numeric_value(jugador["misiones"])
        }
      end

      latest_missions.sort_by! { |item| item["ultimaMisionISO"] }
      latest_missions.reverse!
      latest_missions.slice!(6, latest_missions.length)

      niveles = jugadores.map { |jugador| numeric_value(jugador["nivel"]) }.select { |nivel| nivel.positive? }
      nivel_promedio = niveles.empty? ? 0 : niveles.sum / niveles.length

      {
        "hasData" => total_jugadores.positive?,
        "totalJugadores" => total_jugadores,
        "totalXp" => total_xp,
        "totalMisiones" => total_misiones,
        "xpPromedioPorJugador" => total_jugadores.positive? ? total_xp / total_jugadores : 0,
        "xpPromedioPorMision" => total_misiones.positive? ? total_xp / total_misiones : 0,
        "topXp" => top_xp,
        "topMisiones" => top_misiones,
        "classBreakdown" => class_breakdown,
        "rankDistribution" => rank_distribution,
        "latestMissions" => latest_missions,
        "levelStats" => {
          "promedio" => nivel_promedio,
          "maximo" => niveles.max || 0,
          "minimo" => niveles.min || 0,
          "jugadoresConNivel" => niveles.length
        }
      }
    end

    def numeric_value(value)
      Formatting.to_number(value) || 0.0
    end

    def sanitize_player_summary(jugador)
      {
        "usuario" => jugador["usuario"],
        "nombre" => jugador["nombre"],
        "clase" => jugador["clase"].to_s.empty? ? "Sin clase" : jugador["clase"],
        "nivel" => numeric_value(jugador["nivel"]).positive? ? numeric_value(jugador["nivel"]) : nil,
        "misiones" => numeric_value(jugador["misiones"]),
        "xp" => numeric_value(jugador["xp"])
      }
    end

    def parse_time(value)
      return nil if value.nil? || value.to_s.strip.empty?

      Time.parse(value.to_s)
    rescue StandardError
      nil
    end
  end
end
