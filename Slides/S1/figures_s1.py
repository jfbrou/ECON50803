"""
ECON50803 — Session 1: Figure Generation
=========================================

Generates the six narrative-arc figures shown after the "Where are we now?"
headlines slide:
    1. can_unemployment.png        — "After a very unusual recession…"
    2. can_inflation_longrun.png   — "An old enemy back from the dead…"
    3. policy_rates.png            — "A forceful response…"
    4. canada_inflation_recent.png — "A return to normal…"
    5. canada_employment_exports.png — "An uncertain future…"
    6. hockey_stick_world.png      — "What about long-run growth?"

Canadian data is used whenever possible. Style conventions follow
ECON20852/Programs/figures.py, adapted to the ECON50803 Beamer template
(Fira Sans, HEC colour palette).

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
    print(f'  ✓ {name}')

def tick_ceil(value, step):
    """Round up value to the next multiple of step."""
    return int(np.ceil(value / step)) * step


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
    ax.set_ylim(0, 16)
    ax.set_yticks(range(0, 16 + 1, 2))
    ax.set_yticklabels([str(x) + r'\%' for x in range(0, 16 + 1, 2)], fontsize=12)
    ax.set_ylabel('Unemployment rate', fontsize=12, rotation=0, ha='left')
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
               label='BoC 2\\% target (since 1991)')

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
    ax.set_ylim(-0.03, 0.14)
    ax.set_yticks(np.arange(-0.02, 0.14 + 0.001, 0.02))
    ax.set_yticklabels([f'{x:.0f}' + r'\%' for x in np.arange(-2, 14 + 0.1, 2)],
                       fontsize=12)
    ax.set_ylabel('CPI inflation (12-month)', fontsize=12, rotation=0, ha='left')
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

    ax.plot(fed, color=palette[0], linewidth=2, label='Fed funds rate (US)')
    ax.plot(boc, color=palette[1], linewidth=2, label='Overnight rate (Canada)')

    last_year = max(fed.dropna().index[-1].year, boc.dropna().index[-1].year)
    xlim_end = tick_ceil(last_year, 2)
    ax.set_xlim(pd.to_datetime('2006'), pd.to_datetime(str(xlim_end)))
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(2006, xlim_end + 1, 2)])
    ax.set_xticklabels(range(2006, xlim_end + 1, 2), fontsize=12)
    ax.set_ylim(0, 6)
    ax.set_yticks(range(0, 6 + 1, 1))
    ax.set_yticklabels([str(x) + r'\%' for x in range(0, 6 + 1, 1)], fontsize=12)
    ax.set_ylabel('Policy rate', fontsize=12, rotation=0, ha='left')
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

    # BoC target band (1–3%)
    ax.axhspan(0.01, 0.03, color=palette[1], alpha=0.12, linewidth=0)
    ax.axhline(y=0.02, color=palette[1], linestyle=':', linewidth=1.5,
               label='BoC 2\\% target')

    ax.plot(infl, color=palette[0], linewidth=2, label='CPI inflation')

    # Plot expectations (only future portion, from last actual data onward)
    last_actual = infl.dropna().index[-1]
    future_mask = exp_dates > last_actual
    if future_mask.any():
        # Connect from last actual point to first expectation point
        bridge_dates = pd.Index([last_actual]).append(exp_dates[future_mask])
        bridge_vals = np.concatenate([[infl.loc[last_actual]],
                                      exp_vals[future_mask]])
        ax.plot(bridge_dates, bridge_vals, color=palette[7], linewidth=2,
                linestyle=':', label='Consumer expectations (1-yr ahead)')

    # Annotation for 2022 peak
    peak_date = infl.loc['2021-01-01':'2023-12-31'].idxmax()
    peak_val = infl.loc[peak_date]
    ax.annotate(f'{100*peak_val:.1f}\\%',
                xy=(peak_date, peak_val),
                xytext=(peak_date + pd.DateOffset(months=18), peak_val + 0.005),
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
    ax.set_ylabel('CPI inflation (12-month)', fontsize=12, rotation=0, ha='left')
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
                label='High US export dependence')
    if len(low_matched) > 0:
        low_idx = get_index(low_matched)
        ax.plot(low_idx, color=palette[0], linewidth=2,
                label='Limited US export dependence')
    if len(total) > 0:
        ax.plot(total, color=palette[1], linewidth=2,
                label='All sectors')

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
    ax.set_xticklabels([d.strftime('%b\n%Y') for d in xtick_dates], fontsize=11)
    ax.set_ylabel('Employment index (Jan 2023 = 100)', fontsize=12,
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
    # Download Maddison-based GDP per capita from Our World in Data (GitHub)
    url = ('https://raw.githubusercontent.com/owid/owid-datasets/master/'
           'datasets/Maddison%20Project%20Database%202020%20'
           '(Bolt%20and%20van%20Zanden%20(2020))/'
           'Maddison%20Project%20Database%202020%20'
           '(Bolt%20and%20van%20Zanden%20(2020)).csv')
    df = pd.read_csv(url)

    fig, ax = new_figure()

    countries = {
        'United States': palette[0],
        'United Kingdom': palette[1],
        'Canada': palette[2],
        'France': palette[3],
    }

    max_year = 0
    for country, color in countries.items():
        sub = df.loc[(df['Entity'] == country) & df['GDP per capita'].notna()]
        ax.plot(sub['Year'], sub['GDP per capita'], color=color,
                label=country, linewidth=2)
        max_year = max(max_year, sub['Year'].max())

    ax.set_xlim(0, max_year + 5)
    ax.set_xticks(range(0, max_year + 1, 250))
    ax.set_xticklabels(range(0, max_year + 1, 250), fontsize=12)
    ax.set_ylim(0, 70000)
    ax.set_yticks(range(0, 70000 + 1, 10000))
    ax.set_yticklabels([r'\$' + str(x) + 'K' for x in range(0, 70 + 1, 10)],
                       fontsize=12)
    ax.set_ylabel('Real GDP per capita', fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left',
              bbox_to_anchor=(0.02, 1.0))
    add_source(ax, 'Source: Maddison Project Database (via Our World in Data)')
    save(fig, 'hockey_stick_world.png')


# =====================================================================
# Figure 7: US effective tariff rate since 1790
# =====================================================================
def us_tariff_rate():
    print('Figure 7: US effective tariff rate since 1790')
    # Data from Yale Budget Lab "State of U.S. Tariffs: January 19, 2026"
    xlsx = os.path.join(Path(__file__).resolve().parent, 'tariff_data.xlsx')
    df = pd.read_excel(xlsx, sheet_name='F1', header=None,
                       skiprows=5,  # skip title/subtitle/source/blank/header
                       names=['Year', 'ETR', 'proj_post', 'cur_post',
                              'proj_pre', 'cur_pre'])
    # Keep only rows with a valid year
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)

    # Historical series (1790–2024)
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

    # Annotations — short arrows
    ax.annotate(f'{etr_2025_overall:.1f}\\%  overall',
                xy=(2025, etr_2025_overall),
                xytext=(2005, 22),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))
    ax.annotate(f'{etr_2025_canada:.1f}\\%  on Canadian goods',
                xy=(2025, etr_2025_canada),
                xytext=(1990, 12),
                fontsize=11, color=palette[1], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[1], lw=1.5))

    # Key historical annotations (subtle, in gray)
    etr_1932 = hist.loc[hist['Year'] == 1932, 'ETR'].iloc[0]
    ax.annotate('Smoot-Hawley' + '\n' + f'({etr_1932:.0f}\\%)',
                xy=(1932, etr_1932),
                xytext=(1940, 23),
                fontsize=9, color=palette[7], ha='center',
                arrowprops=dict(arrowstyle='->', color=palette[7],
                                lw=1, alpha=0.6))

    ax.set_xlim(1930, 2027)
    ax.set_xticks(range(1930, 2020 + 1, 10))
    ax.set_xticklabels(range(1930, 2020 + 1, 10), fontsize=12)
    ax.set_ylim(0, 25)
    ax.set_yticks(range(0, 25 + 1, 5))
    ax.set_yticklabels([str(x) + r'\%' for x in range(0, 25 + 1, 5)],
                       fontsize=12)
    ax.set_ylabel('US effective tariff rate', fontsize=12, rotation=0, ha='left')
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
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'gdp_decomposition_canada.png'),
                transparent=True, dpi=300)
    plt.close(fig)
    print('  ✓ gdp_decomposition_canada.png')


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
        'USA': 'United States',
        'CHN': 'China',
        'BRA': 'Brazil',
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
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.8))
    fig.patch.set_alpha(0.0)

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

    fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.02, wspace=0.3)
    fig.text(0.99, 0.005, f'Source: World Bank ({comps["year"]})',
             fontsize=8, ha='right', va='bottom')
    fig.savefig(os.path.join(FIGURES_DIR, 'gdp_decomposition_4countries.png'),
                transparent=True, dpi=300, bbox_inches='tight', pad_inches=0.01)
    plt.close(fig)
    print('  ✓ gdp_decomposition_4countries.png')


# =====================================================================
# Figure 9: Consumption share of GDP
# =====================================================================
def consumption_share_gdp():
    print('Figure 8: Consumption share of GDP')
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


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 1 figures...')
    print(f'Output: {FIGURES_DIR}\n')
    can_unemployment()
    can_inflation_longrun()
    policy_rates()
    canada_inflation_recent()
    canada_employment_exports()
    hockey_stick_world()
    us_tariff_rate()
    gdp_decomposition_canada()
    gdp_decomposition_4countries()
    consumption_share_gdp()
    investment_share_gdp()
    government_share_gdp()
    trade_share_gdp()
    print('\nDone.')
