"""
Income Share (Bottom 50%, WID) — Data Transformation Pipeline

Extracted from Income_Share(Bottom50%).ipynb: only the steps that modify/
produce the final dataframe are kept here. Exploratory cells (df.info,
nunique, value_counts) and all outlier-detection/plotting cells used for
visual data-quality review have been excluded — see
Income_Share(Bottom50%).ipynb if you need that context.
"""

import logging

import pandas as pd
import country_converter as coco

# ---------------------------------------------------------------------------
# 1. Load raw WID data and drop non-country aggregate rows
# ---------------------------------------------------------------------------
df = pd.read_csv('../Data/Raw/Income_Share(Bottom50%).csv', sep=';')

# Removing whitespace before/after column names and country names
df.columns = df.columns.str.strip()
df['Country'] = df['Country'].str.strip()

# Removing null values since Value column has lots of null rows for the
# initial years of data
df = df.dropna(subset=["Value"])

# Every regional/aggregate row ends in (MER) or (PPP) — real countries never do
aggregate_pattern = r'\(MER\)$|\(PPP\)$|^Rural China$|^Urban China$'
is_aggregate = df['Country'].str.contains(aggregate_pattern, regex=True, na=False)
df = df[~is_aggregate].copy()

# ---------------------------------------------------------------------------
# 2. Standardize country names to ISO3 (for joining against gini_index / PWT)
# ---------------------------------------------------------------------------
logging.getLogger('country_converter').setLevel(logging.CRITICAL)
cc = coco.CountryConverter()
df['iso3'] = cc.convert(names=df['Country'], to='ISO3', not_found=None)

# Catches spelling mismatches that would otherwise silently produce a null iso3
unmatched = df[df['iso3'].isna()]['Country'].unique()
if len(unmatched) > 0:
    print(f"Warning: unmatched countries during ISO3 conversion: {unmatched}")

# ---------------------------------------------------------------------------
# 3. Filter countries to comply with gini_index data (114-country project
#    list). Prioritizes highest data coverage within each region while
#    keeping the regional structure meaningful.
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

iso3_codes = coco.convert(names=COUNTRIES, to="ISO3", not_found=None)

df_filtered = df[df['iso3'].isin(iso3_codes)].copy()

# Flags any country in COUNTRIES with zero matching rows in this dataset,
# which would otherwise silently drop out with no warning
missing = set(iso3_codes) - set(df_filtered['iso3'].unique())
if missing:
    print(f"Warning: no data found for: {missing}")

# ---------------------------------------------------------------------------
# 4. Map each country to its region (112 countries, 12 regions)
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

# REGION_MAP is keyed by country name, but df_filtered is joined on iso3, so
# convert the map's keys to iso3 in one batch call before applying it
country_names = list(REGION_MAP.keys())
iso3_codes_region = coco.convert(names=country_names, to="ISO3", not_found="not found")
iso3_region_dict = {
    iso3: REGION_MAP[name]
    for name, iso3 in zip(country_names, iso3_codes_region)
}

df_filtered['region'] = df_filtered['iso3'].map(iso3_region_dict)

# Catches any country present in the data but missing from REGION_MAP,
# which would otherwise silently become NaN
unmapped = df_filtered.loc[df_filtered['region'].isna(), 'Country'].unique()
if len(unmapped) > 0:
    print(f"Warning: {len(unmapped)} countries have no region assigned: {sorted(unmapped)}")

# ---------------------------------------------------------------------------
# Note on outlier handling (see Income_Share(Bottom50%).ipynb for the full
# review): a bounds check (Value <= 0, Value > 50, or Value > 1.00) and
# per-country IQR outlier detection were run on Value, then cross-checked
# against the gini_index outlier list and visually reviewed via time-series
# plots. No data points were dropped as a result of that review — it is
# exploratory/plotting-based, not a transformation, so it is intentionally
# omitted here.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 5. Data Quality Note — Early Years (1950-1960) excluded
# Sparse, inconsistent pre-1960 coverage (most countries lacked independent
# statistical agencies/survey programs until post-independence, mostly late
# 1950s-1960s onward) produced artificial outliers rather than genuine
# economic signal. 1960 onward aligns with WID/SWIID's own stated coverage
# start and gives more consistent country coverage.
# ---------------------------------------------------------------------------
df_filtered_final = df_filtered[df_filtered['Year'] > 1959]

# Final transformed dataframe: df_filtered_final

# ---------------------------------------------------------------------------
# 6. Save transformed data
# ---------------------------------------------------------------------------
df_filtered_final.to_csv("../Data/Processed/CSV_data/Income_Share(Bottom50%).csv", index=False)
df_filtered_final.to_parquet("../Data/Processed/Parquet_data/Income_Share(Bottom50%).parquet", index=False)
