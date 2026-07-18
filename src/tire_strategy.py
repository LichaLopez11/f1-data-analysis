"""
Script que analiza la estrategia de neumáticos de una sesión: resume los
stints de cada piloto (compuesto, vuelta de inicio y fin) y genera un
gráfico de barras horizontales tipo "strategy chart".

Uso:
    python src/tire_strategy.py
"""

import fastf1
import matplotlib.pyplot as plt

# Habilita el cache local para no tener que volver a descargar los datos
# cada vez que corremos el script.
fastf1.Cache.enable_cache("data/cache")

# --- Configuración: cambiá estos valores para explorar otras carreras ---
YEAR = 2024
GRAND_PRIX = "Monza"        # Nombre del GP, ej: "Monza", "Spa", "Bahrain"
SESSION = "R"                # R = Race, Q = Qualifying, FP1/FP2/FP3
DRIVERS = ["VER", "LEC"]

COMPOUND_COLORS = {
    "SOFT": "#DA291C",
    "MEDIUM": "#FFD12E",
    "HARD": "#F0F0F0",
    "INTERMEDIATE": "#43B02A",
    "WET": "#0067AD",
}


def get_driver_stints(session, driver):
    """Devuelve un resumen de stints (compuesto, vuelta inicio/fin) de un piloto."""
    driver_laps = session.laps.pick_drivers(driver)
    stints = driver_laps.groupby("Stint").agg(
        Compound=("Compound", "first"),
        LapStart=("LapNumber", "min"),
        LapEnd=("LapNumber", "max"),
    )
    return stints


def print_stint_summary(driver, stints):
    print(f"\nStints de {driver}:")
    for stint_number, row in stints.iterrows():
        print(
            f"  Stint {int(stint_number)}: {row['Compound']} "
            f"(vueltas {int(row['LapStart'])}-{int(row['LapEnd'])})"
        )


def plot_strategy(all_stints):
    fig, ax = plt.subplots(figsize=(10, 4))

    for position, driver in enumerate(DRIVERS):
        stints = all_stints[driver]
        for _, row in stints.iterrows():
            lap_start = row["LapStart"]
            lap_end = row["LapEnd"]
            compound = row["Compound"]
            ax.barh(
                y=position,
                width=lap_end - lap_start + 1,
                left=lap_start,
                color=COMPOUND_COLORS.get(compound, "#999999"),
                edgecolor="black",
            )

    ax.set_yticks(range(len(DRIVERS)))
    ax.set_yticklabels(DRIVERS)
    ax.invert_yaxis()
    ax.set_xlabel("Vuelta")
    ax.set_title(f"Estrategia de neumáticos - {GRAND_PRIX} {YEAR}")

    handles = [
        plt.Rectangle((0, 0), 1, 1, color=color)
        for color in COMPOUND_COLORS.values()
    ]
    ax.legend(handles, COMPOUND_COLORS.keys(), loc="upper center",
              bbox_to_anchor=(0.5, -0.15), ncol=len(COMPOUND_COLORS))

    plt.tight_layout()

    output_path = "data/tire_strategy.png"
    plt.savefig(output_path)
    print(f"\nGráfico guardado en: {output_path}")


def main():
    print(f"Cargando sesión: {YEAR} {GRAND_PRIX} ({SESSION})...")
    session = fastf1.get_session(YEAR, GRAND_PRIX, SESSION)
    session.load()

    all_stints = {}
    for driver in DRIVERS:
        stints = get_driver_stints(session, driver)
        all_stints[driver] = stints
        print_stint_summary(driver, stints)

    plot_strategy(all_stints)


if __name__ == "__main__":
    main()
