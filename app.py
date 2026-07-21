"""
App de Streamlit para comparar, dentro de una carrera de la temporada 2024,
el ritmo de vuelta y la estrategia de neumáticos de dos pilotos.

Uso:
    streamlit run app.py
"""

import fastf1
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Habilita el cache local para no tener que volver a descargar los datos
# cada vez que corremos la app.
fastf1.Cache.enable_cache("data/cache")

YEAR = 2024

COMPOUND_COLORS = {
    "SOFT": "#DA291C",
    "MEDIUM": "#FFD12E",
    "HARD": "#F0F0F0",
    "INTERMEDIATE": "#43B02A",
    "WET": "#0067AD",
}

# Colores por piloto (en orden de selección), consistentes en ambos gráficos.
DRIVER_COLORS = ["#2a78d6", "#008300"]

st.set_page_config(page_title="F1 2024 - Comparador de pilotos", layout="wide")


@st.cache_data(show_spinner=False)
def get_race_schedule(year):
    """Devuelve el calendario de carreras de temporada regular (sin testing)."""
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    schedule = schedule[schedule["RoundNumber"] > 0]
    return schedule[["RoundNumber", "EventName"]].reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_race_session(year, round_number):
    """Carga la sesión de carrera de una ronda. Cacheada por (year, round_number)
    para no volver a descargar/procesar la sesión si el usuario solo cambia
    de pilotos."""
    session = fastf1.get_session(year, round_number, "R")
    session.load()
    return session


def get_driver_quicklaps(session, driver):
    """Vueltas rápidas (pick_quicklaps()) de un piloto en la sesión."""
    return session.laps.pick_drivers(driver).pick_quicklaps()


def get_driver_stints(driver_laps):
    """Resumen de stints (compuesto, vuelta inicio/fin) a partir de sus vueltas."""
    return driver_laps.groupby("Stint").agg(
        Compound=("Compound", "first"),
        LapStart=("LapNumber", "min"),
        LapEnd=("LapNumber", "max"),
    )


def format_lap_time(lap_time):
    """Formatea un Timedelta de vuelta como m:ss.sss."""
    total_seconds = lap_time.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = total_seconds - minutes * 60
    return f"{minutes}:{seconds:06.3f}"


def plot_lap_time_comparison(laps_by_driver):
    driver_colors = dict(zip(laps_by_driver.keys(), DRIVER_COLORS))

    combined = pd.concat(
        [laps.assign(Driver=driver) for driver, laps in laps_by_driver.items()],
        ignore_index=True,
    )
    combined["LapTimeSeconds"] = combined["LapTime"].dt.total_seconds()
    combined["LapTimeStr"] = combined["LapTime"].apply(format_lap_time)

    fig = px.line(
        combined,
        x="LapNumber",
        y="LapTimeSeconds",
        color="Driver",
        color_discrete_map=driver_colors,
        custom_data=["LapTimeStr", "Compound"],
        labels={"LapNumber": "Vuelta", "LapTimeSeconds": "Tiempo de vuelta (s)"},
        title="Comparación de tiempos de vuelta",
    )
    fig.update_traces(
        mode="lines+markers",
        line=dict(width=2),
        marker=dict(size=6),
        hovertemplate=(
            "Vuelta %{x}<br>"
            "Tiempo: %{customdata[0]}<br>"
            "Compuesto: %{customdata[1]}"
            "<extra>%{fullData.name}</extra>"
        ),
    )
    fig.update_layout(legend_title_text="Piloto")
    return fig


def plot_tire_strategy(laps_by_driver, race_label):
    drivers = list(laps_by_driver.keys())

    stint_rows = []
    for driver in drivers:
        stints = get_driver_stints(laps_by_driver[driver])
        for _, row in stints.iterrows():
            stint_rows.append(
                {
                    "Driver": driver,
                    "Compound": row["Compound"],
                    "LapStart": row["LapStart"],
                    "LapEnd": row["LapEnd"],
                }
            )
    stints_df = pd.DataFrame(stint_rows)

    fig = go.Figure()
    for compound in stints_df["Compound"].unique():
        compound_stints = stints_df[stints_df["Compound"] == compound]
        fig.add_trace(
            go.Bar(
                name=compound,
                y=compound_stints["Driver"],
                x=compound_stints["LapEnd"] - compound_stints["LapStart"] + 1,
                base=compound_stints["LapStart"],
                orientation="h",
                marker=dict(
                    color=COMPOUND_COLORS.get(compound, "#999999"),
                    line=dict(color="black", width=1),
                ),
                customdata=compound_stints[["Compound", "LapStart", "LapEnd"]],
                hovertemplate=(
                    "Compuesto: %{customdata[0]}<br>"
                    "Vuelta inicio: %{customdata[1]}<br>"
                    "Vuelta fin: %{customdata[2]}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=f"Estrategia de neumáticos - {race_label}",
        xaxis_title="Vuelta",
        barmode="overlay",
        height=280,
        legend_title_text="Compuesto",
        yaxis=dict(categoryorder="array", categoryarray=list(reversed(drivers))),
    )
    return fig


def main():
    st.title("F1 2024 - Comparador de pilotos")

    schedule = get_race_schedule(YEAR)
    race_options = {
        f"Ronda {int(row.RoundNumber)} - {row.EventName}": int(row.RoundNumber)
        for row in schedule.itertuples()
    }
    race_label = st.selectbox("Carrera", list(race_options.keys()))
    round_number = race_options[race_label]

    with st.spinner(f"Cargando sesión de carrera ({race_label})..."):
        session = load_race_session(YEAR, round_number)

    available_drivers = sorted(session.laps["Driver"].unique())
    drivers = st.multiselect(
        "Pilotos (elegí 2)",
        available_drivers,
        default=available_drivers[:2],
        max_selections=2,
    )

    if len(drivers) != 2:
        st.info("Elegí exactamente 2 pilotos para comparar.")
        return

    laps_by_driver = {driver: get_driver_quicklaps(session, driver) for driver in drivers}

    for driver, laps in laps_by_driver.items():
        if laps.empty:
            st.warning(f"{driver} no tiene vueltas rápidas registradas en esta carrera.")
            return

    st.plotly_chart(plot_lap_time_comparison(laps_by_driver), use_container_width=True)
    st.plotly_chart(plot_tire_strategy(laps_by_driver, race_label), use_container_width=True)


if __name__ == "__main__":
    main()
