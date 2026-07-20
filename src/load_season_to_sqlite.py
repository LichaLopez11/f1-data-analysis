"""
Script que recorre todas las carreras de la temporada 2024, carga la sesión de
Race de cada una y extrae las vueltas del piloto VER, guardando todo en la
tabla "laps" de data/f1_data.db (agregando RaceName y RoundNumber para poder
distinguir de qué carrera es cada vuelta).

Si alguna carrera todavía no se corrió (o falla al cargar por otro motivo),
se salta y se sigue con la siguiente.

Uso:
    python src/load_season_to_sqlite.py
"""

import sqlite3

import fastf1
import pandas as pd

# Habilita el cache local para no tener que volver a descargar los datos
# cada vez que corremos el script.
fastf1.Cache.enable_cache("data/cache")

# --- Configuración: cambiá estos valores para explorar otra temporada ---
YEAR = 2024
DRIVER = "VER"
SESSION = "R"                # R = Race

DB_PATH = "data/f1_data.db"
TABLE_NAME = "laps"


def get_race_schedule(year):
    """Devuelve el calendario de carreras de temporada regular (sin testing)."""
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    return schedule[schedule["RoundNumber"] > 0]


def get_fastest_lap_of_race(session):
    """Devuelve la vuelta más rápida (en segundos) de toda la sesión, entre
    todos los pilotos, considerando solo vueltas rápidas (pick_quicklaps())."""
    all_quicklaps = session.laps.pick_quicklaps()
    return all_quicklaps["LapTime"].min().total_seconds()


def build_driver_laps(session, race_name, round_number, driver):
    """Arma el DataFrame de vueltas de un piloto agregando RaceName, RoundNumber
    y FastestLapOfRace (la vuelta más rápida de la carrera, de cualquier piloto)."""
    laps = session.laps.pick_drivers(driver).pick_quicklaps()[
        ["Driver", "LapNumber", "LapTime", "Compound", "Stint"]
    ].copy()
    laps["LapTime"] = laps["LapTime"].dt.total_seconds()
    laps["RaceName"] = race_name
    laps["RoundNumber"] = round_number
    laps["FastestLapOfRace"] = get_fastest_lap_of_race(session)
    return laps


def load_season_laps(year, driver):
    """Recorre todas las carreras de la temporada y junta las vueltas del piloto."""
    schedule = get_race_schedule(year)

    all_laps = []
    for _, event in schedule.iterrows():
        race_name = event["EventName"]
        round_number = event["RoundNumber"]

        print(f"\nCargando carrera: Ronda {int(round_number)} - {race_name}...")
        try:
            session = fastf1.get_session(year, round_number, SESSION)
            session.load()
        except Exception as error:
            print(f"  No se pudo cargar {race_name} ({error}). Sigo con la siguiente.")
            continue

        laps = build_driver_laps(session, race_name, round_number, driver)
        all_laps.append(laps)
        print(f"  {len(laps)} vueltas de {driver} cargadas.")

    return all_laps


def run_average_lap_time_query(conn):
    print(f"\nTiempo de vuelta promedio de {DRIVER} por carrera:")
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT RoundNumber, RaceName, AVG(LapTime) AS avg_lap_time
        FROM {TABLE_NAME}
        WHERE Driver = ? AND LapTime IS NOT NULL
        GROUP BY RoundNumber, RaceName
        ORDER BY RoundNumber ASC
        """,
        (DRIVER,),
    )
    for round_number, race_name, avg_lap_time in cursor.fetchall():
        print(f"  Ronda {int(round_number)} - {race_name}: {avg_lap_time:.3f}s")


def main():
    all_laps = load_season_laps(YEAR, DRIVER)

    if not all_laps:
        print("\nNo se pudo cargar ninguna carrera de la temporada.")
        return

    season_laps = pd.concat(all_laps, ignore_index=True)

    print(f"\nGuardando {len(season_laps)} vueltas en {DB_PATH} (tabla '{TABLE_NAME}')...")
    conn = sqlite3.connect(DB_PATH)
    season_laps.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

    run_average_lap_time_query(conn)

    conn.close()


if __name__ == "__main__":
    main()
