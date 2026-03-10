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

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from plot_utils import *


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
        ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

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

    # Recession label
    ax.text(0.02, 0.95, r'\textit{Zones grisées = récessions (NBER)}',
            fontsize=9, color=palette[7], transform=ax.transAxes,
            va='top')

    add_source(ax, r"Source: FRED (GDPC1) --- PIB réel des États-Unis, échelle logarithmique")
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
    ax.set_ylabel(r"Écart de production (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(-10, 6)

    # Annotations
    ax.annotate('Surchauffe',
                xy=(pd.Timestamp('2000-01-01'), 2.5),
                fontsize=10, color=palette[2], fontweight='bold')
    ax.annotate(r'Récession',
                xy=(pd.Timestamp('2009-06-01'), -6),
                fontsize=10, color=palette[0], fontweight='bold')

    style_axes(ax)
    add_source(ax, r"Source: FRED (GDPC1, GDPPOT) --- États-Unis")
    save(fig, 'output_gap_us.png')


# =====================================================================
# Figure 3: Employment recovery across recessions
# =====================================================================
def employment_recovery():
    print('Figure 3: Employment recovery across recessions')

    payems = get_fred_data('PAYEMS', observation_start='1970-01-01')

    # Define recession peaks (last month before employment drops)
    peaks = {
        '1981': pd.Timestamp('1981-07-01'),
        '1990': pd.Timestamp('1990-06-01'),
        '2001': pd.Timestamp('2001-02-01'),
        '2008': pd.Timestamp('2008-01-01'),
        '2020': pd.Timestamp('2020-02-01'),
    }

    colors = {
        '1981': palette[7],
        '1990': palette[4],
        '2001': palette[1],
        '2008': palette[0],
        '2020': palette[2],
    }

    fig, ax = new_figure(9, 4.5)

    for label, peak in peaks.items():
        base = payems.loc[peak]
        # Show from peak to 60 months after
        end = peak + pd.DateOffset(months=60)
        subset = payems.loc[peak:end]
        months = ((subset.index - peak).days / 30.44).astype(int)
        indexed = (subset / base) * 100
        ax.plot(months, indexed.values, color=colors[label],
                linewidth=2, label=label)

    ax.axhline(100, color='black', linewidth=0.8, linestyle='--')

    ax.set_xlim(0, 60)
    ax.set_ylim(85, 110)
    ax.set_yticks([85, 90, 95, 100, 105, 110])
    ax.set_yticklabels([r'85', r'90', r'95', r'100', r'105', r'110'])
    ax.set_xlabel(r"Mois depuis le choc", fontsize=11)
    ax.set_ylabel(r"Emploi (choc = 100)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='lower right',
              title=r'\textbf{Récession}', title_fontsize=10)
    add_source(ax, r"Source: FRED (PAYEMS) --- Emplois non agricoles, États-Unis")
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
               color='grey', alpha=0.3, linewidth=0)


    # Highlight gap between 2% target and actual inflation when below target
    below = inflation[inflation < 2]
    # Find the contiguous below-2% period right after 2020
    below_2020 = below.loc['2020-01-01':'2021-12-31']
    if len(below_2020) > 0:
        start = below_2020.index[0]
        end = below_2020.index[-1]
        mask = (inflation.index >= start) & (inflation.index <= end)
        ax.fill_between(inflation.index[mask], inflation.values[mask], 2,
                        color=palette[2], alpha=0.2, linewidth=0)

    ax.set_xlim(pd.Timestamp('2019-01-01'), pd.Timestamp('2024-12-01'))
    ax.set_ylabel(r"Inflation IPC (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 10)
    ax.set_yticks([0, 2, 4, 6, 8, 10])
    ax.set_yticklabels([r'0', r'2', r'4', r'6', r'8', r'10'])

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right')
    add_source(ax, r"Source: FRED (CPIAUCSL) --- Inflation sur 12 mois, États-Unis")
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
    ax.set_ylabel(r"Croissance (\% annualisé)", fontsize=11,
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
    add_source(ax, r"Source: FRED (GDPC1) --- Taux de croissance trimestriel annualisé")
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
    for start, end in recessions_ca:
        if start >= gdp.index.min():
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    ax.plot(gdp.index, gdp.values, color=palette[0], linewidth=2,
            label=r"PIB réel ($Y$)")
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
    for start, end in recessions_ca:
        if start >= gap.index.min():
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

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
    ax.set_ylabel(r"Écart de production (\%)", fontsize=11,
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
    add_source(ax, r"Source: Banque du Canada (Rapport sur la politique monétaire)")
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
               color='grey', alpha=0.3, linewidth=0)

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
                linestyle='--', label=r'Tendance pré-COVID')

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
    add_source(ax, r"Source: FRED (GDPC1) --- PIB réel des États-Unis")
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
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

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
    ax.text(0.02, 0.95, r'\textit{Zones grisées = récessions (NBER)}',
            fontsize=9, color=palette[7], transform=ax.transAxes, va='top')
    add_source(ax, r"Source: FRED (UMCSENT) --- Université du Michigan")
    save(fig, 'us_consumer_confidence.png')


# =====================================================================
# Figure 9: Oil price close-up Feb–Mar 2026
# =====================================================================
def oil_price_2026():
    print('Figure 6: Oil price (6 months)')

    brent = get_fred_data('DCOILBRENTEU',
                          observation_start='2025-09-01',
                          observation_end='2026-03-31')
    brent = brent.dropna()

    if len(brent) == 0:
        print('  ! No Brent data available. Skipping figure.')
        return

    fig, ax = new_figure(9, 4.5)

    ax.plot(brent.index, brent.values, color=palette[0], linewidth=2)
    ax.fill_between(brent.index, brent.values, 0,
                    color=palette[0], alpha=0.1)

    # Mark Feb 28 with a dashed vertical line and text label (no arrow)
    feb28 = pd.Timestamp('2026-02-28')
    if (brent.index >= feb28).any():
        closest = brent.index[brent.index >= feb28]
        if len(closest) > 0:
            mark_date = closest[0]
            ax.axvline(mark_date, color=palette[2], linewidth=1.5,
                       linestyle='--', alpha=0.7)
            ax.text(mark_date - pd.DateOffset(days=3), ax.get_ylim()[1] * 0.97,
                    r'\textit{Opération Epic Fury}',
                    fontsize=9, color=palette[2], fontweight='bold',
                    ha='right', va='top')

    # -- X-axis: explicit ticks with LaTeX labels --
    ax.set_xlim(pd.Timestamp('2025-09-01'), brent.index[-1])
    xtick_dates = [pd.Timestamp('2025-09-01'), pd.Timestamp('2025-10-01'),
                   pd.Timestamp('2025-11-01'), pd.Timestamp('2025-12-01'),
                   pd.Timestamp('2026-01-01'), pd.Timestamp('2026-02-01'),
                   pd.Timestamp('2026-03-01')]
    xtick_labels = [r'sept.', r'oct.', r'nov.', r'déc.', r'janv.', r'févr.', r'mars']
    ax.set_xticks(xtick_dates)
    ax.set_xticklabels(xtick_labels, fontsize=11)

    # -- Y-axis: explicit ticks --
    ax.set_ylim(50, 80)
    yticks = [50, 55, 60, 65, 70, 75, 80]
    ax.set_yticks(yticks)
    ax.set_yticklabels([rf'{y}' for y in yticks], fontsize=11)

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
    for start, end in recessions_ca:
        if start >= dates[4]:
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

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
            linestyle='--', label=r"Tendance linéaire", zorder=2)

    # Label a few notable years
    for year_int, offset in [(1980, (5, 5)), (2009, (-15, 8)),
                              (2020, (5, -12)), (2022, (5, 5))]:
        if year_int in u.index:
            ax.annotate(str(year_int), xy=(u.loc[year_int], pi.loc[year_int]),
                        xytext=offset, textcoords='offset points',
                        fontsize=8, color=palette[7])

    ax.set_xlabel(r"Taux de chômage (\%)", fontsize=11)
    ax.set_ylabel(r"Inflation IPC (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right')
    add_source(ax, r"Source: FRED (UNRATE, CPIAUCSL) --- Données annuelles, États-Unis")
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

    fig, ax = new_figure(9, 4.5)

    ax.plot(data.index, data.values, color=palette[0], linewidth=1.5)
    ax.fill_between(data.index, data.values, 0,
                    where=data.values < 0,
                    color=palette[2], alpha=0.3, linewidth=0)
    ax.axhline(0, color=palette[2], linestyle='dotted', linewidth=1.5)

    # Recession shading
    for start, end in recessions_us:
        if start >= pd.Timestamp('1976-01-01'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    ax.set_xlim(data.index.min(), data.index.max())
    xticks = [pd.Timestamp(f'{y}-01-01') for y in range(1980, 2030, 5)]
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in range(1980, 2030, 5)], fontsize=10)
    ax.set_ylim(-3, 3)
    ax.set_yticks(range(-3, 4, 1))
    ax.set_yticklabels([f'{x}' + r'\%' for x in range(-3, 4, 1)],
                        fontsize=10)
    ax.set_ylabel(r"Écart 10 ans $-$ 2 ans (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Source: FRED (T10Y2Y) --- États-Unis")
    save(fig, 'yield_curve_usa.png')


# =====================================================================
# Figure 13: Natural rate of unemployment (US)
# =====================================================================
def natural_unemployment_usa():
    """US unemployment rate vs natural rate (NROU) with recession shading."""
    print('Figure 13: Natural unemployment rate (US)')

    unrate = get_fred_data('UNRATE', frequency='m', aggregation_method='avg',
                           observation_start='1950-01-01')
    nrou = get_fred_data('NROU', observation_start='1950-01-01')
    unrate = unrate.dropna()
    nrou = nrou.dropna()

    fig, ax = new_figure(9, 4.5)

    ax.plot(unrate.index, unrate.values, color=palette[0], linewidth=1.5,
            label=r"Taux de chômage")
    ax.plot(nrou.index, nrou.values, color=palette[1], linewidth=2.5,
            label=r"Taux naturel (NROU)")

    # Recession shading
    for start, end in recessions_us:
        if start >= pd.Timestamp('1950-01-01'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    ax.set_xlim(pd.Timestamp('1950-01-01'), unrate.index.max())
    ax.set_ylim(2, 14)
    xticks = [pd.Timestamp(f'{y}-01-01') for y in range(1950, 2030, 10)]
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in range(1950, 2030, 10)], fontsize=10)
    ax.set_yticks(range(2, 15, 2))
    ax.set_yticklabels([f'{x}' + r'\%' for x in range(2, 15, 2)],
                        fontsize=10)
    ax.set_ylabel(r"Taux de chômage (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left')
    add_source(ax, r"Source: FRED (UNRATE, NROU) --- États-Unis")
    save(fig, 'natural_unemployment_usa.png')


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 4 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        us_gdp_recessions,
        output_gap_us,
        employment_recovery,
        us_recession_inflation,
        us_gdp_growth,
        canada_gdp_potential,
        output_gap_canada,
        us_gdp_covid,
        us_consumer_confidence,
        oil_price_2026,
        cyclical_components_canada,
        phillips_curve_usa,
        yield_curve_usa,
        natural_unemployment_usa,
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
