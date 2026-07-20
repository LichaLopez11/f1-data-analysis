"""
Script que lee la tabla "laps" de data/f1_data.db (ya cargada con
load_season_to_sqlite.py, vueltas rápidas filtradas con pick_quicklaps()) y
grafica, a lo largo de la temporada 2024:
  1. El tiempo de vuelta promedio de VER por carrera (data/season_pace.png).
  2. El gap promedio de VER respecto a la vuelta más rápida de cada carrera,
     es decir AVG(LapTime) - FastestLapOfRace (data/season_gap.png).

Uso:
    python src/plot_season.py
"""

import sqlite3

import matplotlib.pyplot as plt

DB_PATH = "data/f1_data.db"
TABLE_NAME = "laps"
DRIVER = "VER"

LINE_COLOR = "#2a78d6"
GRID_COLOR = "#e1e0d9"
AXIS_COLOR = "#898781"
TEXT_COLOR = "#0b0b0b"

PACE_OUTPUT_PATH = "data/season_pace.png"
GAP_OUTPUT_PATH = "data/season_gap.png"


def get_season_pace(conn, driver):
    """Devuelve (ronda, nombre de carrera, tiempo promedio) por carrera, ordenado."""
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT RoundNumber, RaceName, AVG(LapTime) AS avg_lap_time
        FROM {TABLE_NAME}
        WHERE Driver = ? AND LapTime IS NOT NULL
        GROUP BY RoundNumber, RaceName
        ORDER BY RoundNumber ASC
        """,
        (driver,),
    )
    return cursor.fetchall()


def get_season_gap(conn, driver):
    """Devuelve (ronda, nombre de carrera, gap promedio) por carrera, ordenado.

    El gap es AVG(LapTime) - FastestLapOfRace: cuánto más lento fue el
    promedio de vueltas de VER respecto a la vuelta más rápida de la carrera
    (de cualquier piloto).
    """
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT
            RoundNumber,
            RaceName,
            AVG(LapTime) - AVG(FastestLapOfRace) AS avg_gap
        FROM {TABLE_NAME}
        WHERE Driver = ? AND LapTime IS NOT NULL
        GROUP BY RoundNumber, RaceName
        ORDER BY RoundNumber ASC
        """,
        (driver,),
    )
    return cursor.fetchall()


def plot_line_by_round(season_data, title, ylabel, output_path):
    """Grafica una serie (ronda, nombre de carrera, valor) como línea a lo
    largo de la temporada y la guarda en output_path."""
    rounds = [row[0] for row in season_data]
    race_names = [row[1] for row in season_data]
    values = [row[2] for row in season_data]

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(
        rounds,
        values,
        color=LINE_COLOR,
        linewidth=2,
        marker="o",
        markersize=8,
        markerfacecolor=LINE_COLOR,
        markeredgecolor="white",
        markeredgewidth=1,
    )

    ax.set_xticks(rounds)
    ax.set_xticklabels(
        [f"{r}. {name}" for r, name in zip(rounds, race_names)],
        rotation=60,
        ha="right",
        color=AXIS_COLOR,
        fontsize=8,
    )
    ax.tick_params(axis="y", colors=AXIS_COLOR)

    ax.set_xlabel("Carrera (RoundNumber)", color=TEXT_COLOR)
    ax.set_ylabel(ylabel, color=TEXT_COLOR)
    ax.set_title(title, color=TEXT_COLOR)

    ax.grid(axis="y", color=GRID_COLOR, linewidth=1)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(AXIS_COLOR)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"\nGráfico guardado en: {output_path}")


def main():
    conn = sqlite3.connect(DB_PATH)
    season_pace = get_season_pace(conn, DRIVER)
    season_gap = get_season_gap(conn, DRIVER)
    conn.close()

    if not season_pace:
        print(f"No hay datos de {DRIVER} en {DB_PATH} (tabla '{TABLE_NAME}').")
        return

    plot_line_by_round(
        season_pace,
        title=f"Ritmo de {DRIVER} a lo largo de la temporada 2024",
        ylabel="Tiempo de vuelta promedio (s)",
        output_path=PACE_OUTPUT_PATH,
    )
    plot_line_by_round(
        season_gap,
        title=f"Gap promedio de {DRIVER} respecto a la vuelta más rápida - Temporada 2024",
        ylabel="Gap promedio (s)",
        output_path=GAP_OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()
