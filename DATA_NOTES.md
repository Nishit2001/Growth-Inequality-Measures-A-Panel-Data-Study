# Data Pipeline Notes — The Inequality Ledger

Running log of data sources, issues found, and transformations applied.
One entry per source/step, added as work happens (not reconstructed later).

---

## 1. SWIID (Gini / Inequality) — Inequality Data

**Source:** Standardized World Income Inequality Database (SWIID) \
**Version:** 9.92, April 2026 release \
**File:** `swiid9_92.rda` → exported to `Gini_index.csv` \
**Coverage:** 199 countries, 1960 onward (imputed complete coverage)

## SWIID Summary Table — Column Reference

| Column | Type | Explanation |
|---|---|---|
| `country` | Text | Country name, standardized for matching against PWT and World Bank datasets |
| `year` | Integer | Calendar year of the observation |
| `gini_disp` | Float | Mean estimate of the Gini index for **disposable income** (post-tax, post-transfer household income), averaged across the 100 posterior draws. Higher value = more inequality. This is the standard headline inequality figure. |
| `gini_disp_se` | Float | Standard error of `gini_disp` — the standard deviation across the 100 draws. Reflects uncertainty in the estimate; smaller SE = more confident estimate. |
| `gini_mkt` | Float | Mean estimate of the Gini index for **market income** (pre-tax, pre-transfer household income) — inequality before government redistribution. Averaged across the 100 draws. |
| `gini_mkt_se` | Float | Standard error of `gini_mkt`, same logic as `gini_disp_se`. |
| `abs_red` | Float | **Absolute redistribution**: `gini_mkt − gini_disp`. Number of Gini-index points inequality is reduced by due to taxes and transfers. |
| `abs_red_se` | Float | Standard error of `abs_red` across the 100 draws. |
| `rel_red` | Float | **Relative redistribution**: `(gini_mkt − gini_disp) / gini_mkt × 100`. Percentage reduction in inequality due to taxes/transfers — useful for comparing redistribution effort across countries regardless of starting inequality level. |
| `rel_red_se` | Float | Standard error of `rel_red` across the 100 draws. |

---

## 2. Penn World Tables (GDP per Capita) — Economic Growth Data

**Source:** Penn World Table (PWT), version 11.0 — Feenstra, Inklaar & Timmer
**File:** `Gdp_percap_2021 usd).csv`
**Coverage:** 185 countries, 1950–2023 — fully populated, 0 missing values across all rows/columns

### PWT Summary Table — Column Reference

| Column | Type | Explanation |
|---|---|---|
| `iso3` | Text | ISO3 country code (e.g. `ABW` for Aruba) — used as the join key against World Bank data, which also standardizes on ISO3 codes |
| `Country` | Text | Full country name |
| `year` | Integer | Calendar year of the observation |
| `pop` | Float | Population, **in millions**, for that country-year |
| `rgdpe` | Float | **Expenditure-side real GDP**, in millions of constant 2021 US dollars, PPP-adjusted (Purchasing Power Parity). Measures total value of goods/services a country consumes, adjusted so a dollar reflects equivalent real purchasing power across countries — not just a currency conversion. |
| `gdppc` *(derived — not in raw file)* | Float | **GDP per capita** = `rgdpe / pop`, giving real, PPP-adjusted dollars per person. Not present as a ready-made column in the raw file — must be calculated during your pipeline step. |

Sanity-checked range: implied `gdppc` across the dataset spans roughly **$89 to $286,146**, with a median around $7,584 — consistent with expected real-world GDP-per-capita spread once PPP-adjusted.

### Why PPP adjustment matters
Raw GDP converted at market exchange rates can be misleading — $1 buys far more locally in some countries than others. PPP adjustment prices goods using a common, internationally comparable basket, making `rgdpe`/`gdppc` genuinely comparable across countries, not just across time within one country.

### Why PWT over World Bank as primary GDP source
- More rigorous, internationally consistent PPP methodology than raw World Bank GDP figures
- Longer historical coverage (back to 1950) vs. typical World Bank series which often start later
- World Bank API to be used only as a supplementary source to extend coverage to 2024/fill any remaining gaps

### Caveats to remember
- This file only goes to 2023 — the World Bank API supplement step is still needed to extend to 2024
- `gdppc` must be computed, not assumed to already exist, when merging with SWIID/World Bank tables downstream


---


## 3. World Bank PIP — Poverty Headcount Dataset Notes
 
## Summary
 
The **World Bank Poverty and Inequality Platform (PIP)** dataset provides poverty and inequality estimates drawn from household surveys across **172 countries** 
spanning **1963–2025**. This file contains **2,584 rows × 44 columns**, with one row per country-year-reporting_level combination. All monetary values are expressed in 
**2021 PPP-adjusted international dollars** at the **$3.00/day** extreme poverty line. Inflation is accounted for via country-specific CPI sourced from the IMF International 
Financial Statistics (IFS). The dataset includes not just poverty headcounts but full distributional statistics — Gini, decile shares, poverty gap, and national accounts 
anchors — making it suitable for rich cross-country inequality analysis.

## Column Reference
 
| Column | Type | Description |
|---|---|---|
| `region_name` | String | World Bank region (e.g. `Sub-Saharan Africa`, `South Asia`) |
| `region_code` | String | Region abbreviation (e.g. `SSF`, `SAS`) |
| `country_name` | String | Full country name |
| `country_code` | String (ISO3) | 3-letter country identifier (e.g. `IND`, `NGA`) |
| `reporting_year` | Integer | Reference year the estimate is reported for |
| `reporting_level` | String | Geographic coverage — `national`, `urban`, or `rural` |
| `survey_acronym` | String | Short name of the source household survey (e.g. `NSS`, `ENIGH`) |
| `survey_coverage` | String | Population scope the survey covers |
| `survey_year` | Float | Actual decimal year survey fieldwork was conducted (e.g. `2018.17`) |
| `welfare_type` | String | Measure used — `consumption` or `income` |
| `survey_comparability` | Integer | Comparability group ID — surveys with the same ID are methodologically consistent |
| `comparable_spell` | String | Year or year-range over which estimates are directly comparable (e.g. `2002 - 2012`) |
| `poverty_line` | Integer | Poverty line applied in 2021 PPP USD/day — value is `3` ($3.00/day) |
| `headcount` | Float (0–1) | **Primary metric** — share of population living below the poverty line |
| `poverty_gap` | Float | Average shortfall from the poverty line as a share of the line — measures depth of poverty |
| `poverty_severity` | Float | Squared poverty gap — gives extra weight to the poorest; measures severity |
| `watts` | Float | Watts index — logarithmic poverty measure sensitive to the very poorest (9 nulls) |
| `mean` | Float (USD PPP) | Mean daily income or consumption per capita in 2021 PPP dollars |
| `median` | Float (USD PPP) | Median daily income or consumption per capita in 2021 PPP dollars |
| `mld` | Float | Mean Log Deviation — inequality measure; higher = more unequal |
| `gini` | Float (0–1) | Gini coefficient from survey microdata — 0 = perfect equality, 1 = maximum inequality |
| `polarization` | Float | Polarization index — measures clustering of population at income extremes |
| `decile1`–`decile10` | Float | Income/consumption share held by each decile — `decile1` = bottom 10%, `decile10` = top 10% |
| `cpi` | Float | Country-specific CPI used to deflate nominal welfare to constant prices (source: IMF IFS) |
| `ppp` | Float | PPP conversion factor used to convert local currency to 2021 international dollars (23 nulls) |
| `reporting_pop` | Float | Country population in the reporting year (persons) |
| `reporting_gdp` | Float | GDP per capita in reporting year (2021 PPP USD) |
| `reporting_pce` | Float | Private Consumption Expenditure per capita — national accounts anchor (289 nulls) |
| `is_interpolated` | Boolean | `True` if estimate is modelled between survey years; `False` if from actual survey |
| `distribution_type` | String | Data method — `micro` (unit-level), `group` (grouped), `synthetic`, or `imputed` |
| `estimation_type` | String | How estimate was produced — all rows are `survey` in this file |
| `spl` | Float (USD PPP) | Societal Poverty Line — country-specific line that rises with average income |
| `spr` | Float (0–1) | Societal Poverty Rate — headcount at the SPL rather than the fixed $3.00 line |
| `pg` | Float | Poverty Gap at the societal poverty line |
| `estimate_type` | Float | All null in this file — reserved for future classification |

## Calculations & Specifications
 
- **CPI Deflation (Step 1):** Raw survey income/consumption is deflated using country-specific annual CPI from IMF IFS, converting nominal values to constant prices so figures are comparable within the same country across time.
- **PPP Conversion (Step 2):** CPI-adjusted values are then converted to 2021 PPP international dollars via ICP consumption PPPs, ensuring $3.00/day represents the same real purchasing power across all countries.
- **Headcount Calculation:** The share of individuals whose CPI-and-PPP-adjusted daily welfare falls below $3.00 is recorded as `headcount` — the primary poverty metric in this dataset.
- **Deciles:** Each `decile1`–`decile10` value is the income/consumption share of that tenth of the population, summing to ~1.0, directly revealing how growth distributes across the income spectrum.
- **Interpolated Years:** Where no survey exists for a given year, PIP models welfare using CPI growth and national accounts; these rows are flagged `is_interpolated = True`.
 
---
 
## Limitations
 
- **Single poverty line** — file only contains the $3.00/day line; for G7 countries where extreme poverty is near zero, use `gini` and `decile` columns instead.
- **Mixed welfare types** — `income` and `consumption` are not perfectly comparable; be cautious when making direct cross-country comparisons between countries of different types.
- **Interpolated rows** — years between actual surveys are modelled estimates, not observed data; treat year-over-year changes in these periods with caution.
- **Pre-2011 spatial gaps** — estimates before 2011 do not account for rural/urban price variation within countries, introducing potential bias.
- **`reporting_pce` nulls (289 rows)** — private consumption expenditure is missing for several country-years; avoid using as a primary analysis variable.
- **`estimate_type` fully null** — carries no usable information in this file; exclude from analysis.
- **National CPI basket** — CPI reflects average household consumption, not the poor-specific basket (food, fuel), which typically inflates faster and may understate real poverty trends.

---

## 4. World Inequality Database (WID.world) — Top 20% Income Share Dataset
 
---
 
## Summary
 
The **World Inequality Database (WID.world)** dataset provides the **pre-tax national
income share of the top 20% (P80–P100)** of earners across countries, downloaded on
**14 July 2026**. All values are expressed as a **decimal fraction between 0 and 1** representing the
proportion of total pre-tax national income captured by the top 20% of adult earners
in that country and year. The full production dataset will expand this to all 25
project countries.

## Column Reference
 
| Column | Type | Description |
|---|---|---|
| `Country` | String | Full country name — note trailing whitespace in raw file; always apply `.strip()` before use |
| `Variable` | String | Multi-line field containing three embedded lines: (1) WID variable code with country suffix, (2) human-readable label, (3) full specification string — requires parsing to extract cleanly |
| `Percentile` | String | Income group — always `p80p100` in this file, meaning the top 20% of earners (80th to 100th percentile) |
| `Year` | Integer | Calendar year of the estimate — spans 1940 to 2024 across all countries in this file |
| `Value` | Float (0–1) | **Primary metric** — the share of total pre-tax national income earned by the top 20%, expressed as a decimal fraction. Multiply by 100 to convert to percentage |
| `Data quality` | Float (0–5) | Reliability score for each estimate — see Data Quality section below. Null where Value is also null |

## Calculations & Specifications
 
- **Share Definition:** The `Value` for `p80p100` is computed as the total pre-tax
  income accruing to all adults in the top 20% divided by total pre-tax national
  income. It is a ratio and therefore unitless — directly comparable across all
  countries and years without any currency conversion.
- **Pre-Tax National Income:** Income is measured **before** direct taxes (income tax)
  and government cash transfers are applied but **after** pension and unemployment
  insurance contributions. This captures market inequality before redistribution.
  It is distinct from disposable income used in SWIID (`gini_disp`).
- **Equal-Split Adults:** Household income is divided equally among all adults (18+)
  in the household regardless of who earned it. Children are excluded from the
  population denominator. This differs from per-capita measures that include children.
- **No Currency Conversion Needed:** Unlike `aptinc` (average income), share values
  are already dimensionless fractions. A value of `0.50` means exactly the same thing
  in Afghanistan, Brazil, and Belgium — no PPP adjustment required for this metric.

## Limitations
- **Score 0 rows (17.9%)** — modelled estimates with no direct country evidence; these
  are regional averages applied to countries with no data, not real observations.
  Treat with the same caution as score 3.
- **Pre-1980 gaps** — most countries in this file have no data before 1980. The
  project's 1974–2024 scope will have a 6-year gap at the start for these countries.
- **Flat values across years** — some countries (Afghanistan 1980–1999, Angola,
  Benin, Burkina Faso) show identical values across many consecutive years. This
  is not real stability — it is WID holding a single estimate constant when no
  new survey data exists. Do not interpret as evidence of unchanging inequality.
- **Pre-tax only** — does not reflect post-redistribution income. Use alongside
  SWIID `gini_disp` (disposable income Gini) to understand the impact of taxes
  and transfers on inequality.
- **Equal-split method** — not directly comparable to datasets using per-capita or
  tax-unit income assignment; document this distinction in cross-dataset merge notes.

---

  ## 5. World Inequality Database (WID.world) — Bottom 50% Income Share Dataset
 
---
 
## Summary
 
The **World Inequality Database (WID.world)** dataset provides the **pre-tax national
income share of the bottom 50% (P0–P50)** of earners across countries, downloaded on
**15 July 2026**. This file contains **19,725 rows × 6 columns** covering **263
countries and regional aggregates** spanning **1950–2024**. Of these, **12,865 rows
(65.2%) carry actual values** — the remaining 6,860 rows (34.8%) are null, representing
country-years with no available estimate. All values are expressed as a **decimal fraction between 0 and 1** representing the
proportion of total pre-tax national income captured by the bottom 50% of adult earners
in that country and year.

## Column Reference
 
| Column | Type | Description |
|---|---|---|
| `Country` | String | Full country name — note trailing whitespace in raw file; always apply `.strip()` before use |
| `Variable` | String | Multi-line field containing three embedded lines: (1) WID variable code with country suffix e.g. `sptinc_p0p50_999_j_AF`, (2) human-readable label `Pre-tax national income`, (3) full specification string `Bottom 50% \| share \| all ages \| equal split` — requires parsing to extract cleanly |
| `Percentile` | String | Income group — always `p0p50` in this file, meaning the bottom 50% of earners (0th to 50th percentile) |
| `Year` | Integer | Calendar year of the estimate — spans 1950 to 2024 across all countries in this file |
| `Value` | Float (0–1) | **Primary metric** — the share of total pre-tax national income earned by the bottom 50%, expressed as a decimal fraction. Multiply by 100 to convert to percentage |
| `Data quality` | Float (0–5) | Reliability score for each estimate — see Data Quality section below. Null where Value is also null |
 
 ## Calculations & Specifications
 
- **Share Definition:** The `Value` for `p0p50` is the total pre-tax income accruing
  to all adults in the bottom 50% divided by total pre-tax national income. It is
  unitless — directly comparable across all countries and years with no currency
  conversion required.
- **Pre-Tax National Income:** Income is measured before direct taxes and government
  cash transfers but after pension and unemployment insurance contributions. This
  captures market inequality before redistribution — distinct from disposable income
  used in SWIID (`gini_disp`).
- **Equal-Split Adults:** Household income is divided equally among all adults (20+)
  regardless of who earned it. Children excluded from the denominator. This differs
  from per-capita measures that include children — relevant when merging with World
  Bank PIP data which uses per-capita.
- **No Currency Conversion Needed:** Share values are dimensionless fractions.
  A value of `0.15` means exactly the same thing in Nigeria, France, and Vietnam
  — no PPP adjustment required.

## Limitations
 
- **Widespread flat values** — the majority of countries show long runs of identical
  consecutive values (5–44 years). This reflects data scarcity, not real stability.
  Never interpret a flat line as evidence of unchanged inequality without checking
  the data quality score. This is more severe in this file than in the top 20% file.
- **34.8% null rows** — always drop nulls before analysis; never treat null as zero.
- **25.0% score 0 rows** — modelled estimates with no direct country evidence are
  the single largest quality category. These should be treated with the same caution
  as score 3, not as reliable observations.
- **Equal-split method** — not directly comparable to World Bank PIP per-capita
  measures. Document in cross-dataset merge notes.