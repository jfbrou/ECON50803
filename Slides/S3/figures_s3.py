"""
ECON50803 — Session 3 : Figure Generation
============================================

Generates all matplotlib figures for Session 3 slides (labor market,
inequality, saving, current accounts, AI). Figures are exported as native vector PDFs. All figure labels, axis titles, legends, and annotations
are in French.

Run from Slides/S3/:
    python3 figures_s3.py
"""

import os
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "plot-common"))
import teaching_plot_utils
teaching_plot_utils.init(
    figures_dir=str(Path(__file__).resolve().parents[1] / 'Figures'),
    env_file=str(Path(__file__).resolve().parents[2] / '.env'))
from teaching_plot_utils import *


# =====================================================================
# Figure 1: US labor market indicators (1950–2024)
# =====================================================================
def labor_market_indicators_us():
    print('Figure 1: US labor market indicators')

    civpart = get_fred_data('CIVPART', frequency='a', aggregation_method='avg')
    emratio = get_fred_data('EMRATIO', frequency='a', aggregation_method='avg')
    unrate = get_fred_data('UNRATE', frequency='a', aggregation_method='avg')

    fig, ax = new_figure(9, 4.5)

    ax.plot(civpart.index.year, civpart.values, color=palette[0],
            linewidth=2.5, label='Taux de participation')
    ax.plot(emratio.index.year, emratio.values, color=palette[1],
            linewidth=2.5, label="Taux d'emploi")
    ax.plot(unrate.index.year, unrate.values, color=palette[2],
            linewidth=2, label=r"Taux de chômage")

    ax.set_xlim(1950, 2024)
    ax.set_xticks(range(1950, 2025, 10))
    ax.set_xticklabels(range(1950, 2025, 10), fontsize=11)
    ax.set_ylabel(r"Pourcentage (\%)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 70)
    ax.set_yticks(range(0, 71, 10))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(0, 71, 10)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, r"Source: FRED (CIVPART, EMRATIO, UNRATE) --- États-Unis")
    save(fig, 'labor_market_indicators_us.pdf')


# =====================================================================
# Figure 1b: Canadian labor market indicators (1976–present, dual axis)
# =====================================================================
def labor_market_indicators_ca():
    print('Figure 1b: Canadian labor market indicators (dual axis)')

    from stats_can import StatsCan
    sc = StatsCan()

    # Table 14-10-0287-01: Labour force characteristics, monthly, SA
    df = sc.table_to_df('14-10-0287-01')
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])

    # Keep seasonally adjusted, both genders, 15+, estimate only
    df = df[df['Data type'] == 'Seasonally adjusted']
    df = df[df['Gender'] == 'Total - Gender']
    df = df[df['Age group'] == '15 years and over']
    df = df[df['Statistics'] == 'Estimate']

    # Extract the three series
    participation = df[df['Labour force characteristics'] ==
                       'Participation rate'].set_index('REF_DATE')['VALUE']
    employment = df[df['Labour force characteristics'] ==
                    'Employment rate'].set_index('REF_DATE')['VALUE']
    unemployment = df[df['Labour force characteristics'] ==
                      'Unemployment rate'].set_index('REF_DATE')['VALUE']

    # Drop duplicates and sort
    participation = participation[~participation.index.duplicated(keep='first')].sort_index()
    employment = employment[~employment.index.duplicated(keep='first')].sort_index()
    unemployment = unemployment[~unemployment.index.duplicated(keep='first')].sort_index()

    fig, ax1 = new_figure(9, 4.5)
    ax2 = ax1.twinx()

    # Left axis: participation & employment rates
    ax1.plot(participation.index, participation.values, color=palette[0],
             linewidth=1.5, label='Taux de participation')
    ax1.plot(employment.index, employment.values, color=palette[1],
             linewidth=1.5, label="Taux d'emploi")

    # Right axis: unemployment rate
    ax2.plot(unemployment.index, unemployment.values, color=palette[2],
             linewidth=1.5, label=r"Taux de chômage")

    # Left axis formatting
    import matplotlib.dates as mdates
    ax1.set_xlim(pd.Timestamp('1976-01-01'), participation.index.max())
    tick_years = range(1980, participation.index.max().year + 1, 10)
    tick_dates = [pd.Timestamp(f'{y}-01-01') for y in tick_years]
    ax1.set_xticks(tick_dates)
    ax1.set_xticklabels([str(y) for y in tick_years], fontsize=11)
    ax1.set_ylabel(r"Participation / emploi (\%)", fontsize=11,
                   rotation=0, ha='left')
    ax1.yaxis.set_label_coords(0, 1.02)
    ax1.set_ylim(50, 70)
    ax1.set_yticks(range(50, 71, 5))
    ax1.set_yticklabels([f'{y}' + r'\%' for y in range(50, 71, 5)],
                         fontsize=11)

    # Right axis formatting
    ax2.set_ylabel(r"Chômage (\%)", fontsize=11,
                   rotation=0, ha='right')
    ax2.yaxis.set_label_coords(1, 1.06)
    unemployment_max = max(14, tick_ceil(unemployment.max(), 2))
    ax2.set_ylim(4, unemployment_max)
    ax2.set_yticks(range(4, unemployment_max + 1, 2))
    ax2.set_yticklabels([f'{y}' + r'\%' for y in range(4, unemployment_max + 1, 2)],
                         fontsize=11, color=palette[2])
    ax2.tick_params(axis='y', colors=palette[2])
    ax2.spines['right'].set_color(palette[2])
    ax2.spines['top'].set_visible(False)

    # Recession shading
    for start, end in recessions_ca:
        ax1.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    # Style left axis
    style_axes(ax1)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               frameon=False, fontsize=10, loc='lower left')
    ax1.text(0.99, 0.98, r"Source: Statistique Canada, tableau 14-10-0287-01",
             fontsize=8, color='gray', ha='right', va='top',
             transform=ax1.transAxes)
    save(fig, 'labor_market_indicators_ca.pdf')


# =====================================================================
# Figure 2: Male vs female participation rates (US, 1950–2024)
# =====================================================================
def participation_gender():
    print('Figure 2: Participation rates by gender (US)')

    male = get_fred_data('LNS11300001', frequency='a', aggregation_method='avg')
    female = get_fred_data('LNS11300002', frequency='a', aggregation_method='avg')

    fig, ax = new_figure(9, 4.5)

    ax.plot(male.index.year, male.values, color=palette[0],
            linewidth=2.5, label='Hommes')
    ax.plot(female.index.year, female.values, color=palette[2],
            linewidth=2.5, label='Femmes')

    # Annotate the convergence
    ax.annotate('Convergence',
                xy=(2000, 60), xytext=(1975, 50),
                fontsize=11, color=palette[1], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[1], lw=1.5))

    ax.set_xlim(1950, 2024)
    ax.set_xticks(range(1950, 2025, 10))
    ax.set_xticklabels(range(1950, 2025, 10), fontsize=11)
    ax.set_ylabel(r"Taux de participation (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(20, 90)
    ax.set_yticks(range(20, 91, 10))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(20, 91, 10)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='center right')
    add_source(ax, r"Source: FRED (LNS11300001, LNS11300002) --- États-Unis")
    save(fig, 'participation_gender.pdf')


# =====================================================================
# Figure 3: Aging population — old-age dependency ratio
# =====================================================================
def aging_population():
    print('Figure 3: Aging population — old-age dependency ratio')

    # Old-age dependency ratio (65+ / 15-64) * 100
    # Source: World Bank API (SP.POP.DPND.OL)
    countries = [
        ('JPN', 'Japon', palette[0], 2.5),          # HECnavy
        ('ITA', 'Italie', palette[1], 2.5),          # HECgreen
        ('CAN', 'Canada', palette[2], 3.0),          # HECcoral
        ('USA', r"États-Unis", palette[3], 2.0), # yellow
    ]

    fig, ax = new_figure(9, 4.5)

    for iso, label, color, lw in countries:
        s = _get_worldbank('SP.POP.DPND.OL', iso)
        s = s[s.index >= 1960]
        ax.plot(s.index, s.values, color=color, linewidth=lw, label=label)

    ax.set_xlim(1960, 2025)
    ax.set_xticks(range(1960, 2030, 10))
    ax.set_xticklabels(range(1960, 2030, 10), fontsize=11)
    ax.set_ylabel(r"Ratio de dépendance des aînés (\%)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(5, 55)
    ax.set_yticks(range(5, 56, 10))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(5, 56, 10)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0))
    add_source(ax, 'Source: Banque mondiale (SP.POP.DPND.OL)')
    save(fig, 'aging_population.pdf')


# =====================================================================
# Figure 4: US prime-age male participation decline
# =====================================================================
def participation_decline_us():
    print('Figure 4: US prime-age male participation decline')

    prime_male = get_fred_data('LRAC25MAUSA156N')
    prime_male = prime_male.dropna()

    fig, ax = new_figure(9, 4.5)

    ax.plot(prime_male.index.year, prime_male.values, color=palette[0],
            linewidth=2.5)
    ax.fill_between(prime_male.index.year, prime_male.values,
                    prime_male.values.min() - 1, alpha=0.1, color=palette[0])

    # Trend annotation
    ax.annotate(r"Déclin structurel",
                xy=(2010, 88), xytext=(1980, 92),
                fontsize=12, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    ax.set_xlim(1950, 2024)
    ax.set_xticks(range(1950, 2025, 10))
    ax.set_xticklabels(range(1950, 2025, 10), fontsize=11)
    ax.set_ylabel(r"Taux de participation (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(84, 100)
    ax.set_yticks(range(84, 101, 2))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(84, 101, 2)], fontsize=11)

    style_axes(ax)
    add_source(ax, r"Source: FRED (LNS11300061) --- Hommes 25--54 ans, É.-U.")
    save(fig, 'participation_decline_us.pdf')


# =====================================================================
# Figure 5: Labor share of GDP decline
# =====================================================================
def labor_share_decline():
    """Labor share of GDP for Canada, 1950-2023 (Penn World Table via FRED)."""
    print('  labor_share_decline ...', end=' ', flush=True)

    # FRED: Share of Labour Compensation in GDP (Canada, PWT)
    ls = get_fred_data('LABSHPCAA156NRUG')
    ls = ls.dropna() * 100  # convert ratio to %

    ls = ls[ls.index.year >= 1960]

    fig, ax = new_figure(9, 4.5)

    ax.plot(ls.index.year, ls.values, color=palette[0], linewidth=2.5)
    ax.fill_between(ls.index.year, ls.values, 61,
                    alpha=0.08, color=palette[0])

    ax.set_xlim(1960, 2024)
    ax.set_xticks(range(1960, 2025, 10))
    ax.set_xticklabels(range(1960, 2025, 10), fontsize=12)
    ax.set_ylim(61, 76)
    ax.set_yticks(range(61, 77, 3))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(61, 77, 3)], fontsize=12)
    ax.set_ylabel(r"Part du travail dans le PIB",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r'Source: Penn World Table 10.01 (via FRED)')
    save(fig, 'labor_share_canada.pdf')


# =====================================================================
# Figure 6: College/high-school wage premium (US)
# =====================================================================
_SKILL_PREMIUM_DIR = Path(__file__).resolve().parents[1] / 'Data'
_SKILL_PREMIUM_DATA = _SKILL_PREMIUM_DIR / 's3_college_wage_premium.csv'
_SKILL_PREMIUM_ANNUAL = _SKILL_PREMIUM_DIR / 's3_college_wage_premium_annual.csv'
_SKILL_PREMIUM_META = _SKILL_PREMIUM_DIR / 's3_college_wage_premium.json'


def _labour_history_xaxis(ax):
    """Common annual time axis for polarization and the college wage premium."""
    ax.set_xlim(1983, 2025)
    ax.set_xticks(range(1985, 2026, 5))
    ax.set_xticklabels(range(1985, 2026, 5), fontsize=12)


def refresh_college_wage_premium(as_of=None):
    """Cache matched official annual and quarterly BLS earnings; plot offline."""
    from concurrent.futures import ThreadPoolExecutor
    from hashlib import sha256
    from io import BytesIO
    import json

    retrieved_on = pd.Timestamp(as_of or pd.Timestamp.today()).normalize()
    series = {'college_usd': 'LEU0252918500Q', 'highschool_usd': 'LEU0252917300Q',
              'college_annual_usd': 'LEU0252918500A', 'highschool_annual_usd': 'LEU0252917300A'}

    def fetch(item):
        name, series_id = item
        url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}'
        response = requests.get(url, timeout=40)
        response.raise_for_status()
        table = pd.read_csv(BytesIO(response.content), parse_dates=['observation_date'])
        values = pd.to_numeric(table[series_id], errors='coerce')
        values.index = table.observation_date
        values = values.rename(name).loc[values.index <= retrieved_on]
        assert values.index.is_unique and values.notna().sum() > 40
        assert (values.dropna() > 0).all()
        return values, {'id': series_id, 'url': url,
                        'download_sha256': sha256(response.content).hexdigest()}

    with ThreadPoolExecutor(max_workers=4) as pool:
        fetched = list(pool.map(fetch, series.items()))
    data = pd.concat([result[0] for result in fetched[:2]], axis=1).sort_index()
    quarters = data.index.to_period('Q')
    assert quarters.is_unique
    data.index = quarters
    # Keep all quarters, including missing 2025Q4; do not bridge missing values.
    data = data.reindex(pd.period_range(quarters.min(), quarters.max(), freq='Q'))
    valid = data.dropna(subset=['college_usd', 'highschool_usd'])
    data = data.loc[valid.index.min():valid.index.max()].copy()
    data['premium_percent'] = 100 * (data.college_usd / data.highschool_usd - 1)
    data['date'] = data.index.to_timestamp(how='end').normalize()
    assert (data.date <= retrieved_on).all()
    assert data.premium_percent.dropna().between(0, 200).all()
    _SKILL_PREMIUM_DIR.mkdir(parents=True, exist_ok=True)
    data.to_csv(_SKILL_PREMIUM_DATA, index_label='quarter')
    annual = pd.concat([result[0] for result in fetched[2:]], axis=1).sort_index()
    annual.columns = ['college_usd', 'highschool_usd']
    annual.index = annual.index.to_period('Y')
    annual = annual.loc[annual.index.to_timestamp(how='end').normalize() <= retrieved_on].dropna()
    assert annual.index.is_unique and annual.index.min().year <= 1983
    assert annual.index.equals(pd.period_range(annual.index.min(), annual.index.max(), freq='Y'))
    annual['premium_percent'] = 100 * (annual.college_usd / annual.highschool_usd - 1)
    annual['date'] = annual.index.to_timestamp(how='end').normalize()
    annual.to_csv(_SKILL_PREMIUM_ANNUAL, index_label='year')
    metadata = {
        'retrieved_on': retrieved_on.date().isoformat(),
        'source': 'BLS Current Population Survey, Weekly and Hourly Earnings, via FRED.',
        'series': {name: item[1] for name, item in zip(series, fetched)},
        'population': 'US wage and salary workers, full time, age 25 and over, both sexes. Excludes self-employed.',
        'college_definition': "Bachelor's degree and higher, not bachelor's only.",
        'comparison_definition': 'High school graduates, no college; excludes less than high school and some-college groups.',
        'units_input': 'Median usual weekly nominal earnings, dollars, official annual and quarterly series, not seasonally adjusted.',
        'transformation': '100 * (college median / high-school median - 1), within each frequency. Annual values are the official annual medians, not averages of quarterly ratios. Common price deflation cancels. No smoothing, interpolation, or imputation.',
        'plot_frequency': 'Official annual observations, 1983–2025, matching the job-polarization plot: limits 1983 and 2025, ticks every five years from 1985. Quarterly observations remain cached but are not displayed on this common annual axis.',
        'historical_comparability': 'Before 1992, groups reflect years of school completed (4 years high school / 4 or more years college). From 1992, classification uses degrees. The 1994 CPS redesign also limits strict comparability; no artificial correction is applied.',
        'historical_methodology_url': 'https://aspe.hhs.gov/reports/welfare-indicators-risk-factors-fourteenth-report-congress-0',
        'first_annual_year': int(annual.index.min().year),
        'last_annual_year': int(annual.index.max().year),
        'missing_quarters': [str(q) for q in data.index[data.premium_percent.isna()]],
        'missing_observation_note': 'BLS did not produce reliable 2025Q4 estimates because October CPS data were not collected during the federal government shutdown.',
        'methodology_url': 'https://www.bls.gov/news.release/wkyeng.htm',
        'first_quarter': str(data.index.min()),
        'last_quarter': str(data.index.max()),
        'last_percent': float(data.premium_percent.iloc[-1]),
        'interpretation': 'Descriptive difference in group medians, not an adjusted education return or a causal AI effect. Education is not a direct measure of AI complementarity. Composition changes can affect the gap.',
        'related_paper': {
            'authors': 'José Azar, Mireia Giné, Javier Sanz-Espín',
            'title': 'The College Wage Premium in the Generative AI Era',
            'version': 'Revised September 10, 2026',
            'url': 'https://ssrn.com/abstract=7364838',
            'scope': 'Background reading only. This BLS median-ratio figure is not a reproduction of their CPS adjusted/log-wage estimates.',
        },
        'refresh_command': 'python -c "import figures_s3 as f; f.refresh_college_wage_premium(); f.inequality_skill_premium()"',
    }
    _SKILL_PREMIUM_META.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('College wage premium endpoint:', data.index.max(), f'{data.premium_percent.iloc[-1]:.3f}%')


def inequality_skill_premium():
    """Unadjusted college/high-school median weekly earnings gap, percent."""
    data = pd.read_csv(_SKILL_PREMIUM_ANNUAL, parse_dates=['date'])
    data = data.loc[data.year.between(1983, 2025)]
    assert data.premium_percent.notna().sum() > 40
    fig, ax = new_figure(10, 5)
    ax.plot(data.year, data.premium_percent, color=palette[0], linewidth=2.3)
    _labour_history_xaxis(ax)
    ymin = np.floor(data.premium_percent.min() / 10) * 10
    ymax = np.ceil(data.premium_percent.max() / 10) * 10
    ticks = np.arange(ymin, ymax + 1, 10)
    ax.set_ylim(ymin, ymax)
    ax.set_yticks(ticks)
    ax.set_yticklabels([f'{value:.0f}' + r'\%' for value in ticks], fontsize=11)
    ax.set_ylabel(r'Prime salariale universitaire (\%)', rotation=0, ha='left', fontsize=11)
    ax.yaxis.set_label_coords(0, 1.02)
    style_axes(ax)
    add_source(ax, r'Source : BLS / CPS (via FRED), données annuelles')
    save(fig, 'inequality_skill_premium.pdf')


def ai_cfo_employment():
    """Employment effects attributed to AI by CFOs, Baslandze et al., Fig. 1."""
    data = pd.read_csv(_SKILL_PREMIUM_DIR / 's3_ai_cfo_employment.csv')
    fig, ax = new_figure(10, 5)
    centers = np.arange(len(data))
    for shift, column, color, label in [
            (-0.18, 'reported_2025_percent', palette[0], '2025 : déclaré'),
            (0.18, 'expected_2026_percent', palette[2], '2026 : anticipé')]:
        values = data[column]
        ax.bar(centers + shift, values, width=0.32, color=color, zorder=3, label=label)
        for x, value in zip(centers + shift, values):
            label_y = value + (0.025 if value >= 0 else -0.025)
            text = f'{value:+.2f}'.replace('.', ',') + r'\%'
            ax.text(x, label_y, text, ha='center', va='bottom' if value >= 0 else 'top',
                    fontsize=11, color=color)
    ax.axhline(0, color=palette[7], linewidth=0.8, zorder=2)
    ax.set_xlim(-0.65, 1.65)
    ax.set_ylim(-0.85, 0.4)
    ax.set_xticks(centers)
    ax.set_xticklabels(['Moins de 500 salariés', '500 salariés ou plus'], fontsize=11)
    ticks = [-0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f'{value:.1f}'.replace('.', ',') + r'\%' for value in ticks], fontsize=11)
    ax.set_ylabel(r'Effet sur l\textquotesingle emploi (\%)', rotation=0, ha='left', fontsize=11)
    ax.yaxis.set_label_coords(0, 1.02)
    style_axes(ax)
    ax.legend(loc='upper left', frameon=False, fontsize=10, ncol=2)
    add_source(ax, r'Source : Baslandze et al. (2026), figure 1')
    save(fig, 's3_ai_cfo_employment.pdf')


# =====================================================================
# Figure 7: R&D as share of GDP — US private vs public (FRED)
# =====================================================================
def rd_gdp_share():
    """Stacked area: private and public R&D as share of US GDP."""
    print('Figure 7: R&D / GDP — US private vs public')

    private = get_fred_data('Y006RC1Q027SBEA') / get_fred_data('GDP')
    public  = get_fred_data('Y057RC1Q027SBEA') / get_fred_data('GDP')

    # Align on common index and drop NaN
    combined = pd.concat([private.rename('priv'), public.rename('pub')],
                         axis=1).dropna()

    fig, ax = new_figure(9, 4.5)

    ax.stackplot(combined.index, 100 * combined['priv'].values,
                 100 * combined['pub'].values,
                 colors=[palette[0], palette[1]],
                 edgecolor='k', linewidth=0.5)

    ax.set_xlim(pd.to_datetime('1950'), combined.index.max())
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(1950, 2021, 10)])
    ax.set_xticklabels(range(1950, 2021, 10), fontsize=11)
    ax.set_ylim(0, 4)
    ax.set_yticks(np.arange(0, 4.1, 0.5))
    ax.set_yticklabels([f'{x:.1f}' + r'\%' for x in np.arange(0, 4.1, 0.5)],
                       fontsize=11)
    ax.set_ylabel(r"Part du PIB américain (\%)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)

    # In-chart labels
    ax.text(pd.to_datetime('2005'), 0.7, r"R\&D privée",
            fontsize=14, color='white', ha='center', va='center')
    ax.text(pd.to_datetime('1970'), 1.6, r"R\&D publique",
            fontsize=14, color='k', ha='center', va='center')

    add_source(ax, r"Source: FRED (Y006RC, Y057RC, GDP) --- États-Unis")
    save(fig, 'rd_gdp_share.pdf')


# =====================================================================
# Figure 8: Canada GDP/capita growth decomposition by period
# =====================================================================
def canada_gdp_decomposition():
    """Stacked bar: decompose Canadian Y/N growth into A, K/Y, L/N."""
    print('Figure 8: Canada GDP/capita growth decomposition')

    # Load Penn World Tables 10.01 (same source as S2)
    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')
    ca = pwt[pwt['countrycode'] == 'CAN'].set_index('year')

    alpha = 1 / 3
    amp_ky = alpha / (1 - alpha)  # 0.5

    periods = [('1960--80', 1960, 1980),
               ('1980--00', 1980, 2000),
               ('2000--19', 2000, 2019)]

    a_vals, ky_vals, ln_vals, yn_vals = [], [], [], []
    for _, y0, y1 in periods:
        T = y1 - y0
        yn0 = ca.loc[y0, 'rgdpna'] / ca.loc[y0, 'pop']
        yn1 = ca.loc[y1, 'rgdpna'] / ca.loc[y1, 'pop']
        ky0 = ca.loc[y0, 'rkna'] / ca.loc[y0, 'rgdpna']
        ky1 = ca.loc[y1, 'rkna'] / ca.loc[y1, 'rgdpna']
        ln0 = ca.loc[y0, 'emp'] / ca.loc[y0, 'pop']
        ln1 = ca.loc[y1, 'emp'] / ca.loc[y1, 'pop']

        g_yn = ((yn1 / yn0) ** (1 / T) - 1) * 100
        g_ky = ((ky1 / ky0) ** (1 / T) - 1) * 100
        g_ln = ((ln1 / ln0) ** (1 / T) - 1) * 100

        ky_c = amp_ky * g_ky
        ln_c = g_ln
        a_c = g_yn - ky_c - ln_c

        a_vals.append(a_c)
        ky_vals.append(ky_c)
        ln_vals.append(ln_c)
        yn_vals.append(g_yn)

    x = np.arange(len(periods))
    labels = [p[0] for p in periods]
    w = 0.55

    fig, ax = new_figure(9, 4.5)

    # Stacked bars: positive contributions stack upward from 0,
    # negative contributions stack downward from 0
    components = [
        (a_vals, palette[0], r"Productivité ($A$)"),
        (ky_vals, palette[1], r"Capital/PIB ($K/Y$)"),
        (ln_vals, palette[3], r"Taux d'emploi ($L/N$)"),
    ]

    for i in range(len(periods)):
        pos_base = 0
        neg_base = 0
        for j, (vals, color, label) in enumerate(components):
            v = vals[i]
            if v >= 0:
                ax.bar(x[i], v, w, bottom=pos_base, color=color,
                       label=label if i == 0 else None)
                pos_base += v
            else:
                ax.bar(x[i], v, w, bottom=neg_base, color=color,
                       label=label if i == 0 else None)
                neg_base += v

    # Total Y/N markers
    for i in range(len(periods)):
        ax.plot(x[i], yn_vals[i], 'D', color=palette[2], markersize=8,
                zorder=5, label=r'Total $Y/N$' if i == 0 else None)
        ax.annotate(f'{yn_vals[i]:.1f}' + r'\%',
                    xy=(x[i], yn_vals[i]),
                    xytext=(0, 10), textcoords='offset points',
                    ha='center', fontsize=11, fontweight='bold',
                    color=palette[2])

    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=13)
    ax.set_ylabel(r"Contribution à la croissance de $Y/N$ (\%/an)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    ax.set_ylim(0, 3.5)
    ax.set_yticks(np.arange(0, 3.6, 0.5))
    ax.set_yticklabels([f'{y:.1f}' + r'\%' for y in np.arange(0, 3.6, 0.5)],
                       fontsize=12)
    ax.tick_params(axis='x', labelsize=12)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, 'Source: Penn World Tables 10.01 --- Canada')
    save(fig, 'canada_gdp_decomposition.pdf')


# =====================================================================
# Figure 9: Cross-country GDP/capita decomposition (2000–2019)
# =====================================================================
def canada_gdp_decomposition_countries():
    """Horizontal stacked bar: Y/N decomposition for ~18 countries, 2000-2019."""
    print('Figure 9: Cross-country GDP/capita decomposition (2000-2019)')

    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')

    alpha = 1 / 3
    amp_ky = alpha / (1 - alpha)  # 0.5

    countries = {
        'KOR': r'Corée du Sud',
        'POL': 'Pologne',
        'IRL': 'Irlande',
        'AUS': 'Australie',
        'SWE': r'Suède',
        'USA': r'États-Unis',
        'GBR': 'Royaume-Uni',
        'NZL': r'Nouvelle-Zélande',
        'DEU': 'Allemagne',
        'NOR': r'Norvège',
        'CAN': 'Canada',
        'CHE': 'Suisse',
        'NLD': 'Pays-Bas',
        'JPN': 'Japon',
        'DNK': 'Danemark',
        'FRA': 'France',
        'BEL': 'Belgique',
        'ESP': 'Espagne',
        'ITA': 'Italie',
    }

    y0, y1 = 2000, 2019
    T = y1 - y0
    results = {}

    for iso, name in countries.items():
        c = pwt[pwt['countrycode'] == iso].set_index('year')
        if y0 not in c.index or y1 not in c.index:
            continue

        yn0 = c.loc[y0, 'rgdpna'] / c.loc[y0, 'pop']
        yn1 = c.loc[y1, 'rgdpna'] / c.loc[y1, 'pop']
        ky0 = c.loc[y0, 'rkna'] / c.loc[y0, 'rgdpna']
        ky1 = c.loc[y1, 'rkna'] / c.loc[y1, 'rgdpna']
        ln0 = c.loc[y0, 'emp'] / c.loc[y0, 'pop']
        ln1 = c.loc[y1, 'emp'] / c.loc[y1, 'pop']

        g_yn = ((yn1 / yn0) ** (1 / T) - 1) * 100
        g_ky = ((ky1 / ky0) ** (1 / T) - 1) * 100
        g_ln = ((ln1 / ln0) ** (1 / T) - 1) * 100

        ky_c = amp_ky * g_ky
        ln_c = g_ln
        a_c = g_yn - ky_c - ln_c

        results[iso] = (name, g_yn, a_c, ky_c, ln_c)

    # Sort by total Y/N growth
    sorted_isos = sorted(results.keys(), key=lambda k: results[k][1])

    names = [results[iso][0] for iso in sorted_isos]
    yn_vals = [results[iso][1] for iso in sorted_isos]
    a_vals = [results[iso][2] for iso in sorted_isos]
    ky_vals = [results[iso][3] for iso in sorted_isos]
    ln_vals = [results[iso][4] for iso in sorted_isos]

    y_pos = np.arange(len(names))
    h = 0.6

    fig, ax = new_figure(9, 7)

    # Stacked horizontal bars: positive right of 0, negative left of 0
    components = [
        (a_vals, palette[0], r"Productivité ($A$)"),
        (ky_vals, palette[1], r"Capital/PIB ($K/Y$)"),
        (ln_vals, palette[3], r"Taux d'emploi ($L/N$)"),
    ]

    for i in range(len(names)):
        pos_base = 0
        neg_base = 0
        for j, (vals, color, label) in enumerate(components):
            v = vals[i]
            if v >= 0:
                ax.barh(y_pos[i], v, h, left=pos_base, color=color,
                        label=label if i == 0 else None)
                pos_base += v
            else:
                ax.barh(y_pos[i], v, h, left=neg_base, color=color,
                        label=label if i == 0 else None)
                neg_base += v

    # Total Y/N diamond markers
    for i in range(len(names)):
        ax.plot(yn_vals[i], y_pos[i], 'D', color=palette[2], markersize=6,
                zorder=5, label=r'Total $Y/N$' if i == 0 else None)

    ax.axvline(x=0, color='black', linewidth=0.5)

    # Highlight Canada
    can_idx = sorted_isos.index('CAN')
    ax.get_yticklabels()  # force tick creation

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=11)
    # Bold Canada label
    tick_labels = ax.get_yticklabels()
    for tl in tick_labels:
        if tl.get_text() == 'Canada':
            tl.set_fontweight('bold')
            tl.set_color(palette[2])

    # Subtle highlight band for Canada
    ax.axhspan(can_idx - 0.4, can_idx + 0.4, color=palette[2],
               alpha=0.08, zorder=0)

    ax.set_xlabel(r"Contribution à la croissance de $Y/N$ (\%/an)",
                  fontsize=11)
    ax.set_xlim(-1.0, 4.0)
    ax.set_xticks(np.arange(-1.0, 4.1, 0.5))
    ax.set_xticklabels([f'{x:.1f}' + r'\%' for x in np.arange(-1.0, 4.1, 0.5)],
                       fontsize=10)

    style_axes(ax)
    ax.spines['left'].set_visible(False)
    ax.grid(True, which='major', axis='x', color='gray', linestyle=':', linewidth=0.5)
    ax.grid(False, axis='y')
    ax.tick_params(axis='y', length=0)

    ax.legend(frameon=False, fontsize=9, loc='lower right',
              bbox_to_anchor=(1.0, 0.0))
    add_source(ax, r"Source: Penn World Tables 10.01 --- Période 2000--2019")
    save(fig, 'canada_gdp_decomposition_countries.pdf')


# =====================================================================
# Figure 10: Breakthrough patents per million people (Kelly et al. 2021)
# =====================================================================
def breakthrough_inventions():
    """Breakthrough patents per million people from Kelly et al. (2021) data."""
    print('Figure 10: Breakthrough patents (Kelly et al. 2021)')

    # ── Load patent-level breakthrough data ──────────────────────────
    data_dir = os.path.join(Path(__file__).resolve().parent.parent, 'Data')
    patent_csv = os.path.join(data_dir, 'PatentSimilarityImportanceBreakthrough_forPost2022.csv')
    df = pd.read_csv(patent_csv, usecols=['issue_year', 'bk_p90_alqsim05'])
    df = df.dropna(subset=['bk_p90_alqsim05'])

    # Count breakthrough patents (top 10% importance) by issue year
    bt_by_year = (df[df['bk_p90_alqsim05'] == 1]
                  .groupby('issue_year').size()
                  .reindex(range(1840, 2017), fill_value=0))

    # ── US population (millions), decennial census + intercensal ─────
    # Source: US Census Bureau historical estimates
    us_pop_m = {
        1840: 17.1, 1850: 23.2, 1860: 31.4, 1870: 38.6, 1880: 50.2,
        1890: 63.0, 1900: 76.2, 1910: 92.2, 1920: 106.0, 1930: 123.2,
        1940: 132.2, 1950: 151.3, 1960: 179.3, 1970: 203.3, 1980: 226.5,
        1990: 248.7, 2000: 281.4, 2010: 308.7, 2016: 323.1,
    }
    pop_years = sorted(us_pop_m.keys())
    pop_vals = [us_pop_m[y] for y in pop_years]
    # Interpolate annual population
    all_years = np.arange(1840, 2017)
    pop_annual = np.interp(all_years, pop_years, pop_vals)
    pop_series = pd.Series(pop_annual, index=all_years)

    # Breakthrough patents per million people
    # (pop_series is in millions, so count / pop_series = per million)
    bt_per_m = bt_by_year / pop_series

    fig, ax = new_figure(9, 4.5)

    ax.plot(bt_per_m.index, bt_per_m.values, color=palette[0], linewidth=1.8)

    # Annotate three waves (text only, no arrows)
    ax.text(1867, 48,
            r"\textbf{1\textsuperscript{re} vague :}" "\n"
            r"2\textsuperscript{e} rév. industrielle" "\n"
            r"(électricité, transport)",
            fontsize=8, color=palette[0], va='bottom', ha='center')

    ax.text(1932, 78,
            r"\textbf{2\textsuperscript{e} vague :}" "\n"
            r"Entre-deux-guerres" "\n"
            r"(chimie, électricité)",
            fontsize=8, color=palette[0], va='bottom', ha='center')

    ax.text(1978, 78,
            r"\textbf{3\textsuperscript{e} vague :}" "\n"
            r"Technologies de l'information" "\n"
            r"(ordinateurs, communications)",
            fontsize=8, color=palette[0], va='bottom', ha='center')

    ax.set_xlim(1840, 2018)
    ax.set_ylim(0, 100)
    ax.set_xticks(range(1840, 2021, 20))
    ax.set_xticklabels([str(y) for y in range(1840, 2021, 20)], fontsize=11)
    ax.set_yticks(range(0, 101, 20))
    ax.set_yticklabels([str(y) for y in range(0, 101, 20)], fontsize=11)
    ax.set_ylabel(r"Brevets majeurs par million d'habitants",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, 'Source: Kelly et al. (2021), AER: Insights')
    save(fig, 'kelly_et_al_2021.pdf')


# =====================================================================
# Figure 11: Global R&D spending by country (1996–2022)
# =====================================================================
def rd_spending_global():
    """Stacked area: R&D spending in billions of constant 2021 PPP USD."""
    print('Figure 11: Global R&D spending by country')

    # Country codes and French labels (stacking order: bottom to top)
    countries = [
        ('USA', r'États-Unis'),
        ('CHN', 'Chine'),
        ('EUU', 'UE-27'),
        ('JPN', 'Japon'),
        ('KOR', r'Corée du Sud'),
        ('GBR', 'Royaume-Uni'),
    ]

    # Fetch R&D % of GDP and GDP PPP (constant 2021 intl $)
    gerd = {}
    for iso, label in countries:
        rd_pct = _get_worldbank('GB.XPD.RSDV.GD.ZS', iso)
        gdp_ppp = _get_worldbank('NY.GDP.MKTP.PP.KD', iso)
        common = rd_pct.index.intersection(gdp_ppp.index)
        spending = (rd_pct[common] / 100) * gdp_ppp[common] / 1e9  # billions
        gerd[label] = spending

    # Build DataFrame aligned on common years
    df = pd.DataFrame(gerd).dropna()
    df = df.loc[df.index >= 1996]

    colors = [palette[0], palette[1], palette[2], palette[3], palette[4], palette[5]]

    fig, ax = new_figure(9, 4.5)

    labels = list(df.columns)
    values = [df[col].values for col in labels]
    ax.stackplot(df.index, *values, colors=colors, labels=labels,
                 edgecolor='black', linewidth=0.5)

    ax.set_xlim(1996, df.index.max())
    xticks = list(range(2000, int(df.index.max()) + 1, 5))
    if 1996 not in xticks:
        xticks = [1996] + xticks
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)
    ax.set_ylabel(r"Milliards \$US PPA (2021)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ymax = max(2500, tick_ceil(df.sum(axis=1).max(), 500))
    ax.set_ylim(0, ymax)
    ax.set_yticks(range(0, ymax + 1, 500))
    ax.set_yticklabels([f'{y:,}'.replace(',', r'\,') for y in range(0, ymax + 1, 500)],
                       fontsize=11)

    style_axes(ax)

    # Legend: reverse order so it matches visual stacking (top = last)
    handles, leg_labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], leg_labels[::-1], frameon=False, fontsize=9,
              loc='upper left', bbox_to_anchor=(0.0, 1.0))

    add_source(ax, 'Source: Banque mondiale (GERD = R\\&D/PIB $\\times$ PIB PPA)')
    save(fig, 'rd_spending_global.pdf')


# =====================================================================
# Figure 12: Moore's Law — transistor count (1971–2024)
# =====================================================================
def moores_law():
    """Log-scale scatter of transistor counts over time (Moore's Law)."""
    print("Figure 12: Moore's Law")

    data_dir = os.path.join(Path(__file__).resolve().parent.parent, 'Data')
    df = pd.read_csv(os.path.join(data_dir, 'moores_law.csv'))

    fig, ax = new_figure(9, 5)

    ax.scatter(df['year'], df['transistors'], s=70, color=palette[0],
               alpha=0.7, zorder=3, edgecolors='black', linewidths=0.3)

    # Moore's Law reference line: doubling every 2 years, spanning full x-axis
    ref_years = np.arange(1970, 2026)
    # Anchor at Intel 4004 (1971, 2300) and extend back/forward
    ref_transistors = 2300 * 2 ** ((ref_years - 1971) / 2)
    ax.plot(ref_years, ref_transistors, color=palette[1], linewidth=1.8,
            linestyle='-', alpha=0.8, zorder=2,
            label=r"Loi de Moore (doublement tous les 2 ans)")

    ax.set_yscale('log')
    ax.set_xlim(1970, 2025)
    ax.set_xticks(range(1970, 2026, 5))
    ax.set_xticklabels([str(y) for y in range(1970, 2026, 5)], fontsize=11)

    # Y-axis: powers of 10 (LaTeX-rendered for correct font)
    yticks = [10**i for i in range(3, 13)]
    ylabels = [r'$10^{' + str(i) + r'}$' for i in range(3, 13)]
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=11, usetex=True)
    ax.set_ylim(1e3, 1e12)

    ax.set_ylabel(r"Nombre de transistors par puce",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.grid(True, which='major', axis='y', color='gray', linestyle=':', linewidth=0.5)
    ax.legend(frameon=False, fontsize=9, loc='upper left')
    add_source(ax, 'Source: Karl Rupp (via Wikipedia)')
    save(fig, 'moores_law.pdf')


# =====================================================================
# Figure 13: Zimbabwe vs Botswana GDP per capita (1960–2019)
# =====================================================================
def zimbabwe_botswana():
    """GDP per capita comparison: institutions matter."""
    print('Figure 13: Zimbabwe vs Botswana')

    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')

    zwe = pwt[pwt['countrycode'] == 'ZWE'].set_index('year')['rgdpna'] / \
          pwt[pwt['countrycode'] == 'ZWE'].set_index('year')['pop']
    bwa = pwt[pwt['countrycode'] == 'BWA'].set_index('year')['rgdpna'] / \
          pwt[pwt['countrycode'] == 'BWA'].set_index('year')['pop']

    fig, ax = new_figure(9, 4.5)

    ax.plot(zwe.index, zwe.values, color=palette[0], linewidth=2.5,
            label='Zimbabwe')
    ax.plot(bwa.index, bwa.values, color=palette[1], linewidth=2.5,
            label='Botswana')

    ax.set_xlim(1960, 2020)
    ax.set_xticks(range(1960, 2021, 10))
    ax.set_xticklabels(range(1960, 2021, 10), fontsize=11)
    ax.set_ylabel(r"PIB réel par habitant (\$US)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 17500)
    ax.set_yticks(range(0, 17501, 2500))
    ax.set_yticklabels([f'{y:,}'.replace(',', r'\,') for y in range(0, 17501, 2500)],
                       fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'zimbabwe_botswana.pdf')


# =====================================================================
# Figure 14: Education plateau — average years of schooling
# =====================================================================
def education_plateau():
    """Average years of schooling for advanced economies (1880–2040)."""
    print('Figure 14: Education plateau')

    # Barro-Lee / Our World in Data — average years of schooling (25+)
    years = [1880, 1900, 1920, 1940, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2040]
    data = {
        r'États-Unis': [3.0, 4.5, 6.5, 8.0, 9.5, 10.5, 12.0, 12.5, 13.0, 13.2, 13.4, 13.5],
        'Canada':          [2.8, 4.0, 5.5, 7.5, 8.8, 10.0, 11.5, 12.0, 12.5, 13.0, 13.2, 13.3],
        'Australie':       [3.2, 4.8, 6.0, 7.5, 9.0, 10.0, 11.0, 12.0, 12.5, 12.8, 12.9, 13.0],
        'Royaume-Uni':     [2.0, 3.5, 5.0, 6.5, 8.5, 9.5, 10.5, 11.0, 12.0, 12.5, 13.0, 13.1],
        'France':          [1.0, 2.0, 4.0, 5.0, 6.0, 7.0, 8.5, 9.5, 10.5, 11.5, 12.0, 12.5],
        'Allemagne':       [3.0, 4.5, 6.0, 7.0, 6.5, 8.0, 9.5, 10.0, 12.5, 13.5, 14.1, 14.5],
    }
    colors = [palette[0], palette[2], palette[1], palette[3], palette[5], palette[7]]

    fig, ax = new_figure(9, 4.5)

    for (label, vals), color in zip(data.items(), colors):
        ax.plot(years, vals, 'o-', color=color, linewidth=2, markersize=3,
                label=label)

    # Annotation
    ax.annotate('Plateau?',
                xy=(2020, 13.4), xytext=(1985, 14.5),
                fontsize=12, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    ax.set_xlim(1875, 2045)
    ax.set_xticks(range(1880, 2041, 20))
    ax.set_xticklabels(range(1880, 2041, 20), fontsize=10)
    ax.set_ylabel(r"Années moyennes de scolarité (25+)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 16)
    ax.set_yticks(range(0, 17, 2))
    ax.set_yticklabels([str(y) for y in range(0, 17, 2)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=9, loc='center left',
              bbox_to_anchor=(0.0, 0.45))
    add_source(ax, 'Source: Barro-Lee; Our World in Data')
    save(fig, 'education_plateau.pdf')


# =====================================================================
# Figure 15: Development accounting — human capital
# =====================================================================
def development_accounting_human_capital():
    """Scatter: human capital vs GDP/capita relative to US."""
    print('Figure 15: Development accounting — human capital')

    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')
    yr = 2019
    dat = pwt[pwt['year'] == yr].dropna(subset=['rgdpna', 'pop', 'hc']).copy()
    dat['yn'] = dat['rgdpna'] / dat['pop']

    us_yn = dat.loc[dat['countrycode'] == 'USA', 'yn'].values[0]
    us_hc = dat.loc[dat['countrycode'] == 'USA', 'hc'].values[0]
    dat['yn_rel'] = dat['yn'] / us_yn
    dat['hc_rel'] = dat['hc'] / us_hc

    fig, ax = new_figure(9, 5)

    ax.scatter(dat['yn_rel'], dat['hc_rel'], s=50, color=palette[0],
               alpha=0.7, zorder=3)

    # 45-degree line
    ax.plot([1/90, 4], [1/90, 4], color=palette[1], linewidth=1.5, zorder=2)

    ax.set_xscale('log', base=2)
    ax.set_yscale('log', base=2)
    ax.set_xlim(1/90, 2)
    ax.set_ylim(1/90, 2)

    ticks = [1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2]
    tick_labels = ['1/64', '1/32', '1/16', '1/8', '1/4', '1/2', '1', '2']
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels, fontsize=11)
    ax.set_yticks(ticks)
    ax.set_yticklabels(tick_labels, fontsize=11)

    ax.set_xlabel(r"PIB réel par habitant relatif aux É.-U. (2019)",
                  fontsize=11)
    ax.set_ylabel(r"Capital humain relatif aux É.-U. (2019)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'development_accounting_human_capital.pdf')


# =====================================================================
# Figure 16: Tropics map — GDP per capita choropleth
# =====================================================================
def tropics_map():
    """World choropleth: GDP/capita in 3 tiers + tropic lines."""
    print('Figure 16: Tropics map')

    import geopandas as gpd
    from matplotlib.colors import ListedColormap

    # ── Load geometries (Natural Earth 110m) ─────────────────────────
    world = gpd.read_file(
        'https://naciscdn.org/naturalearth/110m/cultural/'
        'ne_110m_admin_0_countries.zip')
    world = world[world['NAME'] != 'Antarctica']

    # ── Load PWT 10.01 for GDP per capita ────────────────────────────
    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')
    pwt = pwt[pwt['year'] == 2019].copy()
    pwt['gdp_pc'] = pwt['rgdpna'] / pwt['pop']
    pwt = pwt[['countrycode', 'gdp_pc']].dropna()

    # ── Merge (ISO_A3 ↔ countrycode) ────────────────────────────────
    # Natural Earth uses -99 for missing ISO codes; also try ISO_A3_EH
    world['iso'] = world['ISO_A3'].where(
        world['ISO_A3'] != '-99', world['ISO_A3_EH'])
    world = world.merge(pwt, left_on='iso', right_on='countrycode',
                        how='left')

    # ── Classify into terciles ──────────────────────────────────────
    valid = world['gdp_pc'].dropna()
    t1 = valid.quantile(1 / 3)
    t2 = valid.quantile(2 / 3)
    world['tier'] = pd.cut(
        world['gdp_pc'], bins=[-np.inf, t1, t2, np.inf],
        labels=[0, 1, 2])
    world['tier'] = world['tier'].astype(float)  # NaN for missing data

    # ── Colours: coral (poor), yellow (mid), green (rich) ─────────────
    cmap = ListedColormap([palette[2], palette[3], palette[1]])

    # ── Plot ─────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    # Countries with data
    world[world['tier'].notna()].plot(
        column='tier', cmap=cmap, ax=ax, linewidth=0.3,
        edgecolor='black')
    # Countries without data: light gray
    world[world['tier'].isna()].plot(
        ax=ax, color='#d9d9d9', linewidth=0.3, edgecolor='black')

    # ── Tropic lines ────────────────────────────────────────────────
    for lat, label in [(23.4364, r'Tropique du Cancer'),
                       (-23.4364, r'Tropique du Capricorne')]:
        ax.axhline(lat, color='black', linewidth=0.8, linestyle='--',
                   zorder=4)

    # ── Equator (subtle) ────────────────────────────────────────────
    ax.axhline(0, color='black', linewidth=0.4, linestyle=':', zorder=4)

    # ── Legend ───────────────────────────────────────────────────────
    from matplotlib.patches import Patch
    legend_items = [
        Patch(facecolor=palette[1], edgecolor='white',
              label=r'PIB/hab. élevé'),
        Patch(facecolor=palette[3], edgecolor='white',
              label=r'PIB/hab. moyen'),
        Patch(facecolor=palette[2], edgecolor='white',
              label=r'PIB/hab. faible'),
    ]
    ax.legend(handles=legend_items, loc='lower left',
              fontsize=9, frameon=False,
              bbox_to_anchor=(0.0, -0.02))

    # ── Clean up axes ───────────────────────────────────────────────
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.axis('off')

    add_source(ax, 'Source: Penn World Tables 10.01 (2019)')
    save(fig, 'tropics.pdf')


# =====================================================================
# Figure 17: Education and prosperity — years of schooling vs GDP/capita
# =====================================================================
def education_prosperity():
    """Scatter: average years of schooling vs real GDP per capita."""
    print('Figure 17: Education and prosperity')

    # Fetch Our World in Data (average years of schooling vs GDP per capita)
    url = ("https://ourworldindata.org/grapher/"
           "average-years-of-schooling-vs-gdp-per-capita"
           ".csv?v=1&csvType=full&useColumnShortNames=true")
    df = pd.read_csv(url,
                      storage_options={'User-Agent':
                                       'Our World In Data data fetch/1.0'})

    # Keep 2022 with complete data, drop world aggregate
    df = df[(df['year'] == 2022)
            & df['mys__sex_total'].notna()
            & df['ny_gdp_pcap_pp_kd'].notna()
            & df['population_historical'].notna()
            & df['code'].notna()
            & (df['code'] != 'OWID_WRL')]

    fig, ax = new_figure(9, 4.5)

    ax.scatter(df['ny_gdp_pcap_pp_kd'], df['mys__sex_total'],
               s=df['population_historical'] / 5e5,
               alpha=0.6, facecolors=palette[0], edgecolors='k',
               linewidths=0.3, zorder=3)

    # X-axis: log scale
    ax.set_xscale('log')
    ax.set_xlim(1000, 150000)
    ax.set_xticks([1e3, 1e4, 1e5])
    ax.set_xticklabels([r'\$1\,000', r'\$10\,000', r'\$100\,000'],
                       fontsize=11)
    ax.set_xlabel(r"PIB réel par habitant, PPA (\$US 2017)",
                  fontsize=11)

    # Y-axis
    ax.set_ylim(0, 16)
    ax.set_yticks(range(0, 17, 2))
    ax.set_yticklabels([str(y) for y in range(0, 17, 2)], fontsize=11)
    ax.set_ylabel(r"Années moyennes de scolarité",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.grid(True, which='major', axis='both', color='gray',
            linestyle=':', linewidth=0.5)
    add_source(ax, 'Source: Our World in Data (2022)')
    save(fig, 'schooling.pdf')


# =====================================================================
# Figure 18: Digital Adoption Index vs GDP per capita
# =====================================================================
def digital_adoption_index():
    """Scatter: DAI vs real GDP per capita (log scale)."""
    print('Figure 16: Digital Adoption Index vs GDP/capita')

    # Load PWT 10.01 for real GDP per capita (2016)
    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')
    pwt = pwt[pwt['year'] == 2016].copy()
    pwt['rgdpe_pc'] = pwt['rgdpe'] / pwt['pop']

    # Load DAI data
    dai = pd.read_excel(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/DAIforweb.xlsx'
    ).rename(columns={'Year': 'year'})
    dai = dai.loc[dai['year'] == 2016, ['country', 'Digital Adoption Index']]

    # Merge
    df = pwt.merge(dai, on='country')

    fig, ax = new_figure(9, 4.5)

    ax.scatter(df['rgdpe_pc'], df['Digital Adoption Index'],
               s=70, color=palette[0], alpha=0.7, edgecolors='black',
               linewidths=0.3, zorder=3)

    # X-axis: log scale
    ax.set_xscale('log')
    ax.set_xlim(700, 120000)
    ax.set_xticks([1e3, 1e4, 1e5])
    ax.set_xticklabels([r'\$1\,000', r'\$10\,000', r'\$100\,000'],
                       fontsize=11)
    ax.set_xlabel(r"PIB réel par habitant (\$US)", fontsize=11)

    # Y-axis
    ax.set_ylim(0, 1)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_yticklabels([f'{x:.1f}' for x in np.arange(0, 1.01, 0.2)],
                       fontsize=11)
    ax.set_ylabel(r"Indice d'adoption numérique",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, 'Source: Banque mondiale (DAI) et Penn World Tables 10.01')
    save(fig, 'dai.pdf')


# =====================================================================
# Figure 19: Canada GDP/capita decomposition — 5-year periods
# =====================================================================
def canada_gdp_decomposition_5y():
    """Stacked bar: decompose Canadian Y/N growth into A, K/Y, L/N (5-yr)."""
    print('Figure 19: Canada GDP/capita decomposition (5-year periods)')

    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')
    ca = pwt[pwt['countrycode'] == 'CAN'].set_index('year')

    alpha = 1 / 3
    amp_ky = alpha / (1 - alpha)  # 0.5

    # 5-year periods from 1970 to 2019
    periods = []
    for y1 in range(1975, 2020, 5):
        y0 = y1 - 5
        periods.append((str(y1), y0, y1))

    a_vals, ky_vals, ln_vals, yn_vals = [], [], [], []
    for label, y0, y1 in periods:
        T = y1 - y0
        yn0 = ca.loc[y0, 'rgdpna'] / ca.loc[y0, 'pop']
        yn1 = ca.loc[y1, 'rgdpna'] / ca.loc[y1, 'pop']
        ky0 = ca.loc[y0, 'rkna'] / ca.loc[y0, 'rgdpna']
        ky1 = ca.loc[y1, 'rkna'] / ca.loc[y1, 'rgdpna']
        ln0 = ca.loc[y0, 'emp'] / ca.loc[y0, 'pop']
        ln1 = ca.loc[y1, 'emp'] / ca.loc[y1, 'pop']

        g_yn = ((yn1 / yn0) ** (1 / T) - 1) * 100
        g_ky = ((ky1 / ky0) ** (1 / T) - 1) * 100
        g_ln = ((ln1 / ln0) ** (1 / T) - 1) * 100

        ky_c = amp_ky * g_ky
        ln_c = g_ln
        a_c = g_yn - ky_c - ln_c

        a_vals.append(a_c)
        ky_vals.append(ky_c)
        ln_vals.append(ln_c)
        yn_vals.append(g_yn)

    x = np.arange(len(periods))
    labels = [p[0] for p in periods]
    w = 0.6

    fig, ax = new_figure(10, 5)

    components = [
        (ln_vals, palette[2], r"Taux d'emploi ($L/N$)"),
        (a_vals, palette[0], r"Productivité ($A$)"),
        (ky_vals, palette[1], r"Capital/PIB ($K/Y$)"),
    ]

    # Track L/N bar positions for circling
    ln_bars = []  # (x_center, bottom, top) for each bar

    for i in range(len(periods)):
        pos_base = 0
        neg_base = 0
        for j, (vals, color, label) in enumerate(components):
            v = vals[i]
            if v >= 0:
                ax.bar(x[i], v, w, bottom=pos_base, color=color,
                       label=label if i == 0 else None)
                if j == 0:  # L/N
                    ln_bars.append((x[i], pos_base, pos_base + v))
                pos_base += v
            else:
                ax.bar(x[i], v, w, bottom=neg_base, color=color,
                       label=label if i == 0 else None)
                if j == 0:  # L/N
                    ln_bars.append((x[i], neg_base + v, neg_base))
                neg_base += v

    # Circle the 1975 and 1980 L/N bars (indices 0 and 1)
    from matplotlib.patches import Ellipse
    for idx in [0, 1]:
        cx, bot, top = ln_bars[idx]
        h = top - bot
        ell = Ellipse((cx, bot + h / 2), width=w + 0.3, height=h + 0.25,
                      fill=False, edgecolor=palette[3], linewidth=2.5,
                      zorder=10)
        ax.add_patch(ell)

    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_xlabel(r"Période de 5 ans se terminant en\ldots", fontsize=11)
    ax.set_ylabel(r"Contribution à la croissance de $Y/N$ (\%/an)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    ax.set_ylim(-1.0, 3.5)
    ax.set_yticks(np.arange(-1.0, 3.6, 0.5))
    ax.set_yticklabels([f'{y:.1f}' + r'\%' for y in np.arange(-1.0, 3.6, 0.5)],
                       fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, 'Source: Penn World Tables 10.01 --- Canada')
    save(fig, 'canada_gdp_decomposition_5y.pdf')


# =====================================================================
# Figure 20: Participation rate by gender (Canada, 1976–present)
# =====================================================================
def participation_gender_ca():
    """Participation rate by gender + total employment rate — Canada."""
    print('Figure 20: Participation & employment by gender (Canada)')

    from stats_can import StatsCan
    sc = StatsCan()

    df = sc.table_to_df('14-10-0287-01')
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])

    # Keep seasonally adjusted, 15+, estimate only
    df = df[df['Data type'] == 'Seasonally adjusted']
    df = df[df['Age group'] == '15 years and over']
    df = df[df['Statistics'] == 'Estimate']

    # Participation rates by gender
    part = df[df['Labour force characteristics'] == 'Participation rate']
    male = part[part['Gender'] == 'Men+'].set_index('REF_DATE')['VALUE']
    female = part[part['Gender'] == 'Women+'].set_index('REF_DATE')['VALUE']
    male = male[~male.index.duplicated(keep='first')].sort_index()
    female = female[~female.index.duplicated(keep='first')].sort_index()

    # Overall employment rate
    emp = df[df['Labour force characteristics'] == 'Employment rate']
    emp_total = emp[emp['Gender'] == 'Total - Gender'].set_index('REF_DATE')['VALUE']
    emp_total = emp_total[~emp_total.index.duplicated(keep='first')].sort_index()

    fig, ax = new_figure(9, 4.5)

    ax.plot(male.index, male.values, color=palette[0],
            linewidth=2, label='Participation --- Hommes')
    ax.plot(female.index, female.values, color=palette[2],
            linewidth=2, label='Participation --- Femmes')
    ax.plot(emp_total.index, emp_total.values, color=palette[1],
            linewidth=2, linestyle='--', label="Emploi --- Total")

    import matplotlib.dates as mdates
    ax.set_xlim(pd.Timestamp('1976-01-01'), pd.Timestamp('2010-12-31'))
    tick_years = range(1980, 2011, 10)
    tick_dates = [pd.Timestamp(f'{y}-01-01') for y in tick_years]
    ax.set_xticks(tick_dates)
    ax.set_xticklabels([str(y) for y in tick_years], fontsize=11)
    ax.set_ylabel(r"Pourcentage (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(45, 80)
    ax.set_yticks(range(45, 81, 5))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(45, 81, 5)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right')
    add_source(ax, r"Source: Statistique Canada, tableau 14-10-0287-01")
    save(fig, 'participation_gender_ca.pdf')


# =====================================================================
# Figure 22: Unemployment rate (Canada, 1976–present)
# =====================================================================
def unemployment_ca():
    """Unemployment rate — Canada (StatsCan 14-10-0287-01)."""
    print('Figure 22: Unemployment rate (Canada)')

    from stats_can import StatsCan
    sc = StatsCan()

    df = sc.table_to_df('14-10-0287-01')
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])

    df = df[df['Data type'] == 'Seasonally adjusted']
    df = df[df['Gender'] == 'Total - Gender']
    df = df[df['Age group'] == '15 years and over']
    df = df[df['Statistics'] == 'Estimate']
    df = df[df['Labour force characteristics'] == 'Unemployment rate']

    unemp = df.set_index('REF_DATE')['VALUE']
    unemp = unemp[~unemp.index.duplicated(keep='first')].sort_index()

    fig, ax = new_figure(9, 4.5)

    ax.plot(unemp.index, unemp.values, color=palette[2], linewidth=2)

    # Recession shading
    for start, end in recessions_ca:
        ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    # Annotate major peaks
    annotations = [
        (pd.Timestamp('1982-12-01'), 13.1, '1982\n$\\sim$13\\%'),
        (pd.Timestamp('1992-11-01'), 11.8, '1992\n$\\sim$12\\%'),
        (pd.Timestamp('2009-06-01'), 8.7, '2009\n$\\sim$9\\%'),
        (pd.Timestamp('2020-05-01'), 13.7, 'COVID\n$\\sim$14\\%'),
    ]
    for date, peak, label in annotations:
        ax.annotate(label,
                    xy=(date, peak), xytext=(0, 15),
                    textcoords='offset points',
                    fontsize=9, color=palette[0], fontweight='bold',
                    ha='center', va='bottom')

    import matplotlib.dates as mdates
    ax.set_xlim(pd.Timestamp('1976-01-01'), unemp.index.max())
    tick_years = range(1980, unemp.index.max().year + 1, 10)
    tick_dates = [pd.Timestamp(f'{y}-01-01') for y in tick_years]
    ax.set_xticks(tick_dates)
    ax.set_xticklabels([str(y) for y in tick_years], fontsize=11)
    ax.set_ylabel(r"Taux de chômage (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(4, 16)
    ax.set_yticks(range(4, 17, 2))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(4, 17, 2)], fontsize=11)

    style_axes(ax)
    add_source(ax, r"Source: Statistique Canada, tableau 14-10-0287-01")
    save(fig, 'unemployment_ca.pdf')


# =====================================================================
# Figure 22b: Participation rate decline (Canada, total)
# =====================================================================
def participation_rate_ca():
    """Total participation rate — Canada (StatsCan 14-10-0287-01)."""
    print('Figure 22b: Participation rate decline (Canada)')

    from stats_can import StatsCan
    sc = StatsCan()

    df = sc.table_to_df('14-10-0287-01')
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])

    df = df[df['Data type'] == 'Seasonally adjusted']
    df = df[df['Gender'] == 'Total - Gender']
    df = df[df['Age group'] == '15 years and over']
    df = df[df['Statistics'] == 'Estimate']
    df = df[df['Labour force characteristics'] == 'Participation rate']

    part = df.set_index('REF_DATE')['VALUE']
    part = part[~part.index.duplicated(keep='first')].sort_index()

    fig, ax = new_figure(9, 4.5)

    ax.plot(part.index, part.values, color=palette[0], linewidth=2.5)

    # Recession shading
    for start, end in recessions_ca:
        ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    import matplotlib.dates as mdates
    ax.set_xlim(pd.Timestamp('1976-01-01'), pd.Timestamp('2020-01-01'))
    tick_years = list(range(1980, 2020, 10)) + [2020]
    tick_dates = [pd.Timestamp(f'{y}-01-01') for y in tick_years]
    ax.set_xticks(tick_dates)
    ax.set_xticklabels([str(y) for y in tick_years], fontsize=11)
    ax.set_ylabel(r"Taux de participation (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(60, 68)
    ax.set_yticks(range(60, 69, 2))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(60, 69, 2)], fontsize=11)

    style_axes(ax)
    add_source(ax, r"Source: Statistique Canada, tableau 14-10-0287-01")
    save(fig, 'participation_rate_ca.pdf')


# =====================================================================
# Figure 23: Immigration to Canada — PR + temporary as % of population
# =====================================================================
def immigration_ca():
    """Stacked area: immigrants (PR) and net non-permanent residents as % of population."""
    print('Figure 23: Immigration to Canada (% of population)')

    from stats_can import StatsCan
    sc = StatsCan()

    # ── Migration data: StatsCan 17-10-0014-01 ───────────────────────
    mig = sc.table_to_df('17-10-0014-01')
    mig = mig[mig['GEO'] == 'Canada']
    mig = mig[mig['Age group'] == 'All ages']
    mig = mig[mig['Gender'] == 'Total - gender']

    # REF_DATE format is '1971/1972' — extract first year
    mig['year'] = mig['REF_DATE'].str.split('/').str[0].astype(int)

    immigrants = (mig[mig['Type of migrant'] == 'Immigrants']
                  .set_index('year')['VALUE'])
    net_npr = (mig[mig['Type of migrant'] == 'Net non-permanent residents']
               .set_index('year')['VALUE'])
    immigrants = immigrants[~immigrants.index.duplicated(keep='first')].sort_index()
    net_npr = net_npr[~net_npr.index.duplicated(keep='first')].sort_index()

    # ── Population: StatsCan 17-10-0005-01 ────────────────────────────
    pop = sc.table_to_df('17-10-0005-01')
    pop = pop[pop['GEO'] == 'Canada']
    pop = pop[pop['Age group'] == 'All ages']
    pop = pop[pop['Gender'] == 'Total - gender']
    pop['REF_DATE'] = pd.to_datetime(pop['REF_DATE'])
    pop['year'] = pop['REF_DATE'].dt.year
    pop = pop.set_index('year')['VALUE']
    pop = pop[~pop.index.duplicated(keep='first')].sort_index()

    # ── Compute as % of population ────────────────────────────────────
    common = immigrants.index.intersection(net_npr.index).intersection(pop.index)
    imm_pct = (immigrants[common] / pop[common]) * 100
    npr_pct = (net_npr[common] / pop[common]) * 100
    # Clip negative NPR values to 0 for stacked area display
    npr_pct_pos = npr_pct.clip(lower=0)

    fig, ax = new_figure(9, 4.5)

    ax.stackplot(imm_pct.index, imm_pct.values, npr_pct_pos.values,
                 colors=[palette[0], palette[1]],
                 labels=[r'Résidents permanents',
                         r'Résidents temporaires (net)'],
                 edgecolor='k', linewidth=0.5)

    ax.set_xlim(imm_pct.index.min(), imm_pct.index.max())
    xticks = list(range(((imm_pct.index.min() // 10) + 1) * 10,
                        imm_pct.index.max() + 1, 10))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)
    ax.set_ylabel(r"Immigration (\% de la population)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 3.5)
    ax.set_yticks(np.arange(0, 3.6, 0.5))
    ax.set_yticklabels([f'{y:.1f}' + r'\%' for y in np.arange(0, 3.6, 0.5)],
                       fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0))
    add_source(ax, r"Source: Statistique Canada, tableaux 17-10-0014-01 et 17-10-0005-01")
    save(fig, 'immigration_ca.pdf')


def elephant_curve():
    """Elephant curve of global inequality, 1980-2020 (WIR 2022)."""
    print('  elephant_curve ...', end=' ', flush=True)

    # ── Data from World Inequality Report 2022, Figure 2.10 ──────────
    url = ('https://wir2022.wid.world/www-site/uploads/2022/03/'
           'WIR2022TablesFigures-Chapter.zip')
    import zipfile, io
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        with zf.open('WIR2022TablesFigures-Chapter/'
                     'WIR2022TablesFigures-Chapter2.xlsx') as f:
            df = pd.read_excel(f, sheet_name='data-F2.10')

    # Values are cumulative growth rates (divided by 100)
    df.columns = ['percentile', 'growth_raw']
    df['growth_pct'] = df['growth_raw'] * 100

    # Keep only the main curve (p10-p99) for clarity on a linear x-axis.
    main = df[df['percentile'] <= 99].copy()

    fig, ax = new_figure(8, 4)

    ax.plot(main['percentile'], main['growth_pct'],
            color=palette[0], linewidth=2.5, zorder=3)
    ax.fill_between(main['percentile'], 50, main['growth_pct'],
                    color=palette[0], alpha=0.08, zorder=2)

    # ── Axes ─────────────────────────────────────────────────────
    ax.set_xlim(10, 100)
    ax.set_xticks(range(10, 101, 10))
    ax.set_xticklabels([str(x) for x in range(10, 101, 10)], fontsize=13)
    ax.set_xlabel(r'Centile de la distribution mondiale du revenu',
                  fontsize=13)

    ax.set_ylim(50, 210)
    yticks = list(range(50, 211, 50))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}' + r'\%' for y in yticks], fontsize=13)
    ax.set_ylabel(r"Croissance cumulée du revenu réel, 1980--2020",
                  fontsize=13, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r'Source: World Inequality Report 2022 (Chancel et al.)')
    save(fig, 'elephant.pdf')


def inequality_top1_share():
    """Top 1% pre-tax income share for 8 countries (WID via OWID)."""
    print('  inequality_top1_share ...', end=' ', flush=True)

    df = pd.read_csv(
        "https://ourworldindata.org/grapher/income-share-top-1-before-tax-wid"
        ".csv?v=1&csvType=full&useColumnShortNames=true",
        storage_options={'User-Agent': 'Our World In Data data fetch/1.0'},
    )

    codes    = ['USA', 'AUS', 'CAN', 'GBR', 'CHN', 'FRA', 'IND', 'DEU']
    labels   = [r'États-Unis', 'Australie', 'Canada', 'Royaume-Uni',
                'Chine', 'France', 'Inde', 'Allemagne']
    colors   = [palette[0], palette[1], palette[2], palette[3],
                palette[4], palette[5], palette[6], palette[7]]

    val_col = [c for c in df.columns if c not in ('entity', 'code', 'year')][0]
    df = df[df['code'].isin(codes)]

    fig, ax = new_figure(8, 4)

    for code, label, color in zip(codes, labels, colors):
        sub = df[df['code'] == code].sort_values('year')
        ax.plot(sub['year'], sub[val_col],
                label=label, color=color, linewidth=2)

    latest = int(df['year'].max())
    ax.set_xlim(1950, latest)
    ax.set_xticks(range(1950, 2020 + 1, 10))
    ax.set_xticklabels(range(1950, 2020 + 1, 10), fontsize=12)

    ax.set_ylim(4, 28)
    ax.set_yticks(range(4, 28 + 1, 4))
    ax.set_yticklabels([f'{x}' + r'\%' for x in range(4, 28 + 1, 4)],
                        fontsize=12)
    ax.set_ylabel(r"Part du revenu du 1\% le plus riche (avant impôt)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(-0.01, 1.0))
    add_source(ax, 'Source: World Inequality Database (2025)')
    save(fig, 'inequality_within_countries.pdf')


# =====================================================================
# Outsourcing: within vs between firm inequality (Song et al. 2019)
# =====================================================================
def outsourcing_inequality():
    """Between- vs within-firm decomposition of earnings inequality growth."""
    print('  outsourcing_inequality ...', end=' ', flush=True)

    # Data from Song, Price, Guvenen, Bloom & von Wachter (QJE, 2019)
    # Change in variance of log earnings, US, 1981-2013
    categories = [r'\textbf{Entre} les' + '\n' + r'entreprises',
                  r'\textbf{Au sein} des' + '\n' + r'entreprises']
    shares = [2/3, 1/3]       # fraction of total increase
    total_increase = 100       # normalised to 100%
    values = [s * total_increase for s in shares]

    fig, ax = new_figure(6, 4.5)

    bars = ax.bar(categories, values, width=0.55,
                  color=[palette[0], palette[1]], edgecolor='none', zorder=3)

    # Value labels on bars
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                f'{v:.0f}' + r'\%', ha='center', va='bottom',
                fontsize=14, fontweight='bold',
                color=palette[0] if v > 50 else palette[1])

    ax.set_ylim(0, 85)
    ax.set_yticks([])
    ax.tick_params(axis='x', labelsize=13)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.set_ylabel(r"Contribution à la hausse des inégalités salariales",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.05)

    add_source(ax, r'Source: Song, Price, Guvenen, Bloom \& von Wachter (QJE, 2019)')
    save(fig, 'outsourcing_inequality.pdf')


# =====================================================================
# Job polarization: routine vs nonroutine employment (US, 1983-2024)
# =====================================================================
def job_polarization():
    """Employment by occupational group (routine vs nonroutine, US)."""
    print('  job_polarization ...', end=' ', flush=True)

    # FRED series (CPS Table A-13, annual averages)
    nrc = get_fred_data('LNU02032201', frequency='a', aggregation_method='avg')  # Mgmt/Prof
    nrm = get_fred_data('LNU02032204', frequency='a', aggregation_method='avg')  # Service
    rc  = get_fred_data('LNU02032205', frequency='a', aggregation_method='avg')  # Sales/Office
    rm1 = get_fred_data('LNU02032210', frequency='a', aggregation_method='avg')  # Production/Transport
    rm2 = get_fred_data('LNU02032211', frequency='a', aggregation_method='avg')  # Construction
    rm3 = get_fred_data('LNU02032212', frequency='a', aggregation_method='avg')  # Install/Maint/Repair

    # Combine routine manual
    rm = rm1 + rm2 + rm3

    # Convert to millions
    nrc, nrm, rc, rm = nrc / 1000, nrm / 1000, rc / 1000, rm / 1000

    # Drop NaNs and align
    df = pd.DataFrame({'nrc': nrc, 'nrm': nrm, 'rc': rc, 'rm': rm}).dropna()

    # Normalize to 100 at start of series (1983)
    for col in df.columns:
        df[col] = df[col] / df[col].iloc[0] * 100

    years = df.index.year

    fig, ax = new_figure(9, 4.5)

    # Non-routine: solid lines; routine: dotted lines
    # Cognitive: navy; Manual: green
    ax.plot(years, df['nrc'], color=palette[0], linewidth=2.5, linestyle='-',
            label='Non routinier cognitif')
    ax.plot(years, df['nrm'], color=palette[1], linewidth=2.5, linestyle='-',
            label='Non routinier manuel')
    ax.plot(years, df['rc'], color=palette[0], linewidth=2.5, linestyle=':',
            label='Routinier cognitif')
    ax.plot(years, df['rm'], color=palette[1], linewidth=2.5, linestyle=':',
            label='Routinier manuel')

    _labour_history_xaxis(ax)
    ax.set_ylim(100, 260)
    ax.set_yticks(range(100, 261, 20))
    ax.set_yticklabels([f'{y}' for y in range(100, 261, 20)], fontsize=12)
    ax.set_ylabel(r"Indice (1983 = 100)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Recession shading
    for start, end in recessions_us:
        if start >= pd.Timestamp('1983-01-01'):
            ax.axvspan(start.year + start.month / 12,
                       end.year + end.month / 12,
                       color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(-0.01, 1.0))
    add_source(ax, r'Source: BLS, Current Population Survey (via FRED)')
    save(fig, 'job_polarization.pdf')


# =====================================================================
# Great Gatsby Curve (Corak 2013)
# =====================================================================
def gatsby_curve():
    """Scatter: Gini coefficient vs intergenerational earnings elasticity.

    IGE estimates: Corak (2013), "Inequality from Generation to Generation:
    The United States in Comparison," Figure 1 — exact published values for
    22 countries, derived from a meta-analysis of the literature as described
    in Corak (2006, IZA DP 1993).

    Gini coefficients: World Bank SI.POV.GINI, closest available to ~2005
    (most recent data available when Corak wrote his paper, ~2010).
    NZL and SGP have no World Bank Gini; we use OECD (NZL, ~2004) and
    Singapore Department of Statistics (SGP, ~2000).
    """
    print('Figure: Great Gatsby Curve')

    # ── IGE: exact values from Corak (2013) Figure 1 ──────────────────
    ige_corak = {
        'DNK': 0.15, 'NOR': 0.17, 'FIN': 0.18, 'CAN': 0.19,
        'SWE': 0.27, 'AUS': 0.26, 'NZL': 0.29, 'DEU': 0.32,
        'JPN': 0.34, 'FRA': 0.41, 'ESP': 0.40, 'PAK': 0.46,
        'CHE': 0.46, 'ITA': 0.50, 'GBR': 0.50, 'USA': 0.47,
        'SGP': 0.44, 'ARG': 0.49, 'CHN': 0.60, 'CHL': 0.52,
        'BRA': 0.58, 'PER': 0.67,
    }

    # ── Gini: World Bank API (SI.POV.GINI), closest to ~1995 ─────────
    iso_to_fr = {
        'DNK': 'Danemark', 'NOR': 'Norvège', 'FIN': 'Finlande',
        'CAN': 'Canada', 'SWE': 'Suède', 'AUS': 'Australie',
        'NZL': 'Nlle-Zélande', 'DEU': 'Allemagne', 'JPN': 'Japon',
        'FRA': 'France', 'ESP': 'Espagne', 'PAK': 'Pakistan',
        'CHE': 'Suisse', 'ITA': 'Italie', 'GBR': 'Royaume-Uni',
        'USA': 'États-Unis', 'SGP': 'Singapour', 'ARG': 'Argentine',
        'CHN': 'Chine', 'CHL': 'Chili', 'BRA': 'Brésil',
        'PER': 'Pérou',
    }

    # Fetch from World Bank
    iso_list = ';'.join(iso_to_fr.keys())
    wb_url = (f'https://api.worldbank.org/v2/country/{iso_list}'
              f'/indicator/SI.POV.GINI?date=1985:2005&format=json&per_page=1500')
    from collections import defaultdict
    gini_wb = defaultdict(list)
    try:
        wb = requests.get(wb_url, timeout=30).json()
        if len(wb) > 1 and wb[1]:
            for e in wb[1]:
                if e['value'] is not None:
                    gini_wb[e['countryiso3code']].append(
                        (int(e['date']), e['value']))
    except Exception as exc:
        print(f'  World Bank API failed ({exc}); using fallback Gini')

    # Pick closest year to 2005 for each country
    target_year = 2005
    gini_selected = {}
    for iso in iso_to_fr:
        entries = sorted(gini_wb.get(iso, []),
                         key=lambda x: abs(x[0] - target_year))
        if entries:
            year, val = entries[0]
            gini_selected[iso] = val

    # Fallback / override for countries with no or sparse WB data
    # JPN: OECD Income Distribution Database, ~2006 ≈ 32.1
    # NZL: OECD Income Distribution Database, ~2004 ≈ 33.5
    # SGP: Singapore Dept of Statistics, ~2000 ≈ 42.5
    fallbacks = {'JPN': 32.1, 'NZL': 33.5, 'SGP': 42.5}
    for iso, val in fallbacks.items():
        if iso not in gini_selected:
            gini_selected[iso] = val

    # Build the final data dict  {French name: (Gini, IGE)}
    data = {}
    for iso, fr_name in iso_to_fr.items():
        if iso in gini_selected and iso in ige_corak:
            data[fr_name] = (gini_selected[iso], ige_corak[iso])

    countries = list(data.keys())
    gini = np.array([data[c][0] for c in countries])
    ige  = np.array([data[c][1] for c in countries])

    fig, ax = new_figure(8, 4)

    # Scatter
    ax.scatter(gini, ige, s=90, color=palette[0], alpha=0.75, zorder=5,
               edgecolors=palette[0], linewidth=0.8)

    # Highlight Canada
    idx_ca = countries.index('Canada')
    ax.scatter(gini[idx_ca], ige[idx_ca], s=110, color=palette[1], alpha=0.85, zorder=6,
               edgecolors=palette[0], linewidth=0.8)

    # Trend line — span the full x-axis range
    z = np.polyfit(gini, ige, 1)
    x_line = np.linspace(22, 62, 100)
    ax.plot(x_line, np.polyval(z, x_line), color=palette[2], linewidth=2, zorder=2)

    # Labels — offset logic to avoid collisions (tuned to WB ~2005 Gini)
    offsets = {
        'Danemark':     ( 1,  -0.025),
        'Norvège':      ( 1,  -0.025),
        'Finlande':     (-1,   0.015),
        'Canada':       ( 1,   0.015),
        'Suède':        (-1,   0.015),
        'Australie':    ( 1,  -0.025),
        'Nlle-Zélande': (-1,  -0.025),
        'Allemagne':    (-1,   0.015),
        'Japon':        (-1,  -0.025),
        'France':       (-1,   0.015),
        'Espagne':      ( 1,  -0.025),
        'Pakistan':     (-1,  -0.025),
        'Suisse':       (-1,   0.02),
        'Italie':       (-1,   0.02),
        'Royaume-Uni':  ( 1,   0.015),
        'États-Unis':   ( 1,  -0.025),
        'Singapour':    ( 1,  -0.025),
        'Argentine':    ( 1,   0.015),
        'Chine':        (-1,   0.015),
        'Chili':        ( 1,  -0.025),
        'Brésil':       ( 1,   0.015),
        'Pérou':        ( 0,   0.025),
    }

    for i, c in enumerate(countries):
        dx, dy = offsets.get(c, (1, 0.01))
        ha = 'right' if dx < 0 else 'left' if dx > 0 else 'center'
        color = palette[1] if c == 'Canada' else palette[7]
        weight = 'bold' if c == 'Canada' else 'normal'
        ax.text(gini[i] + dx * 0.5, ige[i] + dy, c, fontsize=8, ha=ha, va='center',
                color=color, fontweight=weight)

    style_axes(ax)
    ax.grid(True, which='major', axis='x', color='gray', linestyle=':', linewidth=0.5)
    ax.set_xlabel(r"Inégalité des revenus (coefficient de Gini)", fontsize=12)
    ax.set_ylabel(r"Élasticité intergénérationnelle", fontsize=12,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.03)
    ax.set_xlim(22, 62)
    ax.set_ylim(0.10, 0.70)
    ax.set_yticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
    ax.set_yticklabels([r'0.1', r'0.2', r'0.3', r'0.4',
                        r'0.5', r'0.6', r'0.7'])
    ax.set_xticks([25, 30, 35, 40, 45, 50, 55, 60])
    ax.set_xticklabels([r'25', r'30', r'35', r'40', r'45', r'50', r'55', r'60'])
    ax.tick_params(labelsize=12)

    add_source(ax, r"Source: Corak (2013); World Bank"
               r" (Gini, c.\,2005)")
    save(fig, 'gatsby_curve.pdf')


# =====================================================================
# Baumol cost disease — cumulative CPI by sector (Canada, 2000–2025)
# =====================================================================
def baumol_cost_disease_canada():
    """Perry-style 'Chart of the Century' for Canada (2000 = 100).

    Shows 8 CPI sub-categories from Statistics Canada table 18-10-0005-01,
    normalized to 2000 = 100. Labor-intensive services that are hard to
    automate (health care, tuition, restaurants, shelter) soar far above
    the CPI reference line, while tradeable/tech-driven goods (digital
    equipment, telephone, clothing) fall dramatically.

    Inspired by Mark Perry's AEI chart.
    """
    print('  baumol_cost_disease_canada ...', end=' ', flush=True)

    from stats_can import StatsCan
    sc = StatsCan()
    df = sc.table_to_df('18-10-0005-01')

    # Filter: Canada, base 2002 = 100
    ca = df[(df['GEO'] == 'Canada') & (df['UOM'] == '2002=100')].copy()
    ca['year'] = ca['REF_DATE'].dt.year
    ca = ca[ca['year'] >= 2000].sort_values('year')

    # ── Series specification (without colors — assigned by gradient) ──
    # Ordered from highest to lowest final value
    # (eng_name, fr_label, linestyle, linewidth)
    series_spec_no_color = [
        ('Health care services',
         r"Santé", '-', 2.5),
        ('Food purchased from restaurants',
         r"Restaurants", '-', 2.5),
        ('Tuition fees',
         r"Frais de scolarité", '-', 2.5),
        ('Shelter',
         r"Logement", '-', 2.5),
        ('Clothing and footwear',
         r"Vêtements et chaussures", '-', 2.5),
        ('Toys, games (excluding video games) and hobby supplies',
         r"Jouets et jeux", '-', 2.5),
        ('Telephone services',
         r"Téléphone", '-', 2.5),
        ('Home entertainment equipment, parts and services',
         r"Divertissement maison", '-', 2.5),
        ('Video equipment',
         r"Vidéo", '-', 2.5),
        ('Digital computing equipment and devices',
         r"Équipement informatique", '-', 2.5),
    ]

    # ── Colormap gradient: warm (red) → cool (blue) ──────────────────
    from matplotlib.colors import LinearSegmentedColormap
    import matplotlib.cm as cm
    # Custom gradient: saturated red → saturated purple → saturated blue
    # No pale/white midpoint — stays vivid throughout
    from matplotlib.colors import LinearSegmentedColormap as LSC
    custom_cmap = LSC.from_list('warm_cool', [
        '#b5000e',   # deep red
        '#e04530',   # bright red
        '#d4700a',   # orange
        '#8c5fb0',   # muted purple
        '#3a7ebf',   # medium blue
        '#1a4e8a',   # dark blue
        '#0a2f5c',   # navy
    ])
    n = len(series_spec_no_color)
    gradient_colors = [custom_cmap(i / (n - 1)) for i in range(n)]

    # CPI reference stays gray, inserted at its rank position
    c_cpi = palette[7]

    # Build final series_spec with colors
    series_spec = []
    for i, (eng_name, fr_label, ls, lw) in enumerate(series_spec_no_color):
        series_spec.append((eng_name, fr_label, gradient_colors[i], ls, lw))
    # Insert CPI after Shelter (index 4)
    series_spec.insert(4, ('All-items', r"IPC global", c_cpi, ':', 2.5))

    # ── Build data dict {eng_name: Series indexed by year} ─────────────
    series_data = {}
    for eng_name, *_ in series_spec:
        sub = ca[ca['Products and product groups'] == eng_name]
        s = sub.set_index('year')['VALUE'].dropna().sort_index()
        if len(s) == 0:
            print(f'  Warning: no data for "{eng_name}"')
            continue
        base_val = s.loc[2000] if 2000 in s.index else s.iloc[0]
        s = s / base_val * 100
        series_data[eng_name] = s

    # ── Plot ───────────────────────────────────────────────────────────
    fig, ax = new_figure(10, 5.5)

    for eng_name, fr_label, color, ls, lw in series_spec:
        if eng_name not in series_data:
            continue
        s = series_data[eng_name]
        ax.plot(s.index, s.values, color=color, linewidth=lw,
                linestyle=ls, zorder=3)

    # ── End-of-line labels (with repulsion to avoid overlap) ─────────
    last_year = max(s.index[-1] for s in series_data.values())

    # Collect (eng_name, final_value) for all plotted series
    label_items = []
    for eng_name, fr_label, color, ls, lw in series_spec:
        if eng_name not in series_data:
            continue
        s = series_data[eng_name]
        label_items.append((eng_name, fr_label, color, s.iloc[-1]))

    # Sort by final value (descending) and repel labels so they don't overlap
    label_items.sort(key=lambda x: -x[3])
    min_gap = 10.0  # minimum vertical gap in data-units between label centers
    placed_y = []    # list of placed y-positions (descending order)
    label_positions = {}  # eng_name -> placed y

    for eng_name, fr_label, color, raw_y in label_items:
        y = raw_y
        # Push label down if it collides with any already-placed label above
        for py in placed_y:
            if py - y < min_gap:
                y = py - min_gap
        placed_y.append(y)
        label_positions[eng_name] = y

    for eng_name, fr_label, color, raw_y in label_items:
        y_pos = label_positions[eng_name]
        # Draw a thin connector line from the data endpoint to the label
        if abs(y_pos - raw_y) > 3:
            ax.plot([last_year + 0.1, last_year + 0.25],
                    [raw_y, y_pos], color=color, linewidth=0.5,
                    alpha=0.5, clip_on=False)
        ax.text(last_year + 0.3, y_pos, fr_label,
                fontsize=9, color=color, va='center', ha='left',
                fontweight='bold', clip_on=False)

    # ── Reference line at 100 ──────────────────────────────────────────
    ax.axhline(y=100, color='gray', linewidth=0.6, linestyle=':', zorder=1)

    # ── Axes ───────────────────────────────────────────────────────────
    ax.set_xlim(2000, last_year)
    xtick_end = last_year + 1
    ax.set_xticks(range(2000, xtick_end, 5))
    ax.set_xticklabels([str(y) for y in range(2000, xtick_end, 5)],
                       fontsize=11)

    ax.set_ylim(0, 250)
    yticks = list(range(0, 251, 50))
    ax.set_yticks(yticks)
    ax.set_yticklabels([str(y) for y in yticks], fontsize=11)
    ax.set_ylabel(r"Indice des prix (2000 = 100)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Extra right margin for end-of-line labels
    fig.subplots_adjust(right=0.65)

    style_axes(ax)
    add_source(ax, r"Source: Statistique Canada, tableau 18-10-0005-01")
    save(fig, 'baumol_cost_disease_canada.pdf')


# =====================================================================
# Session 6 time-series comparisons, updated with Canada
# =====================================================================
_CA_GROUPS = {
    'Exportateurs de pétrole': (['SAU', 'RUS', 'NOR', 'ARE', 'KWT', 'QAT', 'IRN',
                                 'IRQ', 'NGA', 'DZA', 'KAZ', 'AGO', 'VEN'], '#b8f0d4'),
    'Europe du Nord': (['DEU', 'NLD', 'CHE', 'SWE', 'DNK'], '#6ee0a8'),
    'Chine': (['CHN'], '#1a9e5a'),
    "Asie de l'Est": (['JPN', 'KOR', 'SGP', 'MYS', 'THA', 'HKG'], palette[1]),
    'Anglosphère': (['USA', 'GBR', 'AUS'], '#cc2f33'),
    'Europe périphérique': (['ESP', 'ITA', 'GRC', 'PRT', 'TUR'], '#ff9a9d'),
    'Canada': (['CAN'], palette[0]),
}
_SAVING_COUNTRIES = {
    'CHN': ('China', palette[0]), 'USA': ('United States', palette[2]),
    'NOR': ('Norway', palette[1]), 'SAU': ('Arabie saoudite', palette[3]),
    'KOR': ('South Korea', palette[4]), 'CAN': ('Canada', palette[6]),
}
_INTERNATIONAL_DATA_DIR = Path(__file__).resolve().parents[1] / 'Data'
_CA_TIME_DATA = _INTERNATIONAL_DATA_DIR / 's3_current_accounts_timeseries.csv'
_SAVING_TIME_DATA = _INTERNATIONAL_DATA_DIR / 's3_saving_rates_timeseries.csv'
_TIME_METADATA = _INTERNATIONAL_DATA_DIR / 's3_international_timeseries.json'


def refresh_international_timeseries(as_of=None):
    """Cache the latest completed annual observations; never zero-fill gaps.

    IMF BCA and world NGDPD both use billions of current US dollars. The
    original Session 6 country groups are unchanged, with Canada separate.
    Use their complete common consecutive interval (currently 2001-2025).
    Savings retain each country's own endpoint, without extrapolation.
    """
    from concurrent.futures import ThreadPoolExecutor

    retrieved_on = pd.Timestamp(as_of or pd.Timestamp.today()).date()
    last_year = retrieved_on.year - 1
    urls = {
        'BCA': 'https://www.imf.org/external/datamapper/api/v1/BCA',
        'NGDPD': 'https://www.imf.org/external/datamapper/api/v1/NGDPD',
        'indicators': 'https://www.imf.org/external/datamapper/api/v1/indicators',
        'saving': (f'https://api.worldbank.org/v2/country/{";".join(_SAVING_COUNTRIES)}/'
                   f'indicator/NY.GNS.ICTR.ZS?format=json&per_page=1000&date=1980:{last_year}'),
    }

    def fetch(item):
        key, url = item
        response = requests.get(url, timeout=50)
        response.raise_for_status()
        return key, response.json()

    with ThreadPoolExecutor(max_workers=4) as pool:
        payloads = dict(pool.map(fetch, urls.items()))
    ca_values = payloads['BCA']['values']['BCA']
    gdp_values = payloads['NGDPD']['values']['NGDPD']['WEOWORLD']
    indicators = payloads['indicators']['indicators']
    assert indicators['BCA']['source'] == indicators['NGDPD']['source']
    assert indicators['BCA']['unit'] == indicators['NGDPD']['unit'] == 'Billions of U.S. dollars'
    codes = [iso for members, _ in _CA_GROUPS.values() for iso in members]
    assert len(codes) == len(set(codes)), 'A country occurs in more than one group'
    ca = pd.DataFrame({iso: pd.Series(ca_values[iso], dtype=float) for iso in codes})
    ca.index = ca.index.astype(int)
    world_gdp = pd.Series(gdp_values, dtype=float)
    world_gdp.index = world_gdp.index.astype(int)
    ca['world_gdp_billion_usd'] = world_gdp
    ca = ca.sort_index().loc[1995:last_year]
    complete = ca.notna().all(axis=1)
    if not complete.any():
        raise ValueError('No common complete year for the original country groups')
    first_complete = int(complete[complete].index.min())
    last_complete = int(complete[complete].index.max())
    if not complete.loc[first_complete:last_complete].all():
        raise ValueError('Interior data gap in the regional current-account comparison')
    if not (ca.world_gdp_billion_usd > 0).all():
        raise ValueError('Invalid world GDP denominator')

    wb_meta, wb_records = payloads['saving']
    assert wb_meta['pages'] == 1 and wb_records
    saving = pd.DataFrame(index=range(1980, last_year + 1), columns=_SAVING_COUNTRIES, dtype=float)
    for record in wb_records:
        if record['value'] is not None:
            saving.loc[int(record['date']), record['countryiso3code']] = record['value']
    if saving.notna().sum().min() == 0:
        raise ValueError('An original saving series or Canada is entirely missing')
    ca.index.name = saving.index.name = 'year'
    _INTERNATIONAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    ca.to_csv(_CA_TIME_DATA)
    saving.to_csv(_SAVING_TIME_DATA)
    metadata = {
        'retrieved_on': retrieved_on.isoformat(), 'urls': urls,
        'current_accounts': {
            'source': indicators['BCA']['source'],
            'units_input': 'Billions of current US dollars, both numerator and denominator.',
            'units_output': 'Percent of world GDP.',
            'group_members': {label: members for label, (members, _) in _CA_GROUPS.items()},
            'plotted_range': [first_complete, last_complete],
            'coverage': 'Original Session 6 groups plus separate Canada, constant membership. All members must report every plotted year. Earliest complete year is 2001 because Iraq starts then.',
            'transformation': 'Sum BCA by group; divide by WEOWORLD NGDPD; multiply by 100. Positive/negative group balances stack on the corresponding side of zero in each year.',
            'excluded_years': '2026 and later forecasts excluded; 1995-2000 excluded from plot for incomplete country coverage. Unfilled gaps retained in cached data.',
            'indicator_metadata': {key: indicators[key] for key in ['BCA', 'NGDPD']},
        },
        'saving': {
            'source': 'World Bank, World Development Indicators',
            'last_updated': wb_meta['lastupdated'], 'indicator': 'NY.GNS.ICTR.ZS',
            'units': 'Gross national saving as percent of each country\'s GDP.',
            'countries': list(_SAVING_COUNTRIES),
            'last_year_by_country': {iso: int(saving[iso].last_valid_index()) for iso in saving},
            'missing_values': 'No zero-filling, interpolation, or extrapolation. NaNs break lines.',
        },
        'refresh_command': 'python -c "import figures_s3 as f; f.refresh_international_timeseries(); f.current_accounts_divergence(); f.saving_rates_divergence()"',
    }
    _TIME_METADATA.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Current accounts: complete panel {first_complete}-{last_complete}')
    print('Saving endpoints:', metadata['saving']['last_year_by_country'])


def current_accounts_divergence():
    """Restore the Session 6 regional stacked time series (% of world GDP)."""
    metadata = json.loads(_TIME_METADATA.read_text())
    first, last = metadata['current_accounts']['plotted_range']
    raw = pd.read_csv(_CA_TIME_DATA, index_col='year').loc[first:last]
    assert raw.notna().all().all()
    values = {name: raw[members].sum(axis=1) / raw.world_gdp_billion_usd * 100
              for name, (members, _) in _CA_GROUPS.items()}
    fig, ax = new_figure(10, 5)
    positive = np.zeros(len(raw))
    negative = np.zeros(len(raw))
    # Keep Canada's small contribution next to zero rather than burying it.
    plot_order = ['Canada'] + [name for name in _CA_GROUPS if name != 'Canada']
    handles = {}
    for name in plot_order:
        series = values[name].to_numpy()
        bottom = np.where(series >= 0, positive, negative)
        handles[name] = ax.bar(raw.index, series, bottom=bottom, width=0.75,
                               color=_CA_GROUPS[name][1], label=name,
                               edgecolor='none', linewidth=0, zorder=3)
        positive += np.maximum(series, 0)
        negative += np.minimum(series, 0)
    ax.axhline(0, color='black', linewidth=0.7, zorder=4)
    # Half a bar at either end is the categorical extent of the annual data.
    ax.set_xlim(first - 0.5, last + 0.5)
    ticks = sorted(set([first, last] + list(range(2005, last + 1, 5))))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(year) for year in ticks], fontsize=11)
    bound = max(3.0, np.ceil(max(positive.max(), abs(negative.min())) / 0.5) * 0.5)
    ax.set_ylim(-bound, bound)
    yticks = np.arange(-bound, bound + 0.25, 0.5)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{value:.1f}' + r'\%' for value in yticks], fontsize=11)
    ax.set_ylabel(r'(\% du PIB mondial)', fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.legend([handles[name] for name in _CA_GROUPS], list(_CA_GROUPS),
              fontsize=9, ncol=4, loc='lower right', frameon=False,
              handlelength=1.1, handletextpad=0.4, columnspacing=1.0)
    style_axes(ax)
    ax.set_axisbelow(True)
    # Leave the empty strip containing the legend free of grid lines.
    for line, value in zip(ax.yaxis.get_gridlines(), yticks):
        if value < negative.min() - 0.2:
            line.set_visible(False)
    vintage = re.search(r'\((\w+) (\d{4})\)', metadata['current_accounts']['source'])
    month = {'April': 'avril', 'October': 'oct.'}[vintage.group(1)]
    add_source(ax, f'Source : FMI, WEO ({month} {vintage.group(2)})')
    save(fig, 's3_current_accounts_divergence.pdf')


def saving_rates_divergence():
    """Restore the five Session 6 saving-rate histories and add Canada."""
    saving = pd.read_csv(_SAVING_TIME_DATA, index_col='year')
    assert set(saving.columns) == set(_SAVING_COUNTRIES)
    fig, ax = new_figure(10, 5)
    for iso, (name, color) in _SAVING_COUNTRIES.items():
        # Retain the full index: NaNs must break lines, not be bridged.
        ax.plot(saving.index, saving[iso], color=color,
                linewidth=2.7 if iso == 'CAN' else 2,
                label=COUNTRY_FR.get(name, name))
    first = int(saving.dropna(how='all').index.min())
    last = int(saving.dropna(how='all').index.max())
    ax.set_xlim(first, last)
    ticks = list(range(first, last + 1, 5))
    if last not in ticks:
        ticks.append(last)
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(year) for year in ticks], fontsize=11)
    ax.set_ylim(10, 60)
    ax.set_yticks(range(10, 61, 10))
    ax.set_yticklabels([str(value) + r'\%' for value in range(10, 61, 10)], fontsize=11)
    ax.set_ylabel(r'Épargne brute (\% du PIB)', fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.legend(frameon=False, fontsize=9, loc='upper left', ncol=3,
              bbox_to_anchor=(0.02, 0.99), columnspacing=1.4, handlelength=2)
    style_axes(ax)
    add_source(ax, r'Source : Banque mondiale')
    save(fig, 's3_saving_rates_divergence.pdf')


# =====================================================================
# AI capital-market evidence: construction spending and real Treasury yield
# =====================================================================
_AI_EVIDENCE_DIR = Path(__file__).resolve().parents[1] / 'Data'
_AI_CONSTRUCTION_DATA = _AI_EVIDENCE_DIR / 's3_ai_datacenter_construction.csv'
_AI_REAL_YIELD_DATA = _AI_EVIDENCE_DIR / 's3_ai_real_yield.csv'
_AI_EVIDENCE_META = _AI_EVIDENCE_DIR / 's3_ai_capital_evidence.json'
_AI_REAL_CONSTRUCTION_DATA = _AI_EVIDENCE_DIR / 's3_ai_datacenter_real_monthly.csv'
_AI_NOMINAL_GDP_DATA = _AI_EVIDENCE_DIR / 's3_ai_us_nominal_gdp.csv'
_AI_CONSTRUCTION_GDP_DATA = _AI_EVIDENCE_DIR / 's3_ai_datacenter_gdp_share.csv'
_AI_BOOMS_DATA = _AI_EVIDENCE_DIR / 's3_ai_investment_booms.csv'


def refresh_ai_capital_evidence(as_of=None):
    """Cache public source data; normal figure generation remains offline."""
    from concurrent.futures import ThreadPoolExecutor
    from io import BytesIO
    from hashlib import sha256

    retrieved_on = pd.Timestamp(as_of or pd.Timestamp.today()).normalize()
    urls = {
        'construction': 'https://www.census.gov/construction/c30/xlsx/privsatime.xlsx',
        'real_yield': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFII10&cosd=2015-01-01',
    }

    def fetch(item):
        name, url = item
        response = requests.get(url, timeout=50)
        response.raise_for_status()
        return name, response.content

    with ThreadPoolExecutor(max_workers=2) as pool:
        payloads = dict(pool.map(fetch, urls.items()))
    sheet = pd.read_excel(BytesIO(payloads['construction']), sheet_name='Private SA', header=None)
    header = sheet.index[sheet[0].eq('Date')].item()
    value_col = sheet.columns[sheet.loc[header].eq('Data center')].item()
    date_text = sheet[0].astype(str)
    dates = pd.to_datetime(date_text.str.replace(r'[pr]$', '', regex=True),
                           format='%b-%y', errors='coerce')
    construction = pd.DataFrame({
        'date': dates, 'millions_usd_saar': pd.to_numeric(sheet[value_col], errors='coerce'),
        'release_flag': date_text.str.extract(r'([pr])$', expand=False).fillna(''),
    }).dropna(subset=['date', 'millions_usd_saar']).sort_values('date')
    construction = construction[construction.date <= retrieved_on]
    assert len(construction) > 100 and construction.date.is_unique
    assert (construction.millions_usd_saar > 0).all()
    assert len(pd.date_range(construction.date.min(), construction.date.max(), freq='MS')) == len(construction)
    real_yield = pd.read_csv(BytesIO(payloads['real_yield']))
    real_yield = real_yield.rename(columns={'observation_date': 'date', 'DFII10': 'percent'})
    real_yield['date'] = pd.to_datetime(real_yield.date)
    real_yield['percent'] = pd.to_numeric(real_yield.percent, errors='coerce')
    real_yield = real_yield[real_yield.date <= retrieved_on].sort_values('date')
    assert real_yield.date.is_unique and real_yield.percent.notna().sum() > 1000
    real_yield = real_yield[real_yield.date <= real_yield.loc[real_yield.percent.notna(), 'date'].max()]
    _AI_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    construction.to_csv(_AI_CONSTRUCTION_DATA, index=False)
    real_yield.to_csv(_AI_REAL_YIELD_DATA, index=False)
    metadata = {
        'retrieved_on': retrieved_on.date().isoformat(),
        'construction': {
            'url': urls['construction'], 'source': 'US Census Bureau, Private SA, Data center',
            'units_input': 'Millions of current US dollars, seasonally adjusted annual rate.',
            'transformation': 'No transformation in cached CSV; see construction_share_gdp for the plotted ratio.',
            'coverage': 'Private construction value put in place. Excludes servers/racks and land acquisition. Not exclusively AI facilities.',
            'definitions_url': 'https://www.census.gov/construction/c30/definitions.html',
            'last_date': construction.date.max().date().isoformat(),
            'release_flags': 'p = preliminary; r = revised; flags preserved from source workbook.',
            'download_sha256': sha256(payloads['construction']).hexdigest(),
        },
        'real_yield': {
            'url': urls['real_yield'], 'source': 'Federal Reserve Board, H.15, via FRED, DFII10',
            'units': 'Percent per annum, daily, not seasonally adjusted.',
            'coverage': '10-year inflation-indexed constant-maturity US Treasury yield; observed market real yield, not an estimate of the natural rate or causal AI effect.',
            'transformation': 'None; missing holiday observations retained as gaps; no interpolation.',
            'last_date': real_yield.loc[real_yield.percent.notna(), 'date'].max().date().isoformat(),
            'download_sha256': sha256(payloads['real_yield']).hexdigest(),
        },
        'refresh_command': 'python -c "import figures_s3 as f; f.refresh_ai_capital_evidence(); f.ai_datacenter_construction(); f.ai_real_yield()"',
    }
    _AI_EVIDENCE_META.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Construction endpoint:', metadata['construction']['last_date'])
    print('Real-yield endpoint:', metadata['real_yield']['last_date'])
    refresh_ft_ai_evidence(as_of=as_of)
    refresh_ai_construction_gdp(as_of=as_of)


def refresh_ai_construction_gdp(as_of=None):
    """Match nominal construction and GDP at complete quarterly frequency.

    Uses the cached Census monthly SAAR series refreshed by
    refresh_ai_capital_evidence; never extrapolates quarterly GDP.
    """
    from io import BytesIO
    from hashlib import sha256

    retrieved_on = pd.Timestamp(as_of or pd.Timestamp.today()).normalize()
    construction = pd.read_csv(_AI_CONSTRUCTION_DATA, parse_dates=['date'])
    construction = construction[construction.date <= retrieved_on]
    assert construction.date.is_unique
    assert (construction.millions_usd_saar > 0).all()
    assert len(pd.date_range(construction.date.min(), construction.date.max(), freq='MS')) == len(construction)
    construction['quarter'] = construction.date.dt.to_period('Q')
    quarterly = construction.groupby('quarter').agg(
        construction_millions_usd_saar=('millions_usd_saar', 'mean'),
        months=('millions_usd_saar', 'count'))
    quarterly = quarterly.loc[quarterly.months.eq(3)].drop(columns='months')

    url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDP&cosd=2014-01-01'
    response = requests.get(url, timeout=50)
    response.raise_for_status()
    gdp = pd.read_csv(BytesIO(response.content)).rename(
        columns={'observation_date': 'date', 'GDP': 'gdp_billions_usd_saar'})
    gdp['date'] = pd.to_datetime(gdp.date)
    gdp['gdp_billions_usd_saar'] = pd.to_numeric(gdp.gdp_billions_usd_saar, errors='coerce')
    gdp = gdp.loc[gdp.date <= retrieved_on].dropna().sort_values('date')
    assert gdp.date.is_unique and (gdp.gdp_billions_usd_saar > 0).all()
    gdp.to_csv(_AI_NOMINAL_GDP_DATA, index=False)
    gdp['quarter'] = gdp.date.dt.to_period('Q')
    data = quarterly.join(gdp.set_index('quarter')[['gdp_billions_usd_saar']], how='inner')
    assert len(data) > 40 and data.index.is_unique
    assert len(pd.period_range(data.index.min(), data.index.max(), freq='Q')) == len(data)
    data['percent_gdp'] = 100 * data.construction_millions_usd_saar / (1000 * data.gdp_billions_usd_saar)
    data['date'] = data.index.to_timestamp(how='end').normalize()
    assert (data.date <= retrieved_on).all()
    assert data.percent_gdp.between(0, 1).all()
    data.to_csv(_AI_CONSTRUCTION_GDP_DATA, index_label='quarter')
    metadata = json.loads(_AI_EVIDENCE_META.read_text(encoding='utf-8'))
    metadata['construction'].pop('units_plot', None)
    metadata['construction']['transformation'] = 'No transformation in cached CSV; see construction_share_gdp for the plotted ratio.'
    metadata['construction_share_gdp'] = {
        'retrieved_on': retrieved_on.date().isoformat(),
        'source': 'US Census Bureau private data-center construction; BEA nominal GDP via FRED (GDP).',
        'construction_input': _AI_CONSTRUCTION_DATA.name,
        'construction_download_sha256': metadata['construction']['download_sha256'],
        'construction_vintage': metadata['retrieved_on'],
        'gdp_url': url,
        'gdp_download_sha256': sha256(response.content).hexdigest(),
        'gdp_units': 'Billions of current US dollars, seasonally adjusted annual rate, quarterly.',
        'units_plot': 'Percent of nominal US GDP, quarterly, seasonally adjusted.',
        'transformation': 'Average three monthly construction SAAR values (millions of current dollars) in each complete quarter, divide by contemporaneous nominal GDP SAAR (billions) times 1000, then multiply by 100. Both inputs already annualized; no additional annualization or deflation.',
        'coverage': metadata['construction']['coverage'],
        'last_quarter': str(data.index.max()),
        'last_date': data.date.max().date().isoformat(),
        'last_percent_gdp': float(data.percent_gdp.iloc[-1]),
        'endpoint_policy': 'Only complete quarters with observed GDP and all three construction months; no GDP interpolation, forward filling, forecasts, or partial-quarter averages.',
        'refresh_command': 'python -c "import figures_s3 as f; f.refresh_ai_construction_gdp(); f.ai_datacenter_construction()"',
    }
    _AI_EVIDENCE_META.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Construction / GDP endpoint:', data.index.max(), f'{data.percent_gdp.iloc[-1]:.6f}%')


def refresh_ft_ai_evidence(as_of=None):
    """Refresh OWID's real monthly series used by the FT (18 October 2026)."""
    from io import BytesIO
    from hashlib import sha256

    retrieved_on = pd.Timestamp(as_of or pd.Timestamp.today()).normalize()
    url = ('https://ourworldindata.org/grapher/monthly-spending-data-center-us.csv'
           '?v=1&csvType=full&useColumnShortNames=false')
    response = requests.get(url, headers={'User-Agent': 'Our World In Data data fetch/1.0'}, timeout=50)
    response.raise_for_status()
    data = pd.read_csv(BytesIO(response.content))
    data = data.loc[data.Code.eq('USA'), ['Month', 'Data center construction']]
    data.columns = ['date', 'constant_2021_usd_monthly']
    data['date'] = pd.to_datetime(data.date)
    data = data[data.date <= retrieved_on].sort_values('date')
    assert data.date.is_unique and (data.constant_2021_usd_monthly > 0).all()
    assert len(pd.date_range(data.date.min(), data.date.max(), freq='MS')) == len(data)
    data.to_csv(_AI_REAL_CONSTRUCTION_DATA, index=False)
    metadata = json.loads(_AI_EVIDENCE_META.read_text(encoding='utf-8'))
    metadata['construction_real_monthly'] = {
        'url': url, 'retrieved_on': retrieved_on.date().isoformat(),
        'source': 'US Census Bureau / BLS, processed by Our World in Data; same series as FT chart.',
        'methodology_url': 'https://ourworldindata.org/grapher/monthly-spending-data-center-us',
        'units_input': 'Constant 2021 US dollars per month, not seasonally adjusted.',
        'units_plot': 'Billions of constant 2021 US dollars per month, not seasonally adjusted.',
        'transformation': 'Divide by 1e9 only. OWID deflates Census monthly NSA values with an equal-weight composite of industrial and warehouse construction PPIs, each rebased to 2021 = 100. No annualization or smoothing.',
        'coverage': 'Private construction, excluding IT hardware and land. Includes non-AI data centers. Latest months preliminary.',
        'last_date': data.date.max().date().isoformat(),
        'download_sha256': sha256(response.content).hexdigest(),
    }
    metadata['investment_booms'] = {
        'url': 'https://www.brookings.edu/wp-content/uploads/2026/09/4c_Van-Nieuwerburgh.pdf',
        'source': 'Stijn Van Nieuwerburgh, Financing the AI Buildout, September 2026 conference draft, Table 1 and Appendix C.',
        'article_url': 'https://www.ft.com/content/9ea5a37d-15c9-4d5b-94d6-719048c9cd3c',
        'ft_chart_url': 'https://flo.uri.sh/visualisation/30593759/embed?auto=1',
        'units': 'Average annual capital expenditure as percent of contemporaneous US GDP over each episode.',
        'transformation': 'Manual transcription of exact Table 1 values; display rounded to one decimal as in FT. AI is a conditional scenario, not realized spending or a forecast.',
        'caveats': 'Historical coverage differs across episodes. AI includes IT equipment, buildings and associated power infrastructure; historical railroads exclude at least some rolling stock. See Appendix C.',
    }
    _AI_EVIDENCE_META.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Real monthly construction endpoint:', data.date.max().date())


def _ai_evidence_date_axis(ax, dates, step=2):
    first, last = dates.min(), dates.max()
    ticks = [pd.Timestamp(year=year, month=1, day=1)
             for year in range(first.year, last.year, step)]
    ticks = sorted(set([first] + [date for date in ticks if date >= first]))
    labels = [str(date.year) for date in ticks]
    # Avoid an extra empty year after the actual last observation.
    ticks.append(last)
    labels.append(f'{MONTH_FR[last.month]}\n{last.year}')
    ax.set_xlim(first, last)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=11)


def ai_datacenter_construction():
    data = pd.read_csv(_AI_CONSTRUCTION_GDP_DATA, parse_dates=['date'])
    fig, ax = new_figure(10, 5)
    values = data.percent_gdp
    ax.plot(data.date, values, color=palette[0], linewidth=2.3)
    _ai_evidence_date_axis(ax, data.date)
    labels = [label.get_text() for label in ax.get_xticklabels()]
    labels[-1] = f'T{data.date.iloc[-1].quarter}\n{data.date.iloc[-1].year}'
    ax.set_xticklabels(labels, fontsize=11)
    ymax = np.ceil(values.max() / 0.05) * 0.05
    ticks = np.arange(0, ymax + 0.025, 0.05)
    ax.set_ylim(0, ymax)
    ax.set_yticks(ticks)
    ax.set_yticklabels([f'{value:.2f}'.replace('.', ',') + r'\%' for value in ticks], fontsize=11)
    ax.set_ylabel(r'Construction privée (\% du PIB)',
                  rotation=0, ha='left', fontsize=11)
    ax.yaxis.set_label_coords(0, 1.02)
    style_axes(ax)
    launch = pd.Timestamp('2022-11-30')
    ax.axvline(launch, color=palette[7], linewidth=0.9)
    ax.text(launch - pd.Timedelta(days=100), 0.85, r'Lancement de ChatGPT',
            transform=ax.get_xaxis_transform(), ha='right', va='center',
            fontsize=10, color=palette[0])
    add_source(ax, r'Sources : Census / BEA (via FRED)')
    save(fig, 's3_ai_datacenter_construction.pdf')


def ai_investment_booms():
    """Historical annual averages versus a conditional 2025–32 AI scenario."""
    data = pd.read_csv(_AI_BOOMS_DATA)
    fig, ax = new_figure(10, 4.5)
    positions = np.arange(len(data))
    colors = [palette[2] if flag else palette[0] for flag in data.is_scenario]
    ax.barh(positions, data.average_annual_percent_gdp, color=colors, height=0.62, zorder=3)
    ax.set_yticks(positions)
    labels = [f'{row.label_fr} ({row.start_year}--{row.end_year})'
              + (r' : scénario' if row.is_scenario else '') for row in data.itertuples()]
    ax.set_yticklabels(labels, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlim(0, 4)
    ax.set_xticks(range(5))
    ax.set_xticklabels([str(value) + r'\%' for value in range(5)], fontsize=11)
    ax.set_xlabel(r'Investissement annuel moyen, en \% du PIB américain', fontsize=11)
    style_axes(ax, xgrid=True)
    ax.yaxis.grid(False)
    ax.tick_params(axis='y', length=0)
    for position, value in zip(positions, data.average_annual_percent_gdp):
        ax.text(value + 0.06, position, f'{value:.1f}'.replace('.', ',') + r'\%',
                va='center', fontsize=11, color=palette[0])
    add_source(ax, r'Source : Van Nieuwerburgh (2026), tableau 1, via FT')
    save(fig, 's3_ai_investment_booms.pdf')


def ai_real_yield():
    data = pd.read_csv(_AI_REAL_YIELD_DATA, parse_dates=['date'])
    fig, ax = new_figure(10, 5)
    ax.plot(data.date, data.percent, color=palette[0], linewidth=1.5)
    _ai_evidence_date_axis(ax, data.date)
    ymin, ymax = np.floor(data.percent.min()), np.ceil(data.percent.max())
    ticks = np.arange(ymin, ymax + 0.5, 1)
    ax.set_ylim(ymin, ymax)
    ax.set_yticks(ticks)
    ax.set_yticklabels([f'{value:.0f}' + r'\%' for value in ticks], fontsize=11)
    ax.axhline(0, color=palette[7], linewidth=0.7)
    ax.set_ylabel(r'Rendement réel à 10 ans (\%)', rotation=0, ha='left', fontsize=11)
    ax.yaxis.set_label_coords(0, 1.02)
    style_axes(ax)
    launch = pd.Timestamp('2022-11-30')
    ax.axvline(launch, color=palette[7], linewidth=0.9)
    ax.text(launch - pd.Timedelta(days=100), 0.85, r'Lancement de ChatGPT',
            transform=ax.get_xaxis_transform(), ha='right', va='center',
            fontsize=10, color=palette[0])
    add_source(ax, r'Source : Federal Reserve / FRED (DFII10)')
    save(fig, 's3_ai_real_yield.pdf')


# =====================================================================
# AI distribution: computer capital income and comparable labour shares
# =====================================================================
_AI_LABOUR_SHARES = _AI_EVIDENCE_DIR / 's3_ai_labour_shares.csv'
_AI_COMPUTER_SHARE = _AI_EVIDENCE_DIR / 's3_ai_computer_income_share.csv'
_AI_DISTRIBUTION_META = _AI_EVIDENCE_DIR / 's3_ai_distribution_evidence.json'


def refresh_ai_computer_income_share(as_of=None, pdf_path=None):
    """Cache Figure 2 from Jones–Tonetti, just like the other source refreshes.

    Requires pypdf only for refreshing; normal plotting reads the cached CSV.
    Supply pdf_path to reuse a local copy of the paper without a download.
    """
    from io import BytesIO
    from hashlib import sha256
    from pypdf import PdfReader
    from pypdf.generic import ContentStream

    retrieved_on = pd.Timestamp(as_of or pd.Timestamp.today()).date().isoformat()
    if pdf_path is not None:
        pdf_bytes = Path(pdf_path).read_bytes()
    else:
        response = requests.get('https://web.stanford.edu/~chadj/JonesTonetti_Automation.pdf', timeout=50)
        response.raise_for_status()
        pdf_bytes = response.content
    reader = PdfReader(BytesIO(pdf_bytes))
    page = reader.pages[14]
    assert 'Figure 2: The Share of Factor Income Paid to Computers' in page.extract_text()
    form = page['/Resources']['/XObject']['/Im1'].get_object()
    traces, short_ticks, points, color = [], [], [], None
    for arguments, operation in ContentStream(form, reader).operations:
        if operation in [b'RG', b'rg']:
            color = tuple(float(value) for value in arguments)
        elif operation in [b'm', b'l']:
            points.append(tuple(float(value) for value in arguments))
        elif operation in [b'S', b's', b'f', b'f*', b'B', b'n']:
            if len(points) == 37 and color == (0.0, 0.4471, 0.7412):
                traces.append(points[:])
            if len(points) == 2:
                (x0, y0), (x1, y1) = points
                if abs(y0 - y1) < 1e-6 and 6 < abs(x1 - x0) < 7:
                    short_ticks.append(y0)
            points = []
    assert len(traces) == 1 and len(short_ticks) == 4
    # Original axis: x = 112 at 1985; x = 782 at 2025.
    # Short horizontal ticks, top to bottom: 4.5, 4, 3.5, 3 percent.
    ticks = sorted(short_ticks)
    top_y, bottom_y = ticks[0], ticks[-1]
    scale = (bottom_y - top_y) / 1.5
    assert max(abs((b - a) / scale - 0.5) for a, b in zip(ticks, ticks[1:])) < 1e-6
    rows = []
    for x, y in traces[0]:
        year = 1985 + (x - 112) / (782 - 112) * 40
        assert abs(year - round(year)) < 1e-6
        rows.append((round(year), round(3 + (bottom_y - y) / scale, 6)))
    assert [year for year, _ in rows] == list(range(1987, 2024))
    assert max(rows, key=lambda row: row[1])[0] == 2000
    assert abs(rows[-1][1] - 3.0) < 0.05
    pd.DataFrame(rows, columns=['year', 'approximate_percent']).to_csv(_AI_COMPUTER_SHARE, index=False)
    metadata = json.loads(_AI_DISTRIBUTION_META.read_text(encoding='utf-8'))
    metadata['computer_income_share'].update({
        'retrieved_on': retrieved_on,
        'transformation': 'Recover all 37 annual vertices from the native vector curve in Figure 2. Calibrate against its year and percent tick marks; round to six decimals. No smoothing, interpolation of missing years, or extrapolation. Values reproduce the published curve, rather than newly downloaded BLS microdata.',
        'range': [1987, 2023], 'observations': len(rows),
        'download_sha256': sha256(pdf_bytes).hexdigest(),
        'vector_calibration': {'x_1985': 112, 'x_2025': 782,
                               'y_3_percent': bottom_y, 'y_4_5_percent': top_y},
        'precision': 'Approximate values recovered from plotted vector coordinates; extra decimals preserve curve geometry and are not statistical precision.',
        'transistor_comparison': 'Paper, printed page 14: 100 million times more transistors on a computer chip than in the 1970s; an order-of-magnitude illustration, not a separate measured series in this figure.',
        'refresh_command': 'python -c "import figures_s3 as f; f.refresh_ai_computer_income_share(); f.ai_computer_income_share()"',
    })
    _AI_DISTRIBUTION_META.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Recovered {len(rows)} computer-share observations, {rows[0][0]}–{rows[-1][0]}.')


def refresh_ai_distribution_evidence(as_of=None):
    """Refresh both distribution sources; normal figure generation stays offline."""
    from io import BytesIO
    from hashlib import sha256

    refresh_ai_computer_income_share(as_of=as_of)

    retrieved_on = pd.Timestamp(as_of or pd.Timestamp.today()).normalize()
    url = ('https://fred.stlouisfed.org/graph/fredgraph.csv'
           '?id=LABSHPCAA156NRUG,LABSHPUSA156NRUG')
    response = requests.get(url, timeout=50)
    response.raise_for_status()
    data = pd.read_csv(BytesIO(response.content), parse_dates=['observation_date'])
    data = data.rename(columns={'observation_date': 'date',
                               'LABSHPCAA156NRUG': 'Canada',
                               'LABSHPUSA156NRUG': 'United States'})
    data = data.loc[(data.date.dt.year >= 1960) & (data.date <= retrieved_on)].sort_values('date')
    assert data.date.is_unique and len(data) > 50
    for country in ['Canada', 'United States']:
        data[country] = pd.to_numeric(data[country], errors='coerce')
        assert data[country].dropna().between(0, 1).all()
    data.to_csv(_AI_LABOUR_SHARES, index=False)

    computer_metadata = json.loads(_AI_DISTRIBUTION_META.read_text(encoding='utf-8'))['computer_income_share']
    metadata = {
        'retrieved_on': retrieved_on.date().isoformat(),
        'labour_shares': {
            'url': url, 'source': 'Penn World Table 11.0, labsh, via FRED',
            'series': {'Canada': 'LABSHPCAA156NRUG', 'United States': 'LABSHPUSA156NRUG'},
            'units_input': 'Annual ratio, at current national prices, not seasonally adjusted.',
            'units_plot': 'Percent of GDP. Compensation includes the estimated labour income of self-employed workers.',
            'transformation': 'Multiply by 100; no smoothing or interpolation; retain missing observations as gaps.',
            'last_date': {country: data.loc[data[country].notna(), 'date'].max().date().isoformat()
                          for country in ['Canada', 'United States']},
            'interpretation': 'Descriptive historical series, not a causal estimate of automation or generative AI.',
            'download_sha256': sha256(response.content).hexdigest(),
        },
        'computer_income_share': computer_metadata,
        'theory': {
            'more_versus_better': 'https://doi.org/10.1257/aer.20221180',
            'scarcity_and_weak_links': 'https://web.stanford.edu/~chadj/JonesTonetti_Automation.pdf',
            'conditions': 'Strong complementarity across tasks (elasticity below one), fixed task allocation for the better-machine comparative static. Not every worker benefits; labour-share changes and wage changes are distinct.',
        },
        'refresh_command': 'python -c "import figures_s3 as f; f.refresh_ai_distribution_evidence(); f.ai_computer_income_share(); f.ai_labour_shares()"',
    }
    _AI_DISTRIBUTION_META.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Labour share endpoints:', metadata['labour_shares']['last_date'])


def ai_computer_income_share():
    data = pd.read_csv(_AI_COMPUTER_SHARE)
    fig, ax = new_figure(7.2, 4.2)
    assert data.year.tolist() == list(range(1987, 2024))
    ax.plot(data.year, data.approximate_percent, color=palette[0], linewidth=2.5)
    ticks = [1987, 1995, 2005, 2015, 2023]
    ax.set_xticks(ticks)
    ax.set_xticklabels(ticks, fontsize=11)
    ax.set_xlim(data.year.min(), data.year.max())
    ax.set_ylim(2.8, 4.5)
    ticks = [3, 3.5, 4, 4.5]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f'{value:g}'.replace('.', ',') + r'\%' for value in ticks], fontsize=11)
    ax.set_ylabel(r'Part du revenu versée au capital informatique',
                  rotation=0, ha='left', fontsize=11)
    ax.yaxis.set_label_coords(0, 1.10)
    style_axes(ax)
    add_source(ax, r'Source : BLS, via C. Jones et Tonetti (2026)')
    save(fig, 's3_ai_computer_income_share.pdf')


def ai_labour_shares():
    data = pd.read_csv(_AI_LABOUR_SHARES, parse_dates=['date'])
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.1), sharey=True)
    fig.patch.set_alpha(0)
    for ax, country, label, color in zip(
            axes, ['Canada', 'United States'], ['Canada', 'États-Unis'], [palette[0], palette[2]]):
        ax.patch.set_alpha(0)
        valid = data.loc[data[country].notna()]
        last = valid.date.max().year
        ax.plot(data.date.dt.year, data[country] * 100, color=color, linewidth=2.2)
        ax.set_xlim(valid.date.min().year, last)
        # Keep the last actual year without crowding it with a nearby decade tick.
        ticks = [year for year in range(1960, last, 20) if last - year >= 8] + [last]
        ax.set_xticks(ticks)
        ax.set_xticklabels(ticks, fontsize=11)
        ax.set_ylim(55, 80)
        ax.set_yticks(range(55, 81, 5))
        ax.set_yticklabels([str(value) + r'\%' for value in range(55, 81, 5)], fontsize=11)
        ax.text(0.04, 0.91, label, transform=ax.transAxes, fontsize=12, color=color)
        endpoint = f'{last} : ' + f'{valid[country].iloc[-1] * 100:.1f}'.replace('.', ',') + r'\%'
        ax.text(0.97, 0.91, endpoint, transform=ax.transAxes, ha='right',
                color=color, fontsize=10)
        style_axes(ax)
    axes[0].set_ylabel(r'Part du travail dans le PIB', rotation=0, ha='left', fontsize=11)
    axes[0].yaxis.set_label_coords(0, 1.02)
    add_source(axes[1], r'Source : Penn World Table 11.0 / FRED')
    save(fig, 's3_ai_labour_shares.pdf')


# =====================================================================
# US twin deficits: paired annual bars (the two balances are not additive)
# =====================================================================
_TWIN_DATA = Path(__file__).resolve().parents[1] / 'Data' / 's3_us_twin_deficits.csv'
_TWIN_META = _TWIN_DATA.with_suffix('.json')


def refresh_twin_deficits(as_of=None):
    """Cache the two original source series on their common observed years."""
    from concurrent.futures import ThreadPoolExecutor
    from io import BytesIO
    from hashlib import sha256

    retrieved_on = pd.Timestamp(as_of or pd.Timestamp.today()).normalize()
    urls = {
        'current_account': ('https://api.worldbank.org/v2/country/USA/indicator/'
                            'BN.CAB.XOKA.GD.ZS?format=json&date=1970:'
                            f'{retrieved_on.year - 1}&per_page=1000'),
        'federal_budget': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=FYFSGDA188S&cosd=1970-01-01',
    }

    def fetch(item):
        name, url = item
        response = requests.get(url, timeout=50)
        response.raise_for_status()
        return name, response.content

    with ThreadPoolExecutor(max_workers=2) as pool:
        payloads = dict(pool.map(fetch, urls.items()))
    ca_rows = json.loads(payloads['current_account'])[1]
    ca = pd.Series({int(row['date']): row['value'] for row in ca_rows
                    if row['value'] is not None}, name='current_account_percent_gdp')
    budget = pd.read_csv(BytesIO(payloads['federal_budget']), parse_dates=['observation_date'])
    budget = budget[budget.observation_date <= retrieved_on]
    budget = pd.Series(pd.to_numeric(budget.FYFSGDA188S, errors='coerce').to_numpy(),
                       index=budget.observation_date.dt.year,
                       name='federal_budget_percent_gdp')
    data = pd.concat([ca, budget], axis=1).dropna().sort_index()
    data = data.loc[data.index >= 1970]
    data.index.name = 'year'
    assert data.index.is_unique and len(data) > 40
    assert list(data.index) == list(range(data.index.min(), data.index.max() + 1))
    data.to_csv(_TWIN_DATA)
    metadata = {
        'retrieved_on': retrieved_on.date().isoformat(), 'urls': urls,
        'source_ids': {'current_account': 'World Bank BN.CAB.XOKA.GD.ZS',
                       'federal_budget': 'FRED FYFSGDA188S (OMB / St. Louis Fed)'},
        'units': 'Percent of US GDP; surpluses positive, deficits negative.',
        'coverage': 'US current account (calendar year) and federal budget balance (fiscal-year balance divided by annual GDP). Not the budget of all levels of government.',
        'transformation': 'No sign changes, summing, smoothing, or interpolation. Align only common nonmissing observed years.',
        'range': [int(data.index.min()), int(data.index.max())],
        'display': 'Paired bars rather than stacked bars because the balances are not additive.',
        'download_sha256': {name: sha256(payload).hexdigest() for name, payload in payloads.items()},
        'refresh_command': 'python -c "import figures_s3 as f; f.refresh_twin_deficits(); f.us_twin_deficits()"',
    }
    _TWIN_META.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Twin deficits:', metadata['range'])


def us_twin_deficits():
    data = pd.read_csv(_TWIN_DATA, index_col='year')
    fig, ax = new_figure(10, 5)
    ax.bar(data.index - 0.2, data.current_account_percent_gdp, width=0.38,
           color=palette[0], label='Compte courant', edgecolor='none', zorder=3)
    ax.bar(data.index + 0.2, data.federal_budget_percent_gdp, width=0.38,
           color=palette[2], label='Solde budgétaire fédéral', edgecolor='none', zorder=3)
    ax.axhline(0, color='black', linewidth=0.7, zorder=4)
    first, last = data.index.min(), data.index.max()
    ax.set_xlim(first - 0.5, last + 0.5)
    ticks = [year for year in range(first, last, 10) if last - year >= 7] + [last]
    ax.set_xticks(ticks)
    ax.set_xticklabels(ticks, fontsize=11)
    ymin = min(-12, -tick_ceil(-data.min().min(), 2))
    ymax = max(4, tick_ceil(data.max().max(), 2))
    ax.set_ylim(ymin, ymax)
    ticks = np.arange(ymin, ymax + 1, 2)
    ax.set_yticks(ticks)
    ax.set_yticklabels([f'{value:.0f}' + r'\%' for value in ticks], fontsize=11)
    ax.set_ylabel(r'(\% du PIB)', rotation=0, ha='left', fontsize=11)
    ax.yaxis.set_label_coords(0, 1.02)
    style_axes(ax)
    ax.set_axisbelow(True)
    ax.legend(loc='upper left', ncol=2, frameon=False, fontsize=10,
              handlelength=1.1, handletextpad=0.4, columnspacing=1.4)
    add_source(ax, r'Sources : Banque mondiale / FRED')
    save(fig, 's3_us_twin_deficits.pdf')


# =====================================================================
# Jones--Tonetti growth and labour shares: native curves from Figure 5a--b
# =====================================================================
_AI_GROWTH_SCENARIOS = _AI_EVIDENCE_DIR / 's3_ai_growth_scenarios.csv'
_AI_GROWTH_META = _AI_EVIDENCE_DIR / 's3_ai_growth_evidence.json'


def refresh_ai_growth_scenarios(as_of=None, pdf_path=None):
    """Recover published simulation vertices; plotting itself stays offline."""
    from io import BytesIO
    from hashlib import sha256
    from pypdf import PdfReader
    from pypdf.generic import ContentStream

    url = 'https://web.stanford.edu/~chadj/JonesTonetti_Automation.pdf'
    if pdf_path is None:
        response = requests.get(url, timeout=50)
        response.raise_for_status()
        payload = response.content
    else:
        payload = Path(pdf_path).read_bytes()
    reader = PdfReader(BytesIO(payload))
    page = reader.pages[40]
    assert 'Figure 5: The Future if AI = Private Business' in page.extract_text()
    scenarios = {(0.4902, 0.149, 0.8039): 'full',
                 (0.0, 0.4471, 0.7412): 'asymptotic',
                 (0.4667, 0.6392, 0.1882): 'partial'}
    panels = []
    for form_name, column, upper, complement in [
            ('/Im4', 'annual_growth_percent', 20, False),
            ('/Im3', 'labor_share_percent', 100, True)]:
        form = page['/Resources']['/XObject'][form_name].get_object()
        rows, points, color, counts = [], [], None, {}
        for args, operation in ContentStream(form, reader).operations:
            if operation in [b'RG', b'rg']:
                color = tuple(float(value) for value in args)
            elif operation in [b'm', b'l']:
                points.append(tuple(float(value) for value in args))
            elif operation in [b'S', b's', b'f', b'f*', b'B', b'n']:
                if len(points) > 50 and color in scenarios:
                    name = scenarios[color]
                    assert name not in counts
                    counts[name] = len(points)
                    for x, y in points:
                        year = 2020 + (x - 112) / 670 * 140
                        assert abs(year - round(year)) < 1e-4
                        percent = (427 - y) / (427 - 36) * upper
                        if complement:
                            percent = 100 - percent
                        rows.append((name, round(year), round(percent, 6)))
                points = []
        assert counts == {'partial': 130, 'full': 120, 'asymptotic': 130}
        panels.append(pd.DataFrame(rows, columns=['scenario', 'year', column]))
    data = panels[0].merge(panels[1], on=['scenario', 'year'],
                          how='outer', validate='one_to_one')
    assert data.notna().all().all()
    for name, group in data.groupby('scenario'):
        assert group.year.tolist() == list(range(2020, int(group.year.max()) + 1))
        assert group.annual_growth_percent.between(0, 20).all()
        assert group.labor_share_percent.between(0, 100).all()
        assert abs(group.loc[group.year == 2020, 'labor_share_percent'].iloc[0] - 61.8) < 0.1
    early = data.loc[data.year == 2070, 'annual_growth_percent']
    assert early.max() - early.min() < 0.1
    data.to_csv(_AI_GROWTH_SCENARIOS, index=False)
    metadata = json.loads(_AI_GROWTH_META.read_text(encoding='utf-8'))
    metadata['jones_tonetti']['three_scenarios'] = {
        'source': 'Figure 5a (capital share) and 5b (growth), printed p. 40 / zero-indexed PDF page 40; discussion pp. 39--43.',
        'calibration': 'AI as a continuation of historical private-business patterns; not the faster Moore\'s Law Everywhere calibration of Figure 6.',
        'units': 'Annual growth of output per person, percent; labour income as percent of total factor income. Both are model simulations, not observations or forecasts.',
        'definitions': {'full': 'All tasks automated in finite time.',
                        'asymptotic': 'Automated task share tends to 100 percent without reaching it in finite time; the paper labels this Baseline.',
                        'partial': 'A positive set of essential tasks is never automated.'},
        'long_run': {'full': 'Explosive growth.',
                     'asymptotic': 'Positive finite balanced-growth rate in this historical calibration; not a universal result for asymptotic automation.',
                     'partial': 'Growth ultimately limited by human-task productivity, 0.5 percent per year in the calibration.'},
        'transformation': 'Recover annual vertices of all three scenarios in both panels. x=112/782 maps to 2020/2160. y=427/36 maps to 0/20 percent in growth and 0/100 percent in capital share. Compute labour share as 100 minus the capital-share percentage, consistent with s_L = 1 - s_K in this model. Join scenario/year one-to-one. No simulation re-estimation, smoothing, interpolation, or extrapolation. Omit the separate constant-growth reference line.',
        'labor_share_interpretation': 'A share of factor income, not the share of employed workers, a wage level, or a prediction that individual earnings change in the same direction. Full automation tends to zero labour share; partial automation tends to 100 percent; the asymptotic baseline tends to roughly 64 percent in this calibration.',
        'observations': counts,
        'last_plotted_year': {'full': 2139, 'asymptotic': 2149, 'partial': 2149},
        'precision': 'Approximate values recovered from the published figure; six decimals preserve its geometry, not economic precision.',
        'short_run': 'Figure 5 and its discussion describe nearly indistinguishable paths for approximately the next 50 years. The shaded 2020--2070 interval highlights this comparison, not a predicted structural break.',
        'mechanism': 'Strong complementarity means remaining essential human tasks constrain aggregate production. Automation of goods and ideas accelerates growth, but weak links delay the acceleration.',
        'download_sha256': sha256(payload).hexdigest(),
        'verified_on': pd.Timestamp(as_of or pd.Timestamp.today()).date().isoformat(),
        'refresh_command': 'python -c "import figures_s3 as f; f.refresh_ai_growth_scenarios(); f.ai_growth_scenarios()"',
    }
    metadata['classroom_presentation']['sequence'] = [
        'Solow puzzle', 'Left/right shoe complementarity and bottleneck example',
        'Baumol: full-slide Canadian price chart',
        'Three Jones--Tonetti automation scenarios: similar short run, divergent long run']
    metadata['classroom_presentation']['content_slides'] = [66, 67, 68, 69]
    metadata['classroom_presentation']['jones_tonetti_scope'] = 'Figure 5a--b historical calibration: paired growth and labour-share panels with common years and scenario colours. Labour share is one minus the published capital share. The asymptotic case is the published Baseline.'
    metadata['classroom_presentation']['anthropic_scope'] = 'Removed from slide 69; verified values retained only as source history.'
    _AI_GROWTH_META.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Recovered Jones--Tonetti growth scenarios:', counts)


def ai_growth_scenarios():
    data = pd.read_csv(_AI_GROWTH_SCENARIOS)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.0), sharex=True)
    fig.patch.set_alpha(0)
    specs = [('full', palette[2], r'Complète (100\% en temps fini)'),
             ('asymptotic', palette[0], r'Asymptotique (vers 100\%)'),
             ('partial', palette[1], r'Partielle (des tâches humaines)')]
    for ax, column, upper, step, title, source in [
            (axes[0], 'annual_growth_percent', 20, 5,
             r'Croissance annuelle du PIB par habitant',
             r'Source : C. Jones et Tonetti (2026), fig. 5b'),
            (axes[1], 'labor_share_percent', 100, 25,
             r'Part du revenu du travail',
             r'Source : fig. 5a, $s_L = 1 - s_K$')]:
        ax.patch.set_alpha(0)
        ax.axvspan(2020, 2070, color=palette[0], alpha=0.035, linewidth=0)
        for name, color, label in specs:
            series = data.loc[data.scenario == name].sort_values('year')
            ax.plot(series.year, series[column], color=color,
                    linewidth=2.5, label=label)
        ax.set_xlim(data.year.min(), data.year.max())
        ticks = [2020, 2070, 2100, int(data.year.max())]
        ax.set_xticks(ticks)
        ax.set_xticklabels(ticks, fontsize=11)
        ax.set_ylim(0, upper)
        ticks = np.arange(0, upper + 1, step)
        ax.set_yticks(ticks)
        ax.set_yticklabels([str(value) + r'\%' for value in ticks], fontsize=11)
        ax.set_ylabel(title, rotation=0, ha='left', fontsize=12)
        ax.yaxis.set_label_coords(0, 1.12)
        style_axes(ax)
        add_source(ax, source)
    axes[0].legend(loc='upper left', frameon=False, fontsize=9.5,
                   handlelength=1.6, labelspacing=0.65)
    axes[0].text(2045, 7.5, r'Débuts très proches' + '\n' + r'pendant environ 50 ans',
                 ha='center', va='center', fontsize=10.5, color=palette[0])
    save(fig, 's3_ai_growth_scenarios.pdf')


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 3 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        labor_market_indicators_us,
        labor_market_indicators_ca,
        participation_gender,
        aging_population,
        participation_decline_us,
        labor_share_decline,
        inequality_skill_premium,
        ai_cfo_employment,
        rd_gdp_share,
        canada_gdp_decomposition,
        canada_gdp_decomposition_countries,
        breakthrough_inventions,
        rd_spending_global,
        moores_law,
        zimbabwe_botswana,
        education_plateau,
        development_accounting_human_capital,
        tropics_map,
        education_prosperity,
        digital_adoption_index,
        canada_gdp_decomposition_5y,
        participation_gender_ca,
        unemployment_ca,
        participation_rate_ca,
        immigration_ca,
        inequality_top1_share,
        elephant_curve,
        job_polarization,
        gatsby_curve,
        baumol_cost_disease_canada,
        current_accounts_divergence,
        saving_rates_divergence,
        us_twin_deficits,
        ai_datacenter_construction,
        ai_investment_booms,
        ai_real_yield,
        ai_computer_income_share,
        ai_labour_shares,
        ai_growth_scenarios,
    ]

    failed = []
    for fn in figures:
        try:
            fn()
        except Exception as e:
            print(f'  \u2717 {fn.__name__}: {e}')
            failed.append(fn.__name__)

    if failed:
        print(f'\n{len(failed)} figure(s) failed: {", ".join(failed)}')
        sys.exit(1)
    else:
        print('\nDone \u2014 all figures generated.')
