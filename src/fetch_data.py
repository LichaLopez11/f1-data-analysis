"""
Script inicial: prueba que FastF1 esté bien instalado, baja los datos
de una sesión de carrera y genera un primer gráfico simple comparando
tiempos de vuelta entre dos pilotos.

Uso:
    python src/fetch_data.py
"""

import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt

# Habilita el cache local para no tener que volver a descargar los datos
# cada vez que corremos el script.
fastf1.Cache.enable_cache("data/cache")

# --- Configuración: cambiá estos valores para explorar otras carreras ---
YEAR = 2024
GRAND_PRIX = "Monza"        # Nombre del GP, ej: "Monza", "Spa", "Bahrain"
SESSION = "R"                # R = Race, Q = Qualifying, FP1/FP2/FP3
DRIVER_1 = "VER"
DRIVER_2 = "LEC"


def main():
    print(f"Cargando sesión: {YEAR} {GRAND_PRIX} ({SESSION})...")
    session = fastf1.get_session(YEAR, GRAND_PRIX, SESSION)
    session.load()

    print(f"\nComparando tiempos de vuelta: {DRIVER_1} vs {DRIVER_2}")
    laps_driver_1 = session.laps.pick_drivers(DRIVER_1).pick_quicklaps()
    laps_driver_2 = session.laps.pick_drivers(DRIVER_2).pick_quicklaps()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        laps_driver_1["LapNumber"],
        laps_driver_1["LapTime"].dt.total_seconds(),
        label=DRIVER_1,
    )
    ax.plot(
        laps_driver_2["LapNumber"],
        laps_driver_2["LapTime"].dt.total_seconds(),
        label=DRIVER_2,
    )
    ax.set_xlabel("Vuelta")
    ax.set_ylabel("Tiempo de vuelta (s)")
    ax.set_title(f"{DRIVER_1} vs {DRIVER_2} - {GRAND_PRIX} {YEAR}")
    ax.legend()
    plt.tight_layout()

    output_path = "data/lap_times_comparison.png"
    plt.savefig(output_path)
    print(f"\nGráfico guardado en: {output_path}")


if __name__ == "__main__":
    main()
