# Global CO₂ Emissions & Carbon Pricing Analysis

An interactive visualization project exploring the relationship between global CO₂ emissions and carbon pricing policies (carbon taxes and emissions trading systems).

## Project Summary

This project answers the question: **"Does Carbon Pricing Work?"** by combining three datasets to visualize:
- Total CO₂ emissions by country (2000-2024)
- Carbon pricing policy coverage by country
- The growth of global emissions covered by economic policies

## Data Sources

| Dataset | Description | Source |
|---------|-------------|--------|
| `owid-co2-data.csv` | Comprehensive CO₂ emissions data (1750-present), 50,413 rows, 79 variables | [Our World in Data](https://github.com/owid/co2-data) |
| `Compliance Emissions.csv` | Share of global emissions covered by 92 carbon pricing instruments (1990-2025) | EDGAR Database |
| `API_NY.GDP.MKTP.CD_DS2_en_excel_v2_3.csv` | GDP by country (1960-2025), used for distributing regional policies | World Bank |

## Key Findings

**Global Carbon Pricing Coverage Growth:**
- 2000: 0.7% of global emissions
- 2005: 5.7% (EU ETS launched)
- 2010: 5.7%
- 2015: 11.8%
- 2020: 13.9%
- 2024: 28.6%

**54 countries** now have some form of carbon pricing as of 2025.

## Visualizations

### 1. Carbon Pricing Spread Map (`carbon_pricing_map.py`)
Animated choropleth showing the geographic spread of carbon taxes and ETS from 1990-2025.

### 2. Emissions & Coverage Interactive Map (`emissions_map_v2.py`)
Full-featured interactive map with:
- Year slider (2000-2024)
- Click on any country for detailed data
- Bar charts: % global emissions vs % covered by policy
- Data table: Total CO₂, share of global, emissions covered
- Global coverage tracker (updates with year)
- Regional policies distributed by GDP (e.g., EU ETS)
- Subnational policies attributed to parent country

## Technical Details

- **Language:** Python 3.12
- **Visualization:** Plotly (interactive HTML output)
- **Output:** Self-contained HTML files (no server required)

## Files

```
├── owid-co2-data.csv              # Emissions data
├── Compliance Emissions.csv        # Carbon pricing coverage data
├── API_NY.GDP.MKTP.CD_DS2_en_excel_v2_3.csv  # GDP data
├── carbon_pricing_map.py          # Animated spread visualization
├── emissions_map_v2.py            # Interactive emissions/coverage map
├── dataset_summary.txt            # Dataset descriptions
└── README.md                      # This file
```

## Usage

```bash
# Install dependencies
pip install pandas plotly

# Generate animated carbon pricing map
python carbon_pricing_map.py

# Generate interactive emissions map
python emissions_map_v2.py
```

Output HTML files can be opened directly in any modern browser.

## Authors

The Chums Final Project Team
