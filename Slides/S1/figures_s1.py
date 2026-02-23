"""
ECON50803 — Session 1 : Figure Generation
============================================

Generates all matplotlib figures for Session 1 slides.
All figure labels, axis titles, legends, and annotations are in French.

Run from Slides/S1/:
    python3 figures_s1.py
"""

import os
import re
from pathlib import Path
from datetime import datetime

import dotenv
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
from statsmodels.tsa.filters.hp_filter import hpfilter
from stats_can import StatsCan

# ── Environment ──────────────────────────────────────────────────────────
dotenv.load_dotenv(os.path.join(Path(__file__).resolve().parent.parent.parent, '.env'))
fred_api_key = os.getenv('fred_api_key')

# ── Font (Fira Sans via LaTeX, matching Beamer slides) ───────────────────
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Fira Sans']})
rc('text', usetex=True)
rc('text.latex', preamble=r'\usepackage[sfdefault,light]{FiraSans}'
                           r'\usepackage[T1]{fontenc}')

# ── Colour palette (HEC Montréal) ───────────────────────────────────────
palette = ['#002855',   # HECnavy
           '#26d07c',   # HECgreen
           '#ff585d',   # HECcoral
           '#f3d03e',   # yellow
           '#0072ce',   # blue
           '#eb6fbd',   # pink
           '#00aec7',   # teal
           '#888b8d']   # gray

# ── Output path ─────────────────────────────────────────────────────────
FIGURES_DIR = os.path.join(Path(__file__).resolve().parent.parent, 'Figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

# ── French month abbreviations (for LaTeX/usetex date labels) ───────────
MONTH_FR = {1: 'janv.', 2: r'f\'{e}vr.', 3: 'mars', 4: 'avr.',
            5: 'mai', 6: 'juin', 7: 'juil.', 8: r'ao\^{u}t',
            9: 'sept.', 10: 'oct.', 11: 'nov.', 12: r'd\'{e}c.'}


def french_date_label(d):
    """Format a datetime as 'month_abbr\\nYYYY' in French."""
    return MONTH_FR[d.month] + '\n' + str(d.year)


# ── US recession dates (NBER) ───────────────────────────────────────────
recessions_us = [
    (datetime(2020, 2, 1), datetime(2020, 4, 1)),
    (datetime(2007, 12, 1), datetime(2009, 6, 1)),
    (datetime(2001, 3, 1), datetime(2001, 11, 1)),
    (datetime(1990, 7, 1), datetime(1991, 3, 1)),
    (datetime(1981, 7, 1), datetime(1982, 11, 1)),
    (datetime(1980, 1, 1), datetime(1980, 7, 1)),
    (datetime(1973, 11, 1), datetime(1975, 3, 1)),
    (datetime(1969, 12, 1), datetime(1970, 11, 1)),
    (datetime(1960, 4, 1), datetime(1961, 2, 1)),
    (datetime(1957, 8, 1), datetime(1958, 4, 1)),
    (datetime(1953, 7, 1), datetime(1954, 5, 1)),
    (datetime(1948, 11, 1), datetime(1949, 10, 1)),
]

# ── Canadian recession dates (C.D. Howe Business Cycle Council) ───────
recessions_ca = [
    (datetime(2020, 2, 1), datetime(2020, 4, 1)),
    (datetime(2008, 10, 1), datetime(2009, 5, 1)),
    (datetime(1990, 3, 1), datetime(1992, 4, 1)),
    (datetime(1981, 6, 1), datetime(1982, 10, 1)),
    (datetime(1980, 1, 1), datetime(1980, 6, 1)),
    (datetime(1974, 11, 1), datetime(1975, 3, 1)),
    (datetime(1960, 4, 1), datetime(1961, 3, 1)),
]

# ── FRED helper ─────────────────────────────────────────────────────────
def get_fred_data(series_id, frequency=None, aggregation_method=None):
    """Retrieve a FRED series as a pandas Series."""
    url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'series_id': series_id,
        'api_key': fred_api_key,
        'file_type': 'json',
    }
    if frequency is not None:
        params['frequency'] = frequency
    if aggregation_method is not None:
        params['aggregation_method'] = aggregation_method

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()['observations']

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df.set_index('date')['value']


# ── Bank of Canada Valet helper ─────────────────────────────────────────
THOUSANDS_RX = re.compile(r"[,\u202f\u2009\s]")

def get_valet_series(series_id, start='2000-01-01'):
    """Download a Bank of Canada Valet time-series as a pandas Series."""
    url = (f"https://www.bankofcanada.ca/valet/observations/{series_id}/json"
           f"?start_date={start}")
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    obs = resp.json().get("observations", [])
    records = []
    for row in obs:
        raw = row.get(series_id, {})
        val = raw.get("v")
        if val is None:
            continue
        val = float(THOUSANDS_RX.sub("", str(val)))
        records.append((row["d"], val))
    df = (pd.DataFrame(records, columns=["date", "value"])
            .assign(date=lambda x: pd.to_datetime(x.date))
            .set_index("date").sort_index())
    return df["value"]


# ── OWID Maddison helper ──────────────────────────────────────────────
def _get_owid_maddison():
    """Fetch Maddison GDP per capita from the OWID API (2023 edition, data to 2022)."""
    import json, urllib.request
    url_data = 'https://api.ourworldindata.org/v1/indicators/900793.data.json'
    url_meta = 'https://api.ourworldindata.org/v1/indicators/900793.metadata.json'
    headers = {'User-Agent': 'Mozilla/5.0'}
    data = json.loads(urllib.request.urlopen(
        urllib.request.Request(url_data, headers=headers)).read())
    meta = json.loads(urllib.request.urlopen(
        urllib.request.Request(url_meta, headers=headers)).read())
    entity_map = {e['id']: e['name']
                  for e in meta['dimensions']['entities']['values']}
    df = pd.DataFrame({
        'Entity': [entity_map[eid] for eid in data['entities']],
        'Year': data['years'],
        'GDP per capita': data['values'],
    })
    return df


# ── Shared plot helpers ─────────────────────────────────────────────────
def new_figure():
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    return fig, ax

def style_axes(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, which='major', axis='y', color='gray', linestyle=':', linewidth=0.5)

def add_source(ax, text='Source: Federal Reserve Economic Data'):
    ax.text(1, 1.01, text, fontsize=8, color='k',
            ha='right', va='bottom', transform=ax.transAxes)

def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, name), transparent=True, dpi=300)
    plt.close(fig)
    print(f'  \u2713 {name}')

def tick_ceil(value, step):
    """Round up value to the next multiple of step."""
    return int(np.ceil(value / step)) * step


# ── Country name translation mapping (English data → French labels) ─────
COUNTRY_FR = {
    'United States': r"\'{E}tats-Unis",
    'United Kingdom': 'Royaume-Uni',
    'China': 'Chine',
    'Brazil': r"Br\'{e}sil",
    'Canada': 'Canada',
    'France': 'France',
    'India': 'Inde',
    'Nigeria': r"Nig\'{e}ria",
    'Norway': r"Norv\`{e}ge",
    'Luxembourg': 'Luxembourg',
    'Switzerland': 'Suisse',
    'Japan': 'Japon',
    'Germany': 'Allemagne',
    'Russia': 'Russie',
    'Indonesia': r"Indon\'{e}sie",
    'Mexico': 'Mexique',
    'South Korea': r"Cor\'{e}e du Sud",
    'Euro area': 'Zone euro',
    'Sweden': r"Su\`{e}de",
    'Turkey': 'Turquie',
    'Singapore': 'Singapour',
    'Vietnam': r"Vi\^{e}t Nam",
    'Taiwan': 'Taïwan',
}


def _tr_country(name):
    """Translate a country name to French, falling back to original."""
    return COUNTRY_FR.get(name, name)


# =====================================================================
# Figure 1: Canadian unemployment rate
# =====================================================================
def can_unemployment():
    print('Figure 1: Canadian unemployment rate')
    u = get_fred_data('LRUNTTTTCAM156S')

    u_clean = u.dropna()

    fig, ax = new_figure()

    ax.plot(u, color=palette[0], linewidth=2)

    # Annotation for COVID spike
    covid_peak_date = u.loc['2020-01-01':'2020-12-31'].idxmax()
    covid_peak_val = u.loc[covid_peak_date]
    ax.annotate(f'{covid_peak_val:.1f}\\%',
                xy=(covid_peak_date, covid_peak_val),
                xytext=(covid_peak_date + pd.DateOffset(years=3), covid_peak_val - 0.5),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    last_date = u_clean.index[-1]
    first_year = u_clean.index[0].year
    ax.set_xlim(pd.to_datetime(str(first_year)), last_date + pd.DateOffset(months=3))
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(first_year, last_date.year + 1, 10)])
    ax.set_xticklabels(range(first_year, last_date.year + 1, 10), fontsize=12)
    ax.set_ylim(2, 16)
    ax.set_yticks(range(2, 16 + 1, 2))
    ax.set_yticklabels([str(x) + r'\%' for x in range(2, 16 + 1, 2)], fontsize=12)
    ax.set_ylabel(r"Taux de ch\^{o}mage", fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    for start, end in recessions_ca:
        if start >= pd.to_datetime(str(first_year)):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    add_source(ax, 'Source: OECD (via FRED)')
    save(fig, 'can_unemployment.png')


# =====================================================================
# Figure 2: Canadian inflation (long-run)
# =====================================================================
def can_inflation_longrun():
    print('Figure 2: Canadian inflation (long-run)')
    cpi = get_fred_data('CANCPIALLMINMEI')          # CPI index, 2015=100
    infl = cpi.pct_change(12).dropna()               # 12-month % change

    fig, ax = new_figure()

    ax.plot(infl, color=palette[0], linewidth=2)
    ax.axhline(y=0.02, color=palette[1], linestyle=':', linewidth=1.5,
               label=r"Cible de 2\% de la BdC (depuis 1991)")

    # Annotation for 2022 peak
    peak_date = infl.loc['2021-01-01':'2023-12-31'].idxmax()
    peak_val = infl.loc[peak_date]
    ax.annotate(f'{100*peak_val:.1f}\\%',
                xy=(peak_date, peak_val),
                xytext=(peak_date - pd.DateOffset(years=5), peak_val + 0.005),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    last_date = infl.dropna().index[-1]
    ax.set_xlim(pd.to_datetime('1965'), last_date + pd.DateOffset(months=3))
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(1965, last_date.year + 1, 5)])
    ax.set_xticklabels(range(1965, last_date.year + 1, 5), fontsize=12,
                       rotation=45, ha='right')
    ax.set_ylim(-0.02, 0.14)
    ax.set_yticks(np.arange(-0.02, 0.14 + 0.001, 0.02))
    ax.set_yticklabels([f'{x:.0f}' + r'\%' for x in np.arange(-2, 14 + 0.1, 2)],
                       fontsize=12)
    ax.set_ylabel(r"Inflation IPC (12 mois)", fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('1965'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left',
              bbox_to_anchor=(0.55, 1.0))
    add_source(ax, 'Source: OECD (via FRED)')
    save(fig, 'can_inflation_longrun.png')


# =====================================================================
# Figure 3: Policy rates (Fed + BoC)
# =====================================================================
def policy_rates():
    print('Figure 3: Policy rates (Fed + BoC)')
    fed = get_fred_data('DFF', frequency='m', aggregation_method='avg')
    boc = get_fred_data('IRSTCI01CAM156N')

    fig, ax = new_figure()

    ax.plot(fed, color=palette[0], linewidth=2,
            label=r"Taux des fonds f\'{e}d\'{e}raux (\'{E}.-U.)")
    ax.plot(boc, color=palette[1], linewidth=2,
            label=r"Taux \`{a} un jour (Canada)")

    last_year = max(fed.dropna().index[-1].year, boc.dropna().index[-1].year)
    xlim_end = tick_ceil(last_year, 2)
    ax.set_xlim(pd.to_datetime('2006'), pd.to_datetime(str(xlim_end)))
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(2006, xlim_end + 1, 2)])
    ax.set_xticklabels(range(2006, xlim_end + 1, 2), fontsize=12)
    ax.set_ylim(0, 6)
    ax.set_yticks(range(0, 6 + 1, 1))
    ax.set_yticklabels([str(x) + r'\%' for x in range(0, 6 + 1, 1)], fontsize=12)
    ax.set_ylabel('Taux directeur', fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    for start, end in recessions_ca:
        ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='center left',
              bbox_to_anchor=(0.35, 0.55))
    add_source(ax)
    save(fig, 'policy_rates.png')


# =====================================================================
# Figure 4: Canadian inflation (recent)
# =====================================================================
def canada_inflation_recent():
    print('Figure 4: Canadian inflation (recent)')
    cpi = get_fred_data('CANCPIALLMINMEI')          # CPI index, 2015=100
    infl = cpi.pct_change(12).dropna()               # 12-month % change

    # Fetch BoC consumer inflation expectations (1-year ahead)
    # Survey date maps to expected inflation 1 year forward
    exp_1yr = get_valet_series('CES_C1_SHORT_TERM', start='2014-01-01')
    # Shift dates forward by 1 year (expectation horizon)
    exp_dates = exp_1yr.index + pd.DateOffset(years=1)
    exp_vals = exp_1yr.values / 100  # convert from % to fraction

    fig, ax = new_figure()

    # BoC target band (1-3%)
    ax.axhspan(0.01, 0.03, color=palette[1], alpha=0.12, linewidth=0)
    ax.axhline(y=0.02, color=palette[1], linestyle=':', linewidth=1.5,
               label=r"Cible de 2\% de la BdC")

    ax.plot(infl, color=palette[0], linewidth=2, label='Inflation IPC')

    # Plot expectations (only future portion, from last actual data onward)
    last_actual = infl.dropna().index[-1]
    future_mask = exp_dates > last_actual
    if future_mask.any():
        # Connect from last actual point to first expectation point
        bridge_dates = pd.Index([last_actual]).append(exp_dates[future_mask])
        bridge_vals = np.concatenate([[infl.loc[last_actual]],
                                      exp_vals[future_mask]])
        ax.plot(bridge_dates, bridge_vals, color=palette[7], linewidth=2,
                linestyle=':', label='Anticipations des consommateurs (1 an)')

    # Annotation for 2022 peak
    peak_date = infl.loc['2021-01-01':'2023-12-31'].idxmax()
    peak_val = infl.loc[peak_date]
    ax.annotate(f'{100*peak_val:.1f}\\%',
                xy=(peak_date, peak_val),
                xytext=(peak_date + pd.DateOffset(months=8), peak_val + 0.008),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    # x-axis: end at the last plotted point
    last_plot = last_actual
    if future_mask.any():
        last_plot = max(last_plot, exp_dates[future_mask][-1])
    ax.set_xlim(pd.to_datetime('2016'), last_plot)
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(2016, last_plot.year + 1, 1)])
    ax.set_xticklabels(range(2016, last_plot.year + 1, 1), fontsize=12,
                       rotation=45, ha='right')
    ax.set_ylim(-0.02, 0.10)
    ax.set_yticks(np.arange(-0.02, 0.10 + 0.001, 0.02))
    ax.set_yticklabels([f'{x:.0f}' + r'\%' for x in np.arange(-2, 10 + 0.1, 2)],
                       fontsize=12)
    ax.set_ylabel(r"Inflation IPC (12 mois)", fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0))
    add_source(ax, 'Source: FRED; Bank of Canada (CSCE)')
    save(fig, 'canada_inflation_recent.png')


# =====================================================================
# Figure 5: Canadian employment by US-export dependence
# =====================================================================
def canada_employment_exports():
    print('Figure 5: Canadian employment by export dependence')
    sc = StatsCan()

    # Table 14-10-0355-01: Employment by industry, monthly, seasonally adjusted
    df = sc.table_to_df('14-10-0355-01')

    # Parse dates and keep only seasonally adjusted data
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])
    df = df[df['Data type'] == 'Seasonally adjusted']
    df = df[df['REF_DATE'] >= '2023-01-01']

    # Industries with high US-export dependence
    high_export = [
        'Manufacturing',
        'Mining, quarrying, and oil and gas extraction',
        'Agriculture',
        'Forestry, fishing, mining, quarrying, oil and gas',
    ]

    # Industries with limited US-export dependence
    low_export = [
        'Health care and social assistance',
        'Educational services',
        'Public administration',
        'Construction',
        'Accommodation and food services',
        'Retail trade',
    ]

    # Get available industry names
    industries = df['North American Industry Classification System (NAICS)'].unique()

    # Match industries to categories (partial matching for flexibility)
    def match_industries(target_list, available):
        matched = []
        for t in target_list:
            for a in available:
                if t.lower() in a.lower():
                    matched.append(a)
                    break
        return matched

    high_matched = match_industries(high_export, industries)
    low_matched = match_industries(low_export, industries)

    # Filter and aggregate, indexed to Jan 2023 = 100
    def get_index(industry_list):
        mask = df['North American Industry Classification System (NAICS)'].isin(industry_list)
        sub = df.loc[mask, ['REF_DATE', 'VALUE']].groupby('REF_DATE')['VALUE'].sum()
        base = sub.loc['2023-01-01':'2023-01-31']
        if len(base) > 0:
            sub = sub / base.iloc[0] * 100
        return sub

    # Total employment
    total_mask = df['North American Industry Classification System (NAICS)'].str.contains(
        'Total employed, all industries|Industrial aggregate', case=False, na=False)
    total = df.loc[total_mask, ['REF_DATE', 'VALUE']].groupby('REF_DATE')['VALUE'].sum()
    if len(total) > 0:
        base_total = total.loc['2023-01-01':'2023-01-31']
        if len(base_total) > 0:
            total = total / base_total.iloc[0] * 100

    fig, ax = new_figure()

    # Use HEC colours: coral for high-export, navy for low-export, green for all
    if len(high_matched) > 0:
        high_idx = get_index(high_matched)
        ax.plot(high_idx, color=palette[2], linewidth=2,
                label=r"Forte d\'{e}pendance aux export. am\'{e}ricaines")
    if len(low_matched) > 0:
        low_idx = get_index(low_matched)
        ax.plot(low_idx, color=palette[0], linewidth=2,
                label=r"Faible d\'{e}pendance aux export. am\'{e}ricaines")
    if len(total) > 0:
        ax.plot(total, color=palette[1], linewidth=2,
                label='Tous les secteurs')

    # Determine y-axis range: round to nice ticks
    all_series = []
    if len(high_matched) > 0:
        all_series.append(high_idx)
    if len(low_matched) > 0:
        all_series.append(low_idx)
    if len(total) > 0:
        all_series.append(total)
    if all_series:
        ymin_data = min(s.min() for s in all_series)
        ymax_data = max(s.max() for s in all_series)
        ymin = int(np.floor(ymin_data / 2) * 2)
        ymax = int(np.ceil(ymax_data / 2) * 2)
        ax.set_ylim(ymin, ymax)
        ax.set_yticks(range(ymin, ymax + 1, 2))
        ax.set_yticklabels([str(x) for x in range(ymin, ymax + 1, 2)],
                           fontsize=12)

    # x-axis: end at the next 6-month tick (Jan or Jul) at or after last data
    all_dates = pd.concat(all_series).index if all_series else pd.DatetimeIndex([])
    last_data = all_dates.max() if len(all_dates) > 0 else pd.to_datetime('2026-01-01')
    # Generate enough ticks, then trim to the first one >= last_data
    xtick_all = pd.date_range('2023-01-01', periods=20, freq='6MS')
    xlim_right = xtick_all[xtick_all >= last_data].min()
    xtick_dates = xtick_all[xtick_all <= xlim_right]
    ax.set_xlim(pd.to_datetime('2023-01-01'), xlim_right)
    ax.set_xticks(xtick_dates)
    ax.set_xticklabels([french_date_label(d) for d in xtick_dates], fontsize=11)
    ax.set_ylabel(r"Indice d'emploi (janv. 2023 = 100)", fontsize=12,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, 'Source: Statistics Canada, Table 14-10-0355-01')
    save(fig, 'canada_employment_exports.png')


# =====================================================================
# Figure 6: Hockey stick — world GDP per capita
# =====================================================================
def hockey_stick_world():
    print('Figure 6: Hockey stick (GDP per capita, long-run)')
    # Download Maddison GDP per capita from OWID API (Maddison 2023 edition, data to 2022)
    df = _get_owid_maddison()

    fig, ax = new_figure()

    # Data uses English entity names; display labels are French
    countries = {
        'United States': (r"\'{E}tats-Unis", palette[0]),
        'United Kingdom': ('Royaume-Uni', palette[1]),
        'Canada': ('Canada', palette[2]),
        'France': ('France', palette[3]),
    }

    max_year = 0
    for entity_en, (label_fr, color) in countries.items():
        sub = df.loc[(df['Entity'] == entity_en) & df['GDP per capita'].notna()]
        ax.plot(sub['Year'], sub['GDP per capita'], color=color,
                label=label_fr, linewidth=2)
        max_year = max(max_year, sub['Year'].max())

    ax.set_xlim(0, max_year + 5)
    ax.set_xticks(range(0, max_year + 1, 250))
    ax.set_xticklabels(range(0, max_year + 1, 250), fontsize=12)
    ax.set_ylim(0, 60000)
    ax.set_yticks(range(0, 60000 + 1, 10000))
    ax.set_yticklabels([r'\$' + str(x) + 'K' for x in range(0, 60 + 1, 10)],
                       fontsize=12)
    ax.set_ylabel(r"PIB r\'{e}el par habitant", fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left',
              bbox_to_anchor=(0.02, 1.0))
    add_source(ax, 'Source: Maddison Project Database 2023 (via Our World in Data)')
    save(fig, 'hockey_stick_world.png')


# =====================================================================
# Figure 7: US effective tariff rate since 1790
# =====================================================================
def us_tariff_rate():
    print('Figure 7: US effective tariff rate since 1790')
    # Data from Yale Budget Lab "State of U.S. Tariffs: January 19, 2026"
    xlsx = os.path.join(Path(__file__).resolve().parent.parent, 'Data', 'tariff_data.xlsx')
    df = pd.read_excel(xlsx, sheet_name='F1', header=None,
                       skiprows=5,  # skip title/subtitle/source/blank/header
                       names=['Year', 'ETR', 'proj_post', 'cur_post',
                              'proj_pre', 'cur_pre'])
    # Keep only rows with a valid year
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)

    # Historical series (1790-2024)
    hist = df[df['ETR'].notna()].copy()

    # 2025 rates (pre-substitution)
    row_2025 = df[df['Year'] == 2025].iloc[0]
    etr_2025_overall = row_2025['proj_pre']  # ~17.5% overall

    # Canada-specific ETR from T2 sheet
    t2 = pd.read_excel(xlsx, sheet_name='T2', header=None,
                        skiprows=5, names=['Partner', 'ETR_pre', 'ETR_post',
                                           'Share_pre', 'Share_post',
                                           'Contrib_pre', 'Contrib_post'])
    t2 = t2.dropna(subset=['Partner'])
    canada_row = t2[t2['Partner'].str.strip() == 'Canada'].iloc[0]
    etr_2025_canada = canada_row['ETR_pre']  # ~8.1%

    fig, ax = new_figure()

    # Historical line
    ax.plot(hist['Year'], hist['ETR'], color=palette[0], linewidth=2)

    # Spike to 2025: dotted connectors + markers
    last_hist_year = hist['Year'].iloc[-1]
    last_hist_etr = hist['ETR'].iloc[-1]

    # Overall US rate (coral)
    ax.plot([last_hist_year, 2025], [last_hist_etr, etr_2025_overall],
            color=palette[2], linewidth=2, linestyle=':')
    ax.plot(2025, etr_2025_overall, 'o', color=palette[2], markersize=8, zorder=5)

    # Canada-specific rate (green)
    ax.plot([last_hist_year, 2025], [last_hist_etr, etr_2025_canada],
            color=palette[1], linewidth=2, linestyle=':')
    ax.plot(2025, etr_2025_canada, 'o', color=palette[1], markersize=8, zorder=5)

    # Annotations — equal-length arrows
    # Figure is 8×4 in, axes span 97 yr × 20 pp → x_scale=0.0825 in/yr, y_scale=0.2 in/pp
    # Target visual arrow length ≈ 1.5 in for all three
    ax.annotate(f'{etr_2025_overall:.1f}\\%  global',
                xy=(2025, etr_2025_overall),
                xytext=(2007, 19),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))
    ax.annotate(f'{etr_2025_canada:.1f}\\%  Canada',
                xy=(2025, etr_2025_canada),
                xytext=(2008, 11),
                fontsize=11, color=palette[1], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[1], lw=1.5))

    # Smoot-Hawley (shrinkB=12pt ≈ 0.17 in gap before data line)
    etr_1932 = hist.loc[hist['Year'] == 1932, 'ETR'].iloc[0]
    ax.annotate('Smoot-Hawley' + '\n' + f'({etr_1932:.0f}\\%)',
                xy=(1932, etr_1932),
                xytext=(1949, 15.5),
                fontsize=9, color=palette[7], ha='center',
                arrowprops=dict(arrowstyle='->', color=palette[7],
                                lw=1, alpha=0.6, shrinkB=12))

    ax.set_xlim(1930, 2027)
    ax.set_xticks(range(1930, 2020 + 1, 10))
    ax.set_xticklabels(range(1930, 2020 + 1, 10), fontsize=12)
    ax.set_ylim(0, 20)
    ax.set_yticks(range(0, 20 + 1, 5))
    ax.set_yticklabels([str(x) + r'\%' for x in range(0, 20 + 1, 5)],
                       fontsize=12)
    ax.set_ylabel(r"Taux tarifaire effectif am\'{e}ricain", fontsize=12,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    add_source(ax, 'Source: Yale Budget Lab (January 2026)')
    save(fig, 'us_tariff_rate.png')


# ── StatsCan GDP accounts helper ──────────────────────────────────────
def _load_gdp_accounts():
    """Load and pivot StatsCan table 36-10-0104-01 (GDP by expenditure,
    chained 2017 dollars).  Returns a DataFrame with one column per
    Estimates category, indexed by REF_DATE."""
    sc = StatsCan()
    df = sc.table_to_df('36-10-0104-01')
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])
    df = df[df['Prices'] == 'Chained (2017) dollars']
    df = df.pivot(index='REF_DATE', columns='Estimates',
                  values='VALUE').reset_index()
    return df


def _gdp_share_plot(dates, ratio, ylabel, ylim, ytick_step, fname):
    """Generic GDP-share time-series plot with recession shading."""
    fig, ax = new_figure()
    ax.plot(dates, ratio, color=palette[0], linewidth=2)

    last_date = dates.iloc[-1]
    last_year_tick = (last_date.year // 10) * 10       # round *down* to decade
    ax.set_xlim(pd.to_datetime('1970'), last_date)
    ax.set_xticks([pd.to_datetime(str(y))
                   for y in range(1970, last_year_tick + 1, 10)])
    ax.set_xticklabels(range(1970, last_year_tick + 1, 10), fontsize=12)

    ax.set_ylim(ylim)
    yticks = np.arange(
        np.ceil(ylim[0] / ytick_step) * ytick_step,
        ylim[1] + ytick_step / 2,
        ytick_step)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{100*x:.0f}' + r'\%' for x in yticks], fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('1970'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    add_source(ax, 'Source: Statistics Canada, Table 36-10-0104-01')
    save(fig, fname)


# =====================================================================
# Figure 8: GDP decomposition pie chart (most recent year)
# =====================================================================
def gdp_decomposition_canada():
    print('Figure 8: GDP decomposition pie chart')
    df = _load_gdp_accounts()

    # Use most recent full year of data
    year = df['REF_DATE'].dt.year.max()
    dy = df[df['REF_DATE'].dt.year == year]

    # Components (consistent with time-series definitions)
    C = (dy['Final consumption expenditure'].mean()
         - dy['General governments final consumption expenditure'].mean())
    G = (dy['General governments final consumption expenditure'].mean()
         + dy['General governments gross fixed capital formation'].mean())
    I = (dy['Gross fixed capital formation'].mean()
         + dy['Investment in inventories'].mean()
         - dy['General governments gross fixed capital formation'].mean())
    X = dy['Exports of goods and services'].mean()
    M = dy['Less: imports of goods and services'].mean()
    NX = X - M
    Y = C + G + I + NX

    shares = [C / Y, I / Y, G / Y, np.abs(NX) / Y]
    labels = ['$C$', '$I$', '$G$', '$NX$']
    colors = [palette[0], palette[2], palette[1], palette[3]]

    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    # Place percentage labels at wedge centroids
    pct_labels = [f'{100*s:.0f}\\%' for s in shares]
    # NX label shows sign
    nx_sign = '$-$' if NX < 0 else ''
    pct_labels[3] = f'{nx_sign}{100*np.abs(NX)/Y:.0f}\\%'

    wedges, texts = ax.pie(
        shares, labels=labels, colors=colors,
        startangle=90, counterclock=False,
        textprops={'fontsize': 20, 'fontweight': 'bold'},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2})

    # Add percentage inside each large wedge (at 0.55 radius)
    for i, (wedge, pct) in enumerate(zip(wedges, pct_labels)):
        ang = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
        if i < 3:  # C, I, G — label inside
            x = 0.55 * np.cos(ang)
            y = 0.55 * np.sin(ang)
            ax.text(x, y, pct, fontsize=18, fontweight='bold',
                    color='white', ha='center', va='center')
        else:  # NX — label outside with leader line
            ax.annotate(pct,
                        xy=(0.95 * np.cos(ang), 0.95 * np.sin(ang)),
                        xytext=(1.35 * np.cos(ang), 1.35 * np.sin(ang)),
                        fontsize=18, fontweight='bold', ha='center',
                        arrowprops=dict(arrowstyle='-', color='black',
                                        lw=0.8))

    add_source(ax, f'Source: Statistics Canada ({year})')
    save(fig, 'gdp_decomposition_canada.png')


# =====================================================================
# Figure 8b: GDP decomposition — 4-country comparison
# =====================================================================
def gdp_decomposition_4countries():
    print('Figure 8b: GDP decomposition — 4-country comparison')

    # World Bank indicator codes (most recent year available)
    # NE.CON.PRVT.ZS  Household final consumption (% of GDP)
    # NE.GDI.TOTL.ZS  Gross capital formation (% of GDP)
    # NE.CON.GOVT.ZS  Government final consumption (% of GDP)
    # NE.RSB.GNFS.ZS  External balance (Net exports, % of GDP)
    indicators = {
        'C': 'NE.CON.PRVT.ZS',
        'I': 'NE.GDI.TOTL.ZS',
        'G': 'NE.CON.GOVT.ZS',
        'NX': 'NE.RSB.GNFS.ZS',
    }
    countries = {
        'CAN': 'Canada',
        'USA': r"\'{E}tats-Unis",
        'CHN': 'Chine',
        'BRA': r"Br\'{e}sil",
    }

    # Fetch from World Bank API
    data = {}
    for iso, name in countries.items():
        data[name] = {}
        for comp, ind in indicators.items():
            url = (f'https://api.worldbank.org/v2/country/{iso}/'
                   f'indicator/{ind}?format=json&per_page=5&date=2019:2024')
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            records = resp.json()[1]
            # Take most recent non-null value
            for r in records:
                if r['value'] is not None:
                    data[name][comp] = r['value']
                    data[name]['year'] = r['date']
                    break

    colors = [palette[0], palette[2], palette[1], palette[3]]  # C, I, G, NX
    fig, axes = plt.subplots(1, 4, figsize=(14, 4.5))
    fig.patch.set_alpha(0.0)
    fig.subplots_adjust(top=0.85)

    for ax, (name, comps) in zip(axes, data.items()):
        ax.patch.set_alpha(0.0)
        C, I, G = comps['C'], comps['I'], comps['G']
        NX = comps.get('NX', 0) or 0
        nx_sign = '$-$' if NX < 0 else ''
        shares = [C, I, G, np.abs(NX)]
        labels = ['$C$', '$I$', '$G$',
                  f'$NX$\n{nx_sign}{np.abs(NX):.0f}\\%']

        wedges, texts = ax.pie(
            shares, labels=labels, colors=colors,
            startangle=90, counterclock=False,
            textprops={'fontsize': 18, 'fontweight': 'bold'},
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
            labeldistance=1.15)

        # Percentage labels inside large wedges (C, I, G)
        for i in range(3):
            wedge = wedges[i]
            ang = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
            val = [C, I, G][i]
            ax.text(0.55 * np.cos(ang), 0.55 * np.sin(ang),
                    f'{val:.0f}\\%',
                    fontsize=18, fontweight='bold', color='white',
                    ha='center', va='center')

        ax.set_title(f'\\textbf{{{name}}}', fontsize=20, pad=20)

    fig.text(0.99, 0.005, f'Source: World Bank ({comps["year"]})',
             fontsize=8, ha='right', va='bottom')
    save(fig, 'gdp_decomposition_4countries.png')


# =====================================================================
# Figure 9: Consumption share of GDP
# =====================================================================
def consumption_share_gdp():
    print('Figure 9: Consumption share of GDP')
    df = _load_gdp_accounts()
    df['Consumption'] = (df['Final consumption expenditure']
                         - df['General governments final consumption expenditure'])
    ratio = df['Consumption'] / df['Gross domestic product at market prices']
    _gdp_share_plot(df['REF_DATE'], ratio,
                    ylabel=r'$C / Y$',
                    ylim=(0.47, 0.60), ytick_step=0.02,
                    fname='consumption_share_gdp.png')


# =====================================================================
# Figure 9: Investment share of GDP
# =====================================================================
def investment_share_gdp():
    print('Figure 9: Investment share of GDP')
    df = _load_gdp_accounts()
    df['Investment'] = (df['Gross fixed capital formation']
                        + df['Investment in inventories']
                        - df['General governments gross fixed capital formation'])
    ratio = df['Investment'] / df['Gross domestic product at market prices']
    _gdp_share_plot(df['REF_DATE'], ratio,
                    ylabel=r'$I / Y$',
                    ylim=(0.125, 0.24), ytick_step=0.02,
                    fname='investment_share_gdp.png')


# =====================================================================
# Figure 10: Government spending share of GDP
# =====================================================================
def government_share_gdp():
    print('Figure 10: Government spending share of GDP')
    df = _load_gdp_accounts()
    df['Government'] = (df['General governments final consumption expenditure']
                        + df['General governments gross fixed capital formation'])
    ratio = df['Government'] / df['Gross domestic product at market prices']
    _gdp_share_plot(df['REF_DATE'], ratio,
                    ylabel=r'$G / Y$',
                    ylim=(0.23, 0.34), ytick_step=0.02,
                    fname='government_share_gdp.png')


# =====================================================================
# Figure 11: Trade share of GDP
# =====================================================================
def trade_share_gdp():
    print('Figure 11: Trade share of GDP')
    df = _load_gdp_accounts()
    # Exports + |Imports| = total two-way trade (openness measure)
    df['Trade'] = (df['Exports of goods and services']
                   + df['Less: imports of goods and services'].abs())
    ratio = df['Trade'] / df['Gross domestic product at market prices']
    _gdp_share_plot(df['REF_DATE'], ratio,
                    ylabel=r'$(X + M) / Y$',
                    ylim=(0.28, 0.70), ytick_step=0.10,
                    fname='trade_share_gdp.png')


# ── World Bank API helper ─────────────────────────────────────────────
def _get_worldbank(indicator, country_iso, start=2000, end=2025):
    """Fetch annual data from the World Bank API as a pandas Series."""
    url = (f'https://api.worldbank.org/v2/country/{country_iso}/'
           f'indicator/{indicator}?format=json&per_page=100'
           f'&date={start}:{end}')
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    records = resp.json()[1]
    data = [(int(r['date']), r['value']) for r in records
            if r['value'] is not None]
    s = pd.Series(dict(data)).sort_index()
    s.index = pd.to_datetime(s.index, format='%Y')
    return s


# =====================================================================
# Figure: Real GDP — Canada vs USA (quarterly, indexed)
# =====================================================================
def gdp_canada_usa():
    print('Figure: Real GDP — Canada vs USA (quarterly)')
    can = get_fred_data('NGDPRSAXDCCAQ')   # Real GDP, quarterly, SA, CAD millions
    usa = get_fred_data('GDPC1')           # Real GDP, quarterly, SA, USD billions

    # Index to 2000Q1 = 100
    can_base = can.loc['2000-01-01':'2000-03-31'].iloc[0]
    usa_base = usa.loc['2000-01-01':'2000-03-31'].iloc[0]
    can_idx = (can / can_base * 100).loc['2000-01-01':]
    usa_idx = (usa / usa_base * 100).loc['2000-01-01':]

    fig, ax = new_figure()
    ax.plot(can_idx, color=palette[0], linewidth=2.5, label='Canada')
    ax.plot(usa_idx, color=palette[1], linewidth=2.5,
            label=r"\'{E}tats-Unis")

    last_date = min(can_idx.dropna().index[-1], usa_idx.dropna().index[-1])
    ax.set_xlim(pd.to_datetime('2000-01-01'), last_date)
    xticks = [pd.to_datetime(str(y)) for y in range(2000, last_date.year + 1, 5)]
    ax.set_xticks(xticks)
    ax.set_xticklabels([d.year for d in xticks], fontsize=12)

    ymax = tick_ceil(max(can_idx.max(), usa_idx.max()), 10)
    ax.set_ylim(100, ymax)
    ax.set_yticks(range(100, ymax + 1, 10))
    ax.set_yticklabels(range(100, ymax + 1, 10), fontsize=12)
    ax.set_ylabel(r"PIB r\'{e}el (2000T1 = 100)", fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('2000'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, 'Source: OECD (via FRED)')
    save(fig, 'gdp_canada_usa.png')


# =====================================================================
# Figure: Real GDP per capita — Canada vs USA (quarterly, indexed)
# =====================================================================
def gdp_per_capita_canada_usa():
    print('Figure: Real GDP per capita — Canada vs USA (quarterly)')
    can_gdp = get_fred_data('NGDPRSAXDCCAQ')
    usa_gdp = get_fred_data('GDPC1')

    # Annual total population from World Bank, interpolated to quarterly
    can_pop_a = _get_worldbank('SP.POP.TOTL', 'CAN', start=1999, end=2025)
    usa_pop_a = _get_worldbank('SP.POP.TOTL', 'USA', start=1999, end=2025)

    q_dates = can_gdp.loc['1999-01-01':].index
    combined_can = can_pop_a.index.union(q_dates).sort_values().drop_duplicates()
    combined_usa = usa_pop_a.index.union(q_dates).sort_values().drop_duplicates()
    can_pop_q = can_pop_a.reindex(combined_can).interpolate(method='time').reindex(q_dates)
    usa_pop_q = usa_pop_a.reindex(combined_usa).interpolate(method='time').reindex(q_dates)

    # GDP per capita (units cancel when indexing)
    can_pc = (can_gdp / can_pop_q).dropna()
    usa_pc = (usa_gdp / usa_pop_q).dropna()

    # Index to 2000Q1 = 100
    can_base = can_pc.loc['2000-01-01':'2000-03-31'].iloc[0]
    usa_base = usa_pc.loc['2000-01-01':'2000-03-31'].iloc[0]
    can_idx = (can_pc / can_base * 100).loc['2000-01-01':]
    usa_idx = (usa_pc / usa_base * 100).loc['2000-01-01':]

    fig, ax = new_figure()
    ax.plot(can_idx, color=palette[0], linewidth=2.5, label='Canada')
    ax.plot(usa_idx, color=palette[1], linewidth=2.5,
            label=r"\'{E}tats-Unis")

    last_date = min(can_idx.dropna().index[-1], usa_idx.dropna().index[-1])
    ax.set_xlim(pd.to_datetime('2000-01-01'), last_date)
    xticks = [pd.to_datetime(str(y)) for y in range(2000, last_date.year + 1, 5)]
    ax.set_xticks(xticks)
    ax.set_xticklabels([d.year for d in xticks], fontsize=12)

    ymax = tick_ceil(max(can_idx.max(), usa_idx.max()), 10)
    ax.set_ylim(100, ymax)
    ax.set_yticks(range(100, ymax + 1, 10))
    ax.set_yticklabels(range(100, ymax + 1, 10), fontsize=12)
    ax.set_ylabel(r"PIB r\'{e}el par hab. (2000T1 = 100)", fontsize=12,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('2000'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, 'Source: OECD (via FRED), World Bank')
    save(fig, 'gdp_per_capita_canada_usa.png')


# =====================================================================
# Figure: GDP per capita vs GDP — cross-country scatter
# =====================================================================
def gdp_vs_gdp_per_capita():
    print('Figure: GDP per capita vs GDP — cross-country scatter')
    # GDP, PPP (constant 2021 international $)
    gdp_ind = 'NY.GDP.MKTP.PP.KD'
    # GDP per capita, PPP (constant 2021 international $)
    gdppc_ind = 'NY.GDP.PCAP.PP.KD'
    # Population (for bubble sizes)
    pop_ind = 'SP.POP.TOTL'

    def _fetch_all(indicator, year=2023):
        url = (f'https://api.worldbank.org/v2/country/all/'
               f'indicator/{indicator}?format=json&per_page=500'
               f'&date={year}:{year}')
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        pages = resp.json()[0]['pages']
        records = resp.json()[1]
        for p in range(2, pages + 1):
            resp2 = requests.get(url + f'&page={p}', timeout=30)
            records.extend(resp2.json()[1])
        return {r['countryiso3code']: r['value'] for r in records
                if r['value'] is not None and r['countryiso3code']}

    gdp = _fetch_all(gdp_ind)
    gdppc = _fetch_all(gdppc_ind)
    pop = _fetch_all(pop_ind)

    rows = []
    for iso in gdp:
        if iso in gdppc and iso in pop:
            rows.append({
                'iso': iso,
                'gdp': gdp[iso] / 1e12,       # trillions
                'gdppc': gdppc[iso],           # raw dollars
                'pop': pop[iso],
            })
    df = pd.DataFrame(rows)

    # Drop aggregates (World Bank region/income groups)
    aggregates = {'WLD', 'EAS', 'ECS', 'LCN', 'MEA', 'NAC', 'SAS', 'SSF',
                  'EMU', 'EUU', 'OED', 'HIC', 'LIC', 'LMC', 'MIC', 'UMC',
                  'LDC', 'ARB', 'CSS', 'PST', 'TSA', 'TSS', 'TEA', 'TEC',
                  'TLA', 'TMN', 'TNA', 'FCS', 'HPC', 'IBD', 'IBT', 'IDA',
                  'IDB', 'IDX', 'PRE', 'SSA', 'SST', 'LMY', 'LTE', 'EAP',
                  'EAR', 'ECR', 'LAC', 'MNA', 'INX', 'OSS', 'CEB', 'SXZ',
                  'AFE', 'AFW', 'ECA'}
    df = df[~df['iso'].isin(aggregates)]
    df = df[df['gdp'] > 0]

    # Highlight countries (ISO → French display label)
    highlights = {
        'USA': r"\'{E}tats-Unis", 'CAN': 'Canada', 'CHN': 'Chine',
        'IND': 'Inde', 'BRA': r"Br\'{e}sil", 'NGA': r"Nig\'{e}ria",
        'NOR': r"Norv\`{e}ge", 'LUX': 'Luxembourg',
    }

    fig, ax = new_figure()

    # Bubble sizes proportional to population
    max_pop = df['pop'].max()
    sizes = 500 * (df['pop'] / max_pop) ** 0.5
    sizes = sizes.clip(lower=12)

    ax.scatter(df['gdp'], df['gdppc'], s=sizes,
               color=palette[0], alpha=0.35, edgecolors='white',
               linewidth=0.5)

    # Highlight specific countries
    for iso, name in highlights.items():
        row = df[df['iso'] == iso]
        if len(row) == 0:
            continue
        row = row.iloc[0]
        sz = 500 * (row['pop'] / max_pop) ** 0.5
        sz = max(sz, 12)
        color = palette[1] if iso == 'CAN' else palette[0]
        ax.scatter(row['gdp'], row['gdppc'], s=sz,
                   color=color, alpha=0.7, edgecolors='white', linewidth=0.5,
                   zorder=5)
        # Offset tuning
        offsets = {
            'USA': (12, 10), 'CAN': (12, 12), 'CHN': (12, -16),
            'IND': (12, 8), 'BRA': (12, -14), 'NGA': (-55, -10),
            'NOR': (-55, 14), 'LUX': (10, -14),
        }
        ox, oy = offsets.get(iso, (12, 8))
        ax.annotate(name, xy=(row['gdp'], row['gdppc']),
                    xytext=(ox, oy), textcoords='offset points',
                    fontsize=9, fontweight='bold', color='black',
                    arrowprops=dict(arrowstyle='-', color=palette[7],
                                    lw=0.8, shrinkB=3),
                    zorder=10)

    ax.set_xscale('log')
    ax.set_xlim(0.005, 80)
    ax.set_xticks([0.01, 0.1, 1, 10])
    ax.set_xticklabels([r'\$0.01T', r'\$0.1T', r'\$1T', r'\$10T'],
                       fontsize=12)
    ax.set_xlabel(r"PIB r\'{e}el, PPA (milliers de Mds, \$ int. 2021)",
                  fontsize=12)

    ax.set_yscale('log')
    ax.set_ylim(800, 150000)
    yticks = [1000, 2000, 5000, 10000, 20000, 50000, 100000]
    ax.set_yticks(yticks)
    ax.set_yticklabels([r'\$1K', r'\$2K', r'\$5K', r'\$10K',
                        r'\$20K', r'\$50K', r'\$100K'], fontsize=12)
    ax.set_ylabel(r"PIB r\'{e}el par habitant (PPA)", fontsize=12,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    add_source(ax, 'Source: World Bank, WDI (2023)')
    save(fig, 'gdp_vs_gdp_per_capita.png')


# =====================================================================
# Figure: Real GDP at PPP — horizontal bar chart of top economies
# =====================================================================
def gdp_ppp_time_series():
    print('Figure: Real GDP at PPP — top economies bar chart')
    # World Bank: GDP, PPP (constant 2021 international $)
    indicator = 'NY.GDP.MKTP.PP.KD'

    # Top 12 economies by GDP PPP (approximate ordering)
    # ISO → (English name for API, French label for display)
    countries_iso = {
        'CHN': ('China', 'Chine'),
        'USA': ('United States', r"\'{E}tats-Unis"),
        'IND': ('India', 'Inde'),
        'JPN': ('Japan', 'Japon'),
        'DEU': ('Germany', 'Allemagne'),
        'RUS': ('Russia', 'Russie'),
        'IDN': ('Indonesia', r"Indon\'{e}sie"),
        'BRA': ('Brazil', r"Br\'{e}sil"),
        'GBR': ('United Kingdom', 'Royaume-Uni'),
        'FRA': ('France', 'France'),
        'MEX': ('Mexico', 'Mexique'),
        'CAN': ('Canada', 'Canada'),
    }

    data = {}
    for iso, (name_en, name_fr) in countries_iso.items():
        s = _get_worldbank(indicator, iso, start=2020, end=2025)
        if len(s) > 0:
            data[name_fr] = s.iloc[-1] / 1e12  # most recent year, in trillions

    # Sort descending
    data = dict(sorted(data.items(), key=lambda x: x[1], reverse=False))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    names = list(data.keys())
    values = list(data.values())
    colors = [palette[1] if n == 'Canada' else palette[0] for n in names]

    bars = ax.barh(names, values, color=colors, height=0.65, edgecolor='white',
                   linewidth=0.5)

    # Value labels at end of each bar
    for bar, val in zip(bars, values):
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                f'\\${val:.1f}T', va='center', fontsize=10, color=palette[7])

    ax.set_xlim(0, max(values) * 1.2)
    ax.set_xticks([])
    ax.tick_params(axis='y', labelsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.invert_yaxis()

    ax.set_title(r"PIB r\'{e}el en PPA (milliers de Mds, \$ int. 2021)",
                 fontsize=12, loc='left', pad=10)
    add_source(ax, 'Source: World Bank, WDI')
    save(fig, 'gdp_ppp_world.png')


# =====================================================================
# Figure: GDP per capita vs price level (cross-section scatter)
# =====================================================================
def gdp_per_capita_vs_price_level():
    print('Figure: GDP per capita vs price level')
    # GDP per capita, PPP (constant 2021 international $)
    gdppc_ind = 'NY.GDP.PCAP.PP.KD'
    # PPP conversion factor, GDP (LCU per international $)
    ppp_ind = 'PA.NUS.PPP'
    # Official exchange rate (LCU per US$, period average)
    xr_ind = 'PA.NUS.FCRF'
    # Population
    pop_ind = 'SP.POP.TOTL'

    # Fetch all countries at once (keyed by ISO3 code)
    def _fetch_all(indicator, year=2024):
        url = (f'https://api.worldbank.org/v2/country/all/'
               f'indicator/{indicator}?format=json&per_page=500'
               f'&date={year}:{year}')
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        pages = resp.json()[0]['pages']
        records = resp.json()[1]
        for p in range(2, pages + 1):
            resp2 = requests.get(url + f'&page={p}', timeout=30)
            records.extend(resp2.json()[1])
        return {r['countryiso3code']: r['value'] for r in records
                if r['value'] is not None and r['countryiso3code']}

    gdppc = _fetch_all(gdppc_ind)
    ppp = _fetch_all(ppp_ind)
    xr = _fetch_all(xr_ind)
    pop = _fetch_all(pop_ind)

    # Price level = PPP / market exchange rate (US = 1 by definition)
    rows = []
    for iso in gdppc:
        if iso in ppp and iso in xr and iso in pop:
            if xr[iso] > 0:
                pl = ppp[iso] / xr[iso]
                rows.append({
                    'iso': iso,
                    'gdppc': gdppc[iso],
                    'price_level': pl,
                    'pop': pop[iso],
                })
    df = pd.DataFrame(rows)

    # Drop aggregates (World Bank aggregates have non-standard codes)
    aggregates = {'WLD', 'EAS', 'ECS', 'LCN', 'MEA', 'NAC', 'SAS', 'SSF',
                  'EMU', 'EUU', 'OED', 'HIC', 'LIC', 'LMC', 'MIC', 'UMC',
                  'LDC', 'ARB', 'CSS', 'PST', 'TSA', 'TSS', 'TEA', 'TEC',
                  'TLA', 'TMN', 'TNA', 'FCS', 'HPC', 'IBD', 'IBT', 'IDA',
                  'IDB', 'IDX', 'PRE', 'SSA', 'SST'}
    df = df[~df['iso'].isin(aggregates)]
    df = df[(df['gdppc'] > 500) & (df['price_level'] > 0.05)]

    # Highlight countries (ISO → French display label)
    highlights = {
        'USA': r"\'{E}tats-Unis", 'CAN': 'Canada', 'CHN': 'Chine',
        'IND': 'Inde', 'JPN': 'Japon', 'BRA': r"Br\'{e}sil",
        'NGA': r"Nig\'{e}ria", 'NOR': r"Norv\`{e}ge", 'CHE': 'Suisse',
    }

    fig, ax = new_figure()

    # Bubble sizes proportional to population
    max_pop = df['pop'].max()
    sizes = 500 * (df['pop'] / max_pop) ** 0.5
    sizes = sizes.clip(lower=12)

    ax.scatter(df['gdppc'], df['price_level'], s=sizes,
               color=palette[0], alpha=0.45, edgecolors='white',
               linewidth=0.5)

    # Highlight specific countries with arrows connecting labels to dots
    for iso, name in highlights.items():
        row = df[df['iso'] == iso]
        if len(row) == 0:
            continue
        row = row.iloc[0]
        sz = 500 * (row['pop'] / max_pop) ** 0.5
        sz = max(sz, 12)
        color = palette[1] if iso == 'CAN' else palette[0]
        ax.scatter(row['gdppc'], row['price_level'], s=sz,
                   color=color, alpha=0.85, edgecolors='white', linewidth=0.5,
                   zorder=5)
        # Offset in points — tuned to avoid overlap at figsize (9, 4.5)
        offsets = {
            'USA': (12, 10), 'CAN': (-50, -14), 'CHN': (14, 10),
            'IND': (12, -14), 'JPN': (-45, 14), 'BRA': (-45, 10),
            'NGA': (-52, -10), 'NOR': (-55, -14), 'CHE': (-65, 10),
        }
        ox, oy = offsets.get(iso, (12, 8))
        ax.annotate(name, xy=(row['gdppc'], row['price_level']),
                    xytext=(ox, oy), textcoords='offset points',
                    fontsize=9, fontweight='bold', color='black',
                    arrowprops=dict(arrowstyle='-', color=palette[7],
                                    lw=0.8, shrinkB=3),
                    zorder=10)

    ax.set_xscale('log')
    ax.set_xlim(1000, 150000)
    ax.set_xticks([1000, 10000, 100000])
    ax.set_xticklabels([r'\$1,000', r'\$10,000', r'\$100,000'], fontsize=12)
    ax.set_xlabel(r"PIB r\'{e}el par habitant (PPA)", fontsize=12)
    ax.set_ylim(0.05, 1.2)
    ax.set_yticks(np.arange(0.2, 1.2 + 0.01, 0.2))
    ax.set_yticklabels([f'{x:.1f}' for x in np.arange(0.2, 1.2 + 0.01, 0.2)],
                       fontsize=12)
    ax.set_ylabel(r'$P\,/\,P^{US}$', fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.grid(True, which='major', axis='x', color='gray', linestyle=':', linewidth=0.5)
    add_source(ax, 'Source: World Bank, WDI (2024)')
    save(fig, 'gdp_per_capita_vs_price_level.png')


# =====================================================================
# Figure: Big Mac Index — dot chart (Economist-style)
# =====================================================================
def big_mac_index():
    print('Figure: Big Mac Index — dot chart')
    url = ('https://raw.githubusercontent.com/TheEconomist/'
           'big-mac-data/master/output-data/big-mac-full-index.csv')
    df = pd.read_csv(url)

    # Two most recent dates
    dates = sorted(df['date'].unique())
    d_latest = dates[-1]       # Jan 2025
    d_prev = dates[-2]         # Jul 2024

    latest = df[df['date'] == d_latest].set_index('iso_a3')
    prev = df[df['date'] == d_prev].set_index('iso_a3')

    # Selected countries (mix of over- and under-valued)
    selected = [
        'CHE', 'NOR', 'EUZ', 'GBR', 'USA', 'CAN', 'SWE',
        'TUR', 'SGP', 'MEX', 'KOR', 'BRA', 'CHN', 'JPN',
        'VNM', 'IND', 'TWN',
    ]

    rows = []
    for iso in selected:
        if iso in latest.index:
            row = {'iso': iso, 'name': latest.loc[iso, 'name'],
                   'pct_latest': latest.loc[iso, 'USD_raw'] * 100,
                   'price_latest': latest.loc[iso, 'dollar_price']}
            if iso in prev.index:
                row['pct_prev'] = prev.loc[iso, 'USD_raw'] * 100
            else:
                row['pct_prev'] = np.nan
            rows.append(row)

    rdf = pd.DataFrame(rows)
    # Sort by latest valuation descending
    rdf = rdf.sort_values('pct_latest', ascending=True).reset_index(drop=True)

    # Translate country names to French for y-axis labels
    rdf['name_fr'] = rdf['name'].apply(_tr_country)

    fig, ax = plt.subplots(figsize=(7, 5.5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    y = np.arange(len(rdf))

    # Previous period dots (lighter)
    ax.scatter(rdf['pct_prev'], y, s=55, color=palette[2], alpha=0.3,
               zorder=3, label='Jul 2024')
    # Latest dots
    colors = [palette[1] if iso == 'CAN' else palette[2] for iso in rdf['iso']]
    ax.scatter(rdf['pct_latest'], y, s=65, color=colors, alpha=0.85,
               zorder=4, label='Jan 2025')

    # Zero line
    ax.axvline(x=0, color='black', linewidth=0.8)

    # Price labels on the right margin
    xmax = rdf['pct_latest'].max()
    price_x = 52
    for i, row in rdf.iterrows():
        idx = rdf.index.get_loc(i)
        ax.text(price_x, idx, f'\\${row["price_latest"]:.2f}',
                va='center', fontsize=9, color=palette[7])

    # Country names on the left (French)
    ax.set_yticks(y)
    ax.set_yticklabels(rdf['name_fr'], fontsize=10)

    # x-axis
    ax.set_xlim(-65, 70)
    xticks = range(-60, 41, 20)
    ax.set_xticks(list(xticks))
    ax.set_xticklabels([f'{x:+d}' if x != 0 else '0' for x in xticks],
                       fontsize=10)
    ax.set_xlabel(r"\'{E}valuation de la monnaie locale face au dollar, \%",
                  fontsize=10)

    # Price column header — right-aligned above the price column
    ax.text(price_x + 8, len(rdf) + 0.3,
            'Prix, \\$', fontsize=9, fontweight='bold',
            va='bottom', ha='center', color=palette[0])

    # Horizontal grid lines
    for yi in y:
        ax.axhline(y=yi, color='gray', linewidth=0.3, alpha=0.5)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', length=0)

    ax.legend(frameon=False, fontsize=9, loc='upper left',
              bbox_to_anchor=(0.0, 1.0), ncol=2,
              markerscale=1.2)
    add_source(ax, r"Source: \textit{The Economist}, Big Mac Index")
    save(fig, 'big_mac_index.png')


# ── Shared helper for GDP growth plots ────────────────────────────────
def _gdp_growth_plot(real_g, nom_g, show_real, fname):
    """Plot nominal (and optionally real) GDP growth for Canada."""
    fig, ax = new_figure()
    ax.plot(nom_g, color=palette[0], linewidth=2, label='Nominal')
    if show_real:
        ax.plot(real_g, color=palette[1], linewidth=2, label=r"R\'{e}el")
    ax.axhline(y=0, color='black', linewidth=0.5)

    first_year = max(real_g.dropna().index[0].year, 1962)
    last_date = min(real_g.dropna().index[-1], nom_g.dropna().index[-1])
    last_year_tick = (last_date.year // 10) * 10
    ax.set_xlim(pd.to_datetime(str(first_year)), last_date)
    tick_years = list(range(first_year, last_year_tick + 11, 10))
    ax.set_xticks([pd.to_datetime(str(y)) for y in tick_years])
    ax.set_xticklabels(tick_years, fontsize=12)

    ymin = -0.10
    ymax = 0.25
    ax.set_ylim(ymin, ymax)
    yticks = np.arange(ymin, ymax + 0.001, 0.05)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{100*x:.0f}' + r'\%' for x in yticks], fontsize=12)
    ax.set_ylabel(r"Croissance du PIB", fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    for start, end in recessions_ca:
        if start >= pd.to_datetime(str(first_year)):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='lower left',
              bbox_to_anchor=(0.0, 0.0))
    add_source(ax, 'Source: OECD (via FRED)')
    save(fig, fname)


# =====================================================================
# Figure: Nominal GDP growth — Canada (alone)
# =====================================================================
def gdp_nominal_canada():
    print('Figure: Nominal GDP growth — Canada')
    real = get_fred_data('NGDPRSAXDCCAQ')
    nom = get_fred_data('NGDPSAXDCCAQ')
    real_g = real.pct_change(4).dropna()
    nom_g = nom.pct_change(4).dropna()
    _gdp_growth_plot(real_g, nom_g, show_real=False, fname='gdp_nominal_canada.png')


# =====================================================================
# Figure: Nominal vs real GDP growth — Canada
# =====================================================================
def gdp_nominal_real_canada():
    print('Figure: Nominal vs real GDP growth — Canada')
    real = get_fred_data('NGDPRSAXDCCAQ')
    nom = get_fred_data('NGDPSAXDCCAQ')
    real_g = real.pct_change(4).dropna()
    nom_g = nom.pct_change(4).dropna()
    _gdp_growth_plot(real_g, nom_g, show_real=True, fname='gdp_nominal_real_canada.png')


# =====================================================================
# Figure: CPI vs GDP deflator inflation — Canada (recent)
# =====================================================================
def inflation_cpi_deflator_canada():
    print('Figure: CPI vs GDP deflator inflation — Canada')
    # CPI (monthly, index 2015=100) -> 12-month % change
    cpi = get_fred_data('CANCPIALLMINMEI')
    cpi_infl = cpi.pct_change(12).dropna()

    # GDP deflator = nominal GDP / real GDP -> 4-quarter % change
    nom_gdp = get_fred_data('NGDPSAXDCCAQ')
    real_gdp = get_fred_data('NGDPRSAXDCCAQ')
    deflator = nom_gdp / real_gdp
    defl_infl = deflator.pct_change(4).dropna()

    fig, ax = new_figure()

    # BoC target band (1-3%)
    ax.axhspan(0.01, 0.03, color=palette[1], alpha=0.12, linewidth=0)
    ax.axhline(y=0.02, color=palette[1], linestyle=':', linewidth=1.5,
               label=r"Cible de 2\% de la BdC")

    ax.plot(cpi_infl, color=palette[0], linewidth=2, label='IPC')
    ax.plot(defl_infl, color=palette[2], linewidth=2,
            label=r"D\'{e}flateur du PIB")

    last_date = min(cpi_infl.dropna().index[-1], defl_infl.dropna().index[-1])
    ax.set_xlim(pd.to_datetime('2016'), last_date)
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(2016, last_date.year + 1)])
    ax.set_xticklabels(range(2016, last_date.year + 1), fontsize=12)

    ax.set_ylim(-0.02, 0.10)
    ax.set_yticks(np.arange(-0.02, 0.10 + 0.001, 0.02))
    ax.set_yticklabels([f'{x:.0f}' + r'\%' for x in np.arange(-2, 10 + 0.1, 2)],
                       fontsize=12)
    ax.set_ylabel(r"Inflation (sur 12 mois)", fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('2016'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, 'Source: OECD (via FRED)')
    save(fig, 'inflation_cpi_deflator_canada.png')


# =====================================================================
# Figure: Headline vs core CPI inflation — Canada
# =====================================================================
def inflation_headline_core_canada():
    print('Figure: Headline vs core CPI inflation — Canada')
    # Headline CPI (monthly, index 2015=100)
    cpi = get_fred_data('CANCPIALLMINMEI')
    headline = cpi.pct_change(12).dropna()

    # Core CPI — OECD definition: all items less food and energy
    core_cpi = get_fred_data('CANCPICORMINMEI')
    core = core_cpi.pct_change(12).dropna()

    fig, ax = new_figure()

    # BoC target band (1-3%)
    ax.axhspan(0.01, 0.03, color=palette[1], alpha=0.12, linewidth=0)
    ax.axhline(y=0.02, color=palette[1], linestyle=':', linewidth=1.5,
               label=r"Cible de 2\% de la BdC")

    ax.plot(headline, color=palette[0], linewidth=2, label='IPC global')
    ax.plot(core, color=palette[2], linewidth=2,
            label=r"IPC de base (hors alim. \& \'{e}nergie)")

    last_date = min(headline.dropna().index[-1], core.dropna().index[-1])
    ax.set_xlim(pd.to_datetime('2016'), last_date)
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(2016, last_date.year + 1)])
    ax.set_xticklabels(range(2016, last_date.year + 1), fontsize=12)

    ax.set_ylim(-0.02, 0.10)
    ax.set_yticks(np.arange(-0.02, 0.10 + 0.001, 0.02))
    ax.set_yticklabels([f'{x:.0f}' + r'\%' for x in np.arange(-2, 10 + 0.1, 2)],
                       fontsize=12)
    ax.set_ylabel(r"Inflation IPC (sur 12 mois)", fontsize=12,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('2016'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, 'Source: OECD (via FRED)')
    save(fig, 'inflation_headline_core_canada.png')


# =====================================================================
# Figure: High-frequency online price indices (Cavallo et al.)
# =====================================================================
def inflation_highfreq_cavallo():
    print('Figure: High-frequency online prices (Cavallo et al.)')
    url = ('https://www.pricinglab.org/files/'
           'Cavallo_Llamas_Vazquez_domestic_imported_trend_line.csv')
    df = pd.read_csv(url)
    df['date'] = pd.to_datetime(df['date'], format='%d%b%Y')
    df = df.sort_values('date').reset_index(drop=True)

    # Convert to cumulative % change from first observation
    dom_pct = (df['index_domestic'] - 1) * 100
    imp_pct = (df['index_imported'] - 1) * 100

    # 14-day rolling average for smoothed lines
    dom_smooth = dom_pct.rolling(14, center=True, min_periods=1).mean()
    imp_smooth = imp_pct.rolling(14, center=True, min_periods=1).mean()

    fig, ax = new_figure()

    # Raw daily data
    ax.plot(df['date'], dom_pct, color=palette[0], linewidth=2,
            label='Biens domestiques')
    ax.plot(df['date'], imp_pct, color=palette[2], linewidth=2,
            label=r"Biens import\'{e}s")

    ax.axhline(y=0, color='black', linewidth=0.5)

    # x-axis: monthly ticks
    first_date = df['date'].min()
    last_date = df['date'].max()
    xticks = pd.date_range(first_date.replace(day=1), last_date, freq='2MS')
    ax.set_xlim(first_date, last_date)
    ax.set_xticks(xticks)
    ax.set_xticklabels([french_date_label(d) for d in xticks], fontsize=11)

    # y-axis
    ymin = int(np.floor(min(dom_pct.min(), imp_pct.min())))
    ymax = int(np.ceil(max(dom_pct.max(), imp_pct.max())))
    ax.set_ylim(ymin, ymax)
    yticks = np.arange(ymin, ymax + 0.1, 1)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{x:+.0f}' + r'\%' for x in yticks], fontsize=12)
    ax.set_ylabel(r"Variation cumul\'{e}e des prix", fontsize=12,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, r'Source: Cavallo, Llamas \& V\'azquez (PricingLab)')
    save(fig, 'inflation_highfreq_cavallo.png')


# =====================================================================
# Figure: HDI vs GDP per capita (cross-country scatter)
# =====================================================================
def hdi_vs_gdp_per_capita():
    print('Figure: HDI vs GDP per capita')
    url = ('https://ourworldindata.org/grapher/'
           'human-development-index-vs-gdp-per-capita.csv'
           '?v=1&csvType=full&useColumnShortNames=true')
    df = pd.read_csv(url, storage_options={'User-Agent': 'OWID fetch/1.0'})

    # Normalise column names (OWID schema changed to lowercase + hdi__sex_total)
    df.columns = df.columns.str.lower()
    if 'hdi__sex_total' in df.columns:
        df = df.rename(columns={'hdi__sex_total': 'hdi'})

    # Most recent year with broad coverage
    df = df[(df.year == 2022)
            & df.hdi.notna()
            & df.ny_gdp_pcap_pp_kd.notna()
            & df.population_historical.notna()
            & df.code.notna()]

    world_pop = df.loc[df.entity == 'World', 'population_historical'].values
    if len(world_pop) > 0:
        df['pop_share'] = df['population_historical'] / world_pop[0]
    else:
        df['pop_share'] = df['population_historical'] / df['population_historical'].max()
    df = df[df.entity != 'World']

    # Highlight countries
    highlights = {
        'USA': r"\'{E}tats-Unis", 'CAN': 'Canada', 'CHN': 'Chine',
        'IND': 'Inde', 'BRA': r"Br\'{e}sil", 'NGA': r"Nig\'{e}ria",
        'NOR': r"Norv\`{e}ge", 'JPN': 'Japon',
    }

    fig, ax = new_figure()

    # Bubble sizes proportional to population
    sizes = 800 * df['pop_share'] ** 0.5
    sizes = sizes.clip(lower=15)

    ax.scatter(df.ny_gdp_pcap_pp_kd, df.hdi, s=sizes,
               color=palette[0], alpha=0.45, edgecolors='white',
               linewidth=0.5)

    # Regression line (log GDP vs HDI)
    log_x = np.log(df.ny_gdp_pcap_pp_kd.values)
    y_vals = df.hdi.values
    slope, intercept = np.polyfit(log_x, y_vals, 1)
    x_line = np.linspace(np.log(1000), np.log(150000), 200)
    ax.plot(np.exp(x_line), slope * x_line + intercept,
            color=palette[1], linewidth=1.5, zorder=1)

    # Correlation coefficient
    corr = np.corrcoef(log_x, y_vals)[0, 1]
    ax.text(0.03, 0.95, f'$\\rho = {corr:.2f}$', fontsize=9, color=palette[7],
            ha='left', va='top', transform=ax.transAxes)

    # Highlight Canada with accent color
    can = df[df.code == 'CAN']
    if len(can) > 0:
        can = can.iloc[0]
        sz = max(800 * can['pop_share'] ** 0.5, 15)
        ax.scatter(can.ny_gdp_pcap_pp_kd, can.hdi, s=sz,
                   color=palette[1], alpha=0.7, edgecolors='white',
                   linewidth=0.5, zorder=5, label='Canada')
    ax.legend(loc='lower right', frameon=False, fontsize=11)

    ax.set_xscale('log')
    ax.set_xlim(1000, 150000)
    ax.set_xticks([1000, 10000, 100000])
    ax.set_xticklabels([r'\$1,000', r'\$10,000', r'\$100,000'], fontsize=12)
    ax.set_xlabel(r"PIB r\'{e}el par habitant (PPA)", fontsize=12)

    ax.set_ylim(0.3, 1.0)
    ax.set_yticks(np.arange(0.3, 1.01, 0.1))
    ax.set_yticklabels([f'{x:.1f}' for x in np.arange(0.3, 1.01, 0.1)],
                       fontsize=12)
    ax.set_ylabel('IDH', fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.grid(True, which='major', axis='x', color='gray',
            linestyle=':', linewidth=0.5)
    add_source(ax, 'Source: Our World in Data (2022)')
    save(fig, 'hdi_vs_gdp_per_capita.png')


# =====================================================================
# Figure: Beyond GDP — Jones and Klenow (2016) welfare metric
# =====================================================================
def beyond_gdp():
    print('Figure: Beyond GDP — Jones and Klenow (2016)')
    url = 'https://web.stanford.edu/~chadj/BeyondGDP500.xls'
    df = pd.read_excel(url, sheet_name='Levels in 2007',
                       skiprows=8, usecols=[0, 1, 2])
    df.columns = ['country', 'welfare', 'y']
    df = df.dropna(subset=['welfare', 'y'])
    df['welfare'] = df['welfare'] / 100
    df['y'] = df['y'] / 100

    # Fetch 2007 population from World Bank for bubble sizing
    pop_ind = 'SP.POP.TOTL'
    pop_url = (f'https://api.worldbank.org/v2/country/all/'
               f'indicator/{pop_ind}?format=json&per_page=500&date=2007:2007')
    resp = requests.get(pop_url, timeout=30)
    resp.raise_for_status()
    pages = resp.json()[0]['pages']
    records = resp.json()[1]
    for p in range(2, pages + 1):
        resp2 = requests.get(pop_url + f'&page={p}', timeout=30)
        records.extend(resp2.json()[1])
    pop_by_name = {}
    for r in records:
        if r['value'] is not None and r['country']['value']:
            pop_by_name[r['country']['value']] = r['value']

    # Match population to JK country names (fuzzy match common differences)
    name_map = {
        'Korea, Rep.': 'Korea, Republic of',
        'Iran, Islamic Rep.': 'Iran, Islamic Republic of',
        'Egypt, Arab Rep.': 'Egypt',
        'Venezuela, RB': 'Venezuela',
        'Russian Federation': 'Russia',
        'Slovak Republic': 'Slovakia',
        'Kyrgyz Republic': 'Kyrgyzstan',
        'Congo, Dem. Rep.': 'Congo, Democratic Republic of',
        'Cote d\'Ivoire': "C\u00f4te d'Ivoire",
    }
    df['pop'] = df['country'].apply(
        lambda c: pop_by_name.get(c.strip())
                  or pop_by_name.get(name_map.get(c.strip(), ''))
                  or None)
    # Fill missing with a small default so they still appear
    df['pop'] = df['pop'].fillna(df['pop'].min())

    fig, ax = new_figure()

    # 45-degree line
    ax.plot([1 / 100, 2.7], [1 / 100, 2.7], color=palette[1],
            linestyle='-', linewidth=1.5, zorder=1)

    # Bubble sizes proportional to population
    max_pop = df['pop'].max()
    sizes = 500 * (df['pop'] / max_pop) ** 0.5
    sizes = sizes.clip(lower=10)

    ax.scatter(df.y, df.welfare, s=sizes, color=palette[0], alpha=0.45,
               edgecolors='white', linewidth=0.5, zorder=3)

    # Correlation coefficient (log-log)
    corr = np.corrcoef(np.log(df.y.values), np.log(df.welfare.values))[0, 1]
    ax.text(0.03, 0.95, f'$\\rho = {corr:.2f}$', fontsize=9, color=palette[7],
            ha='left', va='top', transform=ax.transAxes)

    # Highlight Canada with accent color
    can = df[df['country'].str.strip() == 'Canada']
    if len(can) > 0:
        can = can.iloc[0]
        sz = max(500 * (can['pop'] / max_pop) ** 0.5, 10)
        ax.scatter(can.y, can.welfare, s=sz, color=palette[1], alpha=0.7,
                   edgecolors='white', linewidth=0.5, zorder=5, label='Canada')
    ax.legend(loc='lower right', frameon=False, fontsize=11)

    ax.set_xscale('log', base=2)
    ax.set_xlim(1 / 100, 2.7)
    xticks = [1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2]
    ax.set_xticks(xticks)
    ax.set_xticklabels(['1/64', '1/32', '1/16', '1/8', '1/4', '1/2',
                         '1', '2'], fontsize=12)
    ax.set_xlabel(r"PIB r\'{e}el par habitant (relatif aux \'{E}.-U.)",
                  fontsize=12)

    ax.set_yscale('log', base=2)
    ax.set_ylim(1 / 100, 2)
    yticks = [1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2]
    ax.set_yticks(yticks)
    ax.set_yticklabels(['1/64', '1/32', '1/16', '1/8', '1/4', '1/2',
                         '1', '2'], fontsize=12)
    ax.set_ylabel(r'$\lambda$', fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.grid(True, which='major', axis='x', color='gray',
            linestyle=':', linewidth=0.5)
    add_source(ax, 'Source: Jones and Klenow (2016)')
    save(fig, 'beyond_gdp.png')


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 1 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        can_unemployment,
        can_inflation_longrun,
        policy_rates,
        canada_inflation_recent,
        canada_employment_exports,
        hockey_stick_world,
        us_tariff_rate,
        gdp_decomposition_canada,
        gdp_decomposition_4countries,
        consumption_share_gdp,
        investment_share_gdp,
        government_share_gdp,
        trade_share_gdp,
        gdp_ppp_time_series,
        gdp_per_capita_vs_price_level,
        big_mac_index,
        gdp_canada_usa,
        gdp_per_capita_canada_usa,
        gdp_vs_gdp_per_capita,
        gdp_nominal_canada,
        gdp_nominal_real_canada,
        inflation_cpi_deflator_canada,
        inflation_headline_core_canada,
        inflation_highfreq_cavallo,
        hdi_vs_gdp_per_capita,
        beyond_gdp,
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
    else:
        print('\nDone \u2014 all figures generated.')
