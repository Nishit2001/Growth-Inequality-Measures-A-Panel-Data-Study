"""
Master Merge Script — Sequential Outer Merge on (iso3, Year)

Extracted from Master_MergeScript.ipynb: only the steps that build/produce
the final merged panel are kept here. Exploratory cells (column-name
inspection, coverage-diff printouts, df.info) used for visual review have
been excluded — see Master_MergeScript.ipynb if you need that context.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# 1. Import processed data to merge
# ---------------------------------------------------------------------------
Gini_df = pd.read_parquet("../Data/Processed/Parquet_data/Gini_Index.parquet")
Gdp_df = pd.read_parquet("../Data/Processed/Parquet_data/Gdp_percap(2021 usd).parquet")
Top20_df = pd.read_parquet("../Data/Processed/Parquet_data/Income_Share(Top20).parquet")
Bottom50_df = pd.read_parquet("../Data/Processed/Parquet_data/Income_Share(Bottom50%).parquet")

# ---------------------------------------------------------------------------
# 2. Changing the column names to avoid complication while merging the
#    datasets (Top20/Bottom50 share overlapping column names, so suffix them)
# ---------------------------------------------------------------------------
Gini_df = Gini_df.rename(columns={'year': 'Year', 'country': 'Country'})
Gdp_df = Gdp_df.rename(columns={'year': 'Year'})
Top20_df = Top20_df.rename(columns={
    'Variable': 'Variable_Top20', 'Percentile': 'Percentile_Top20',
    'Value': 'Value_Top20', 'Data quality': 'DataQuality_Top20',
})
Bottom50_df = Bottom50_df.rename(columns={
    'Variable': 'Variable_Bottom50', 'Percentile': 'Percentile_Bottom50',
    'Value': 'Value_Bottom50', 'Data quality': 'DataQuality_Bottom50',
})

datasets = {
    'GiniIndex': Gini_df, 'GdpPerCapita': Gdp_df,
    'IncomeShare(Top20)': Top20_df, 'IncomeShare(Bottom50)': Bottom50_df,
}

# ---------------------------------------------------------------------------
# 3. Country/region are static per iso3 (they don't change by year), and all
#    four dataframes carry their own copy of these columns. Build a single
#    clean lookup table (one row per country) instead of letting duplicate
#    copies ride along into the merge. This also avoids ending up with
#    multiple slightly different names for the same country (e.g. "USA" vs
#    "United States") sitting side by side once the datasets are combined --
#    by collapsing to one row per iso3, the panel keeps a single consistent
#    name/region per country instead of a version per source.
# ---------------------------------------------------------------------------
METADATA_COLS = ['Country', 'region']

# For each dataframe, keep only iso3 + metadata columns, and collapse
# each country's repeated per-year rows down to a single row.
metadata_frames = [df[['iso3'] + METADATA_COLS].drop_duplicates() for df in datasets.values()]

# Stack all four sources' metadata on top of each other, then deduplicate
# again across sources -- keeping exactly one row per iso3 overall.
country_lookup = pd.concat(metadata_frames, ignore_index=True).drop_duplicates(subset='iso3')

# ---------------------------------------------------------------------------
# 4. Merge all four datasets on (iso3, Year), with Country/region dropped
#    from each one first -- they're already saved separately in
#    country_lookup, so keeping them here would cause duplicate-column
#    collisions once more than two dataframes are merged in sequence.
# ---------------------------------------------------------------------------
panel = None
for name, df in datasets.items():
    df = df.drop(columns=['Country', 'region'])
    if panel is None:
        # First dataframe: just becomes the starting point for panel.
        panel = df.copy()
    else:
        # Outer join keeps every country-year row from every source --
        # if a source doesn't cover that year, the cell becomes NaN
        # instead of the row being dropped entirely.
        panel = panel.merge(df, on=['iso3', 'Year'], how='outer')

# Attach Country/region back onto the panel, joining on iso3 ALONE (not Year)
panel = panel.merge(country_lookup, on='iso3', how='left')

# Sort rows so each country's years run in order, then reset the index
# to a clean 0, 1, 2... sequence
panel = panel.sort_values(['iso3', 'Year']).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 5. Save merged panel
# ---------------------------------------------------------------------------
panel.to_csv("../Data/Processed/CSV_data/Master_Panel.csv", index=False)
panel.to_parquet("../Data/Processed/Parquet_data/Master_Panel.parquet", index=False)
