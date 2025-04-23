""" 
Copyright C Philipp Mc Guire, 2025
Lincensed under GPL V3.0 https://www.fsf.org/licensing/licenses/gpl-3.0.html 
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def run_initial_eda(prep):
    """
    Perform initial exploratory data analysis (EDA) on the merged dataset 
    provided by the DataPreparation class instance.

    Parameters:
    -----------
    prep : DataPreparation
        An initialized and processed DataPreparation object with merged_df attribute.
    """

    df = prep.merged_df

    #Data structure and summary statistics
    print("=== DATAFRAME HEAD ===")
    print(df.head(1).T)
    print("=== DATAFRAME INFO ===")
    print(df.info())
    print("\n=== DESCRIPTIVE STATISTICS ===")
    print(df.describe())

    #Number of records per year
    year_counts = df["Year"].value_counts().sort_index()
    plt.figure(figsize=(10, 4))
    sns.barplot(x=year_counts.index, y=year_counts.values, palette="crest")
    plt.title("Number of Records per Year")
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    #Top 10 countries by record count
    top_countries = df["country"].value_counts().head(10)
    plt.figure(figsize=(8, 4))
    sns.barplot(x=top_countries.values, y=top_countries.index, palette="flare")
    plt.title("Top 10 Countries by Number of Records")
    plt.xlabel("Number of Records")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.show()

    #Heatmap of deaths by cause and year
    pivot = df.pivot_table(index="Cause", columns="Year", values="Deaths", aggfunc="sum")
    plt.figure(figsize=(14, 10))
    sns.heatmap(pivot, cmap="mako_r", linewidths=0.3)
    plt.title("Total Number of Deaths by Cause and Year")
    plt.xlabel("Year")
    plt.ylabel("Cause of Death")
    plt.tight_layout()
    plt.show()

    #Alcohol consumption vs. liver-related death rate
    liver_df = df[df["Cause"].str.contains("Liver", case=False, na=False)]
    plt.figure(figsize=(6, 5))
    sns.scatterplot(data=liver_df, x="Alcohol_Consumption_Liters", y="Death_Rate_per_100k", alpha=0.5)
    plt.title("Alcohol Consumption vs. Death Rate from Liver Diseases")
    plt.xlabel("Alcohol Consumption (liters per capita)")
    plt.ylabel("Death Rate per 100,000")
    plt.tight_layout()
    plt.show()

    #Histogram of death rate distribution
    plt.figure(figsize=(6, 4))
    sns.histplot(df["Death_Rate_per_100k"], bins=40, kde=True, color="steelblue")
    plt.title("Distribution of Death Rates per 100,000")
    plt.xlabel("Death Rate")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()
