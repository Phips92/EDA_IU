""" 
Copyright C Philipp Mc Guire, 2025
Lincensed under GPL V3.0 https://www.fsf.org/licensing/licenses/gpl-3.0.html 
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import mapping, Polygon, MultiPolygon

from bokeh.io import curdoc
from bokeh.models import Select, ColorBar, LinearColorMapper, HoverTool, ColumnDataSource
from bokeh.layouts import row, column
from bokeh.plotting import figure
from bokeh.palettes import OrRd9
from bokeh.models import Slider
from bokeh.models import BasicTicker, PrintfTickFormatter
from bokeh.models import LinearColorMapper

# Load data
death_df = pd.read_csv("cause_of_deaths.csv")
pop_df = pd.read_csv("WPP2024_Population1JanuaryByAge5GroupSex_Medium.csv", low_memory=False)

# Prepare population 
pop_df = pop_df[(pop_df["Variant"] == "Medium") & (pop_df["Time"].between(1990, 2019))]
pop_df = pop_df[pop_df["LocTypeID"] == 4] 
pop_df = pop_df[["Location", "Time", "PopTotal"]]
pop_df.columns = ["country", "Year", "Population_Total"]

# Multiply by 1000 (data is in thousands)
pop_df["Population_Total"] *= 1000

# Group to get single value per country-year
pop_df = pop_df.groupby(["country", "Year"], as_index=False)["Population_Total"].sum()
#print(pop_df)

# Prepare death data
death_df = death_df.rename(columns={"Country/Territory": "country"})
cause_cols = death_df.columns.difference(["country", "Year", "Code"])
death_long = death_df.melt(id_vars=["country", "Year"], value_vars=cause_cols, var_name="Cause", value_name="Deaths")
death_long["Deaths"] = pd.to_numeric(death_long["Deaths"], errors="coerce")
merged = death_long.merge(pop_df, on=["country", "Year"], how="left")
merged = merged[merged["Population_Total"].notna() & (merged["Population_Total"] > 0)]
merged = merged[merged["Deaths"].notna()]
merged["Death_Rate_per_100k"] = (merged["Deaths"] / merged["Population_Total"]) * 100000
#print(merged)


# Load world shapes
world = gpd.read_file("data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")
world = world.rename(columns={"ADMIN": "country"})
world = world.to_crs("EPSG:4326")

# Utility function to extract x/y from geometry
def geo_to_coords(gdf):
    xs, ys, countries, rates = [], [], [], []
    for _, row in gdf.iterrows():
        geom = row.geometry
        if isinstance(geom, Polygon):
            coords = [geom.exterior.coords]
        elif isinstance(geom, MultiPolygon):
            coords = [p.exterior.coords for p in geom.geoms]
        else:
            continue

        for ring in coords:
            x, y = zip(*ring)
            xs.append(list(x))
            ys.append(list(y))
            countries.append(row["country"])
            rates.append(row["Death_Rate_per_100k"])
    return ColumnDataSource(data={"x": xs, "y": ys, "country": countries, "Death_Rate_per_100k": rates})

# Widgets
cause_options = sorted(merged["Cause"].unique().tolist())
year_options = sorted(merged["Year"].unique().tolist())
cause_select = Select(title="Cause of Death", value="Tuberculosis", options=cause_options)
year_slider = Slider(title="Year", start=min(year_options), end=max(year_options), step=1, value=2019)

# Initial data
initial_df = merged[(merged["Cause"] == "Tuberculosis") & (merged["Year"] == 2019)]
initial_geo = world.merge(initial_df, on="country", how="left").dropna(subset=["Death_Rate_per_100k", "geometry"])
source = geo_to_coords(initial_geo)

# Color mapper
color_mapper = LinearColorMapper(palette=OrRd9[::-1],
                                 low=merged["Death_Rate_per_100k"].min(),
                                 high=merged["Death_Rate_per_100k"].max())

# Plot
p = figure(height=600, width=1200, toolbar_location="left", tools="pan,wheel_zoom,reset", title="Death Rate per 100k")
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
patches = p.patches("x", "y", source=source,
                    fill_color={"field": "Death_Rate_per_100k", "transform": color_mapper},
                    line_color="white", line_width=0.7, fill_alpha=1)

# Hover
hover = HoverTool(tooltips=[("Country", "@country"),("Death Rate", "@Death_Rate_per_100k{0.0}")], renderers=[patches])
p.add_tools(hover)

# Color bar
color_bar = ColorBar(
    color_mapper=color_mapper,
    label_standoff=12,
    location=(0, 0),
    title="Rate per 100k",
    ticker=BasicTicker(),  
    formatter=PrintfTickFormatter(format="%.1f")  
)
p.add_layout(color_bar, "right")

# Update function
def update_data(attr, old, new):
    cause = cause_select.value
    year = year_slider.value
    df = merged[(merged["Cause"] == cause) & (merged["Year"] == year)]

    geo_df = world.merge(df, on="country", how="left").dropna(subset=["Death_Rate_per_100k", "geometry"])
    
    # Update data
    source.data = dict(geo_to_coords(geo_df).data)
    p.title.text = f"{cause} Death Rate per 100k in {year}"

    # Dynamically update color mapper range
    if not geo_df.empty:
        vmin = geo_df["Death_Rate_per_100k"].min()
        vmax = geo_df["Death_Rate_per_100k"].max()
        color_mapper.low = vmin
        color_mapper.high = vmax

# Callbacks
cause_select.on_change("value", update_data)
year_slider.on_change("value", update_data)

# Layout
layout = column(cause_select, p, year_slider)
curdoc().add_root(layout)
curdoc().title = "Interactive Global Mortality Map"


