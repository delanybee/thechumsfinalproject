"""
Interactive World Emissions Map v2
Shows total CO2 emissions by country and emissions covered by carbon pricing policies.
Features:
- Clickable countries with bar charts and data tables
- Year toggle (2000-2024)
- Global coverage tracker
"""

import pandas as pd
import numpy as np
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

YEARS = list(range(2000, 2025))

# EU ETS member countries (for distributing regional policy coverage)
EU_ETS_COUNTRIES = [
    "AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA",
    "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD",
    "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE", "ISL", "LIE", "NOR"
]

# Mapping from initiative names to ISO codes
# Format: initiative_name: list of (iso_code, type) where type is 'country', 'subnational', or 'regional'
INITIATIVE_MAPPING = {
    # National ETS
    "China national ETS": [("CHN", "country")],
    "Korea ETS": [("KOR", "country")],
    "New Zealand ETS": [("NZL", "country")],
    "Kazakhstan ETS": [("KAZ", "country")],
    "Indonesia ETS": [("IDN", "country")],
    "Mexico ETS": [("MEX", "country")],
    "UK ETS": [("GBR", "country")],
    "Switzerland ETS": [("CHE", "country")],
    "Montenegro ETS": [("MNE", "country")],
    "Germany ETS": [("DEU", "country")],
    "Austria ETS": [("AUT", "country")],
    
    # Regional ETS - will be distributed by GDP
    "EU ETS": [(c, "regional_eu") for c in EU_ETS_COUNTRIES],
    
    # Subnational - attributed to parent country
    "California CaT": [("USA", "subnational")],
    "RGGI": [("USA", "subnational")],
    "Washington CCA": [("USA", "subnational")],
    "Oregon ETS": [("USA", "subnational")],
    "Massachusetts ETS": [("USA", "subnational")],
    "Quebec CaT": [("CAN", "subnational")],
    "Ontario CaT": [("CAN", "subnational")],
    "Alberta TIER": [("CAN", "subnational")],
    "BC OBPS": [("CAN", "subnational")],
    "Saskatchewan OBPS": [("CAN", "subnational")],
    "Nova Scotia OBPS": [("CAN", "subnational")],
    "New Brunswick OBPS": [("CAN", "subnational")],
    "Ontario EPS": [("CAN", "subnational")],
    "Newfoundland and Labrador PSS": [("CAN", "subnational")],
    
    # China pilots - already covered by national
    "Beijing pilot ETS": [("CHN", "subnational")],
    "Shanghai pilot ETS": [("CHN", "subnational")],
    "Guangdong pilot ETS": [("CHN", "subnational")],
    "Shenzhen pilot ETS": [("CHN", "subnational")],
    "Hubei pilot ETS": [("CHN", "subnational")],
    "Tianjin pilot ETS": [("CHN", "subnational")],
    "Chongqing pilot ETS": [("CHN", "subnational")],
    "Fujian pilot ETS": [("CHN", "subnational")],
    
    # Japan
    "Tokyo CaT": [("JPN", "subnational")],
    "Saitama ETS": [("JPN", "subnational")],
    "Japan carbon tax": [("JPN", "country")],
    
    # Carbon Taxes - National
    "Finland carbon tax": [("FIN", "country")],
    "Sweden carbon tax": [("SWE", "country")],
    "Norway carbon tax": [("NOR", "country")],
    "Denmark carbon tax": [("DNK", "country")],
    "Poland carbon tax": [("POL", "country")],
    "Switzerland carbon tax": [("CHE", "country")],
    "Slovenia carbon tax": [("SVN", "country")],
    "Estonia carbon tax": [("EST", "country")],
    "Latvia carbon Tax": [("LVA", "country")],
    "Iceland carbon tax": [("ISL", "country")],
    "Ireland carbon tax": [("IRL", "country")],
    "France carbon tax": [("FRA", "country")],
    "Portugal carbon tax": [("PRT", "country")],
    "Spain carbon tax": [("ESP", "country")],
    "Luxembourg carbon tax": [("LUX", "country")],
    "Netherlands carbon tax": [("NLD", "country")],
    "UK Carbon Price Support": [("GBR", "country")],
    "Mexico carbon tax": [("MEX", "country")],
    "Chile carbon tax": [("CHL", "country")],
    "Colombia carbon tax": [("COL", "country")],
    "Argentina carbon tax": [("ARG", "country")],
    "South Africa carbon tax": [("ZAF", "country")],
    "Singapore carbon tax": [("SGP", "country")],
    "Ukraine carbon tax": [("UKR", "country")],
    "Albania carbon tax": [("ALB", "country")],
    "Liechtenstein carbon tax": [("LIE", "country")],
    "Uruguay CO2 tax": [("URY", "country")],
    "Taiwan carbon fee": [("TWN", "country")],
    "Israel carbon tax": [("ISR", "country")],
    "Hungary carbon tax": [("HUN", "country")],
    "Andorra carbon tax": [("AND", "country")],
    
    # Canadian carbon taxes
    "BC carbon tax": [("CAN", "subnational")],
    "Alberta carbon tax": [("CAN", "subnational")],
    "Canada federal fuel charge": [("CAN", "country")],
    "Canada federal OBPS": [("CAN", "country")],
    "New Brunswick carbon tax": [("CAN", "subnational")],
    "Newfoundland and Labrador carbon tax": [("CAN", "subnational")],
    "Northwest Territories carbon tax": [("CAN", "subnational")],
    "Prince Edward Island carbon tax": [("CAN", "subnational")],
    
    # Mexican subnational
    "Baja California carbon tax": [("MEX", "subnational")],
    "Durango carbon tax": [("MEX", "subnational")],
    "Guanajuato carbon tax": [("MEX", "subnational")],
    "Queretaro carbon tax": [("MEX", "subnational")],
    "State of Mexico carbon tax": [("MEX", "subnational")],
    "Tamaulipas carbon tax": [("MEX", "subnational")],
    "Yucatan carbon tax": [("MEX", "subnational")],
    "Zacatecas carbon tax": [("MEX", "subnational")],
    
    # Australia
    "Australia CPM": [("AUS", "country")],
    "Australia Safeguard Mechanism": [("AUS", "country")],
}

# Country name to ISO code mapping (for OWID data)
COUNTRY_TO_ISO = {
    "United States": "USA",
    "United Kingdom": "GBR",
    "China": "CHN",
    "Russia": "RUS",
    "Germany": "DEU",
    "Japan": "JPN",
    "India": "IND",
    "Canada": "CAN",
    "France": "FRA",
    "Brazil": "BRA",
    "South Korea": "KOR",
    "Australia": "AUS",
    "Mexico": "MEX",
    "Indonesia": "IDN",
    "Saudi Arabia": "SAU",
    "South Africa": "ZAF",
    "Turkey": "TUR",
    "Poland": "POL",
    "Italy": "ITA",
    "Spain": "ESP",
    "Iran": "IRN",
    "Thailand": "THA",
    "Argentina": "ARG",
    "Netherlands": "NLD",
    "Egypt": "EGY",
    "Vietnam": "VNM",
    "Pakistan": "PAK",
    "Malaysia": "MYS",
    "Kazakhstan": "KAZ",
    "Ukraine": "UKR",
    "United Arab Emirates": "ARE",
    "Belgium": "BEL",
    "Philippines": "PHL",
    "Czech Republic": "CZE",
    "Czechia": "CZE",
    "Colombia": "COL",
    "Chile": "CHL",
    "Austria": "AUT",
    "Singapore": "SGP",
    "Israel": "ISR",
    "Norway": "NOR",
    "Sweden": "SWE",
    "Denmark": "DNK",
    "Finland": "FIN",
    "Ireland": "IRL",
    "Portugal": "PRT",
    "Greece": "GRC",
    "Romania": "ROU",
    "Hungary": "HUN",
    "New Zealand": "NZL",
    "Switzerland": "CHE",
}


def load_emissions_data():
    """Load OWID CO2 emissions data."""
    print("Loading emissions data...")
    df = pd.read_csv("owid-co2-data.csv")
    
    # Filter to relevant years and columns
    df = df[df['year'].isin(YEARS)]
    
    # Use iso_code if available, otherwise map country name
    df['iso'] = df['iso_code'].fillna(df['country'].map(COUNTRY_TO_ISO))
    
    # Keep only rows with valid ISO codes (3 letters)
    df = df[df['iso'].str.len() == 3]
    
    # Select relevant columns
    cols = ['iso', 'country', 'year', 'co2', 'co2_per_capita', 'share_global_co2', 'population', 'gdp']
    df = df[[c for c in cols if c in df.columns]]
    
    return df


def load_compliance_data():
    """Load carbon pricing compliance data."""
    print("Loading compliance data...")
    df = pd.read_csv("Compliance Emissions.csv", skiprows=2)
    df = df.rename(columns={df.columns[0]: 'initiative'})
    
    # Get year columns
    year_cols = [str(y) for y in YEARS if str(y) in df.columns]
    
    return df, year_cols


def load_gdp_data():
    """Load GDP data for distributing regional policies."""
    print("Loading GDP data...")
    df = pd.read_csv("API_NY.GDP.MKTP.CD_DS2_en_excel_v2_3.csv", skiprows=3)
    
    # Rename columns
    df = df.rename(columns={'Country Code': 'iso'})
    
    # Melt to long format
    year_cols = [str(y) for y in YEARS if str(y) in df.columns]
    df_long = df.melt(
        id_vars=['iso'],
        value_vars=year_cols,
        var_name='year',
        value_name='gdp'
    )
    df_long['year'] = df_long['year'].astype(int)
    
    return df_long


def calculate_country_coverage(compliance_df, year_cols, gdp_df, emissions_df):
    """
    Calculate the % of global emissions covered by each country's carbon pricing.
    Handles regional policies by distributing based on GDP.
    """
    print("Calculating country coverage...")
    
    # Initialize result dictionary: {year: {iso: coverage}}
    coverage = {year: {} for year in YEARS}
    
    for _, row in compliance_df.iterrows():
        initiative = row['initiative']
        if pd.isna(initiative):
            continue
        
        # Find matching initiative in our mapping
        matched_mapping = None
        for init_name, mapping in INITIATIVE_MAPPING.items():
            if init_name.lower() in initiative.lower() or initiative.lower() in init_name.lower():
                matched_mapping = mapping
                break
        
        if not matched_mapping:
            continue
        
        for year_str in year_cols:
            year = int(year_str)
            if year not in YEARS:
                continue
                
            value = row.get(year_str, 0)
            if pd.isna(value) or value == 0:
                continue
            
            try:
                value = float(value)
            except:
                continue
            
            # Check if this is a regional policy (EU ETS)
            is_regional = any(t == "regional_eu" for _, t in matched_mapping)
            
            if is_regional:
                # Distribute by GDP among member countries
                countries_in_mapping = [iso for iso, _ in matched_mapping]
                
                # Get GDP for these countries in this year
                gdp_subset = gdp_df[(gdp_df['iso'].isin(countries_in_mapping)) & 
                                    (gdp_df['year'] == year)]
                total_gdp = gdp_subset['gdp'].sum()
                
                if total_gdp > 0:
                    for _, gdp_row in gdp_subset.iterrows():
                        iso = gdp_row['iso']
                        country_gdp = gdp_row['gdp']
                        if pd.notna(country_gdp) and country_gdp > 0:
                            share = country_gdp / total_gdp
                            country_coverage = value * share
                            
                            if iso not in coverage[year]:
                                coverage[year][iso] = 0
                            coverage[year][iso] += country_coverage
            else:
                # Direct attribution to country
                for iso, _ in matched_mapping:
                    if iso not in coverage[year]:
                        coverage[year][iso] = 0
                    # For subnational, we sum them up for the country
                    coverage[year][iso] += value
    
    return coverage


def build_country_data(emissions_df, coverage_dict):
    """Build comprehensive country data for each year."""
    print("Building country datasets...")
    
    country_data = {}
    
    for year in YEARS:
        year_emissions = emissions_df[emissions_df['year'] == year].copy()
        
        # Calculate global total for this year
        global_co2 = year_emissions['co2'].sum()
        
        year_data = {}
        for _, row in year_emissions.iterrows():
            iso = row['iso']
            
            co2 = row.get('co2', 0) or 0
            share_global = row.get('share_global_co2', 0) or 0
            if share_global == 0 and global_co2 > 0:
                share_global = (co2 / global_co2) * 100
            
            # Get coverage for this country
            policy_coverage = coverage_dict.get(year, {}).get(iso, 0)
            # Convert from share of global to actual coverage
            policy_coverage_pct = policy_coverage * 100  # Already in fraction
            
            year_data[iso] = {
                'country': row.get('country', iso),
                'co2_mt': round(co2, 2),
                'share_global_pct': round(share_global, 4),
                'policy_coverage_pct': round(policy_coverage_pct, 4),
                'co2_covered_mt': round(co2 * policy_coverage, 2) if policy_coverage > 0 else 0,
            }
        
        country_data[year] = {
            'global_co2': round(global_co2, 2),
            'countries': year_data
        }
    
    return country_data


def calculate_global_coverage(country_data):
    """Calculate global % of emissions covered by policies for each year."""
    global_coverage = {}
    for year, data in country_data.items():
        total_coverage = sum(
            c['policy_coverage_pct'] for c in data['countries'].values()
        )
        global_coverage[year] = round(total_coverage, 2)
    return global_coverage


def generate_html(country_data, global_coverage):
    """Generate the interactive HTML map."""
    print("Generating HTML...")
    
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Emissions & Carbon Pricing Map</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #1a1a2e; 
            color: #eee;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #0f3460;
        }
        .header h1 { color: #e94560; margin-bottom: 5px; }
        .header p { color: #aaa; font-size: 14px; }
        
        .container { display: flex; flex-wrap: wrap; padding: 20px; gap: 20px; }
        
        .map-section { 
            flex: 2; 
            min-width: 600px;
            background: #16213e;
            border-radius: 10px;
            padding: 15px;
        }
        
        .sidebar {
            flex: 1;
            min-width: 350px;
            background: #16213e;
            border-radius: 10px;
            padding: 20px;
        }
        
        .year-control {
            background: #0f3460;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .year-control label { 
            display: block; 
            margin-bottom: 8px; 
            color: #e94560;
            font-weight: bold;
        }
        .year-slider {
            width: 100%;
            height: 8px;
            -webkit-appearance: none;
            background: #1a1a2e;
            border-radius: 4px;
            outline: none;
        }
        .year-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            background: #e94560;
            border-radius: 50%;
            cursor: pointer;
        }
        .year-display {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #e94560;
            margin-top: 10px;
        }
        
        .global-tracker {
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 15px;
            border: 1px solid #e94560;
        }
        .global-tracker .label { color: #aaa; font-size: 12px; text-transform: uppercase; }
        .global-tracker .value { 
            font-size: 48px; 
            font-weight: bold; 
            color: #e94560;
            text-shadow: 0 0 20px rgba(233, 69, 96, 0.5);
        }
        .global-tracker .unit { color: #aaa; font-size: 14px; }
        
        .country-details {
            background: #0f3460;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }
        .country-details.active { display: block; }
        .country-details h3 { 
            color: #e94560; 
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #1a1a2e;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
            font-size: 13px;
        }
        .data-table th, .data-table td {
            padding: 8px 10px;
            text-align: left;
            border-bottom: 1px solid #1a1a2e;
        }
        .data-table th { color: #e94560; font-weight: normal; }
        .data-table td { color: #fff; }
        
        .chart-container {
            height: 200px;
            margin-top: 15px;
        }
        
        .placeholder {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .placeholder i { font-size: 48px; margin-bottom: 15px; display: block; }
        
        .legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 10px;
            font-size: 12px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .legend-color {
            width: 20px;
            height: 12px;
            border-radius: 2px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Global CO₂ Emissions & Carbon Pricing Coverage</h1>
        <p>Click on any country to see detailed emissions and policy coverage data</p>
    </div>
    
    <div class="container">
        <div class="map-section">
            <div id="map"></div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #f7fbff;"></div>
                    <span>No Policy</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #6baed6;"></div>
                    <span>Low Coverage</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #08519c;"></div>
                    <span>High Coverage</span>
                </div>
            </div>
        </div>
        
        <div class="sidebar">
            <div class="year-control">
                <label>SELECT YEAR</label>
                <input type="range" class="year-slider" id="yearSlider" 
                       min="2000" max="2024" value="2024" step="1">
                <div class="year-display" id="yearDisplay">2024</div>
            </div>
            
            <div class="global-tracker">
                <div class="label">Global Emissions Covered by Carbon Pricing</div>
                <div class="value" id="globalCoverage">23.4</div>
                <div class="unit">% of global CO₂ emissions</div>
            </div>
            
            <div class="country-details" id="countryDetails">
                <h3 id="countryName">Select a Country</h3>
                
                <table class="data-table">
                    <tr>
                        <th>Total CO₂ Emissions</th>
                        <td id="totalEmissions">-</td>
                    </tr>
                    <tr>
                        <th>Share of Global Emissions</th>
                        <td id="shareGlobal">-</td>
                    </tr>
                    <tr>
                        <th>Emissions Covered by Policy</th>
                        <td id="emissionsCovered">-</td>
                    </tr>
                    <tr>
                        <th>Coverage Rate</th>
                        <td id="coverageRate">-</td>
                    </tr>
                </table>
                
                <div class="chart-container" id="barChart"></div>
            </div>
            
            <div class="placeholder" id="placeholder">
                <i>🌍</i>
                <p>Click on a country on the map to view detailed emissions and carbon pricing data</p>
            </div>
        </div>
    </div>
    
    <script>
        // Country data by year
        const countryData = ''' + json.dumps(country_data) + ''';
        const globalCoverage = ''' + json.dumps(global_coverage) + ''';
        
        let currentYear = 2024;
        let selectedCountry = null;
        
        // Initialize map
        function initMap() {
            updateMap();
        }
        
        function updateMap() {
            const yearData = countryData[currentYear];
            if (!yearData) return;
            
            const countries = yearData.countries;
            const locations = Object.keys(countries);
            const emissions = locations.map(iso => countries[iso].co2_mt);
            const coverage = locations.map(iso => countries[iso].policy_coverage_pct);
            const names = locations.map(iso => countries[iso].country);
            const hoverText = locations.map(iso => {
                const c = countries[iso];
                return `<b>${c.country}</b><br>` +
                       `CO₂: ${c.co2_mt.toLocaleString()} Mt<br>` +
                       `Global Share: ${c.share_global_pct.toFixed(2)}%<br>` +
                       `Policy Coverage: ${c.policy_coverage_pct.toFixed(2)}%`;
            });
            
            const data = [{
                type: 'choropleth',
                locations: locations,
                z: coverage,
                text: hoverText,
                hoverinfo: 'text',
                colorscale: [
                    [0, '#f7fbff'],
                    [0.01, '#deebf7'],
                    [0.1, '#c6dbef'],
                    [0.3, '#6baed6'],
                    [0.5, '#3182bd'],
                    [1, '#08519c']
                ],
                zmin: 0,
                zmax: 20,
                showscale: true,
                colorbar: {
                    title: 'Coverage %',
                    thickness: 15,
                    len: 0.6,
                    bgcolor: 'rgba(0,0,0,0)',
                    tickfont: { color: '#aaa' },
                    titlefont: { color: '#aaa' }
                },
                marker: {
                    line: {
                        color: '#1a1a2e',
                        width: 0.5
                    }
                }
            }];
            
            const layout = {
                geo: {
                    showframe: false,
                    showcoastlines: true,
                    coastlinecolor: '#333',
                    projection: { type: 'natural earth' },
                    bgcolor: '#1a1a2e',
                    landcolor: '#2a2a4e',
                    showocean: true,
                    oceancolor: '#0f1525',
                    showlakes: false,
                    showcountries: true,
                    countrycolor: '#333'
                },
                paper_bgcolor: '#16213e',
                plot_bgcolor: '#16213e',
                margin: { t: 10, b: 10, l: 10, r: 10 },
                height: 500
            };
            
            const config = {
                displayModeBar: false,
                responsive: true
            };
            
            Plotly.newPlot('map', data, layout, config);
            
            // Add click handler
            document.getElementById('map').on('plotly_click', function(data) {
                if (data.points && data.points[0]) {
                    const iso = data.points[0].location;
                    showCountryDetails(iso);
                }
            });
            
            // Update global coverage
            document.getElementById('globalCoverage').textContent = 
                globalCoverage[currentYear].toFixed(1);
            
            // Update selected country if one is selected
            if (selectedCountry) {
                showCountryDetails(selectedCountry);
            }
        }
        
        function showCountryDetails(iso) {
            selectedCountry = iso;
            const yearData = countryData[currentYear];
            if (!yearData || !yearData.countries[iso]) {
                return;
            }
            
            const country = yearData.countries[iso];
            
            // Show details panel
            document.getElementById('placeholder').style.display = 'none';
            document.getElementById('countryDetails').classList.add('active');
            
            // Update text data
            document.getElementById('countryName').textContent = country.country;
            document.getElementById('totalEmissions').textContent = 
                country.co2_mt.toLocaleString() + ' Mt CO₂';
            document.getElementById('shareGlobal').textContent = 
                country.share_global_pct.toFixed(2) + '%';
            document.getElementById('emissionsCovered').textContent = 
                country.co2_covered_mt.toLocaleString() + ' Mt CO₂';
            document.getElementById('coverageRate').textContent = 
                country.policy_coverage_pct.toFixed(2) + '%';
            
            // Create bar chart
            const barData = [
                {
                    x: ['Share of Global Emissions', 'Covered by Carbon Pricing'],
                    y: [country.share_global_pct, country.policy_coverage_pct],
                    type: 'bar',
                    marker: {
                        color: ['#3182bd', '#e94560']
                    },
                    text: [
                        country.share_global_pct.toFixed(2) + '%',
                        country.policy_coverage_pct.toFixed(2) + '%'
                    ],
                    textposition: 'outside',
                    textfont: { color: '#fff' }
                }
            ];
            
            const barLayout = {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: { t: 20, b: 60, l: 40, r: 20 },
                yaxis: {
                    gridcolor: '#333',
                    tickfont: { color: '#aaa' },
                    title: { text: '%', font: { color: '#aaa' } }
                },
                xaxis: {
                    tickfont: { color: '#aaa', size: 10 }
                },
                showlegend: false,
                height: 200
            };
            
            Plotly.newPlot('barChart', barData, barLayout, { displayModeBar: false });
        }
        
        // Year slider handler
        document.getElementById('yearSlider').addEventListener('input', function(e) {
            currentYear = parseInt(e.target.value);
            document.getElementById('yearDisplay').textContent = currentYear;
            updateMap();
        });
        
        // Initialize
        initMap();
    </script>
</body>
</html>'''
    
    return html_template


def main():
    """Main function to build the emissions map."""
    
    # Load all data
    emissions_df = load_emissions_data()
    compliance_df, year_cols = load_compliance_data()
    gdp_df = load_gdp_data()
    
    print(f"Loaded {len(emissions_df)} emission records")
    print(f"Loaded {len(compliance_df)} compliance initiatives")
    print(f"Loaded {len(gdp_df)} GDP records")
    
    # Calculate coverage by country
    coverage_dict = calculate_country_coverage(compliance_df, year_cols, gdp_df, emissions_df)
    
    # Build country data
    country_data = build_country_data(emissions_df, coverage_dict)
    
    # Calculate global coverage
    global_coverage = calculate_global_coverage(country_data)
    
    print("\nGlobal coverage by year:")
    for year in [2000, 2005, 2010, 2015, 2020, 2024]:
        if year in global_coverage:
            print(f"  {year}: {global_coverage[year]:.1f}%")
    
    # Generate HTML
    html_content = generate_html(country_data, global_coverage)
    
    # Save to file (use temp directory to avoid OneDrive issues)
    import os
    output_path = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'emissions_map_v2.html')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✓ Map saved to: {output_path}")
    print("Open the file in your browser to view the interactive map.")
    
    # Also save to user folder
    user_path = os.path.join(os.path.expanduser('~'), 'emissions_map_v2.html')
    try:
        with open(user_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Also saved to: {user_path}")
    except:
        pass
    
    return output_path


if __name__ == "__main__":
    main()
