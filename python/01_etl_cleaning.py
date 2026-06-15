# Parental Labor Force Participation Data Cleaning 
# Ingest raw IPUMS CPS data, clean, filter to analysis population,
# run code clean checks, and output a clean Parquet file 


import pandas as pd # using pandas to shape and transofrm the data
import numpy as np
from ipumspy import IpumsApiClient, readers #library built for working with IPUMS data
from pathlib import Path

# 1. FILE PATHS

# using relative paths so code works on any machine, keeping file locations organized
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"

DDI_FILE = RAW_DIR / "cps_raw.xml"
DATA_FILE = RAW_DIR / "cps_raw.dat.gz"

print(" FILE PATHS ")
print(f"DDI: {DDI_FILE}")
print(f"Data: {DATA_FILE}")
print(f"Files exist: DDI={DDI_FILE.exists()}, Data={DATA_FILE.exists()}")

# 2. LOAD RAW IPUMS DATA

# ipumspy reads the DDI codebook to understand the fixed-width data file
print("\n LOADING RAW DATA ")
ddi = readers.read_ipums_ddi(DDI_FILE)
df = readers.read_microdata(ddi, DATA_FILE)

print(f"Raw data shape: {df.shape}")
print(f"Years available: {sorted(df['YEAR'].unique())}")
print(f"Columns: {list(df.columns)}")


# 3. FILTER TO ASEC RECORDS ONLY

# just need the asec records because this has the annual supplement detailed with education, income, and family data
print("\n FILTERING TO ASEC RECORDS ")
df_asec = df[df['ASECFLAG'] == 1].copy()
print(f"ASEC records: {df_asec.shape[0]:,} of {df.shape[0]:,} total")
print(f"Years in ASEC: {sorted(df_asec['YEAR'].unique())}")


# 4. FILTER TO STUDY YEARS 2022-2025

# using 2022-2025 to capture post-COVID labor market
# avoids the disruption of 2020-2022 pandemic years
print("\n FILTERING TO 2022-2025 ")
df_asec = df_asec[df_asec['YEAR'].isin([2022, 2023, 2024, 2025])].copy()
print(f"Records after year filter: {df_asec.shape[0]:,}")
print(f"Years confirmed: {sorted(df_asec['YEAR'].unique())}")

# 5. FILTER TO ANALYSIS POPULATION

# prime working age adults (25-54) to avoid confounding with school enrollment (younger) or early retirement (older)
print("\n FILTERING TO ANALYSIS POPULATION ")

df_pop = df_asec[
    (df_asec['AGE'] >= 25) &
    (df_asec['AGE'] <= 54)
].copy()

print(f"Prime age adults (25-54): {df_pop.shape[0]:,}")

# flag parents with at least one own child under 5 in household
# NCHLT5 = 0 means no children under 5
df_pop['has_young_child'] = (df_pop['NCHLT5'] > 0).astype(int)

parents = df_pop[df_pop['has_young_child'] == 1]
non_parents = df_pop[df_pop['has_young_child'] == 0]

print(f"Parents with child under 5: {len(parents):,}")
print(f"Without young child: {len(non_parents):,}")


# 6. CREATE ANALYSIS VARIABLES

print("\n CREATING ANALYSIS VARIABLES ")

# EMPSTAT codes in this extract:
# 1  = Armed Forces
# 10 = At work
# 12 = Has job not at work
# 21 = Unemployed experienced worker
# 22 = Unemployed new worker  
# 32 = NILF - wants a job
# 34 = NILF - does not want a job
# 36 = NILF - retired (but we're capping age at 54 so minimal)
df_pop['nilf'] = (df_pop['EMPSTAT'].isin([32, 34, 36])).astype(int)
df_pop['in_labor_force'] = (df_pop['EMPSTAT'].isin([1, 10, 12, 21, 22])).astype(int)
print(f"EMPSTAT value counts:\n{df_pop['EMPSTAT'].value_counts().sort_index()}")

# --- Education Categories ---
# EDUC codes collapsed into four meaningful groups
def categorize_educ(code):
    if code < 73:
        return '1_less_than_hs'
    elif code == 73:
        return '2_hs_diploma'
    elif code in [80, 81, 90, 91, 92]:
        return '3_some_college'
    elif code >= 111:
        return '4_bachelors_plus'
    else:
        return '3_some_college'

df_pop['educ_cat'] = df_pop['EDUC'].apply(categorize_educ)
print(f"\nEducation category counts:\n{df_pop['educ_cat'].value_counts().sort_index()}")

# --- Sex Label ---
df_pop['sex_label'] = df_pop['SEX'].map({1: 'Male', 2: 'Female'})

# 7. FINAL CHECKS

print("\n FINAL CHECKS ")

# Check 1 — no missing values in key variables
key_vars = ['EMPSTAT', 'EDUC', 'NCHLT5', 'AGE', 'ASECWT', 'sex_label']
missing = df_pop[key_vars].isnull().sum()
print(f"Missing values in key variables:\n{missing}")
assert missing.sum() == 0, "ERROR: Missing values found in key variables"
print("PASS: No missing values in key variables")

# Check 2 — age range is correct
assert df_pop['AGE'].min() >= 25, "ERROR: Ages below 25 found"
assert df_pop['AGE'].max() <= 54, "ERROR: Ages above 54 found"
print(f"PASS: Age range confirmed {df_pop['AGE'].min()}-{df_pop['AGE'].max()}")

# Check 3 — survey weights are positive
assert (df_pop['ASECWT'] > 0).all(), "ERROR: Non-positive survey weights found"
print(f"PASS: All survey weights positive")

# Check 4 — years are correct
assert set(df_pop['YEAR'].unique()) == {2022, 2023, 2024, 2025}, "ERROR: Unexpected years"
print(f"PASS: Years confirmed as 2023-2025")

# Check 5 — NILF and in_labor_force are mutually exclusive
overlap = ((df_pop['nilf'] == 1) & (df_pop['in_labor_force'] == 1)).sum()
assert overlap == 0, "ERROR: Records flagged as both NILF and in labor force"
print(f"PASS: NILF and in_labor_force are mutually exclusive")

print("\nAll QA checks passed.")

# 8. OUTPUT CLEAN DATA

print("\n SAVING CLEAN DATA ")

# select only the columns we need for downstream analysis
cols_to_keep = [
    'YEAR', 'STATEFIP', 'AGE', 'SEX', 'sex_label',
    'RACE', 'HISPAN', 'EDUC', 'educ_cat',
    'EMPSTAT', 'nilf', 'in_labor_force',
    'NCHLT5', 'has_young_child',
    'INCWAGE', 'ASECWT'
]

df_clean = df_pop[cols_to_keep].copy()

# save as Parquet — columnar format that's fast to query with DuckDB and standard in modern research data pipelines
output_path = CLEAN_DIR / "cps_clean.parquet"
df_clean.to_parquet(output_path, index=False)

print(f"Clean data saved to: {output_path}")
print(f"Final shape: {df_clean.shape[0]:,} rows x {df_clean.shape[1]} columns")
print(f"File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")

# final summary of analysis population
print("\n FINAL POPULATION SUMMARY ")
print(f"Total prime age adults (25-54): {len(df_clean):,}")
print(f"Parents with child under 5: {df_clean['has_young_child'].sum():,}")
print(f"Study years: {sorted(df_clean['YEAR'].unique())}")
print(f"NILF rate (unweighted): {df_clean['nilf'].mean():.1%}")
print(f"NILF rate among parents (unweighted): {df_clean[df_clean['has_young_child']==1]['nilf'].mean():.1%}")