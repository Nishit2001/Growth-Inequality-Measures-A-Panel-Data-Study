import pandas as pd
from sqlalchemy import create_engine, text


# CONNECTION CONFIG 
DB_USER = "postgres"
DB_PASSWORD = "Ni846986"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "MasterPanel_InequalityMeasures"


engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Load the merged panel (parquet preferred -- preserves dtypes)
panel = pd.read_parquet("../Data/Processed/Parquet_data/Master_Panel.parquet")
# Postgres lowercases unquoted identifiers automatically. Align the
# dataframe's column names to lowercase now, so they match the table
# schema below exactly -- otherwise to_sql() will try to insert into
# e.g. "Year" and fail because the table column is actually "year".
panel.columns = panel.columns.str.lower()
print(f"Loaded panel: {len(panel)} rows, {len(panel.columns)} columns")
print(panel.dtypes)

# Create the table explicitly, with real Postgres types
CREATE_TABLE_SQL = """
DROP TABLE IF EXISTS country_year_panel;
 
CREATE TABLE country_year_panel (
    iso3                  CHAR(3),
    year                  INT,
    country               VARCHAR(100),
    region                VARCHAR(100),
    gini_disp             NUMERIC,
    gini_disp_se          NUMERIC,
    gini_mkt              NUMERIC,
    gini_mkt_se           NUMERIC,
    abs_red               NUMERIC,
    abs_red_se            NUMERIC,
    rel_red               NUMERIC,
    rel_red_se            NUMERIC,
    abs_red_source        VARCHAR(20),
    pop                   NUMERIC,
    rgdpe                 NUMERIC,
    gdp_per_capita        NUMERIC,
    variable_top20        TEXT,
    percentile_top20      VARCHAR(20),
    value_top20           NUMERIC,
    dataquality_top20     VARCHAR(20),
    variable_bottom50     TEXT,
    percentile_bottom50   VARCHAR(20),
    value_bottom50        NUMERIC,
    dataquality_bottom50  VARCHAR(20),
    PRIMARY KEY (iso3, year)
);
"""

with engine.connect() as conn:
    conn.execute(text(CREATE_TABLE_SQL))
    conn.commit()
 
print("Table created.")

panel.to_sql(
    "country_year_panel",
    engine,
    if_exists="append",
    index=False,
    method="multi",   # batches inserts, much faster than row-by-row
    chunksize=1000,
)

print("Data loaded into country_year_panel.")