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
# Figure 5: US quarterly GDP growth (annualized)
# =====================================================================
def us_gdp_growth():
    print('Figure 5: US quarterly GDP growth')

    gdp = get_fred_data('GDPC1', observation_start='1960-01-01')

    # Quarterly annualized growth rate
    growth = ((gdp / gdp.shift(1)) ** 4 - 1) * 100
    growth = growth.dropna()

    fig, ax = new_figure(9, 4.5)

    ax.fill_between(growth.index, growth.values, 0,
                    where=growth.values >= 0,
                    color=palette[1], alpha=0.4, linewidth=0)
    ax.fill_between(growth.index, growth.values, 0,
                    where=growth.values < 0,
                    color=palette[2], alpha=0.4, linewidth=0)
    ax.plot(growth.index, growth.values, color=palette[0], linewidth=0.8)
    ax.axhline(0, color='black', linewidth=0.8)

    ax.set_xlim(pd.Timestamp('1960-01-01'), growth.index.max())
    ax.set_ylabel(r"Croissance (\% annualis\'{e})", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(-35, 35)

    # Annotate COVID crash
    ax.annotate(r'$-$31\,\%',
                xy=(pd.Timestamp('2020-04-01'), -31),
                xytext=(-50, -15), textcoords='offset points',
                fontsize=10, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.2))

    style_axes(ax)
    add_source(ax, r"Source: FRED (GDPC1) --- Taux de croissance trimestriel annualis\'{e}")
    save(fig, 'us_gdp_growth.png')


# ── Canada GDP + HP trend helper ──────────────────────────────────────
def _get_canada_gdp_and_trend():
    """Fetch Canada real GDP and compute HP-filtered trend."""
    gdp = get_fred_data('NGDPRSAXDCCAQ', observation_start='1980-01-01')
    if len(gdp) == 0:
        gdp = get_fred_data('NAEXKP01CAQ189S', observation_start='1990-01-01')
    if len(gdp) == 0:
        return None, None

    # HP filter (lambda = 1600 for quarterly data)
    T = len(gdp)
    lam = 1600
    I = np.eye(T)
    D = np.zeros((T - 2, T))
    for i in range(T - 2):
        D[i, i] = 1
        D[i, i+1] = -2
        D[i, i+2] = 1
    trend = np.linalg.solve(I + lam * D.T @ D, gdp.values)
    return gdp, trend


# Canadian recession dates
can_recessions = [
    (datetime(1981, 6, 1), datetime(1982, 10, 1)),
    (datetime(1990, 3, 1), datetime(1992, 4, 1)),
    (datetime(2008, 10, 1), datetime(2009, 5, 1)),
    (datetime(2020, 2, 1), datetime(2020, 4, 1)),
]


# =====================================================================
# Figure 6a: Canada real GDP vs potential (Bank of Canada output gap)
# =====================================================================
def canada_gdp_potential():
    """Canada real GDP and potential GDP (derived from BoC output gap)."""
    print('Figure 6a: Canada real vs potential GDP')

    # ── 1. Real GDP from FRED ────────────────────────────────────────
    gdp = get_fred_data('NGDPRSAXDCCAQ', observation_start='1980-01-01')
    if len(gdp) == 0:
        print('  ! No Canada GDP data. Skipping.')
        return

    # ── 2. Output gap from Bank of Canada Valet API (CSV) ────────────
    url = ('https://www.bankofcanada.ca/valet/observations/'
           'INDINF_OUTGAPMPR_Q/csv')
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    # Skip metadata lines (lines starting with non-date content)
    import io
    lines = resp.text.splitlines()
    data_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('"date"') or line.strip().startswith('date'):
            data_start = i
            break
    if data_start is None:
        print('  ! Could not parse BoC CSV. Skipping.')
        return

    csv_text = '\n'.join(lines[data_start:])
    gap_df = pd.read_csv(io.StringIO(csv_text))
    gap_df.columns = [c.strip().strip('"') for c in gap_df.columns]

    # Parse quarter dates (e.g. "1981Q1" → Timestamp)
    gap_df['date'] = pd.PeriodIndex(gap_df['date'], freq='Q').to_timestamp()
    gap_df['gap'] = pd.to_numeric(gap_df['INDINF_OUTGAPMPR_Q'],
                                  errors='coerce')
    gap_df = gap_df.dropna(subset=['gap']).set_index('date').sort_index()

    # ── 3. Align on common dates ─────────────────────────────────────
    common = gdp.index.intersection(gap_df.index)
    gdp = gdp.loc[common]
    gap = gap_df.loc[common, 'gap']

    # Potential = Y / (1 + gap/100)
    potential = gdp / (1 + gap / 100)

    # ── 4. Plot ──────────────────────────────────────────────────────
    fig, ax = new_figure(9, 4.5)

    # Recession shading
    for start, end in can_recessions:
        if start >= gdp.index.min():
            ax.axvspan(start, end, color='grey', alpha=0.15, linewidth=0)

    ax.plot(gdp.index, gdp.values, color=palette[0], linewidth=2,
            label=r"PIB r\'{e}el ($Y$)")
    ax.plot(potential.index, potential.values, color=palette[1], linewidth=2,
            label=r"PIB potentiel ($Y^{\mathrm{POT}}$)")

    # ── 5. Axis formatting ───────────────────────────────────────────
    ax.set_xlim(gdp.index.min(), gdp.index.max())
    ax.set_ylim(None, 650_000)
    ax.set_ylabel(r"Millions CAD (2012)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Y-axis: display as e.g. 300K, 400K, …, 650K
    from matplotlib.ticker import FuncFormatter, MultipleLocator
    ax.yaxis.set_major_locator(MultipleLocator(50_000))
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, _: f'{x/1000:.0f}K'))

    # X-axis: clean round ticks every 4 years
    first_year = gdp.index.min().year
    last_year = gdp.index.max().year
    start_tick = first_year + (4 - first_year % 4) % 4  # next multiple of 4
    xticks = list(range(start_tick, last_year + 1, 4))
    ax.set_xticks([pd.Timestamp(f'{y}-01-01') for y in xticks])
    ax.set_xticklabels([str(y) for y in xticks], fontsize=10)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10)
    add_source(ax, r"Source: FRED, Banque du Canada")
    save(fig, 'canada_gdp_potential.png')


# =====================================================================
# Figure 6b: Canada output gap
# =====================================================================
def output_gap_canada():
    """Canada output gap using Bank of Canada official estimates."""
    print('Figure 6b: Canada output gap')

    # ── Fetch output gap from Bank of Canada Valet API (CSV) ──────────
    import io
    url = ('https://www.bankofcanada.ca/valet/observations/'
           'INDINF_OUTGAPMPR_Q/csv')
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    lines = resp.text.splitlines()
    data_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('"date"') or line.strip().startswith('date'):
            data_start = i
            break
    if data_start is None:
        print('  ! Could not parse BoC CSV. Skipping.')
        return

    csv_text = '\n'.join(lines[data_start:])
    gap_df = pd.read_csv(io.StringIO(csv_text))
    gap_df.columns = [c.strip().strip('"') for c in gap_df.columns]

    gap_df['date'] = pd.PeriodIndex(gap_df['date'], freq='Q').to_timestamp()
    gap_df['gap'] = pd.to_numeric(gap_df['INDINF_OUTGAPMPR_Q'],
                                  errors='coerce')
    gap_df = gap_df.dropna(subset=['gap']).set_index('date').sort_index()
    gap = gap_df['gap']

    # ── Interpolate to daily for gap-free shading at zero crossings ──
    daily_idx = pd.date_range(gap.index.min(), gap.index.max(), freq='D')
    gap_daily = gap.reindex(daily_idx).interpolate(method='linear')

    # ── Plot ──────────────────────────────────────────────────────────
    fig, ax = new_figure(9, 4.5)

    # Recession shading
    for start, end in can_recessions:
        if start >= gap.index.min():
            ax.axvspan(start, end, color='grey', alpha=0.15, linewidth=0)

    # Shading with interpolation to avoid gaps at zero crossings
    ax.fill_between(gap_daily.index, gap_daily.values, 0,
                    where=gap_daily.values >= 0, interpolate=True,
                    color=palette[1], alpha=0.3, linewidth=0)
    ax.fill_between(gap_daily.index, gap_daily.values, 0,
                    where=gap_daily.values < 0, interpolate=True,
                    color=palette[2], alpha=0.3, linewidth=0)
    ax.plot(gap.index, gap.values, color=palette[0], linewidth=0.9)
    ax.axhline(0, color='black', linewidth=0.5)

    # ── Axis formatting ───────────────────────────────────────────────
    ax.set_xlim(gap.index.min(), gap.index.max())
    ax.set_ylim(None, 4)
    ax.set_ylabel(r"\'{E}cart de production (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Y-axis: explicit ticks with text-mode LaTeX for Fira Sans font
    ax.set_yticks([-6, -4, -2, 0, 2, 4])
    ax.set_yticklabels([r'$-$6', r'$-$4', r'$-$2', r'0', r'2', r'4'])

    # X-axis: clean round ticks every 5 years
    first_year = gap.index.min().year
    last_year = gap.index.max().year
    start_tick = first_year + (5 - first_year % 5) % 5
    xticks = list(range(start_tick, last_year + 1, 5))
    ax.set_xticks([pd.Timestamp(f'{y}-01-01') for y in xticks])
    ax.set_xticklabels([str(y) for y in xticks])

    style_axes(ax)
    add_source(ax, r"Source: Banque du Canada (Rapport sur la politique mon\'{e}taire)")
    save(fig, 'output_gap_canada.png')


# =====================================================================
# Figure 7: US real GDP around COVID (2018–2024)
# =====================================================================
def us_gdp_covid():
    print('Figure 7: US real GDP around COVID')

    gdp = get_fred_data('GDPC1', observation_start='2018-01-01',
                         observation_end='2024-12-31')

    fig, ax = new_figure(9, 4.5)

    ax.plot(gdp.index, gdp.values, color=palette[0], linewidth=2.5,
            marker='o', markersize=4, markerfacecolor=palette[0])

    # Recession shading
    ax.axvspan(pd.Timestamp('2020-02-01'), pd.Timestamp('2020-04-01'),
               color='grey', alpha=0.25, linewidth=0)

    # Pre-COVID trend line
    pre = gdp.loc[:'2020-01-01']
    if len(pre) >= 4:
        x_pre = np.arange(len(pre))
        log_pre = np.log(pre.values)
        slope, intercept = np.polyfit(x_pre, log_pre, 1)
        # Extend trend
        x_all = np.arange(len(gdp))
        trend_vals = np.exp(intercept + slope * x_all)
        ax.plot(gdp.index, trend_vals, color=palette[7], linewidth=1.5,
                linestyle='--', label=r'Tendance pr\'{e}-COVID')

    # Annotate the trough
    trough_date = pd.Timestamp('2020-04-01')
    if trough_date in gdp.index:
        trough_val = gdp.loc[trough_date]
        ax.annotate(f'{trough_val/1000:.1f}' + r'\,T\,\$',
                    xy=(trough_date, trough_val),
                    xytext=(40, 15), textcoords='offset points',
                    fontsize=10, color=palette[2], fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.2))

    ax.set_ylabel(r"Milliards USD (2017)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Format y-axis with thousands separator
    from matplotlib.ticker import FuncFormatter
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, _: r'{:,.0f}'.format(x).replace(',', r'\,')))

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='lower right')
    add_source(ax, r"Source: FRED (GDPC1) --- PIB r\'{e}el des \'{E}tats-Unis")
    save(fig, 'us_gdp_covid.png')


# =====================================================================
# Figure 8: US consumer confidence (University of Michigan)
# =====================================================================
def us_consumer_confidence():
    print('Figure 8: US consumer confidence')

    # University of Michigan Consumer Sentiment
    sent = get_fred_data('UMCSENT', observation_start='1978-01-01')

    if len(sent) == 0:
        print('  ! No consumer sentiment data. Skipping.')
        return

    fig, ax = new_figure(9, 4.5)

    ax.plot(sent.index, sent.values, color=palette[0], linewidth=1.5)
    ax.fill_between(sent.index, sent.values, sent.values.min() - 5,
                    color=palette[0], alpha=0.08)

    # Recession shading
    for start, end in recessions_us:
        if start >= pd.Timestamp('1978-01-01'):
            ax.axvspan(start, end, color='grey', alpha=0.2, linewidth=0)

    # Long-run average
    avg = sent.mean()
    ax.axhline(avg, color=palette[7], linewidth=1, linestyle='--',
               label=f'Moyenne ({avg:.0f})')

    ax.set_xlim(sent.index.min(), sent.index.max())
    ax.set_ylabel(r"Indice de confiance", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(45, 115)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right')
    ax.text(0.02, 0.95, r'\textit{Zones gris\'{e}es = r\'{e}cessions (NBER)}',
            fontsize=9, color=palette[7], transform=ax.transAxes, va='top')
    add_source(ax, r"Source: FRED (UMCSENT) --- Universit\'{e} du Michigan")
    save(fig, 'us_consumer_confidence.png')


# =====================================================================
# Figure 9: Oil price close-up Feb–Mar 2026
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
# Figure 10: Cyclical components of GDP, C, and I (Canada)
# =====================================================================
def cyclical_components_canada():
    """HP-filtered cyclical components of Y, C, and I for Canada."""
    print('Figure 10: Cyclical components (Canada)')

    from statsmodels.tsa.filters.hp_filter import hpfilter
    from stats_can import StatsCan

    sc = StatsCan()
    df = sc.table_to_df('36-10-0104-01')

    # Parse dates and filter chained dollars
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])
    df = df[df['Prices'] == 'Chained (2017) dollars']

    dates = df['REF_DATE'].unique()

    # Calculate components
    C = (df.loc[df['Estimates'] == 'Final consumption expenditure', 'VALUE'].values
         - df.loc[df['Estimates'] == 'General governments final consumption expenditure', 'VALUE'].values)
    G = df.loc[df['Estimates'] == 'General governments final consumption expenditure', 'VALUE'].values
    I = (df.loc[df['Estimates'] == 'Gross fixed capital formation', 'VALUE'].values
         + df.loc[df['Estimates'] == 'Investment in inventories', 'VALUE'].values)
    X = df.loc[df['Estimates'] == 'Exports of goods and services', 'VALUE'].values
    M = df.loc[df['Estimates'] == 'Less: imports of goods and services', 'VALUE'].values
    Y = C + G + I + X - M

    fig, ax = new_figure(9, 4.5)

    # HP-filter the year-over-year growth rates (skip first 4 quarters)
    ax.plot(dates[4:],
            hpfilter(pd.DataFrame(Y)[0].pct_change(4).values[4:], lamb=1600)[0],
            color=palette[0], linewidth=2, label='PIB', zorder=2)
    ax.plot(dates[4:],
            hpfilter(pd.DataFrame(C)[0].pct_change(4).values[4:], lamb=1600)[0],
            color=palette[1], linewidth=2, label='Consommation', zorder=3)
    ax.plot(dates[4:],
            hpfilter(pd.DataFrame(I)[0].pct_change(4).values[4:], lamb=1600)[0],
            color=palette[2], linewidth=2, label='Investissement', zorder=1)

    # Recession shading (Canada)
    for start, end in can_recessions:
        if start >= dates[4]:
            ax.axvspan(start, end, color='grey', alpha=0.2, linewidth=0)

    ax.axhline(0, color='black', linewidth=0.5)

    ax.set_xlim(pd.to_datetime('1962'), dates[-1])
    first_tick = 1965
    last_tick = dates[-1].year
    xticks = list(range(first_tick, last_tick + 1, 5))
    ax.set_xticks([pd.to_datetime(str(y)) for y in xticks])
    ax.set_xticklabels([str(y) for y in xticks], fontsize=10)

    ax.set_ylim(-0.3, 0.3)
    ax.set_yticks(np.arange(-0.3, 0.3 + 0.1, 0.1))
    ax.set_yticklabels([f'{x:.1f}' for x in np.arange(-0.3, 0.3 + 0.1, 0.1)],
                        fontsize=10)
    ax.set_ylabel(r"Composante cyclique (croissance annuelle)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10)
    add_source(ax, r"Source: Statistique Canada (36-10-0104-01), filtre HP")
    save(fig, 'cyclical_components_canada.png')


# =====================================================================
# Figure 11: Phillips curve (US) — inflation vs unemployment scatter
# =====================================================================
def phillips_curve_usa():
    """Scatter plot of CPI inflation vs unemployment rate (US)."""
    print('Figure 11: Phillips curve (US)')

    unrate = get_fred_data('UNRATE', observation_start='1960-01-01')
    cpi = get_fred_data('CPIAUCSL', observation_start='1959-01-01')

    # Year-over-year inflation
    inflation = cpi.pct_change(12) * 100
    inflation = inflation.dropna()

    # Annual averages keyed by year integer
    u_annual = unrate.groupby(unrate.index.year).mean()
    pi_annual = inflation.groupby(inflation.index.year).mean()

    # Align on common years
    common_years = u_annual.index.intersection(pi_annual.index)
    u = u_annual.loc[common_years]
    pi = pi_annual.loc[common_years]

    # Drop NaN
    mask = u.notna() & pi.notna()
    u = u[mask]
    pi = pi[mask]

    fig, ax = new_figure(8, 5)

    ax.scatter(u.values, pi.values, color=palette[0], s=30, alpha=0.7,
               edgecolors='white', linewidth=0.5, zorder=3)

    # Trend line
    z = np.polyfit(u.values, pi.values, 1)
    x_line = np.linspace(u.min(), u.max(), 100)
    ax.plot(x_line, np.polyval(z, x_line), color=palette[2], linewidth=2,
            linestyle='--', label=r"Tendance lin\'{e}aire", zorder=2)

    # Label a few notable years
    for year_int, offset in [(1980, (5, 5)), (2009, (-15, 8)),
                              (2020, (5, -12)), (2022, (5, 5))]:
        if year_int in u.index:
            ax.annotate(str(year_int), xy=(u.loc[year_int], pi.loc[year_int]),
                        xytext=offset, textcoords='offset points',
                        fontsize=8, color=palette[7])

    ax.set_xlabel(r"Taux de ch\^{o}mage (\%)", fontsize=11)
    ax.set_ylabel(r"Inflation IPC (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right')
    add_source(ax, r"Source: FRED (UNRATE, CPIAUCSL) --- Donn\'{e}es annuelles, \'{E}tats-Unis")
    save(fig, 'phillips_curve_usa.png')


# =====================================================================
# Figure 12: Yield curve spread (10y - 2y) with recession shading
# =====================================================================
def yield_curve_usa():
    """US 10-year minus 2-year Treasury yield spread."""
    print('Figure 12: Yield curve spread (US)')

    data = get_fred_data('T10Y2Y', frequency='m', aggregation_method='avg',
                         observation_start='1976-01-01')
    data = data.dropna()

    fig, ax = new_figure(8, 4.5)

    ax.plot(data.index, data.values, color=palette[0], linewidth=1.5)
    ax.fill_between(data.index, data.values, 0,
                    where=data.values < 0,
                    color=palette[2], alpha=0.3, linewidth=0)
    ax.axhline(0, color=palette[2], linestyle='dotted', linewidth=1.5)

    # Recession shading
    for start, end in recessions_us:
        if start >= pd.Timestamp('1976-01-01'):
            ax.axvspan(start, end, color='grey', alpha=0.2, linewidth=0)

    ax.set_xlim(data.index.min(), data.index.max())
    ax.set_ylim(-3, 3)
    ax.set_yticks(range(-3, 4, 1))
    ax.set_yticklabels([f'{x}' + r'\,\%' for x in range(-3, 4, 1)],
                        fontsize=10)
    ax.set_ylabel(r"\'{E}cart 10 ans $-$ 2 ans (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.text(0.02, 0.95, r'\textit{Zones gris\'{e}es = r\'{e}cessions (NBER)}',
            fontsize=9, color=palette[7], transform=ax.transAxes, va='top')
    add_source(ax, r"Source: FRED (T10Y2Y) --- \'{E}tats-Unis")
    save(fig, 'yield_curve_usa.png')


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('ECON50803 S4 — Generating figures...\n')
    us_gdp_recessions()
    output_gap_us()
    employment_recovery()
    us_recession_inflation()
    us_gdp_growth()
    canada_gdp_potential()
    output_gap_canada()
    us_gdp_covid()
    us_consumer_confidence()
    oil_price_2026()
    cyclical_components_canada()
    phillips_curve_usa()
    yield_curve_usa()
    print('\nDone.')
