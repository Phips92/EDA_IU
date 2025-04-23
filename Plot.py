""" 
Copyright C Philipp Mc Guire, 2025
Lincensed under GPL V3.0 https://www.fsf.org/licensing/licenses/gpl-3.0.html 
"""
from preprocess import DataPreparation
from EDA import run_initial_eda
from Visualizations import plot_global_deathrate_trend, plot_top_and_bottom_causes, plot_population_age_violin, plot_top_causes_by_continent, plot_alcohol_vs_deathrate, plot_joint_kde, plot_rising_falling_causes, plot_top_cause_rank_shift


# Initialize preprocessing class
prep = DataPreparation("data/cause_of_deaths.csv", "data/WPP2024_Population1JanuaryByAge5GroupSex_Medium.csv", "data/total-alcohol-consumption-per-capita-litres-of-pure-alcohol.csv")

#run_initial_eda(prep)

#plot_global_deathrate_trend(prep)
#plot_top_and_bottom_causes(prep)
#plot_population_age_violin(prep)

#continents = ["Africa", "Europe", "Asia", "North America", "South America", "Oceania"]
#for cont in continents:
#    plot_top_causes_by_continent(prep, cont)

#plot_alcohol_vs_deathrate(prep, "Cirrhosis and Other Chronic Liver Diseases", continent="Europe")
#plot_alcohol_vs_deathrate(prep, "Drug Use Disorders") 

plot_joint_kde(prep,"Diarrheal Diseases", "Digestive Diseases",continent="Africa", year=1995)

#plot_rising_falling_causes(prep, continent="Oceania")  
#plot_rising_falling_causes(prep, continent="Africa")    
#plot_rising_falling_causes(prep)

#plot_top_cause_rank_shift(prep, continent="Oceania", top_n=5)
#plot_top_cause_rank_shift(prep, continent="Asia", top_n=5)
#plot_top_cause_rank_shift(prep, continent="North America", top_n=5)
#plot_top_cause_rank_shift(prep, country="Germany", top_n=5)
