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

    # ── Annotations ─────────────────────────────────────────────────
    # Post-2008 near-zero
    ax.annotate(r'Taux quasi nul apr\`{e}s 2008',
                xy=(pd.Timestamp('2010-06-01'), 0.5),
                xytext=(pd.Timestamp('2005-01-01'), 5.5),
                fontsize=9, color=palette[7],
                arrowprops=dict(arrowstyle='->', color=palette[7], lw=1.2))

    # COVID cut
    ax.annotate(r'COVID : 0.25\%',
                xy=(pd.Timestamp('2020-04-01'), 0.25),
                xytext=(pd.Timestamp('2016-01-01'), 1.8),
                fontsize=9, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.2))

    # 2022-23 hiking cycle peak
    peak_date = rate.loc['2022-01-01':].idxmax()
    peak_val = rate.loc[peak_date]
    ax.annotate(f'{peak_val:.1f}\\%',
                xy=(peak_date, peak_val),
                xytext=(peak_date - pd.DateOffset(years=3), peak_val + 0.5),
                fontsize=10, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

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
            linewidth=2, label=r'Taux hypoth\'{e}caire 5 ans')

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

    # Compute CPI y/y inflation from CPI level (CANCPIALLMINMEI)
    cpi_level = get_fred_data('CANCPIALLMINMEI', observation_start='2018-01-01')
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

    # ── Annotations ─────────────────────────────────────────────────
    # Inflation peak
    inflation_peak_date = cpi.idxmax()
    inflation_peak_val = cpi.max()
    ax.annotate(f'{inflation_peak_val:.1f}\\%',
                xy=(inflation_peak_date, inflation_peak_val),
                xytext=(inflation_peak_date + pd.DateOffset(months=6),
                        inflation_peak_val + 0.8),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    # "Retard de réaction" arrow between peak inflation and the rate at that time
    rate_at_peak = overnight.asof(inflation_peak_date)
    mid_y = (inflation_peak_val + rate_at_peak) / 2
    ax.annotate(r'Retard de r\'{e}action',
                xy=(inflation_peak_date - pd.DateOffset(months=3), mid_y),
                xytext=(pd.Timestamp('2020-09-01'), 7.0),
                fontsize=10, color=palette[0], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[0], lw=1.5))

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(pd.Timestamp('2019-01-01'), max(overnight.index.max(),
                                                  cpi.index.max()))
    xticks = list(range(2019, 2028, 1))
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
    add_source(ax, r"Source: Banque du Canada, FRED")
    save(fig, 'inflation_vs_rate_2019.png')


# =====================================================================
# Figure 5: Global policy rates (Fed, ECB, BoC, BoJ)
# =====================================================================
def policy_rates_global():
    """Policy rates of the Fed, ECB, BoC, and BoJ."""
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

    # BoJ: immediate rate (call rate)
    boj = get_fred_data('IRSTCB01JPM156N', observation_start='2000-01-01')

    fig, ax = new_figure(9, 4.5)

    ax.plot(fed.index, fed.values, color=palette[0], linewidth=2,
            label='Fed (taux des fonds)')
    ax.plot(boc.index, boc.values, color=palette[1], linewidth=2,
            label='BdC (taux directeur)')
    if len(ecb) > 0:
        ax.plot(ecb.index, ecb.values, color=palette[4], linewidth=2,
                label=r'BCE (taux de d\'{e}p\^{o}t)')
    if len(boj) > 0:
        ax.plot(boj.index, boj.values, color=palette[2], linewidth=2,
                label='BdJ (taux directeur)')

    # ZLB zone: light shading below 0.5%
    ax.axhspan(-1, 0.5, color=palette[7], alpha=0.08, linewidth=0)
    ax.text(pd.Timestamp('2001-01-01'), 0.1,
            r'\textit{Zone de la borne z\'{e}ro}',
            fontsize=8, color=palette[7], va='center')

    # ── Axis formatting ─────────────────────────────────────────────
    end_date = max(s.index.max() for s in [fed, boc, ecb, boj]
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

    # ── Annotate QE and QT periods ──────────────────────────────────
    # QE: roughly March 2020 to early 2022
    # QT: roughly mid-2022 onwards
    # Find peak for positioning
    peak_date = assets.idxmax()
    peak_val = assets.max()

    ax.annotate('QE',
                xy=(pd.Timestamp('2020-10-01'), peak_val * 0.75),
                fontsize=14, color=palette[1], fontweight='bold',
                ha='center')
    if peak_date < pd.Timestamp('2024-01-01'):
        ax.annotate('QT',
                    xy=(pd.Timestamp('2023-06-01'), peak_val * 0.55),
                    fontsize=14, color=palette[2], fontweight='bold',
                    ha='center')

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
# Figure 7: Government debt-to-GDP ratios (1990–2025)
# =====================================================================
def debt_to_gdp():
    """Government gross debt as share of GDP for Canada, US, Japan, France."""
    print('Figure 7: Government debt-to-GDP ratios')

    series = {
        'Canada':    'GGGDTACAA188N',
        'US':        'GGGDTAUSA188N',
        'Japan':     'GGGDTAJPA188N',
        'France':    'GGGDTAFRA188N',
    }

    colors = {
        'Canada':    palette[1],
        'US':        palette[0],
        'Japan':     palette[2],
        'France':    palette[4],
    }

    labels = {
        'Canada':    'Canada',
        'US':        r"\'{E}tats-Unis",
        'Japan':     'Japon',
        'France':    r"France",
    }

    fig, ax = new_figure(9, 4.5)

    data_dict = {}
    for name, fred_id in series.items():
        try:
            s = get_fred_data(fred_id, observation_start='1990-01-01')
            s = s.dropna()
            if len(s) > 0:
                data_dict[name] = s
                ax.plot(s.index, s.values, color=colors[name],
                        linewidth=2, label=labels[name])
        except Exception:
            pass

    if len(data_dict) == 0:
        print('  ! No debt-to-GDP data. Skipping.')
        plt.close(fig)
        return

    # ── End-of-line labels ──────────────────────────────────────────
    for name, s in data_dict.items():
        last_val = s.iloc[-1]
        last_date = s.index[-1]
        # Offset to avoid overlap
        va = 'center'
        ax.text(last_date + pd.DateOffset(months=6), last_val,
                labels[name], fontsize=9, color=colors[name],
                fontweight='bold', va=va)

    # ── Axis formatting ─────────────────────────────────────────────
    end_date = max(s.index.max() for s in data_dict.values())
    ax.set_xlim(pd.Timestamp('1990-01-01'),
                end_date + pd.DateOffset(years=3))

    xticks = list(range(1990, 2030, 5))
    ax.set_xticks([pd.Timestamp(f'{y}-01-01') for y in xticks])
    ax.set_xticklabels([str(y) for y in xticks], fontsize=10)

    ax.set_ylim(0, 260)
    ax.set_yticks(range(0, 280, 40))
    ax.set_yticklabels([f'{y}\\%' for y in range(0, 280, 40)], fontsize=11)
    ax.set_ylabel(r"Dette / PIB (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    # No legend — using end-of-line labels instead
    add_source(ax, r"Source: FRED (FMI via FRED)")
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
        r"Ann\'{e}es 1960": (1960, 1969, palette[4]),
        r"Ann\'{e}es 1970": (1970, 1979, palette[2]),
        r"Ann\'{e}es 1980": (1980, 1989, palette[3]),
        r"Ann\'{e}es 1990": (1990, 1999, palette[1]),
        r"Ann\'{e}es 2000": (2000, 2009, palette[0]),
        r"Ann\'{e}es 2010": (2010, 2019, palette[7]),
        r"Ann\'{e}es 2020": (2020, 2029, palette[5]),
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
    ax.set_xlabel(r"Taux de ch\^{o}mage (\%)", fontsize=11, ha='center')
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
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 5 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        overnight_rate_ca,
        overnight_vs_mortgage,
        rate_vs_inflation_ca,
        inflation_vs_rate_2019,
        policy_rates_global,
        boc_balance_sheet,
        debt_to_gdp,
        phillips_curve_decades,
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
