"""
GDP per Capita, 2021 USD (Penn World Table) — Data Transformation Pipeline

Extracted from Gdp_percap(2021 usd)(Transform).ipynb: only the steps that
modify/produce the final dataframe are kept here. Exploratory cells
(df.head, df.info, nunique, value_counts) and all plotting/visual
outlier-review cells have been excluded — see the notebook if you need
that context.
"""

import pandas as pd
import country_converter as coco

# ---------------------------------------------------------------------------
# 1. Load raw data
# ---------------------------------------------------------------------------
# Script lives in Scripts/, data lives in the sibling Data/ folder at project root
df = pd.read_csv("../Data/Raw/Gdp_percap(2021 usd).csv")

# ---------------------------------------------------------------------------
# 2. Filter to the 114-country project list (to comply with gini_index data)
# ---------------------------------------------------------------------------
COUNTRIES = [
    # North America
    "United States", "Canada", "Puerto Rico",
    # Western Europe
    "United Kingdom", "Germany", "France", "Ireland", "Belgium",
    "Netherlands", "Switzerland", "Luxembourg", "Austria",
    # Nordic
    "Sweden", "Norway", "Finland", "Denmark",
    # Southern Europe
    "Italy", "Portugal", "Spain", "Greece", "Cyprus",
    # Eastern Europe & Former Soviet
    "Hungary", "Poland", "Ukraine", "Uzbekistan", "Georgia", "Kyrgyzstan",
    "Slovenia", "Tajikistan", "Kazakhstan", "Moldova", "Estonia", "Belarus",
    "Armenia", "Croatia", "Lithuania", "Slovakia", "Czech Republic",
    "Latvia", "Russia", "Bulgaria", "Romania",
    # East Asia
    "Japan", "Taiwan", "Korea", "Hong Kong", "China",
    # South Asia
    "Pakistan", "India", "Bangladesh", "Sri Lanka", "Nepal",
    # Southeast Asia
    "Philippines", "Thailand", "Indonesia", "Malaysia", "Singapore",
    "Vietnam", "Laos",
    # Middle East & North Africa
    "Iran", "Israel", "Egypt", "Turkey", "Jordan", "Tunisia", "Morocco", "Qatar",
    # Sub-Saharan Africa
    "Madagascar", "Malawi", "Tanzania", "Sierra Leone", "South Africa",
    "Zambia", "Sudan", "Kenya", "Nigeria", "Rwanda", "Côte d'Ivoire",
    "Mauritania", "Lesotho", "Eswatini", "Guinea-Bissau", "Mauritius",
    "Mali", "Uganda", "Senegal", "Botswana", "Central African Republic",
    "Niger", "Ghana",
    # Latin America & Caribbean
    "Brazil", "Costa Rica", "Argentina", "Mexico", "Venezuela", "Chile",
    "Panama", "Colombia", "Peru", "Uruguay", "Guatemala",
    "Dominican Republic", "Barbados", "Honduras", "El Salvador", "Paraguay",
    "Trinidad and Tobago", "Jamaica", "Bolivia", "Ecuador",
    # Oceania
    "New Zealand", "Australia", "Fiji", "Tonga",
]

# Guard against typos introducing duplicate entries in the list above
assert len(COUNTRIES) == len(set(COUNTRIES)), "Duplicate country names found in list!"

# The raw data is keyed by ISO3 (not country name), so convert the project's
# country list to ISO3 before filtering
iso3_codes = coco.convert(names=COUNTRIES, to="ISO3", not_found=None)

df_filtered = df[df['iso3'].isin(iso3_codes)].copy()

# Catches countries in the project list with zero matching rows in this
# dataset, which would otherwise silently be dropped
missing = set(iso3_codes) - set(df_filtered['iso3'].unique())
if missing:
    print(f"Warning: no data found for: {missing}")
# Puerto Rico (PRI) and Tonga (TON) are expected here — not covered by PWT.

# ---------------------------------------------------------------------------
# 3. Map each country to its region (114 countries, 12 regions)
# ---------------------------------------------------------------------------
REGION_MAP = {
    # North America
    "United States": "North America", "Canada": "North America",

    # Western Europe
    "United Kingdom": "Western Europe", "Germany": "Western Europe",
    "France": "Western Europe", "Ireland": "Western Europe",
    "Belgium": "Western Europe", "Netherlands": "Western Europe",
    "Switzerland": "Western Europe", "Luxembourg": "Western Europe",
    "Austria": "Western Europe",

    # Nordic
    "Sweden": "Nordic", "Norway": "Nordic",
    "Finland": "Nordic", "Denmark": "Nordic",

    # Southern Europe
    "Italy": "Southern Europe", "Portugal": "Southern Europe",
    "Spain": "Southern Europe", "Greece": "Southern Europe",
    "Cyprus": "Southern Europe",

    # Eastern Europe & Former Soviet
    "Hungary": "Eastern Europe & FSU", "Poland": "Eastern Europe & FSU",
    "Ukraine": "Eastern Europe & FSU", "Uzbekistan": "Eastern Europe & FSU",
    "Georgia": "Eastern Europe & FSU", "Kyrgyzstan": "Eastern Europe & FSU",
    "Slovenia": "Eastern Europe & FSU", "Tajikistan": "Eastern Europe & FSU",
    "Kazakhstan": "Eastern Europe & FSU", "Moldova": "Eastern Europe & FSU",
    "Estonia": "Eastern Europe & FSU", "Belarus": "Eastern Europe & FSU",
    "Armenia": "Eastern Europe & FSU", "Croatia": "Eastern Europe & FSU",
    "Lithuania": "Eastern Europe & FSU", "Slovakia": "Eastern Europe & FSU",
    "Czech Republic": "Eastern Europe & FSU", "Latvia": "Eastern Europe & FSU",
    "Russia": "Eastern Europe & FSU", "Bulgaria": "Eastern Europe & FSU",
    "Romania": "Eastern Europe & FSU",

    # East Asia
    "Japan": "East Asia", "Taiwan": "East Asia", "Korea": "East Asia",
    "Hong Kong": "East Asia", "China": "East Asia",

    # South Asia
    "Pakistan": "South Asia", "India": "South Asia",
    "Bangladesh": "South Asia", "Sri Lanka": "South Asia",
    "Nepal": "South Asia",

    # Southeast Asia
    "Philippines": "Southeast Asia", "Thailand": "Southeast Asia",
    "Indonesia": "Southeast Asia", "Malaysia": "Southeast Asia",
    "Singapore": "Southeast Asia", "Vietnam": "Southeast Asia",
    "Laos": "Southeast Asia",

    # Middle East & North Africa
    "Iran": "MENA", "Israel": "MENA", "Egypt": "MENA",
    "Turkey": "MENA", "Jordan": "MENA", "Tunisia": "MENA",
    "Morocco": "MENA", "Qatar": "MENA",

    # Sub-Saharan Africa
    "Madagascar": "Sub-Saharan Africa", "Malawi": "Sub-Saharan Africa",
    "Tanzania": "Sub-Saharan Africa", "Sierra Leone": "Sub-Saharan Africa",
    "South Africa": "Sub-Saharan Africa", "Zambia": "Sub-Saharan Africa",
    "Sudan": "Sub-Saharan Africa", "Kenya": "Sub-Saharan Africa",
    "Nigeria": "Sub-Saharan Africa", "Rwanda": "Sub-Saharan Africa",
    "Côte d'Ivoire": "Sub-Saharan Africa", "Mauritania": "Sub-Saharan Africa",
    "Lesotho": "Sub-Saharan Africa", "Eswatini": "Sub-Saharan Africa",
    "Guinea-Bissau": "Sub-Saharan Africa", "Mauritius": "Sub-Saharan Africa",
    "Mali": "Sub-Saharan Africa", "Uganda": "Sub-Saharan Africa",
    "Senegal": "Sub-Saharan Africa", "Botswana": "Sub-Saharan Africa",
    "Central African Republic": "Sub-Saharan Africa", "Niger": "Sub-Saharan Africa",
    "Ghana": "Sub-Saharan Africa",

    # Latin America & Caribbean
    "Brazil": "Latin America & Caribbean", "Costa Rica": "Latin America & Caribbean",
    "Argentina": "Latin America & Caribbean", "Mexico": "Latin America & Caribbean",
    "Venezuela": "Latin America & Caribbean", "Chile": "Latin America & Caribbean",
    "Panama": "Latin America & Caribbean", "Colombia": "Latin America & Caribbean",
    "Peru": "Latin America & Caribbean", "Uruguay": "Latin America & Caribbean",
    "Guatemala": "Latin America & Caribbean", "Dominican Republic": "Latin America & Caribbean",
    "Barbados": "Latin America & Caribbean", "Honduras": "Latin America & Caribbean",
    "El Salvador": "Latin America & Caribbean", "Paraguay": "Latin America & Caribbean",
    "Trinidad and Tobago": "Latin America & Caribbean", "Jamaica": "Latin America & Caribbean",
    "Bolivia": "Latin America & Caribbean", "Ecuador": "Latin America & Caribbean",

    # Oceania
    "New Zealand": "Oceania", "Australia": "Oceania",
    "Fiji": "Oceania",
}

# The region map is keyed by country name, so convert its keys to ISO3
# (matching df_filtered['iso3']) in one batch call rather than row-by-row
country_names = list(REGION_MAP.keys())
region_iso3_codes = coco.convert(names=country_names, to="ISO3", not_found="not found")
iso3_region_dict = {
    iso3: REGION_MAP[name]
    for name, iso3 in zip(country_names, region_iso3_codes)
}

df_filtered['region'] = df_filtered['iso3'].map(iso3_region_dict)

# Catches any country present in the data but missing from REGION_MAP,
# which would otherwise silently become NaN
unmapped = df_filtered.loc[df_filtered['region'].isna(), 'Country'].unique()
if len(unmapped) > 0:
    print(f"Warning: {len(unmapped)} countries have no region assigned: {sorted(unmapped)}")

# ---------------------------------------------------------------------------
# 4. Derive GDP per capita (rgdpe is expressed in millions, pop in millions,
#    so the ratio gives GDP per capita directly in 2021 USD)
# ---------------------------------------------------------------------------
df_filtered['gdp_per_capita'] = df_filtered['rgdpe'] / df_filtered['pop']

# Catches any silent NaN/inf introduced by the division before moving on
n_null = df_filtered['gdp_per_capita'].isna().sum()
n_inf = (df_filtered['gdp_per_capita'] == float('inf')).sum()
if n_null or n_inf:
    print(f"Warning: gdp_per_capita has {n_null} null and {n_inf} infinite values")

# ---------------------------------------------------------------------------
# Note on outlier handling (see Gdp_percap(2021 usd)(Transform).ipynb for the
# full review): per-country IQR outlier detection was run on gdp_per_capita
# and each flagged country's time series was visually reviewed. No data
# points were dropped — flagged values reflected real, documented economic
# history (e.g. Ireland's 2015 "Leprechaun Economics" jump from multinational
# tax inversions, and Venezuela's mid-2010s hyperinflation/collapse) rather
# than data errors. That detection/plotting step is exploratory, not a
# transformation, so it is intentionally omitted here.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 5. Save transformed data
# ---------------------------------------------------------------------------
df_filtered.to_csv("../Data/Processed/CSV_data/Gdp_percap(2021 usd).csv", index=False)
df_filtered.to_parquet("../Data/Processed/Parquet_data/Gdp_percap(2021 usd).parquet", index=False)
