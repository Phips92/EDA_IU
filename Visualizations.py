import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from matplotlib.patches import Patch

def plot_global_deathrate_trend(prep):
    # Access data
    df = prep.death_df.pivot_table(index="Year", columns="Cause", values="Deaths", aggfunc="sum")
    df["Total Deaths"] = df.sum(axis=1)

    pop_total = prep.pop_df.groupby("Year")["Population_Total"].sum().reset_index()
    global_summary = df.merge(pop_total, on="Year")
    global_summary["Death_Rate_per_100k"] = (global_summary["Total Deaths"] / global_summary["Population_Total"]) * 1e5

    # Regression
    x = global_summary["Year"]
    y = global_summary["Death_Rate_per_100k"]
    slope, intercept = np.polyfit(x, y, 1)
    reg_line = slope * x + intercept
    percent_label = f"{abs((slope / y.iloc[0]) * 100):.1f}% decrease per year"

    # Plot
    plt.figure(figsize=(12, 7))
    plt.plot(x, y, marker="o", linewidth=2.5, color="#0072B2", label="Observed Death Rate")
    plt.plot(x, reg_line, linestyle="--", color="forestgreen", linewidth=2, label="Linear Trend")
    plt.legend()

    plt.text(x.iloc[0], y.iloc[0] - 10, f"{y.iloc[0]:.1f}", color="red", weight="bold", ha="center")
    plt.text(x.iloc[-1], y.iloc[-1] + 5, f"{y.iloc[-1]:.1f}", color="green", weight="bold", ha="center")
    mid_x = x.iloc[len(x)//2]
    mid_y = reg_line.iloc[len(x)//2]
    plt.text(mid_x + 2, mid_y + 10, f"▼ {percent_label}", color="forestgreen", fontsize=14, weight="bold")

    plt.title("Global Death Rate per 100,000 (1990–2019)", fontsize=18, weight="bold")
    plt.suptitle("Visualizing the Long-Term Trend in Mortality", fontsize=14, style="italic")
    plt.xlabel("Year")
    plt.ylabel("Deaths per 100,000")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

def plot_top_and_bottom_causes(prep):
    df = prep.death_df.copy()
    total_deaths = df.groupby("Cause")["Deaths"].sum().sort_values(ascending=False)

    top5 = total_deaths.head(5).index.tolist()
    bottom5 = total_deaths.tail(5).index.tolist()

    df = df[df["Cause"].isin(top5 + bottom5)]
    pop_total = prep.pop_df.groupby(["country", "Year"])["Population_Total"].sum().reset_index()
    merged = df.merge(pop_total, on=["country", "Year"], how="left")
    merged = merged[merged["Population_Total"].notna()]
    merged["Death_Rate_per_100k"] = (merged["Deaths"] / merged["Population_Total"]) * 1e5

    agg = merged.groupby(["Year", "Cause"])["Death_Rate_per_100k"].sum().reset_index()

    fig, axs = plt.subplots(2, 1, figsize=(15, 10), sharex=True)

    # Top 5
    sns.lineplot(data=agg[agg["Cause"].isin(top5)], x="Year", y="Death_Rate_per_100k", hue="Cause", ax=axs[0])
    axs[0].set_title("Top 5 Global Causes of Death (1990–2019)")
    axs[0].set_ylabel("Deaths per 100k")

    # Bottom 5
    sns.lineplot(data=agg[agg["Cause"].isin(bottom5)], x="Year", y="Death_Rate_per_100k", hue="Cause", ax=axs[1])
    axs[1].set_title("5 Least Common Causes of Death (1990–2019)")
    axs[1].set_xlabel("Year")
    axs[1].set_ylabel("Deaths per 100k")

    for ax in axs:
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(loc="upper right")

    plt.suptitle("Cause-Specific Global Mortality Trends", fontsize=18, weight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


def plot_population_age_violin(prep):
    pop_df = prep.pop_df.copy()

    # Filter to 1990 and 2019
    pop_compare = pop_df[pop_df["Year"].isin([1990, 2019])].copy()

    # Compute total population per country-year
    total_pop = pop_compare.groupby(["country", "Year"])["Population_Total"].sum().reset_index()
    total_pop.rename(columns={"Population_Total": "Country_Pop"}, inplace=True)

    # Merge and compute age share
    pop_compare = pop_compare.merge(total_pop, on=["country", "Year"])
    pop_compare["Age_Share"] = pop_compare["Population_Total"] / pop_compare["Country_Pop"]

    # Filter to major continents
    major_continents = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania"]
    pop_compare = pop_compare[pop_compare["Continent"].isin(major_continents)]

    # Create Continent-Year label
    pop_compare["Continent_Year"] = pop_compare["Continent"] + " (" + pop_compare["Year"].astype(str) + ")"

    # Expand rows to simulate age distribution
    expanded_rows = []
    for _, row in pop_compare.iterrows():
        n = int(row["Age_Share"] * 500)  # Scale to 500 samples per continent-year
        expanded_rows.extend([{
            "Continent_Year": row["Continent_Year"],
            "Age_Group": row["Age_Group"],
            "Year": row["Year"],
            "Continent": row["Continent"]
        }] * n)

    expanded_df = pd.DataFrame(expanded_rows)

    # Violin plot
    plt.figure(figsize=(16, 10))
    sns.violinplot(data=expanded_df,x="Continent", y="Age_Group", hue="Year", split=True, palette="Set2", inner="quartile")
    plt.title("Age Distribution by Continent: 1990 vs. 2019", fontsize=18, weight="bold")
    plt.xlabel("Continent", fontsize=14)
    plt.ylabel("Age Group", fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(title="Year", loc="upper right")
    plt.tight_layout()
    plt.show()


def plot_top_causes_by_continent(prep, continent):

    # Extract and filter data
    death_df = prep.death_df.copy()
    pop_df = prep.pop_df.copy()
    death_subset = death_df[death_df["Year"].isin([1990, 2019])].copy()
    pop_subset = pop_df[pop_df["Year"].isin([1990, 2019])].copy()
    
    death_subset = death_subset.pivot_table(index=["country", "Year"], columns="Cause", values="Deaths").reset_index()
    death_subset = death_subset.merge(pop_df[["country", "Continent"]].drop_duplicates(), on="country")
    
    death_data = death_subset[death_subset["Continent"] == continent]
    pop_data = pop_subset[pop_subset["Continent"] == continent]

    pop_totals = pop_data.groupby(["country", "Year"])["Population_Total"].sum().reset_index()
    death_data = death_data.merge(pop_totals, on=["country", "Year"])

    # Calculate death rates
    cause_cols = death_data.columns.difference(["country", "Year", "Continent", "Population_Total"])
    for cause in cause_cols:
        death_data[cause + "_rate"] = (death_data[cause] / death_data["Population_Total"]) * 100000

    rate_cols = [c for c in death_data.columns if c.endswith("_rate")]
    by_year = death_data.groupby("Year")[rate_cols].sum().reset_index()
    df_melted = by_year.melt(id_vars="Year", var_name="Cause", value_name="Death Rate per 100k")
    df_melted["Cause"] = df_melted["Cause"].str.replace("_rate", "", regex=False)

    # Top 5 causes
    top5_1990 = df_melted[df_melted["Year"] == 1990].nlargest(5, "Death Rate per 100k")["Cause"].tolist()
    top5_2019 = df_melted[df_melted["Year"] == 2019].nlargest(5, "Death Rate per 100k")["Cause"].tolist()
    new_causes = [cause for cause in top5_2019 if cause not in top5_1990]

    # Prepare plotting data
    df_1990 = df_melted[df_melted["Cause"].isin(top5_1990)].copy()
    df_1990["Cause"] = pd.Categorical(df_1990["Cause"], categories=top5_1990, ordered=True)
    df_1990 = df_1990.sort_values(["Cause", "Year"])

    df_2019 = df_melted[df_melted["Cause"].isin(top5_2019)].copy()
    order_2019 = df_2019[df_2019["Year"] == 2019].sort_values("Death Rate per 100k", ascending=False)["Cause"].tolist()
    df_2019["Cause"] = pd.Categorical(df_2019["Cause"], categories=order_2019, ordered=True)
    df_2019 = df_2019.sort_values(["Cause", "Year"])

    # Plotting
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

    sns.barplot(data=df_1990, x="Cause", y="Death Rate per 100k", hue="Year", palette="Set2", ax=axes[0])
    axes[0].set_title(f"Death causes in {continent} (1990 Base)")
    axes[0].set_xlabel("Cause of Death")
    axes[0].set_ylabel("Deaths per 100,000")
    axes[0].tick_params(axis='x', rotation=45, labelsize=11)

    sns.barplot(data=df_2019, x="Cause", y="Death Rate per 100k", hue="Year", palette="Set2", ax=axes[1])
    axes[1].set_title(f"Death causes in {continent} (2019 Base)")
    axes[1].set_xlabel("Cause of Death")
    axes[1].set_ylabel("")
    axes[1].tick_params(axis='x', rotation=45, labelsize=11)

    # Highlight new causes in red
    xtick_labels = axes[1].get_xticklabels()
    for label in xtick_labels:
        if label.get_text() in new_causes:
            label.set_color("red")
        else:
            label.set_color("black")

    plt.suptitle(f"Most Common Causes of Death in {continent} Compared: 1990 vs. 2019", fontsize=20, fontweight="bold")
    axes[0].legend(title="Year")
    axes[1].legend().remove()
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


def plot_alcohol_vs_deathrate(prep, cause, continent=None, country=None):

    death_df = prep.death_df.pivot_table(index=["country", "Year"], columns="Cause", values="Deaths").reset_index()
    pop_df = prep.pop_df.copy()
    alcohol_df = prep.alcohol_df.copy()

    cause_cols = death_df.columns.difference(["country", "Year"])
    death_long = death_df.melt(id_vars=["country", "Year"], value_vars=cause_cols, var_name="Cause", value_name="Deaths")

    merged = death_long.merge(alcohol_df, on=["country", "Year"], how="left")

    merged = merged.merge(pop_df[["country", "Continent"]].drop_duplicates(), on="country", how="left")

    pop_total = pop_df.groupby(["country", "Year"])["Population_Total"].sum().reset_index()
    merged = merged.merge(pop_total, on=["country", "Year"], how="left")

    # Filter by cause and location
    merged = merged[merged["Cause"] == cause]
    if continent:
        merged = merged[merged["Continent"] == continent]
    if country:
        merged = merged[merged["country"] == country]

    merged = merged[(merged["Population_Total"] > 0)& merged["Deaths"].notna()& merged["Alcohol_Consumption_Liters"].notna()].copy()
    merged["Death_Rate_per_100k"] = (merged["Deaths"] / merged["Population_Total"]) * 1e5

    if merged.empty or len(merged) < 5:
        print("Not enough data to plot.")
        return

    corr = merged[["Alcohol_Consumption_Liters", "Death_Rate_per_100k"]].corr().iloc[0, 1]

    sns.set(style="whitegrid", context="talk")
    g = sns.jointplot(data=merged, x="Alcohol_Consumption_Liters", y="Death_Rate_per_100k", kind="hex", cmap="viridis", height=10, marginal_kws=dict(bins=30, fill=True))
    g.fig.set_figwidth(15)
    g.fig.set_figheight(10)
    g.ax_joint.set_xlabel("Alcohol Consumption (liters per capita)")
    g.ax_joint.set_ylabel(f"{cause} Death Rate (per 100k)")

    # Dynamic title
    title = f"Alcohol vs. {cause} Death Rate (2000–2019)"
    if country:
        title += f" — {country}"
    elif continent:
        title += f" — {continent}"
    else:
        title += " — Worldwide"


    g.fig.subplots_adjust(top=0.9)
    g.fig.suptitle(title, fontsize=18, fontweight="bold")
    g.fig.text(0.5, 0.87, f"Pearson Corr: {corr:.2f}", ha="center", fontsize=13, style="italic")
    plt.show()


def plot_joint_kde(prep, cause_x, cause_y, continent=None, year=None):

    death_df = prep.death_df.pivot_table(index=["country", "Year"], columns="Cause", values="Deaths").reset_index()
    pop_df = prep.pop_df.copy()

    df = death_df.merge(pop_df[["country", "Continent"]].drop_duplicates(), on="country", how="left")

    pop_total = pop_df.groupby(["country", "Year"])["Population_Total"].sum().reset_index()
    df = df.merge(pop_total, on=["country", "Year"], how="left")

    # Filter
    if continent:
        df = df[df["Continent"] == continent]
    if year:
        df = df[df["Year"] == year]

    # Compute death rates
    df["x_rate"] = (df[cause_x] / df["Population_Total"]) * 100000
    df["y_rate"] = (df[cause_y] / df["Population_Total"]) * 100000
    df = df[(df["x_rate"].notna()) & (df["y_rate"].notna())]

    if df.empty or len(df) < 5:
        print("Not enough data to plot.")
        return

    # Plot KDE
    sns.set(style="white", font_scale=1.2)
    g = sns.jointplot(data=df, x="x_rate", y="y_rate", kind="kde", fill=True, thresh=0.05, cmap="mako", height=8)
    g.set_axis_labels( f"{cause_x} Death Rate (per 100k)", f"{cause_y} Death Rate (per 100k)", fontsize=12)
    g.fig.set_figwidth(15)
    g.fig.set_figheight(10)

    # Title
    title_main = f"{cause_x} vs. {cause_y} Death Rate Distribution"
    title_sub = ""
    if continent:
        title_sub += f"{continent} "
    if year:
        title_sub += f"({year})"

    # Correlation
    corr, _ = pearsonr(df["x_rate"], df["y_rate"])
    corr_label = f"Pearson Correlation: {corr:.2f}"

    plt.subplots_adjust(top=0.9)
    g.fig.suptitle(title_main, fontsize=16, weight="bold")
    if title_sub:
        g.fig.text(0.5, 0.88, f"{title_sub.strip()} — {corr_label}", ha="center", fontsize=12, style="italic")

    plt.show()

def plot_rising_falling_causes(prep, continent=None):

    df = prep.merged_df.copy()

    if continent:
        df = df[df["Continent"] == continent]

    agg = df.groupby(["Year", "Cause"])["Death_Rate_per_100k"].sum().reset_index()
    pivot = agg.pivot(index="Cause", columns="Year", values="Death_Rate_per_100k")

    if 1990 not in pivot.columns or 2019 not in pivot.columns:
        print("1990 or 2019 missing from data.")
        return

    pivot = pivot.dropna(subset=[1990, 2019])
    pivot["% Change"] = ((pivot[2019] - pivot[1990]) / pivot[1990]) * 100
    pivot = pivot.sort_values("% Change", ascending=False).reset_index()

    # Color logic
    def classify_color(change):
        if change <= -75:
            return "green"
        elif change <= -50:
            return "yellow"
        elif change < 0:
            return "orange"
        else:
            return "red"

    pivot["Color"] = pivot["% Change"].apply(classify_color)

    # Plot with legend outside (like slope plot)
    fig, ax = plt.subplots(figsize=(16, 12))
    bars = ax.barh(pivot["Cause"], pivot["% Change"], color=pivot["Color"])

    ax.axvline(0, color="black", linewidth=1)
    ax.set_title(f"Change in Cause of Death Rates (1990–2019){' — ' + continent if continent else ' — World wide'}", fontsize=16, weight="bold")
    ax.set_xlabel("Percent Change in Death Rate")
    ax.set_ylabel("Cause of Death")
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)

    # Legend
    legend_elements = [
        Patch(facecolor="green", label="Huge decrease (≤ –75%)"),
        Patch(facecolor="yellow", label="Moderate decrease (–75% to –50%)"),
        Patch(facecolor="orange", label="Slight decrease (–50% to 0%)"),
        Patch(facecolor="red", label="Increase (≥ 0%)")
    ]

    fig.subplots_adjust(left=0.25, right=0.75) 
    ax.legend(handles=legend_elements, title="Change Interpretation", loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=True)

    plt.show()

def plot_top_cause_rank_shift(prep, continent=None, country=None, top_n=10):

    df = prep.merged_df.copy()

    if continent:
        df = df[df["Continent"] == continent]
    if country:
        df = df[df["country"] == country]

    df = df[df["Year"].isin([1990, 2019])]

    pivot_df = df.pivot_table(index=["country", "Year"], columns="Cause", values="Deaths").reset_index()
    pivot_df = pivot_df.merge(df[["country", "Continent"]].drop_duplicates(), on="country")
    if continent:
        pivot_df = pivot_df[pivot_df["Continent"] == continent]

    pop_df = prep.pop_df.copy()
    pop_df = pop_df[pop_df["Year"].isin([1990, 2019])]
    if continent:
        pop_df = pop_df[pop_df["Continent"] == continent]

    pop_totals = pop_df.groupby(["country", "Year"])["Population_Total"].sum().reset_index()
    pivot_df = pivot_df.merge(pop_totals, on=["country", "Year"])

    cause_cols = pivot_df.columns.difference(["country", "Year", "Continent", "Population_Total"])
    for cause in cause_cols:
        pivot_df[cause + "_rate"] = (pivot_df[cause] / pivot_df["Population_Total"]) * 100000

    # Sum by Year for the continent
    rate_cols = [c for c in pivot_df.columns if c.endswith("_rate")]
    by_year = pivot_df.groupby("Year")[rate_cols].sum().reset_index()

    df_melted = by_year.melt(id_vars="Year", var_name="Cause", value_name="Death Rate per 100k")
    df_melted["Cause"] = df_melted["Cause"].str.replace("_rate", "", regex=False)

    # Top N causes per year
    top_1990 = df_melted[df_melted["Year"] == 1990].nlargest(top_n, "Death Rate per 100k")["Cause"]
    top_2019 = df_melted[df_melted["Year"] == 2019].nlargest(top_n, "Death Rate per 100k")["Cause"]
    top_combined = pd.Series(top_1990.tolist() + top_2019.tolist()).unique()

    # Filter and rank
    df_melted = df_melted[df_melted["Cause"].isin(top_combined)]
    df_melted["Rank"] = df_melted.groupby("Year")["Death Rate per 100k"].rank(ascending=False, method="min")

    # Pivot to get ranks
    pivot = df_melted.pivot(index="Cause", columns="Year", values="Rank").dropna()
    all_ranks = sorted(set(pivot[1990]).union(pivot[2019]))
    pivot = pivot.sort_values(1990)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 8))
    lines = []
    labels = []

    for cause, row in pivot.iterrows():
        line, = ax.plot([1990, 2019], [row[1990], row[2019]], marker="o", label=cause, linewidth=2)
        lines.append(line)
        labels.append(cause)

    ax.set_title(
        f"Change in Top {top_n} Causes of Death Rank (1990 → 2019)"
        f"{' — ' + country if country else (' — ' + continent if continent else ' — World wide')}",
        fontsize=14, weight="bold"
    )
    ax.invert_yaxis()
    ax.set_xticks([1990, 2019])
    ax.set_xlabel("Year")
    ax.set_ylabel("Rank (1 = Most Deadly)")
    ax.set_yticks(all_ranks)
    ax.grid(True, linestyle="--", alpha=0.5)

    fig.subplots_adjust(right=0.6)
    ax.legend(handles=lines, labels=labels, loc="center left", bbox_to_anchor=(1.01, 0.5), title="Cause of Death", frameon=True)

    plt.show()




