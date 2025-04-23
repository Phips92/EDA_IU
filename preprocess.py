""" 
Copyright C Philipp Mc Guire, 2025
Lincensed under GPL V3.0 https://www.fsf.org/licensing/licenses/gpl-3.0.html 
"""
import pandas as pd
import numpy as np
import pycountry_convert as pc

class DataPreparation:
    # Manual fallback for country -> continent mapping
    manual_continent_map = {
        "Bolivia (Plurinational State of)": "South America",
        "China, Hong Kong SAR": "Asia",
        "China, Macao SAR": "Asia",
        "China, Taiwan Province of China": "Asia",
        "Dem. People's Republic of Korea": "Asia",
        "Holy See": "Europe",
        "Iran (Islamic Republic of)": "Asia",
        "Kosovo (under UNSC res. 1244)": "Europe",
        "Micronesia (Fed. States of)": "Oceania",
        "Republic of Korea": "Asia",
        "Saint Helena": "Africa",
        "Sint Maarten (Dutch part)": "North America",
        "State of Palestine": "Asia",
        "Timor-Leste": "Asia",
        "Venezuela (Bolivarian Republic of)": "South America",
        "Wallis and Futuna Islands": "Oceania",
        "Western Sahara": "Africa"
    }

    def __init__(self, death_path, pop_path, alcohol_path):
        self.death_df = pd.read_csv(death_path)
        self.pop_df = pd.read_csv(pop_path, low_memory=False)
        self.alcohol_df = pd.read_csv(alcohol_path)
        self._preprocess_all()

    def _preprocess_all(self):
        self._prep_population()
        self._prep_deaths()
        self._prep_alcohol()
        self._merge_data()
        self._add_continents()

    def _prep_population(self):
        df = self.pop_df
        df = df[(df["Variant"] == "Medium") & (df["Time"].between(1990, 2019))]
        df = df[df["LocTypeID"] == 4]
    
        df = df[["Location", "Time", "AgeGrp", "PopMale", "PopFemale", "PopTotal"]].copy()
        df.rename(columns={
            "Location": "country",
            "Time": "Year",
            "AgeGrp": "Age_Group",
            "PopMale": "Population_Male",
            "PopFemale": "Population_Female",
            "PopTotal": "Population_Total"
        }, inplace=True)
    
        df["Population_Male"] *= 1000
        df["Population_Female"] *= 1000
        df["Population_Total"] *= 1000
    
        self.pop_df = df

    def _prep_deaths(self):
        df = self.death_df.rename(columns={"Country/Territory": "country"}).copy()
        cause_cols = df.columns.difference(["country", "Year", "Code"])
        df = df.melt(
            id_vars=["country", "Year"],
            value_vars=cause_cols,
            var_name="Cause",
            value_name="Deaths"
        )
        df["Deaths"] = pd.to_numeric(df["Deaths"], errors="coerce")
        self.death_df = df
        self.cause_list = sorted(df["Cause"].unique().tolist())

    def _prep_alcohol(self):
        df = self.alcohol_df
        df = df[(df["Year"] >= 2000) & (df["Year"] <= 2019)]
        df = df.rename(columns={
            "Entity": "country",
            "Total alcohol consumption per capita (liters of pure alcohol, projected estimates, 15+ years of age)": "Alcohol_Consumption_Liters"
        })
        df = df[["country", "Year", "Alcohol_Consumption_Liters"]]
        df = df.groupby(["country", "Year"]).mean().reset_index()
        self.alcohol_df = df

    def _merge_data(self):
        merged = self.death_df.merge(self.pop_df, on=["country", "Year"], how="left")
        merged = merged[merged["Population_Total"].notna() & (merged["Population_Total"] > 0)]
        merged["Death_Rate_per_100k"] = (merged["Deaths"] / merged["Population_Total"]) * 100000
        merged = merged.merge(self.alcohol_df, on=["country", "Year"], how="left")
        self.merged_df = merged

    def _get_continent_from_country(self, country):
        try:
            code = pc.country_name_to_country_alpha2(country)
            continent_code = pc.country_alpha2_to_continent_code(code)
            return pc.convert_continent_code_to_continent_name(continent_code)
        except:
            return self.manual_continent_map.get(country, "Other")

    def _add_continents(self):
        self.merged_df["Continent"] = self.merged_df["country"].apply(self._get_continent_from_country)
        self.pop_df["Continent"] = self.pop_df["country"].apply(self._get_continent_from_country)



