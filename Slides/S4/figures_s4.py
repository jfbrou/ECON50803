"""
ECON50803 — Session 4 : Figure Generation
============================================

Generates all matplotlib figures for Session 4 slides (business cycles,
AD-AS model, recessions). All figure labels, axis titles, legends, and
annotations are in French.

Run from Slides/S4/:
    python3 figures_s4.py
"""

import os
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import requests
import dotenv

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
    (datetime(1960, 4, 1), datetime(1961, 2, 1)),
    (datetime(1969, 12, 1), datetime(1970, 11, 1)),
    (datetime(1973, 11, 1), datetime(1975, 3, 1)),
    (datetime(1980, 1, 1), datetime(1980, 7, 1)),
    (datetime(1981, 7, 1), datetime(1982, 11, 1)),
    (datetime(1990, 7, 1), datetime(1991, 3, 1)),
    (datetime(2001, 3, 1), datetime(2001, 11, 1)),
    (datetime(2007, 12, 1), datetime(2009, 6, 1)),
    (datetime(2020, 2, 1), datetime(2020, 4, 1)),
]


# ── FRED helper ─────────────────────────────────────────────────────────
def get_fred_data(series_id, frequency=None, aggregation_method=None,
                  observation_start=None, observation_end=None):
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
    if observation_start is not None:
        params['observation_start'] = observation_start
    if observation_end is not None:
        params['observation_end'] = observation_end

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()['observations']

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df.set_index('date')['value']


# ── Shared plot helpers ─────────────────────────────────────────────────
def new_figure(w=8, h=4):
    fig, ax = plt.subplots(figsize=(w, h))
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


# =====================================================================
# Figure 1: US Real GDP with NBER recession shading (1960–2025)
# =====================================================================
def us_gdp_recessions():
    print('Figure 1: US real GDP with recessions')

    gdp = get_fred_data('GDPC1', observation_start='1960-01-01')

    fig, ax = new_figure(9, 4.5)

    ax.plot(gdp.index, gdp.values, color=palette[0], linewidth=2)

    # Recession shading
    for start, end in recessions_us:
        ax.axvspan(start, end, color='grey', alpha=0.25, linewidth=0)

    ax.set_yscale('log')
    ax.set_xlim(pd.Timestamp('1960-01-01'), gdp.index.max())
    ax.set_ylabel(r"Milliards USD (2017)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Custom log ticks
    ax.set_yticks([3000, 5000, 8000, 12000, 18000, 23000])
    ax.set_yticklabels([r'3\,000', r'5\,000', r'8\,000',
                        r'12\,000', r'18\,000', r'23\,000'], fontsize=10)
    ax.minorticks_off()

    style_axes(ax)
    ax.grid(True, which='major', axis='y', color='gray',
            linestyle=':', linewidth=0.5)

    # Recession label
    ax.text(0.02, 0.95, r'\textit{Zones gris\'{e}es = r\'{e}cessions (NBER)}',
            fontsize=9, color=palette[7], transform=ax.transAxes,
            va='top')

    add_source(ax, r"Source: FRED (GDPC1) --- PIB r\'{e}el des \'{E}tats-Unis, \'{e}chelle logarithmique")
    save(fig, 'us_gdp_recessions.png')


# =====================================================================
# Figure 2: US output gap (%)
# =====================================================================
def output_gap_us():
    print('Figure 2: US output gap')

    gdp = get_fred_data('GDPC1', observation_start='1960-01-01')
    pot = get_fred_data('GDPPOT', observation_start='1960-01-01')

    # Align on common dates
    common = gdp.index.intersection(pot.index)
    gdp = gdp.loc[common]
    pot = pot.loc[common]

    gap = ((gdp - pot) / pot) * 100

    fig, ax = new_figure(9, 4.5)

    ax.fill_between(gap.index, gap.values, 0,
                    where=gap.values >= 0,
                    color=palette[2], alpha=0.3, linewidth=0)
    ax.fill_between(gap.index, gap.values, 0,
                    where=gap.values < 0,
                    color=palette[0], alpha=0.3, linewidth=0)
    ax.plot(gap.index, gap.values, color=palette[0], linewidth=1.5)
    ax.axhline(0, color='black', linewidth=0.8)

    ax.set_xlim(pd.Timestamp('1960-01-01'), gap.index.max())
    ax.set_ylabel(r"\'{E}cart de production (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(-10, 6)

    # Annotations
    ax.annotate('Surchauffe',
                xy=(pd.Timestamp('2000-01-01'), 2.5),
                fontsize=10, color=palette[2], fontweight='bold')
    ax.annotate(r'R\'{e}cession',
                xy=(pd.Timestamp('2009-06-01'), -6),
                fontsize=10, color=palette[0], fontweight='bold')

    style_axes(ax)
    add_source(ax, r"Source: FRED (GDPC1, GDPPOT) --- \'{E}tats-Unis")
    save(fig, 'output_gap_us.png')


# =====================================================================
# Figure 3: Employment recovery across recessions
# =====================================================================
def employment_recovery():
    print('Figure 3: Employment recovery across recessions')

    payems = get_fred_data('PAYEMS', observation_start='1970-01-01')

    # Define recession troughs (month of lowest employment near NBER end)
    troughs = {
        '1981': pd.Timestamp('1982-12-01'),
        '1990': pd.Timestamp('1991-06-01'),
        '2001': pd.Timestamp('2002-08-01'),
        '2008': pd.Timestamp('2010-02-01'),
        '2020': pd.Timestamp('2020-04-01'),
    }

    colors = {
        '1981': palette[7],
        '1990': palette[4],
        '2001': palette[6],
        '2008': palette[0],
        '2020': palette[2],
    }

    fig, ax = new_figure(9, 4.5)

    for label, trough in troughs.items():
        base = payems.loc[trough]
        # Show 12 months before to 60 months after trough
        start = trough - pd.DateOffset(months=12)
        end = trough + pd.DateOffset(months=60)
        subset = payems.loc[start:end]
        months = ((subset.index - trough).days / 30.44).astype(int)
        indexed = (subset / base) * 100
        lw = 2.5 if label in ('2008', '2020') else 1.5
        ax.plot(months, indexed.values, color=colors[label],
                linewidth=lw, label=label)

    ax.axhline(100, color='black', linewidth=0.8, linestyle='--')
    ax.axvline(0, color='gray', linewidth=0.5, linestyle=':')

    ax.set_xlim(-12, 60)
    ax.set_xlabel(r"Mois depuis le creux", fontsize=11)
    ax.set_ylabel(r"Emploi (creux = 100)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='lower right',
              title=r'\textbf{R\'{e}cession}', title_fontsize=10)
    add_source(ax, r"Source: FRED (PAYEMS) --- Emplois non agricoles, \'{E}tats-Unis")
    save(fig, 'employment_recovery.png')


# =====================================================================
# Figure 4: CPI inflation around the 2020 recession (2019–2024)
# =====================================================================
def us_recession_inflation():
    print('Figure 4: US recession & inflation (2019–2024)')

    cpi = get_fred_data('CPIAUCSL', observation_start='2018-01-01',
                        observation_end='2024-12-31')

    # Year-over-year inflation
    inflation = cpi.pct_change(12) * 100
    inflation = inflation.dropna()
    inflation = inflation.loc['2019-01-01':'2024-12-31']

    fig, ax = new_figure(9, 4.5)

    ax.plot(inflation.index, inflation.values, color=palette[0], linewidth=2.5)
    ax.axhline(2, color=palette[1], linewidth=1.5, linestyle='--',
               label=r"Cible d'inflation (2\,\%)")

    # Recession shading
    ax.axvspan(pd.Timestamp('2020-02-01'), pd.Timestamp('2020-04-01'),
               color='grey', alpha=0.25, linewidth=0)

    # Annotation: peak
    peak_date = inflation.idxmax()
    peak_val = inflation.max()
    ax.annotate(f'{peak_val:.1f}' + r'\,\%',
                xy=(peak_date, peak_val),
                xytext=(peak_date - pd.DateOffset(months=6), peak_val + 0.8),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    ax.set_xlim(pd.Timestamp('2019-01-01'), pd.Timestamp('2024-12-01'))
    ax.set_ylabel(r"Inflation IPC (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(-1, 10)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right')
    add_source(ax, r"Source: FRED (CPIAUCSL) --- Inflation sur 12 mois, \'{E}tats-Unis")
    save(fig, 'us_recession_inflation.png')


# =====================================================================
# Figure 5: Oil price history (1970–2026)
# =====================================================================
def oil_price_history():
    print('Figure 5: Oil price history (Brent)')

    # Brent crude: DCOILBRENTEU (daily, from May 1987)
    # For earlier data, use WTI: DCOILWTICO
    brent = get_fred_data('DCOILBRENTEU', frequency='m',
                          aggregation_method='avg')
    wti = get_fred_data('DCOILWTICO', frequency='m',
                        aggregation_method='avg',
                        observation_start='1970-01-01',
                        observation_end='1987-06-01')

    # Combine: WTI for pre-1987, Brent after
    combined = pd.concat([wti.loc[:'1987-04-01'], brent.loc['1987-05-01':]])
    combined = combined.dropna()

    fig, ax = new_figure(9, 4.5)

    ax.plot(combined.index, combined.values, color=palette[0], linewidth=1.5)
    ax.fill_between(combined.index, combined.values, 0,
                    color=palette[0], alpha=0.1)

    # Key event annotations
    events = [
        (pd.Timestamp('1974-01-01'), 12, 'Embargo\nOPEP\n1973', -60, 50),
        (pd.Timestamp('1979-06-01'), 35, r'R\'{e}volution' + '\niranienne\n1979', -60, 30),
        (pd.Timestamp('2008-07-01'), 133, 'Bulle\n2008', -50, -30),
        (pd.Timestamp('2020-04-01'), 20, 'COVID\n2020', 20, 30),
        (pd.Timestamp('2026-03-01'), 82, 'Iran/\nOrmuz\n2026', -60, -20),
    ]

    for date, price, label, dx, dy in events:
        if date <= combined.index.max():
            ax.annotate(label,
                        xy=(date, price),
                        xytext=(dx, dy), textcoords='offset points',
                        fontsize=8, color=palette[2], fontweight='bold',
                        ha='center',
                        arrowprops=dict(arrowstyle='->', color=palette[2],
                                        lw=1.2))

    ax.set_xlim(pd.Timestamp('1970-01-01'), pd.Timestamp('2026-06-01'))
    ax.set_ylabel(r"USD / baril", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 160)

    style_axes(ax)
    add_source(ax, r"Source: FRED (DCOILWTICO, DCOILBRENTEU) --- Prix du p\'{e}trole brut")
    save(fig, 'oil_price_history.png')


# =====================================================================
# Figure 6: Oil price close-up Feb–Mar 2026
# =====================================================================
def oil_price_2026():
    print('Figure 6: Oil price close-up (2026)')

    brent = get_fred_data('DCOILBRENTEU',
                          observation_start='2026-01-01',
                          observation_end='2026-03-31')
    brent = brent.dropna()

    if len(brent) < 5:
        # Fallback: use broader date range if 2026 data not yet available
        print('  ! 2026 data limited, using 2025-Q4 to 2026-Q1')
        brent = get_fred_data('DCOILBRENTEU',
                              observation_start='2025-10-01',
                              observation_end='2026-03-31')
        brent = brent.dropna()

    if len(brent) == 0:
        print('  ! No Brent data available for 2026. Skipping figure.')
        return

    fig, ax = new_figure(9, 4.5)

    ax.plot(brent.index, brent.values, color=palette[0], linewidth=2)
    ax.fill_between(brent.index, brent.values, brent.values.min() - 2,
                    color=palette[0], alpha=0.1)

    # Mark Feb 28 if it exists
    feb28 = pd.Timestamp('2026-02-28')
    if feb28 in brent.index or (brent.index >= feb28).any():
        closest = brent.index[brent.index >= feb28]
        if len(closest) > 0:
            mark_date = closest[0]
            mark_val = brent.loc[mark_date]
            ax.axvline(mark_date, color=palette[2], linewidth=1.5,
                       linestyle='--', alpha=0.7)
            ax.annotate(r'\textit{Op\'{e}ration Epic Fury}',
                        xy=(mark_date, mark_val),
                        xytext=(30, 20), textcoords='offset points',
                        fontsize=9, color=palette[2], fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color=palette[2],
                                        lw=1.2))

    ax.set_ylabel(r"Brent (USD / baril)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Source: FRED (DCOILBRENTEU) --- Prix du Brent, quotidien")
    save(fig, 'oil_price_2026.png')


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('ECON50803 S4 — Generating figures...\n')
    us_gdp_recessions()
    output_gap_us()
    employment_recovery()
    us_recession_inflation()
    oil_price_history()
    oil_price_2026()
    print('\nDone.')
