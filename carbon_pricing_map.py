"""
Animated Choropleth Map: Global Spread of Carbon Pricing (1990-2025)
Creates an interactive visualization showing how carbon taxes and ETS systems
spread across the world over time.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Mapping from initiative names to ISO-3 country codes
# Note: EU ETS countries joined at different times, simplified here to 2005 launch
INITIATIVE_TO_COUNTRIES = {
    # Emissions Trading Systems (ETS)
    "EU ETS": ["AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", 
               "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD", 
               "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE", "ISL", "LIE", "NOR"],
    "UK ETS": ["GBR"],
    "Switzerland ETS": ["CHE"],
    "China national ETS": ["CHN"],
    "Korea ETS": ["KOR"],
    "Kazakhstan ETS": ["KAZ"],
    "New Zealand ETS": ["NZL"],
    "Australia CPM": ["AUS"],  # Carbon Pricing Mechanism (2012-2014)
    "Australia Safeguard Mechanism": ["AUS"],
    "Indonesia ETS": ["IDN"],
    "Montenegro ETS": ["MNE"],
    "Mexico ETS": ["MEX"],
    "Germany ETS": ["DEU"],  # National ETS for transport/buildings
    "Austria ETS": ["AUT"],  # National ETS
    
    # Regional/Provincial ETS
    "California CaT": ["USA"],
    "RGGI": ["USA"],  # Regional Greenhouse Gas Initiative (Northeast US)
    "Quebec CaT": ["CAN"],
    "Ontario CaT": ["CAN"],
    "Alberta TIER": ["CAN"],
    "BC OBPS": ["CAN"],
    "Washington CCA": ["USA"],
    "Oregon ETS": ["USA"],
    "Massachusetts ETS": ["USA"],
    
    # China Pilot ETS
    "Beijing pilot ETS": ["CHN"],
    "Shanghai pilot ETS": ["CHN"],
    "Guangdong pilot ETS": ["CHN"],
    "Shenzhen pilot ETS": ["CHN"],
    "Hubei pilot ETS": ["CHN"],
    "Tianjin pilot ETS": ["CHN"],
    "Chongqing pilot ETS": ["CHN"],
    "Fujian pilot ETS": ["CHN"],
    
    # Tokyo/Saitama
    "Tokyo CaT": ["JPN"],
    "Saitama ETS": ["JPN"],
    
    # Carbon Taxes
    "Finland carbon tax": ["FIN"],
    "Sweden carbon tax": ["SWE"],
    "Norway carbon tax": ["NOR"],
    "Denmark carbon tax": ["DNK"],
    "Poland carbon tax": ["POL"],
    "Switzerland carbon tax": ["CHE"],
    "Slovenia carbon tax": ["SVN"],
    "Estonia carbon tax": ["EST"],
    "Latvia carbon Tax": ["LVA"],
    "Iceland carbon tax": ["ISL"],
    "Ireland carbon tax": ["IRL"],
    "France carbon tax": ["FRA"],
    "Portugal carbon tax": ["PRT"],
    "Spain carbon tax": ["ESP"],
    "Luxembourg carbon tax": ["LUX"],
    "Netherlands carbon tax": ["NLD"],
    "UK Carbon Price Support": ["GBR"],
    "Japan carbon tax": ["JPN"],
    "Mexico carbon tax": ["MEX"],
    "Chile carbon tax": ["CHL"],
    "Colombia carbon tax": ["COL"],
    "Argentina carbon tax": ["ARG"],
    "South Africa carbon tax": ["ZAF"],
    "Singapore carbon tax": ["SGP"],
    "Ukraine carbon tax": ["UKR"],
    "Albania carbon tax": ["ALB"],
    "Liechtenstein carbon tax": ["LIE"],
    "Uruguay CO2 tax": ["URY"],
    "Taiwan carbon fee": ["TWN"],
    "Israel carbon tax": ["ISR"],
    "Hungary carbon tax": ["HUN"],
    "Andorra carbon tax": ["AND"],
    
    # Canadian Provincial Carbon Taxes
    "BC carbon tax": ["CAN"],
    "Alberta carbon tax": ["CAN"],
    "Canada federal fuel charge": ["CAN"],
    "Canada federal OBPS": ["CAN"],
    "New Brunswick carbon tax": ["CAN"],
    "Newfoundland and Labrador carbon tax": ["CAN"],
    "Northwest Territories carbon tax": ["CAN"],
    "Prince Edward Island carbon tax": ["CAN"],
    "Saskatchewan OBPS": ["CAN"],
    "Nova Scotia OBPS": ["CAN"],
    "Newfoundland and Labrador PSS": ["CAN"],
    "New Brunswick OBPS": ["CAN"],
    "Ontario EPS": ["CAN"],
}


def load_compliance_data(filepath):
    """Load and parse the Compliance Emissions CSV file."""
    # Read CSV, skip the first 2 header rows
    df = pd.read_csv(filepath, skiprows=2)
    
    # First column is initiative name
    df = df.rename(columns={df.columns[0]: 'initiative'})
    
    # Get year columns (1990-2025)
    year_cols = [col for col in df.columns if col.isdigit() or (isinstance(col, str) and col.replace('.', '').isdigit())]
    
    return df, year_cols


def create_country_year_data(df, year_cols):
    """Transform initiative data to country-year format with coverage levels."""
    records = []
    
    for _, row in df.iterrows():
        initiative = row['initiative']
        if pd.isna(initiative):
            continue
            
        # Find matching countries for this initiative
        countries = []
        for init_name, country_codes in INITIATIVE_TO_COUNTRIES.items():
            if init_name.lower() in initiative.lower() or initiative.lower() in init_name.lower():
                countries.extend(country_codes)
                break
        
        if not countries:
            # Try partial match
            for init_name, country_codes in INITIATIVE_TO_COUNTRIES.items():
                if any(word in initiative.lower() for word in init_name.lower().split()):
                    countries.extend(country_codes)
                    break
        
        # Create records for each country and year
        for year in year_cols:
            coverage = row.get(year, 0)
            if pd.isna(coverage):
                coverage = 0
            try:
                coverage = float(coverage)
            except:
                coverage = 0
                
            if coverage > 0:
                for country in set(countries):  # Use set to avoid duplicates
                    records.append({
                        'iso_code': country,
                        'year': int(float(year)),
                        'initiative': initiative,
                        'coverage': coverage
                    })
    
    return pd.DataFrame(records)


def aggregate_country_coverage(df):
    """Aggregate coverage by country and year (sum of all initiatives)."""
    # Group by country and year, sum coverage
    agg_df = df.groupby(['iso_code', 'year']).agg({
        'coverage': 'sum',
        'initiative': lambda x: ', '.join(set(x))
    }).reset_index()
    
    # Cap coverage at 1 (100%)
    agg_df['coverage'] = agg_df['coverage'].clip(upper=1.0)
    
    # Convert coverage to percentage
    agg_df['coverage_pct'] = agg_df['coverage'] * 100
    
    return agg_df


def fill_missing_years(df, start_year=1990, end_year=2025):
    """Ensure all years are present for animation continuity."""
    all_countries = df['iso_code'].unique()
    all_years = range(start_year, end_year + 1)
    
    # Create a complete grid of country-years
    full_grid = pd.MultiIndex.from_product([all_countries, all_years], 
                                            names=['iso_code', 'year'])
    full_df = pd.DataFrame(index=full_grid).reset_index()
    
    # Merge with actual data
    merged = full_df.merge(df, on=['iso_code', 'year'], how='left')
    merged['coverage_pct'] = merged['coverage_pct'].fillna(0)
    merged['initiative'] = merged['initiative'].fillna('No carbon pricing')
    
    return merged


def create_animated_map(df, output_file=None):
    """Create an animated choropleth map."""
    import os
    
    if output_file is None:
        # Use absolute path in temp directory to avoid OneDrive issues
        output_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'carbon_pricing_map.html')
    
    # Add country names for hover info
    fig = px.choropleth(
        df,
        locations='iso_code',
        color='coverage_pct',
        animation_frame='year',
        hover_name='iso_code',
        hover_data={
            'coverage_pct': ':.2f',
            'initiative': True,
            'iso_code': False
        },
        color_continuous_scale=[
            [0, 'rgb(240, 240, 240)'],      # No coverage - light gray
            [0.001, 'rgb(255, 245, 235)'],  # Very low - pale orange
            [0.1, 'rgb(253, 208, 162)'],    # Low
            [0.3, 'rgb(253, 174, 107)'],    # Medium-low
            [0.5, 'rgb(253, 141, 60)'],     # Medium
            [0.7, 'rgb(241, 105, 19)'],     # Medium-high
            [1.0, 'rgb(166, 54, 3)']        # High - dark orange/red
        ],
        range_color=[0, 25],  # 0-25% global emissions coverage
        title='<b>Global Spread of Carbon Pricing (1990-2025)</b><br><sup>Share of national emissions covered by carbon taxes and emissions trading systems</sup>',
        labels={'coverage_pct': 'Coverage (%)'}
    )
    
    # Update layout
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='rgb(100, 100, 100)',
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(240, 240, 240)',
            showocean=True,
            oceancolor='rgb(220, 235, 245)',
            showlakes=True,
            lakecolor='rgb(220, 235, 245)',
        ),
        width=1200,
        height=700,
        font=dict(family='Arial', size=12),
        title_x=0.5,
        coloraxis_colorbar=dict(
            title='Coverage (%)',
            ticksuffix='%',
            len=0.6
        ),
        # Slow down animation
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            y=0,
            x=0.1,
            xanchor='right',
            yanchor='top',
            buttons=[
                dict(label='Play',
                     method='animate',
                     args=[None, {'frame': {'duration': 500, 'redraw': True},
                                  'fromcurrent': True,
                                  'transition': {'duration': 300}}]),
                dict(label='Pause',
                     method='animate',
                     args=[[None], {'frame': {'duration': 0, 'redraw': False},
                                    'mode': 'immediate',
                                    'transition': {'duration': 0}}])
            ]
        )]
    )
    
    # Save to HTML
    fig.write_html(output_file)
    print(f"Map saved to {output_file}")
    
    return fig


def create_summary_stats(df):
    """Print summary statistics about carbon pricing adoption."""
    latest = df[df['year'] == df['year'].max()]
    with_pricing = latest[latest['coverage_pct'] > 0]
    
    print("\n" + "="*60)
    print("CARBON PRICING SUMMARY STATISTICS")
    print("="*60)
    print(f"\nCountries with carbon pricing in 2025: {len(with_pricing)}")
    print(f"\nTop 10 countries by coverage:")
    top10 = with_pricing.nlargest(10, 'coverage_pct')[['iso_code', 'coverage_pct', 'initiative']]
    for _, row in top10.iterrows():
        print(f"  {row['iso_code']}: {row['coverage_pct']:.1f}% - {row['initiative'][:50]}...")
    
    # Timeline of adoption
    print(f"\nAdoption timeline:")
    first_adoption = df[df['coverage_pct'] > 0].groupby('iso_code')['year'].min().sort_values()
    for decade in [1990, 2000, 2010, 2020]:
        decade_adopters = first_adoption[(first_adoption >= decade) & (first_adoption < decade + 10)]
        print(f"  {decade}s: {len(decade_adopters)} new countries")


def main():
    """Main function to create the animated carbon pricing map."""
    
    # Load data
    print("Loading Compliance Emissions data...")
    filepath = 'Compliance Emissions.csv'
    df, year_cols = load_compliance_data(filepath)
    
    print(f"Found {len(df)} initiatives across {len(year_cols)} years")
    
    # Transform to country-year format
    print("Mapping initiatives to countries...")
    country_df = create_country_year_data(df, year_cols)
    
    if len(country_df) == 0:
        print("Warning: No data mapped. Check initiative names.")
        return
    
    print(f"Created {len(country_df)} country-year-initiative records")
    
    # Aggregate by country-year
    print("Aggregating coverage by country...")
    agg_df = aggregate_country_coverage(country_df)
    
    # Fill missing years for smooth animation
    print("Preparing animation data...")
    full_df = fill_missing_years(agg_df)
    
    # Print summary stats
    create_summary_stats(full_df)
    
    # Create the animated map
    print("\nCreating animated choropleth map...")
    fig = create_animated_map(full_df)
    
    print("\nDone! Open carbon_pricing_map.html in your browser.")


if __name__ == "__main__":
    main()
