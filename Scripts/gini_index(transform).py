"""
Gini Index (SWIID) — Data Transformation Pipeline

Extracted from gini_index(transform).ipynb: only the steps that modify/produce
the final dataframe are kept here. Exploratory cells (df.head, df.info,
value_counts, nunique) and all plotting/visual outlier-review cells
have been excluded — see gini_index(transform).ipynb if you need that context.
"""

import pandas as pd
import country_converter as coco

# ---------------------------------------------------------------------------
# 1. Load raw data
# ---------------------------------------------------------------------------
# Script lives in Scripts/, data lives in the sibling Data/ folder at project root
df = pd.read_csv("../Data/Raw/Gini_Index.csv")

# ---------------------------------------------------------------------------
# 2. Filter to the 114-country project list
# Prioritizes highest data coverage within each region while keeping the
# regional structure meaningful (full regional breakdown trimmed to 114).
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

df_filtered = df[df['country'].isin(COUNTRIES)].copy()

# Catches spelling mismatches between COUNTRIES and the raw data that would
# otherwise silently drop a country with zero matching rows
missing = set(COUNTRIES) - set(df_filtered['country'].unique())
if missing:
    print(f"Warning: no data found for: {missing}")

# ---------------------------------------------------------------------------
# 3. Map each country to its region (114 countries, 12 regions)
# ---------------------------------------------------------------------------
REGION_MAP = {
    # North America
    "United States": "North America", "Canada": "North America",
    "Puerto Rico": "North America",

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
    "Fiji": "Oceania", "Tonga": "Oceania",
}

df_filtered['region'] = df_filtered['country'].map(REGION_MAP)

# Catches any country present in the data but missing from REGION_MAP,
# which would otherwise silently become NaN
unmapped = df_filtered.loc[df_filtered['region'].isna(), 'country'].unique()
if len(unmapped) > 0:
    print(f"Warning: {len(unmapped)} countries have no region assigned: {sorted(unmapped)}")

# ---------------------------------------------------------------------------
# 4. Standardize country names to ISO3 (for joining against PWT/World Bank)
# ---------------------------------------------------------------------------
cc = coco.CountryConverter()
df_filtered['iso3'] = cc.convert(names=df_filtered['country'], to='ISO3', not_found=None)

unmatched = df_filtered[df_filtered['iso3'].isna()]['country'].unique()
if len(unmatched) > 0:
    print(f"Warning: unmatched countries during ISO3 conversion: {unmatched}")

# ---------------------------------------------------------------------------
# 5. Fill missing abs_red / rel_red using the arithmetic relationship,
#    while flagging which rows are original survey values vs. derived.
# ---------------------------------------------------------------------------
df_filtered['abs_red_source'] = df_filtered['abs_red'].apply(lambda x: 'survey' if pd.notna(x) else 'derived')

df_filtered['abs_red'] = df_filtered['abs_red'].fillna(df_filtered['gini_mkt'] - df_filtered['gini_disp'])
df_filtered['rel_red'] = df_filtered['rel_red'].fillna(
    (df_filtered['gini_mkt'] - df_filtered['gini_disp']) / df_filtered['gini_mkt']
)

# ---------------------------------------------------------------------------
# Note on outlier handling (see gini_index(transform).ipynb for the full review):
# Per-country IQR outlier detection was run on gini_disp/gini_mkt and each
# flagged country's time series was visually reviewed. No data points were
# dropped — flagged values reflected real, documented economic history
# (e.g. post-Soviet transition shifts) rather than data errors. That
# detection/plotting step is exploratory, not a transformation, so it is
# intentionally omitted here.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 6. Check final dataframe before saving
# ---------------------------------------------------------------------------
print(df_filtered.shape)
print(df_filtered.info())
print(df_filtered.isna().sum())
print(df_filtered.head())

# Final transformed dataframe: df_filtered

# ---------------------------------------------------------------------------
# 7. Save transformed data
# ---------------------------------------------------------------------------
df_filtered.to_csv("../Data/Processed/CSV_data/Gini_Index.csv", index=False)
df_filtered.to_parquet("../Data/Processed/Parquet_data/Gini_Index.parquet", index=False)
