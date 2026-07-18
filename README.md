# F1 Data Analysis

Proyecto de análisis de datos de Fórmula 1 usando [FastF1](https://docs.fastf1.dev/), pensado como pieza de portfolio orientada a data analysis en motorsport.

## Objetivo

Explorar y analizar datos reales de F1 (tiempos de vuelta, telemetría, estrategias de neumáticos, resultados históricos) para practicar Python, pandas, SQL y visualización de datos.

## Estructura del proyecto

```
f1-data-analysis/
├── data/
│   └── cache/          # Cache local de FastF1 (no se sube a git)
├── notebooks/           # Jupyter notebooks de exploración y análisis
├── src/                 # Scripts reutilizables (fetch, procesamiento, utils)
├── requirements.txt      # Dependencias del proyecto
└── README.md
```

## Setup

1. Clonar el repo y crear un entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Probar que todo funciona bajando datos de una carrera:

```bash
python src/fetch_data.py
```

La primera vez va a tardar un poco más porque descarga y cachea los datos de la sesión.

## Roadmap

- [x] Setup inicial del repo y entorno
- [ ] Comparación de tiempos de vuelta entre pilotos (una carrera)
- [ ] Análisis de estrategia de neumáticos (paradas en boxes, compuestos)
- [ ] Pasar datos procesados a SQLite y practicar consultas SQL
- [ ] Comparar rendimiento de un piloto a lo largo de una temporada
- [ ] (Opcional) Dashboard interactivo con Streamlit

## Fuente de datos

Los datos vienen de la API pública de FastF1, que a su vez obtiene información oficial de telemetría y timing de la F1. Ver [documentación de FastF1](https://docs.fastf1.dev/) para más detalle sobre qué datos están disponibles.
