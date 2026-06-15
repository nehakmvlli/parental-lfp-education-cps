# Parental Labor Force Participation Analysis
# Use DuckDB to query clean Parquet data and produce weighted
# summary statistics by education level and sex

import duckdb
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_FILE = BASE_DIR / "data" / "clean" / "cps_clean.parquet"
OUTPUT_DIR = BASE_DIR / "outputs"

# connect to DuckDB, no database file needed, runs in memory
con = duckdb.connect()

print(f"Reading from: {CLEAN_FILE}")

# QUERY 1 — Overall NILF rate by young parent status

q1 = con.execute(f"""
    SELECT
        has_young_child,
        ROUND(
            SUM(nilf * ASECWT) / SUM(ASECWT) * 100, 1
        ) AS weighted_nilf_pct,
        COUNT(*) AS n_records
    FROM read_parquet('{CLEAN_FILE}')
    GROUP BY has_young_child
    ORDER BY has_young_child
""").df()

print("\n--- Query 1: Weighted NILF Rate by Young Parent Status ---")
print(q1.to_string(index=False))

# QUERY 2 — NILF rate by education level among parents with young children

q2 = con.execute(f"""
    SELECT
        educ_cat,
        ROUND(
            SUM(nilf * ASECWT) / SUM(ASECWT) * 100, 1
        ) AS weighted_nilf_pct,
        COUNT(*) AS n_records
    FROM read_parquet('{CLEAN_FILE}')
    WHERE has_young_child = 1
    GROUP BY educ_cat
    ORDER BY educ_cat
""").df()

print("\n--- Query 2: Weighted NILF Rate by Education (Parents Only) ---")
print(q2.to_string(index=False))

# QUERY 3 — NILF rate by education AND sex among parents with young children

q3 = con.execute(f"""
    SELECT
        educ_cat,
        sex_label,
        ROUND(
            SUM(nilf * ASECWT) / SUM(ASECWT) * 100, 1
        ) AS weighted_nilf_pct,
        COUNT(*) AS n_records
    FROM read_parquet('{CLEAN_FILE}')
    WHERE has_young_child = 1
    GROUP BY educ_cat, sex_label
    ORDER BY educ_cat, sex_label
""").df()

print("\n--- Query 3: Weighted NILF Rate by Education AND Sex (Parents Only) ---")
print(q3.to_string(index=False))


# QUERY 4 — Trend over time: NILF rate by year among parents

q4 = con.execute(f"""
    SELECT
        YEAR,
        ROUND(
            SUM(nilf * ASECWT) / SUM(ASECWT) * 100, 1
        ) AS weighted_nilf_pct,
        COUNT(*) AS n_records
    FROM read_parquet('{CLEAN_FILE}')
    WHERE has_young_child = 1
    GROUP BY YEAR
    ORDER BY YEAR
""").df()

print("\n--- Query 4: NILF Rate Trend Among Parents (2022-2025) ---")
print(q4.to_string(index=False))

q2.to_csv(OUTPUT_DIR / "nilf_by_educ.csv", index=False)
q3.to_csv(OUTPUT_DIR / "nilf_by_educ_sex.csv", index=False)
q4.to_csv(OUTPUT_DIR / "nilf_trend.csv", index=False)

print("\n OUTPUT FILES SAVED ")
print(f"nilf_by_educ.csv")
print(f"nilf_by_educ_sex.csv")
print(f"nilf_trend.csv")

# QUERY 5 — NILF rate by year AND sex among parents with young children

q5 = con.execute(f"""
    SELECT
        YEAR,
        sex_label,
        ROUND(
            SUM(nilf * ASECWT) / SUM(ASECWT) * 100, 1
        ) AS weighted_nilf_pct,
        COUNT(*) AS n_records
    FROM read_parquet('{CLEAN_FILE}')
    WHERE has_young_child = 1
    GROUP BY YEAR, sex_label
    ORDER BY YEAR, sex_label
""").df()

print("\n--- Query 5: NILF Rate by Year AND Sex (Parents Only) ---")
print(q5.to_string(index=False))


# QUERY 6 — NILF rate by year AND education level among MOTHERS only

q6 = con.execute(f"""
    SELECT
        YEAR,
        educ_cat,
        ROUND(
            SUM(nilf * ASECWT) / SUM(ASECWT) * 100, 1
        ) AS weighted_nilf_pct,
        COUNT(*) AS n_records
    FROM read_parquet('{CLEAN_FILE}')
    WHERE has_young_child = 1
        AND sex_label = 'Female'
    GROUP BY YEAR, educ_cat
    ORDER BY YEAR, educ_cat
""").df()

print("\n--- Query 6: NILF Rate by Year AND Education (Mothers Only) ---")
print(q6.to_string(index=False))

# QUERY 7 — NILF rate among bachelor's degree MOTHERS by state

q7 = con.execute(f"""
    SELECT
        STATEFIP,
        ROUND(
            SUM(nilf * ASECWT) / SUM(ASECWT) * 100, 1
        ) AS weighted_nilf_pct,
        COUNT(*) AS n_records
    FROM read_parquet('{CLEAN_FILE}')
    WHERE has_young_child = 1
        AND sex_label = 'Female'
        AND educ_cat = '4_bachelors_plus'
    GROUP BY STATEFIP
    ORDER BY weighted_nilf_pct DESC
""").df()

print("\n--- Query 7: NILF Rate Among Bachelor's Degree Mothers by State ---")
print(q7.to_string(index=False))

q5.to_csv(OUTPUT_DIR / "nilf_trend_by_sex.csv", index=False)
q6.to_csv(OUTPUT_DIR / "nilf_trend_mothers_by_educ.csv", index=False)
q7.to_csv(OUTPUT_DIR / "nilf_bachelors_mothers_by_state.csv", index=False)

print("\n NEW OUTPUT FILES SAVED ")
print("nilf_trend_by_sex.csv")
print("nilf_trend_mothers_by_educ.csv")
print("nilf_bachelors_mothers_by_state.csv")


con.close()