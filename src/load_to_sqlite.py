"""
Script que carga los tiempos de vuelta de una sesión a una base SQLite
y corre un par de consultas SQL de ejemplo directo contra la base.

Uso:
    python src/load_to_sqlite.py
"""

import sqlite3

import fastf1

# Habilita el cache local para no tener que volver a descargar los datos
# cada vez que corremos el script.
fastf1.Cache.enable_cache("data/cache")

# --- Configuración: cambiá estos valores para explorar otras carreras ---
YEAR = 2024
GRAND_PRIX = "Monza"        # Nombre del GP, ej: "Monza", "Spa", "Bahrain"
SESSION = "R"                # R = Race, Q = Qualifying, FP1/FP2/FP3

DB_PATH = "data/f1_data.db"
TABLE_NAME = "laps"


def build_laps_table(session):
    """Arma el DataFrame de vueltas con las columnas que vamos a persistir."""
    laps = session.laps[["Driver", "LapNumber", "LapTime", "Compound", "Stint"]].copy()
    laps["LapTime"] = laps["LapTime"].dt.total_seconds()
    return laps


def run_example_queries(conn):
    cursor = conn.cursor()

    # Las 5 vueltas más rápidas de toda la carrera: ordenamos por LapTime
    # ascendente (excluyendo vueltas sin tiempo registrado, ej. la de boxes)
    # y nos quedamos con las primeras 5 filas.
    print("\nLas 5 vueltas más rápidas de la carrera:")
    cursor.execute(
        f"""
        SELECT Driver, LapNumber, LapTime
        FROM {TABLE_NAME}
        WHERE LapTime IS NOT NULL
        ORDER BY LapTime ASC
        LIMIT 5
        """
    )
    for driver, lap_number, lap_time in cursor.fetchall():
        print(f"  {driver} - vuelta {int(lap_number)}: {lap_time:.3f}s")

    # Tiempo de vuelta promedio por piloto: agrupamos las filas por Driver
    # y aplicamos AVG() sobre LapTime, ignorando vueltas sin tiempo.
    print("\nTiempo de vuelta promedio por piloto:")
    cursor.execute(
        f"""
        SELECT Driver, AVG(LapTime) AS avg_lap_time
        FROM {TABLE_NAME}
        WHERE LapTime IS NOT NULL
        GROUP BY Driver
        ORDER BY avg_lap_time ASC
        """
    )
    for driver, avg_lap_time in cursor.fetchall():
        print(f"  {driver}: {avg_lap_time:.3f}s")


def main():
    print(f"Cargando sesión: {YEAR} {GRAND_PRIX} ({SESSION})...")
    session = fastf1.get_session(YEAR, GRAND_PRIX, SESSION)
    session.load()

    laps = build_laps_table(session)

    print(f"\nGuardando {len(laps)} vueltas en {DB_PATH} (tabla '{TABLE_NAME}')...")
    conn = sqlite3.connect(DB_PATH)
    laps.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

    run_example_queries(conn)

    conn.close()


if __name__ == "__main__":
    main()
