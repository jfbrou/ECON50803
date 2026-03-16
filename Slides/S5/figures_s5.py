"""
ECON50803 — Session 5 : Figure Generation
============================================

Generates all matplotlib figures for Session 5 slides (monetary and
fiscal policy). All figure labels, axis titles, legends, and
annotations are in French.

Run from Slides/S5/:
    python3 figures_s5.py
"""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Import shared utilities (palette, helpers, data loaders) ────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from plot_utils import *


# =====================================================================
# Figure 1: Bank of Canada overnight rate (1996–2026)
# =====================================================================
def overnight_rate_ca():
    """Bank of Canada overnight target rate since 1996."""
    print('Figure 1: Bank of Canada overnight rate')

    # FRED IRSTCI01CAM156N: monthly overnight rate, full history from 1996
    rate = get_fred_data('IRSTCI01CAM156N', observation_start='1996-01-01')
    rate = rate.dropna()

    fig, ax = new_figure(9, 4.5)

    ax.plot(rate.index, rate.values, color=palette[0], linewidth=2)

    # Recession shading (Canadian)
    for start, end in recessions_ca:
        if start >= pd.Timestamp('1996-01-01'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(pd.Timestamp('1996-01-01'), rate.index.max())
    xticks = list(range(1996, 2028, 2))
    ax.set_xticks([pd.Timestamp(f'{y}-01-01') for y in xticks])
    ax.set_xticklabels([str(y) for y in xticks], fontsize=10)

    ax.set_ylim(0, 6)
    ax.set_yticks(range(0, 7, 1))
    ax.set_yticklabels([f'{y}\\%' for y in range(0, 7, 1)], fontsize=11)
    ax.set_ylabel(r"Taux directeur (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Source: FRED (OCDE)")
    save(fig, 'overnight_rate_ca.png')


# =====================================================================
# Figure 2: Overnight rate vs 5-year mortgage rate
# =====================================================================
def overnight_vs_mortgage():
    """Bank of Canada overnight rate vs 5-year conventional mortgage rate."""
    print('Figure 2: Overnight rate vs 5-year mortgage rate')

    # FRED IRSTCI01CAM156N: monthly overnight rate (full history)
    overnight = get_fred_data('IRSTCI01CAM156N', observation_start='2000-01-01')
    overnight = overnight.dropna()

    # Valet V121764: 5-year conventional mortgage rate
    mortgage = get_valet_series('V121764', start='2000-01-01')
    mortgage = mortgage.dropna()

    fig, ax = new_figure(9, 4.5)

    ax.plot(overnight.index, overnight.values, color=palette[0],
            linewidth=2, label='Taux directeur')
    ax.plot(mortgage.index, mortgage.values, color=palette[2],
            linewidth=2, label=r'Taux hypothécaire 5 ans')

    # Recession shading (Canadian)
    for start, end in recessions_ca:
        if start >= pd.Timestamp('2000-01-01'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(pd.Timestamp('2000-01-01'), max(overnight.index.max(),
                                                  mortgage.index.max()))
    xticks = list(range(2000, 2028, 2))
    ax.set_xticks([pd.Timestamp(f'{y}-01-01') for y in xticks])
    ax.set_xticklabels([str(y) for y in xticks], fontsize=10)

    ax.set_ylim(0, 8)
    ax.set_yticks(range(0, 9, 1))
    ax.set_yticklabels([f'{y}\\%' for y in range(0, 9, 1)], fontsize=11)
    ax.set_ylabel(r"\%", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, r"Source: FRED, Banque du Canada (Valet)")
    save(fig, 'overnight_vs_mortgage.png')


# =====================================================================
# Figure 2b: Transmission chain — overnight → 5yr bond → 5yr mortgage
# =====================================================================
def transmission_taux():
    """Overnight rate, 5-year GoC bond yield, 5-year mortgage rate."""
    print('Figure 2b: Transmission du taux directeur')

    # FRED IRSTCI01CAM156N: monthly overnight rate (full history)
    overnight = get_fred_data('IRSTCI01CAM156N', observation_start='2000-01-01')
    overnight = overnight.dropna()

    # Valet BD.CDN.5YR.DQ.YLD: 5-year Government of Canada benchmark bond yield
    bond5 = get_valet_series('BD.CDN.5YR.DQ.YLD', start='2000-01-01')
    bond5 = bond5.dropna().resample('MS').mean()  # monthly average

    # Valet V121764: 5-year conventional mortgage rate
    mortgage = get_valet_series('V121764', start='2000-01-01')
    mortgage = mortgage.dropna().resample('MS').mean()  # monthly average

    fig, ax = new_figure(9, 4.5)

    ax.plot(overnight.index, overnight.values, color=palette[0],
            linewidth=2, label='Taux directeur')
    ax.plot(bond5.index, bond5.values, color=palette[1],
            linewidth=2, label='Obligations du GdC 5 ans')
    ax.plot(mortgage.index, mortgage.values, color=palette[2],
            linewidth=2, label=r'Taux hypothécaire 5 ans')

    # Recession shading (Canadian)
    for start, end in recessions_ca:
        if start >= pd.Timestamp('2000-01-01'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    # ── Axis formatting ─────────────────────────────────────────────
    end_date = max(overnight.index.max(), bond5.index.max(),
                   mortgage.index.max())
    ax.set_xlim(pd.Timestamp('2000-01-01'), end_date)
    xticks = list(range(2000, 2028, 2))
    ax.set_xticks([pd.Timestamp(f'{y}-01-01') for y in xticks])
    ax.set_xticklabels([str(y) for y in xticks], fontsize=10)

    ax.set_ylim(0, 9)
    ax.set_yticks(range(0, 10, 1))
    ax.set_yticklabels([f'{y}\\%' for y in range(0, 10, 1)], fontsize=11)
    ax.set_ylabel(r"\%", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper center', ncol=3)
    add_source(ax, r"Source: FRED, Banque du Canada (Valet)")
    save(fig, 'transmission_taux.png')


# =====================================================================
# Figure 3: Policy rate vs CPI inflation (Canada, 2000–present)
# =====================================================================
def rate_vs_inflation_ca():
    """Bank of Canada overnight rate vs CPI inflation."""
    print('Figure 3: Policy rate vs CPI inflation (Canada)')

    # FRED IRSTCI01CAM156N: monthly overnight rate (full history)
    overnight = get_fred_data('IRSTCI01CAM156N', observation_start='2000-01-01')
    overnight = overnight.dropna()

    # Compute CPI y/y inflation from CPI level (CANCPIALLMINMEI)
    cpi_level = get_fred_data('CANCPIALLMINMEI', observation_start='1999-01-01')
    cpi = cpi_level.pct_change(periods=12) * 100
    cpi = cpi.dropna()
    cpi = cpi.loc['2000-01-01':]

    fig, ax = new_figure(9, 4.5)

    ax.plot(overnight.index, overnight.values, color=palette[0],
            linewidth=2, label='Taux directeur')
    ax.plot(cpi.index, cpi.values, color=palette[2],
            linewidth=2, label='Inflation IPC (a/a)')

    # Inflation target at 2%
    ax.axhline(2, color=palette[1], linewidth=1.5, linestyle='--',
               label=r"Cible d'inflation (2\%)")

    # Recession shading (Canadian)
    for start, end in recessions_ca:
        if start >= pd.Timestamp('2000-01-01'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(pd.Timestamp('2000-01-01'), max(overnight.index.max(),
                                                  cpi.index.max()))
    xticks = list(range(2000, 2028, 2))
    ax.set_xticks([pd.Timestamp(f'{y}-01-01') for y in xticks])
    ax.set_xticklabels([str(y) for y in xticks], fontsize=10)

    ax.set_ylim(-2, 10)
    ax.set_yticks(range(-2, 12, 2))
    ax.set_yticklabels([f'{y}\\%' for y in range(-2, 12, 2)], fontsize=11)
    ax.set_ylabel(r"\%", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0))
    add_source(ax, r"Source: FRED")
    save(fig, 'rate_vs_inflation_ca.png')


# =====================================================================
# Figure 4: Zoomed 2019–2026 — the policy error
# =====================================================================
def inflation_vs_rate_2019():
    """Zoomed view of the policy rate lag behind inflation (2019-2026)."""
    print('Figure 4: Inflation vs rate (2019-2026)')

    # Valet V39079 is fine here (covers from 2009)
    overnight = get_valet_series('V39079', start='2019-01-01')
    overnight = overnight.dropna()

    # Compute CPI y/y inflation from CPI level (Valet V41690973, all-items NSA)
    cpi_level = get_valet_series('V41690973', start='2018-01-01')
    cpi_level = cpi_level.dropna()
    cpi = cpi_level.pct_change(periods=12) * 100
    cpi = cpi.dropna()
    cpi = cpi.loc['2019-01-01':]

    fig, ax = new_figure(9, 4.5)

    ax.plot(overnight.index, overnight.values, color=palette[0],
            linewidth=2.5, label='Taux directeur')
    ax.plot(cpi.index, cpi.values, color=palette[2],
            linewidth=2.5, label='Inflation IPC (a/a)')

    # 2% target dashed line
    ax.axhline(2, color=palette[1], linewidth=1.5, linestyle='--',
               label=r"Cible (2\%)")

    # COVID recession shading
    ax.axvspan(pd.Timestamp('2020-02-01'), pd.Timestamp('2020-05-01'),
               color='grey', alpha=0.3, linewidth=0)

    # ── Axis formatting ─────────────────────────────────────────────
    last_date = max(overnight.index.max(), cpi.index.max())
    ax.set_xlim(pd.Timestamp('2019-01-01'), last_date)
    xticks = [y for y in range(2019, last_date.year + 1)]
    ax.set_xticks([pd.Timestamp(f'{y}-01-01') for y in xticks])
    ax.set_xticklabels([str(y) for y in xticks], fontsize=10)

    ax.set_ylim(0, 10)
    ax.set_yticks(range(0, 12, 2))
    ax.set_yticklabels([f'{y}\\%' for y in range(0, 12, 2)], fontsize=11)
    ax.set_ylabel(r"\%", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, r"Source: Banque du Canada")
    save(fig, 'inflation_vs_rate_2019.png')


# =====================================================================
# Figure 5: Global policy rates (Fed, ECB, BoC)
# =====================================================================
def policy_rates_global():
    """Policy rates of the Fed, ECB, and BoC."""
    print('Figure 5: Global policy rates')

    # Fed: federal funds rate
    fed = get_fred_data('FEDFUNDS', frequency='m', aggregation_method='avg',
                        observation_start='2000-01-01')

    # BoC: FRED IRSTCI01CAM156N (monthly, full history)
    boc = get_fred_data('IRSTCI01CAM156N', observation_start='2000-01-01')

    # ECB: deposit facility rate
    ecb = get_fred_data('ECBDFR', observation_start='2000-01-01')
    if len(ecb) == 0:
        ecb = get_fred_data('ECBMLFR', observation_start='2000-01-01')

    fig, ax = new_figure(9, 4.5)

    ax.plot(fed.index, fed.values, color=palette[4], linewidth=2,
            label='Fed (taux des fonds)')
    ax.plot(boc.index, boc.values, color=palette[2], linewidth=2,
            label='BdC (taux directeur)')
    if len(ecb) > 0:
        ax.plot(ecb.index, ecb.values, color=palette[1], linewidth=2,
                label=r'BCE (taux de dépôt)')

    # ZLB zone: shading below 0%
    ax.axhspan(-1, 0, color=palette[7], alpha=0.08, linewidth=0)
    ax.text(pd.Timestamp('2001-01-01'), -0.5,
            r'\textit{Zone de la borne zéro}',
            fontsize=8, color=palette[7], va='center')

    # ── Axis formatting ─────────────────────────────────────────────
    end_date = max(s.index.max() for s in [fed, boc, ecb]
                   if len(s) > 0)
    ax.set_xlim(pd.Timestamp('2000-01-01'), end_date)
    xticks = list(range(2000, 2028, 2))
    ax.set_xticks([pd.Timestamp(f'{y}-01-01') for y in xticks])
    ax.set_xticklabels([str(y) for y in xticks], fontsize=10)

    ax.set_ylim(-1, 7)
    ax.set_yticks(range(-1, 8, 1))
    ax.set_yticklabels([f'{y}\\%' for y in range(-1, 8, 1)], fontsize=11)
    ax.set_ylabel(r"\%", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=9, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, r"Source: FRED")
    save(fig, 'policy_rates_global.png')


# =====================================================================
# Figure 6: Bank of Canada total assets (QE visible)
# =====================================================================
def boc_balance_sheet():
    """Bank of Canada total assets showing QE and QT periods."""
    print('Figure 6: Bank of Canada balance sheet')

    # Try Valet series for BoC total assets (weekly)
    try:
        assets = get_valet_series('V36610', start='2007-01-01')
        assets = assets.dropna()
        if len(assets) == 0:
            raise ValueError('Empty series')
    except Exception:
        # Fallback: try FRED series
        try:
            assets = get_fred_data('BCNSDCBS', observation_start='2007-01-01')
            assets = assets.dropna()
            if len(assets) == 0:
                raise ValueError('Empty series')
        except Exception:
            print('  ! No BoC balance sheet data available. Skipping.')
            return

    if len(assets) == 0:
        print('  ! No BoC balance sheet data available. Skipping.')
        return

    # Convert to billions (data is in millions CAD)
    if assets.max() > 10000:
        assets = assets / 1000

    fig, ax = new_figure(9, 4.5)

    ax.fill_between(assets.index, assets.values, 0,
                    color=palette[0], alpha=0.3, linewidth=0)
    ax.plot(assets.index, assets.values, color=palette[0], linewidth=2)

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(assets.index.min(), assets.index.max())

    first_year = assets.index.min().year
    last_year = assets.index.max().year
    xticks = list(range(first_year + (2 - first_year % 2) % 2,
                        last_year + 1, 2))
    ax.set_xticks([pd.Timestamp(f'{y}-01-01') for y in xticks])
    ax.set_xticklabels([str(y) for y in xticks], fontsize=10)

    ax.set_ylim(0, 600)
    ax.set_yticks([0, 100, 200, 300, 400, 500, 600])
    ax.set_yticklabels(['0', '100', '200', '300', '400', '500', '600'],
                       fontsize=11)
    ax.set_ylabel(r"Milliards CAD", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Source: Banque du Canada")
    save(fig, 'boc_balance_sheet.png')


# =====================================================================
# Figure 7: Government debt-to-GDP — horizontal bar chart (latest)
# =====================================================================
def debt_to_gdp():
    """Horizontal bar chart of government gross debt / GDP (latest observation)."""
    print('Figure 7: Government debt-to-GDP ratios (bar chart)')

    # ── FRED series IDs and French labels ─────────────────────────────
    # Target year for consistent cross-country comparison
    TARGET_YEAR = 2023

    countries = [
        ('Japon',         'GGGDTAJPA188N'),
        ('Italie',        'GGGDTAITA188N'),
        (r'États-Unis',   'GGGDTAUSA188N'),
        ('Espagne',       'GGGDTAESA188N'),
        ('France',        'GGGDTAFRA188N'),
        ('Royaume-Uni',   'GGGDTAGBA188N'),
        ('Canada',        'GGGDTACAA188N'),
        ('Chine',         'GGGDTACNA188N'),
        (r'Brésil',       'GGGDTABRA188N'),
        ('Inde',          'GGGDTAINA188N'),
        ('Allemagne',     'GGGDTADEA188N'),
        ('Mexique',       'GGGDTAMXA188N'),
        (r'Corée du Sud', 'GGGDTAKRA188N'),
    ]

    # Hardcoded fallbacks (IMF WEO, 2023)
    fallback = {
        'GGGDTAJPA188N': 240,
        'GGGDTAITA188N': 135,
        'GGGDTAUSA188N': 121,
        'GGGDTAESA188N': 105,
        'GGGDTAFRA188N': 110,
        'GGGDTAGBA188N': 101,
        'GGGDTACAA188N': 107,
        'GGGDTACNA188N': 84,
        'GGGDTABRA188N': 84,
        'GGGDTAINA188N': 81,
        'GGGDTADEA188N': 64,
        'GGGDTAMXA188N': 53,
        'GGGDTAKRA188N': 51,
    }

    # Fetch the TARGET_YEAR observation for each country
    labels = []
    values = []
    for label, fred_id in countries:
        try:
            s = get_fred_data(fred_id)
            s = s.dropna()
            # Pick the observation closest to TARGET_YEAR
            yr_data = s[s.index.year == TARGET_YEAR]
            if len(yr_data) > 0:
                values.append(yr_data.iloc[-1])
            elif len(s) > 0:
                values.append(s.iloc[-1])  # fallback to latest
            else:
                values.append(fallback[fred_id])
        except Exception:
            values.append(fallback[fred_id])
        labels.append(label)

    # Sort descending (largest debt at top)
    order = np.argsort(values)[::-1]
    labels = [labels[i] for i in order]
    values = [values[i] for i in order]

    # ── Bar colors: Canada in green, others in navy ───────────────────
    colors = [palette[1] if lab == 'Canada' else palette[0] for lab in labels]

    fig, ax = new_figure(9, 5.5)

    bars = ax.barh(range(len(labels)), values, color=colors, height=0.65)

    # Value labels at the end of each bar
    for bar, val, col in zip(bars, values, colors):
        ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height() / 2,
                f'{val:.0f}\\%', va='center', fontsize=11,
                fontweight='bold', color=col)

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=11)
    ax.invert_yaxis()  # largest at top

    ax.set_xlim(0, 250)
    xticks = list(range(0, 251, 50))
    ax.set_xticks(xticks)
    ax.set_xticklabels([f'{x}\\%' for x in xticks], fontsize=11)
    ax.set_xlabel(r"\% du PIB", fontsize=11, ha='center')
    ax.xaxis.set_label_coords(0.5, -0.1)

    style_axes(ax, xgrid=True)
    ax.grid(False, axis='y')  # keep only vertical gridlines
    add_source(ax, r"Source: FMI via FRED (2023)")
    save(fig, 'debt_to_gdp.png')


# =====================================================================
# Figure 8: Phillips curve scatter by decade (US)
# =====================================================================
def phillips_curve_decades():
    """Phillips curve scatter plot colored by decade (US, 1960-present)."""
    print('Figure 8: Phillips curve by decade')

    unrate = get_fred_data('UNRATE', observation_start='1960-01-01')
    cpi = get_fred_data('CPIAUCSL', observation_start='1959-01-01')

    # Year-over-year inflation (suppress FutureWarning)
    inflation = cpi.pct_change(periods=12, fill_method=None) * 100
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

    # Define decades
    decades = {
        r"Années 1960": (1960, 1969, palette[4]),
        r"Années 1970": (1970, 1979, palette[2]),
        r"Années 1980": (1980, 1989, palette[3]),
        r"Années 1990": (1990, 1999, palette[1]),
        r"Années 2000": (2000, 2009, palette[0]),
        r"Années 2010": (2010, 2019, palette[7]),
        r"Années 2020": (2020, 2029, palette[5]),
    }

    fig, ax = new_figure(8, 5)

    for label, (yr_start, yr_end, color) in decades.items():
        mask_dec = (u.index >= yr_start) & (u.index <= yr_end)
        if mask_dec.sum() > 0:
            ax.scatter(u[mask_dec].values, pi[mask_dec].values,
                       color=color, s=40, alpha=0.8,
                       edgecolors='white', linewidth=0.5,
                       label=label, zorder=3)

    # ── Label notable years ──────────────────────────────────────────
    notable = {1973: (5, 5), 1980: (5, 5), 2020: (-15, -12), 2022: (5, 5)}
    for year_int, offset in notable.items():
        if year_int in u.index:
            ax.annotate(str(year_int),
                        xy=(u.loc[year_int], pi.loc[year_int]),
                        xytext=offset, textcoords='offset points',
                        fontsize=8, color=palette[7])

    # ── Axis formatting ──────────────────────────────────────────────
    ax.set_xlim(3, 11)
    ax.set_xticks(range(3, 12, 1))
    ax.set_xticklabels([f'{x}\\%' for x in range(3, 12, 1)], fontsize=11)
    ax.set_xlabel(r"Taux de chômage (\%)", fontsize=11, ha='center')
    ax.xaxis.set_label_coords(0.5, -0.1)

    ax.set_ylim(-2, 14)
    ax.set_yticks(range(-2, 16, 2))
    ax.set_yticklabels([f'{y}\\%' for y in range(-2, 16, 2)], fontsize=11)
    ax.set_ylabel(r"Inflation IPC (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax, xgrid=True)
    ax.legend(frameon=False, fontsize=9, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, r"Source: FRED (UNRATE, CPIAUCSL)")
    save(fig, 'phillips_curve_decades.png')


# =====================================================================
# Figure 9: Fed dot plot (March 2025 FOMC SEP)
# =====================================================================
def fed_dot_plot():
    """FOMC dot plot: each participant's projected federal funds rate."""
    print('Figure 9: Fed dot plot (mars 2025)')

    # ── March 2025 FOMC SEP data (19 participants) ────────────────────
    # Rate midpoints and number of participants at each level per year.
    dot_data = {
        '2025': {
            3.625: 2, 3.875: 9, 4.125: 4, 4.375: 4,
        },
        '2026': {
            2.875: 3, 3.125: 1, 3.375: 9, 3.625: 2,
            3.875: 1, 4.125: 3,
        },
        '2027': {
            2.625: 2, 2.875: 3, 3.125: 6, 3.375: 2,
            3.625: 4, 3.875: 2,
        },
        'Plus long\nterme': {
            2.500: 2, 2.625: 2, 2.875: 4, 3.000: 3,
            3.125: 1, 3.375: 1, 3.500: 2, 3.625: 2,
            3.750: 1, 3.875: 1,
        },
    }

    categories = list(dot_data.keys())
    x_positions = {cat: i for i, cat in enumerate(categories)}

    fig, ax = new_figure(8, 5)

    # Dot radius in data coords (for side-by-side placement)
    dot_spacing = 0.10  # horizontal offset between same-rate dots

    for cat in categories:
        x_center = x_positions[cat]
        rates = dot_data[cat]
        for rate, count in rates.items():
            # Center the dots horizontally around x_center
            offsets = np.linspace(-(count - 1) / 2 * dot_spacing,
                                  (count - 1) / 2 * dot_spacing,
                                  count)
            for dx in offsets:
                ax.plot(x_center + dx, rate, 'o',
                        color=palette[0], markersize=8,
                        markeredgecolor='white', markeredgewidth=0.5,
                        zorder=3)

    # ── Compute and show medians ──────────────────────────────────────
    for cat in categories:
        x_center = x_positions[cat]
        rates = dot_data[cat]
        all_rates = []
        for rate, count in rates.items():
            all_rates.extend([rate] * count)
        median_rate = np.median(all_rates)
        # Small horizontal dash for the median
        ax.plot([x_center - 0.28, x_center + 0.28], [median_rate, median_rate],
                color=palette[2], linewidth=2.5, zorder=4)

    # ── Axis formatting ───────────────────────────────────────────────
    ax.set_xlim(-0.6, len(categories) - 0.4)
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, fontsize=11)

    # Y-axis: labels every 0.50%, grid lines every 0.25%
    y_min, y_max = 2.25, 4.50
    ax.set_ylim(y_min, y_max)
    yticks_major = np.arange(2.50, 4.51, 0.50)
    ax.set_yticks(yticks_major)
    ax.set_yticklabels([f'{y:.1f}\\%' for y in yticks_major], fontsize=11)

    # Minor ticks at every 0.25% for finer grid
    yticks_minor = np.arange(2.25, 4.51, 0.25)
    ax.set_yticks(yticks_minor, minor=True)
    ax.grid(True, which='minor', axis='y', color='gray',
            linestyle=':', linewidth=0.3, alpha=0.5)

    ax.set_ylabel(r"Taux des fonds fédéraux (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Legend for median marker
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=palette[0],
               markersize=8, markeredgecolor='white', markeredgewidth=0.5,
               label='Projection individuelle'),
        Line2D([0], [0], color=palette[2], linewidth=2.5,
               label=r'Médiane'),
    ]
    ax.legend(handles=legend_elements, frameon=False, fontsize=9,
              loc='upper right', bbox_to_anchor=(1.0, 1.0))

    style_axes(ax, xgrid=False)
    ax.set_ylim(2.25, 4.50)
    add_source(ax, r"Source: Federal Reserve, FOMC SEP (mars 2025)")
    save(fig, 'fed_dot_plot.png')


# =====================================================================
# Figure 10: Gross vs Net Debt (bar chart, 2023)
# =====================================================================
def gross_vs_net_debt():
    """Grouped bar chart: gross vs net debt as % of GDP (2023, IMF WEO)."""
    print('Figure 10: Gross vs net debt comparison')

    # ── Data: IMF Fiscal Monitor (oct. 2024), general government, 2023 ──
    # Verified via IMF datamapper API (GGXWDN_G01_GDP_PT, G_XWDG_G01_GDP_PT)
    # Order: ascending by net debt
    countries = ['CAN', 'DEU', 'GBR', r'É.-U.', 'FRA', 'ITA', 'JPN']
    gross = [107.7, 62.4, 100.4, 119.8, 109.6, 134.6, 240.5]
    net   = [ 14.4, 45.9,  91.8,  94.5, 101.5, 124.2, 136.3]

    x = np.arange(len(countries))
    width = 0.32

    fig, ax = new_figure(9, 5)

    # Gross debt (HECnavy bars)
    bars_gross = ax.bar(x - width / 2 - 0.02, gross, width,
                        color=palette[0],
                        label='Dette brute')

    # Net debt (HECgreen bars)
    bars_net = ax.bar(x + width / 2 + 0.02, net, width,
                      color=palette[1],
                      label='Dette nette')

    # Highlight Canada with a solid coral border on its net debt bar
    can_idx = 0  # Canada is first
    bars_net[can_idx].set_edgecolor(palette[2])
    bars_net[can_idx].set_linewidth(2.5)

    # Value labels on net debt bars
    for bar, val in zip(bars_net, net):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
                f'{val:.0f}\\%', ha='center', fontsize=10, fontweight='bold',
                color=palette[1])

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xticks(x)
    ax.set_xticklabels(countries, fontsize=11)

    ax.set_ylim(0, 250)
    ax.set_yticks(range(0, 251, 50))
    ax.set_yticklabels([f'{y}\\%' for y in range(0, 251, 50)], fontsize=11)
    ax.set_ylabel(r"\% du PIB", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0))
    add_source(ax, r"Source: FMI, Fiscal Monitor (oct. 2024)")
    save(fig, 'gross_vs_net_debt.png')


# =====================================================================
# Figure 11: Government interest expense (% GDP), 2000–2030
# =====================================================================
def interest_expense():
    """Line chart: government interest payments as % of GDP (IMF)."""
    print('Figure 11: Government interest expense')

    # ── Fetch from IMF datamapper API (indicator: ie, dataset: FPP) ──
    import urllib.request as _req

    series = {
        r'États-Unis': ('USA', palette[0], 2.5),
        'Canada':       ('CAN', palette[1], 2.5),
        'Italie':       ('ITA', palette[2], 2.5),
        'Royaume-Uni':  ('GBR', palette[4], 2),
        'Japon':        ('JPN', palette[3], 2),
        'Allemagne':    ('DEU', palette[7], 1.5),
    }

    fig, ax = new_figure(9, 4.5)

    for label, (iso, color, lw) in series.items():
        url = f'https://www.imf.org/external/datamapper/api/v1/ie/{iso}'
        try:
            resp = _req.urlopen(url, timeout=15)
            d = json.loads(resp.read())
            vals = d.get('values', {}).get('ie', {}).get(iso, {})
            years = sorted(int(y) for y in vals if 2000 <= int(y) <= 2024)
            yvals = [vals[str(y)] for y in years]
            ax.plot(years, yvals, color=color, linewidth=lw)
            # End-of-line label
            ax.text(years[-1] + 0.3, yvals[-1], label, fontsize=8,
                    color=color, fontweight='bold', va='center')
        except Exception as e:
            print(f'  ! {iso}: {e}')

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(2000, 2027)
    xticks = list(range(2000, 2026, 5))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)

    ax.set_ylim(0, 8)
    ax.set_yticks(range(0, 9, 1))
    ax.set_yticklabels([f'{y}\\%' for y in range(0, 9, 1)], fontsize=11)
    ax.set_ylabel(r"\% du PIB", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Source: FMI")
    save(fig, 'interest_expense.png')


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 5 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        overnight_rate_ca,
        overnight_vs_mortgage,
        transmission_taux,
        rate_vs_inflation_ca,
        inflation_vs_rate_2019,
        policy_rates_global,
        boc_balance_sheet,
        debt_to_gdp,
        phillips_curve_decades,
        fed_dot_plot,
        gross_vs_net_debt,
        interest_expense,
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
