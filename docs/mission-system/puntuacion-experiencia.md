# Puntuación y Experiencia

## Factores cuantificables por misión

| Factor medible                           | Fórmula o peso sugerido                           |
|------------------------------------------|---------------------------------------------------|
| Líneas netas (añadidas + modificadas)    | `XP_lineas = √(líneas_net / 5) * 20`               |
| Referencias actualizadas                 | `XP_refs = refs_actualizadas * 15`                |
| Commits validados                        | `XP_commits = commits * 25`                       |
| Pull requests aceptados                  | `XP_pr = pr * 60`                                 |
| Casos de prueba o validaciones nuevas    | `XP_tests = tests_nuevos * 30`                    |
| Revisiones útiles realizadas             | `XP_reviews = reviews_útiles * 40`                |

### Multiplicadores por nivel de misión

| Nivel | Multiplicador XP |
|-------|------------------|
| F     | 0.8              |
| E     | 0.9              |
| D     | 1.0              |
| C     | 1.1              |
| B     | 1.25             |
| A     | 1.45             |
| S     | 1.7              |
| SS    | 2.0              |
| SSS   | 2.4              |
| Z     | 3.0              |

**XP total de la misión** = `(XP_lineas + XP_refs + XP_commits + XP_pr + XP_tests + XP_reviews) * mult_nivel`.

Ajustes adicionales:

- Bonificación del 10 % para misiones con documentación exhaustiva.
- Penalización del 20 % si la revisión detecta faltantes (la penalización se elimina tras corregir). 

## Curva de experiencia personal

La experiencia acumulada determina el nivel del integrante del gremio. La progresión es parabólica
y combina un incremento fijo, un porcentaje sobre el nivel anterior y una ponderación exponencial.

- Requisito para nivel 1: 800 XP (`(0 + 500) * 1.6`).
- Fórmula general: `XP_n = XP_{n-1} + 500 * 1.6^(n-1) + 0.12 * XP_{n-1}`.

### Ejemplo de niveles iniciales

| Nivel | XP total acumulado requerido |
|-------|------------------------------|
| 1     | 800                          |
| 2     | 1 952                        |
| 3     | 3 539                        |
| 4     | 5 893                        |
| 5     | 9 449                        |
| 6     | 14 821                       |
| 7     | 22 814                       |
| 8     | 34 669                       |
| 9     | 52 174                       |
| 10    | 78 702                       |
| 11    | 119 903                      |
| 12    | 183 225                      |

La curva proyecta millones de puntos de experiencia para niveles 40 y superiores, asegurando un
camino desafiante y atractivo durante al menos diez años.
