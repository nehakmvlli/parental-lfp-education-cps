# Parental Labor Force Participation and Educational Attainment
**Neha Kallamvalli**

## Overview
What share of parents, especially mothers, with young children are out of the labor force, and does that vary by education level?

For parents of young children, it is no surprise that the decision to work is rarely straightforward. Childcare costs, salary progression, caregiving demands, early years
with their kid, are just a few of the many thoughts parents might be absorbed by at that point in time. Understanding tradeoffs can be complicated too. It is not hard to imagine
that these pressures also fall unevenly across different education levels and between mothers and fathers. This analysis uses nationally representative survey data to observe
and examine who is out of the labor force, how education can impact that, and how the pattern has shifted between 2022 and 2025.

Please take a look at parental_lfp_analysis.pdf in this repo for the full analysis!

## Data
This project uses IPUMS CPS ASEC data (2022–2025). I have not included the data in this repo per the IPUMS data use agreement. To replicate, please register at IPU
MS and extract the following variables:

`AGE, SEX, RACE, HISPAN, EDUC, EMPSTAT, INCWAGE, WTFINL, ASECWT, NCHLT5, RELATE, STATEFIP`

## Project Structure
- `python/01_etl_cleaning.py` — ingests raw IPUMS extract, cleans and filters to analysis population, runs sanity code checks, outputs clean Parquet file
- `sql/02_analysis_queries.py` — uses DuckDB to query clean Parquet and produce weighted summary statistics
- `r/03_analysis_viz.R` — builds all visualizations and regression table
- `parental_lfp_analysis.ipynb` — full analysis narrative and findings as a Jupyter notebook, a pdf version is included as well
- `outputs/figures/` — all charts and tables

## Tools
Python 3.11, R 4.3, DuckDB

## Citation
Sarah Flood, Miriam King, Renae Rodgers, Steven Ruggles, J. Robert Warren, Daniel Backman, Etienne Breton, Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, David Van Riper, and Kari C.W. Williams. IPUMS CPS: Version 13.0 [dataset]. Minneapolis, MN: IPUMS, 2025. https://doi.org/10.18128/D030.V13.0


Thank you!