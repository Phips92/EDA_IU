# Global Mortality Trends – Explorative Data Analysis & Visualization

## Project Overview
This project explores long-term trends and regional differences in causes of death worldwide using extensive datasets from the United Nations and the World Health Organization. It combines static and interactive data visualizations to uncover mortality patterns, the impact of alcohol, demographic shifts, and the evolution of global health burdens between 1990 and 2019.

---

## Datasets
Three main datasets are used:
- **Cause of Death Dataset:** Mortality by country, year, and cause ([Kaggle](https://www.kaggle.com/datasets/iamsouravbanerjee/cause-of-deaths-around-the-world?select=cause_of_deaths.csv))
- **Population Dataset:** Age-structured population by country and year ([UN WPP 2024](https://population.un.org/wpp/downloads?folder=Standard%20Projections&group=CSV%20format)).
- **Alcohol Consumption:** Per capita consumption (liters of pure alcohol) by country and year ([Our World in Data](https://ourworldindata.org/grapher/total-alcohol-consumption-per-capita-litres-of-pure-alcohol?v=1&csvType=full&useColumnShortNames=false)).

All datasets are preprocessed and merged using a custom pipeline (`preprocess.py`).

---

## Objectives
- **Data Preparation:** Clean, merge, and standardize death, population, and alcohol datasets.
- **Trend Analysis:** Examine how global and regional death rates evolved.
- **Cause Ranking:** Compare shifts in leading causes of death across years and continents.
- **Risk Factor Analysis:** Analyze correlations between alcohol use and disease-specific death rates.
- **Geospatial Visualization:** Display cause-specific mortality globally using Bokeh maps.

---

## Key Visualizations

| Visualization Function | Description |
|------------------------|-------------|
| `plot_global_deathrate_trend` | Global trend in death rate per 100k (1990–2019) with regression. |
| `plot_top_and_bottom_causes` | Top 5 vs. bottom 5 causes of death over time. |
| `plot_population_age_violin` | Age structure comparison by continent for 1990 vs. 2019. |
| `plot_top_causes_by_continent` | Most common causes by continent (1990 vs. 2019), with changes highlighted. |
| `plot_alcohol_vs_deathrate` | Hexbin plot showing link between alcohol and disease death rates. |
| `plot_joint_kde` | KDE heatmap for co-occurrence of death rates between two diseases. |
| `plot_rising_falling_causes` | Color-coded bar chart of % change in cause-specific death rates. |
| `plot_top_cause_rank_shift` | Slope graph showing rank shifts in top causes between 1990 and 2019. |
| `Interactive.py` | Interactive global mortality map built with Bokeh. |

---
## Example Outputs

A selection of generated plots has been included in the Visualizations/ directory for reference. These static images showcase the output of the main visualization functions, such as global death rate trends, cause-specific mortality comparisons, and correlation-based hexbin or KDE plots. They provide a quick overview of what users can expect when running the analysis.
---

## How to Run

### 1. Run Static Visualizations
Choose functions to execute by editing `Plot.py`:
```python
plot_global_deathrate_trend(prep)
plot_top_causes_by_continent(prep, "Europe")
plot_top_cause_rank_shift(prep, country="Germany", top_n=8)
```
Then run:
```bash
python Plot.py
```

### 2. Launch Interactive Mortality Map
```bash
bokeh serve Interactive.py --show
```

---

## Installation & Dependencies

```bash
pip install pandas numpy seaborn matplotlib bokeh geopandas shapely pycountry-convert
```
Some systems may require:
```bash
conda install -c conda-forge geopandas pyproj shapely
```

Additional Requirement for Map

To run the interactive map, you need to download the Natural Earth shapefiles.
Make sure you have the folder ne_110m_admin_0_countries (with .shp, .dbf, .shx, etc.) located under the data/ directory. You can download it from:

https://www.naturalearthdata.com/downloads/110m-cultural-vectors/

---

## Contributions
Contributions are welcome!
- Fork this repo.
- Create a feature branch.
- Commit and push your changes.
- Open a pull request for review.

---

## License
This project is licensed under the GNU General Public License v3.0


## Author
For questions or feedback, feel free to contact me at [philipp92.mcguire@gmail.com].




