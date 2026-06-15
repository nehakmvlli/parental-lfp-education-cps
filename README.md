# Parental Labor Force Participation and Educational Attainment
**Neha Kallamvalli** | IPUMS CPS ASEC 2022–2025

## Overview
This project examines what share of parents with young children are out of the labor force, and whether that varies by education level and sex. Using nationally representative survey data from the Current Population Survey, the analysis finds a gender gap in labor force non-participation, one that education narrows but doesn't seem to close.

## Data
This project uses IPUMS CPS ASEC data (2022–2025). Data is not included in this repository per the IPUMS data use agreement. To replicate, register at https://cps.ipums.org and extract the following variables for ASEC samples:

`AGE, SEX, RACE, HISPAN, EDUC, EMPSTAT, INCWAGE, WTFINL, ASECWT, NCHLT5, RELATE, STATEFIP`

## Project Structure
- `python/01_etl_cleaning.py` — ingests raw IPUMS extract, cleans and filters to analysis population, runs sanity code checks, outputs clean Parquet file
- `sql/02_analysis_queries.py` — uses DuckDB to query clean Parquet and produce weighted summary statistics
- `r/03_analysis_viz.R` — builds all visualizations and regression table
- `parental_lfp_analysis.ipynb` — full analysis narrative and findings as a Jupyter notebook
- `outputs/figures/` — all charts and tables

## Tools
Python 3.11 | R 4.3 | DuckDB | IPUMS CPS | ggplot2 | survey

## Citation
Sarah Flood, Miriam King, Renae Rodgers, Steven Ruggles, J. Robert Warren, Daniel Backman, Etienne Breton, Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, David Van Riper, and Kari C.W. Williams. IPUMS CPS: Version 13.0 [dataset]. Minneapolis, MN: IPUMS, 2025. https://doi.org/10.18128/D030.V13.0