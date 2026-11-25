"""
ECON50803 — Session 5 : Figure Generation
============================================

Generates all matplotlib figures for Session 5 slides (monetary and
fiscal policy). Figures are exported as native vector PDFs. All figure labels, axis titles, legends, and
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
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "plot-common"))
import teaching_plot_utils
teaching_plot_utils.init(
    figures_dir=str(Path(__file__).resolve().parents[1] / 'Figures'),
    env_file=str(Path(__file__).resolve().parents[2] / '.env'))
from teaching_plot_utils import *


def _s5_fred_series(series_id, start):
    """Download public FRED observations without an API key."""
    from io import StringIO
    import requests

    response = requests.get(
        'https://fred.stlouisfed.org/graph/fredgraph.csv',
        params={'id': series_id, 'cosd': start},
        timeout=30,
    )
    response.raise_for_status()
    data = pd.read_csv(StringIO(response.text), index_col=0, parse_dates=True)
    return pd.to_numeric(data[series_id], errors='coerce').dropna().loc[start:]


def _canadian_overnight_rate(start):
    """Use the BoC target where available and the OECD overnight rate before it."""
    target = get_valet_series('V39079', start=start).dropna()
    if start >= '2009-04-21':
        return target
    history = _s5_fred_series('IRSTCI01CAM156N', start)
    return pd.concat([history.loc[history.index < target.index[0]], target])


def _last_complete_month():
    """Timestamp for the first day of the most recently completed month."""
    return (pd.Timestamp.today().to_period('M') - 1).start_time


# =====================================================================
# Figure 1: Bank of Canada overnight rate (1996–2026)
# =====================================================================
def overnight_rate_ca():
    """Canadian overnight rate since 1996."""
    print('Figure 1: Bank of Canada overnight rate')

    rate = _canadian_overnight_rate('1996-01-01')

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
    ax.set_ylabel(r"Taux à un jour (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Sources : OCDE/FRED (avant avr. 2009), Banque du Canada (cible)")
    save(fig, 'overnight_rate_ca.pdf')


# =====================================================================
# Figure 2: Overnight rate vs 5-year mortgage rate
# =====================================================================
def overnight_vs_mortgage():
    """Bank of Canada overnight rate vs 5-year conventional mortgage rate."""
    print('Figure 2: Overnight rate vs 5-year mortgage rate')

    overnight = _canadian_overnight_rate('2000-01-01')
    # V121764: posted 5-year conventional mortgage rate, weekly.
    mortgage = get_valet_series('V121764', start='2000-01-01').dropna()

    fig, ax = new_figure(9, 4.5)

    ax.plot(overnight.index, overnight.values, color=palette[0],
            linewidth=2, label='Taux à un jour')
    ax.plot(mortgage.index, mortgage.values, color=palette[2],
            linewidth=2, label=r'Taux hypothécaire affiché (5 ans)')

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

    ymax = max(8, int(tick_ceil(max(overnight.max(), mortgage.max()), 1)))
    ax.set_ylim(0, ymax)
    ax.set_yticks(range(0, ymax + 1))
    ax.set_yticklabels([f'{y}\\%' for y in range(0, ymax + 1)], fontsize=11)
    ax.set_ylabel(r"\%", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, r"Sources : OCDE/FRED (avant avr. 2009), Banque du Canada")
    save(fig, 'overnight_vs_mortgage.pdf')


# =====================================================================
# Figure 2b: Transmission chain — overnight → 5yr bond → 5yr mortgage
# =====================================================================
def transmission_taux():
    """Overnight rate, 5-year GoC bond yield, 5-year mortgage rate."""
    print('Figure 2b: Transmission du taux directeur')

    last_complete = _last_complete_month()
    overnight = _canadian_overnight_rate('2000-01-01').resample('MS').mean().loc[:last_complete]
    bond5 = get_valet_series('BD.CDN.5YR.DQ.YLD', start='2000-01-01').resample('MS').mean().loc[:last_complete]
    mortgage = get_valet_series('V121764', start='2000-01-01').resample('MS').mean().loc[:last_complete]

    fig, ax = new_figure(9, 4.5)

    ax.plot(overnight.index, overnight.values, color=palette[0],
            linewidth=2, label='Taux à un jour')
    ax.plot(bond5.index, bond5.values, color=palette[1],
            linewidth=2, label='Obligations du Canada (5 ans)')
    ax.plot(mortgage.index, mortgage.values, color=palette[2],
            linewidth=2, label=r'Taux hypothécaire affiché (5 ans)')

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
    ax.legend(frameon=False, fontsize=10, loc='upper right')
    add_source(ax, r"Sources : OCDE/FRED et Banque du Canada, moyennes mensuelles")
    save(fig, 'transmission_taux.pdf')


# =====================================================================
# Figure 3: Canadian policy rate and year-over-year CPI inflation since 1996
# =====================================================================
def rate_vs_inflation_ca():
    """Daily overnight target and monthly all-items CPI with its 1–3% target range."""
    from stats_can.sc import vectors_to_df

    start = pd.Timestamp('1996-01-01')
    today = pd.Timestamp.today().normalize()
    # StatCan v39079 is the BoC's announced target, available back to 1992.
    daily_periods = (today - start).days + 1
    rate = vectors_to_df('39079', periods=daily_periods)['v39079'].dropna().sort_index()
    rate = rate.loc[start:today]
    # StatCan v41690973: national, all-items CPI, not seasonally adjusted.
    months = today.to_period('M').ordinal - start.to_period('M').ordinal + 13
    level = vectors_to_df('41690973', periods=months)['v41690973'].sort_index().asfreq('MS')
    inflation = level.pct_change(12, fill_method=None).mul(100).loc[start:today]
    inflation.index = inflation.index + pd.offsets.MonthEnd(0)

    fig, ax = new_figure(9, 4.5)
    for begin, end in recessions_ca:
        if begin >= start:
            recession = ax.axvspan(begin, end, color='grey', alpha=0.14, linewidth=0)
    band = ax.axhspan(1, 3, color=palette[1], alpha=0.20, linewidth=0)
    target = ax.axhline(2, color='#17854f', linewidth=1, linestyle='--')
    rate_line, = ax.step(rate.index, rate, where='post', color=palette[0], linewidth=1.8)
    cpi_line, = ax.plot(inflation.index, inflation, color=palette[2], linewidth=1.5)

    end = max(rate.index[-1], inflation.last_valid_index())
    years = list(range(start.year, end.year + 1, 2))
    ax.set_xticks([pd.Timestamp(year, 1, 1) for year in years], labels=years, fontsize=10)
    ax.set_xlim(start, end)
    low = 2 * int(np.floor(min(rate.min(), inflation.min()) / 2))
    high = tick_ceil(max(rate.max(), inflation.max()), 2)
    yticks = list(range(low, high + 1, 2))
    ax.set_yticks(yticks, labels=[rf'{y}\%' for y in yticks], fontsize=11)
    ax.set_ylim(low, high)
    style_axes(ax)
    ax.legend([rate_line, cpi_line, (band, target), recession],
              ['Taux directeur', 'Inflation de l’IPC (sur 12 mois)',
               r'Cible de 2\,\% (fourchette de 1 à 3\,\%)', 'Récessions'],
              loc='upper left', ncol=2, frameon=False, fontsize=10)
    add_source(ax, 'Sources : Banque du Canada, Statistique Canada')
    save(fig, 'rate_vs_inflation_ca.pdf')


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
    add_source(ax, r"Sources : Statistique Canada et Banque du Canada")
    save(fig, 'inflation_vs_rate_2019.pdf')


# =====================================================================
# Figure 5: Global policy rates (Fed, ECB, BoC)
# =====================================================================
def policy_rates_global():
    """Policy rates of the Fed, ECB, and BoC."""
    print('Figure 5: Global policy rates')

    start = '2000-01-01'
    cutoff = _last_complete_month()
    fed = _s5_fred_series('FEDFUNDS', start).loc[:cutoff]
    boc = _canadian_overnight_rate(start).resample('MS').last().loc[:cutoff]
    ecb = _s5_fred_series('ECBDFR', start).resample('MS').last().loc[:cutoff]

    fig, ax = new_figure(9, 4.5)

    ax.plot(fed.index, fed.values, color=palette[4], linewidth=2,
            label='Fed (taux effectif moyen)')
    ax.plot(boc.index, boc.values, color=palette[2], linewidth=2,
            label='BdC (taux à un jour)')
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
    add_source(ax, r"Sources : FRED et Banque du Canada")
    save(fig, 'policy_rates_global.pdf')


# =====================================================================
# Figure 6: Bank of Canada total assets (QE visible)
# =====================================================================
def boc_balance_sheet():
    """Bank of Canada total assets showing QE and QT periods."""
    print('Figure 6: Bank of Canada balance sheet')

    # Valet V36610 records total assets weekly in millions of Canadian dollars.
    assets = get_valet_series('V36610', start='2007-01-01').dropna() / 1000

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
    last = assets.index[-1]
    add_source(ax, f'Source : Banque du Canada ({last.day} {MONTH_FR[last.month]} {last.year})')
    save(fig, 'boc_balance_sheet.pdf')


def federal_debt_gdp_ca():
    """Federal accumulated deficit in % of GDP, by March fiscal year-end."""
    from io import BytesIO
    import requests

    url = ('https://www.canada.ca/en/department-finance/services/publications/'
           'fiscal-reference-tables/2025/part-1.html')
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    fiscal, = pd.read_html(BytesIO(response.content), attrs={'id': 'tbl2'})
    years = fiscal['Year'].astype(str)
    rows = fiscal.loc[years.str.fullmatch(r'\d{4}-\d{2}'), ['Year', 'Accumulated deficit']].copy()
    rows['year_end'] = rows['Year'].str[:4].astype(int) + 1
    debt = pd.to_numeric(rows.set_index('year_end')['Accumulated deficit']).sort_index().loc[1994:2007]
    if debt.isna().any() or not np.array_equal(debt.index, np.arange(1994, 2008)):
        raise ValueError('Expected federal debt observations for every March from 1994 to 2007')

    fig, ax = new_figure(9, 4.4)
    ax.plot(debt.index, debt, color=palette[0], linewidth=2.6)
    for year, align in [(debt.idxmax(), 'center'), (debt.index[-1], 'right')]:
        value = debt.loc[year]
        ax.plot(year, value, 'o', color=palette[0], markersize=4, clip_on=False)
        label = f'{value:.1f}'.replace('.', ',') + r'\,\%'
        offset = (0, 8) if align == 'center' else (0, 16)
        ax.annotate(label, (year, value), xytext=offset, textcoords='offset points',
                    ha=align, fontsize=11, color=palette[0])

    # Plain-text ticks use the course's Fira Sans instead of TeX math numerals.
    xticks = debt.index
    yticks = range(30, 71, 10)
    ax.set_xticks(xticks, labels=[str(year) for year in xticks], fontsize=11)
    ax.set_yticks(yticks, labels=[str(value) for value in yticks], fontsize=11)
    ax.set_xlim(xticks[0], xticks[-1])
    ax.set_ylim(yticks[0], yticks[-1])
    ax.set_xlabel("Année de clôture de l’exercice (31 mars)", fontsize=11)
    ax.set_ylabel(r"Déficit accumulé, en \% du PIB", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.025)
    style_axes(ax)
    add_source(ax, r"Finances Canada, Tableaux de référence financiers (2025), tableau 2")
    save(fig, 'ess_dette_federale_pib_canada.pdf')


# =====================================================================
# Figure 7: Government debt-to-GDP — horizontal bar chart (latest)
# =====================================================================
# Annual observations from the IMF October 2026 WEO workbook, Countries sheet.
# GGXWDG_NGDP and GGXWDN_NGDP are general government debt as a share of GDP.
# https://data.imf.org/datasets/WEO
_DEBT_YEAR = 2025
_DEBT_GROSS = {
    'Canada': 113.583,
    'États-Unis': 124.377,
    'Japon': 204.775,
    'Royaume-Uni': 102.056,
    'Allemagne': 62.658,
    'France': 115.534,
    'Italie': 137.105,
    'Espagne': 100.513,
    'Chine': 98.609,
    'Brésil': 93.329,
    'Inde': 84.261,
    'Mexique': 61.670,
    'Corée du Sud': 52.417,
}


def debt_to_gdp():
    """Horizontal bar chart of government gross debt / GDP (IMF WEO, 2025)."""
    print('Figure 7: Government debt-to-GDP ratios (bar chart)')

    ranked = sorted(_DEBT_GROSS.items(), key=lambda item: item[1], reverse=True)
    labels, values = zip(*ranked)

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
    add_source(ax, f'Source : FMI, WEO d’octobre 2026 (données de {_DEBT_YEAR})')
    save(fig, 'debt_to_gdp.pdf')


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
    save(fig, 'phillips_curve_decades.pdf')


# =====================================================================
# Figure 9: Fed dot plot (September 2026 FOMC SEP)
# =====================================================================
def fed_dot_plot():
    """FOMC dot plot: each participant's projected federal funds rate."""
    print('Figure 9: Fed dot plot (septembre 2026)')

    # September 2026 FOMC SEP, Figure 2: published rate/count pairs.
    # https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm
    dot_data = {
        '2026': {3.875: 2, 4.125: 12, 4.375: 4},
        '2027': {3.125: 1, 3.625: 3, 4.125: 6, 4.375: 8},
        '2028': {3.125: 4, 3.375: 1, 3.625: 3, 3.875: 5, 4.125: 4},
        '2029': {2.875: 1, 3.125: 4, 3.375: 2, 3.625: 7, 3.875: 3},
        'Plus long\nterme': {
            2.875: 1, 3.000: 6, 3.125: 1, 3.250: 2, 3.375: 1,
            3.500: 2, 3.625: 2, 3.750: 1, 3.875: 2,
        },
    }

    categories = list(dot_data.keys())
    x_positions = {cat: i for i, cat in enumerate(categories)}

    fig, ax = new_figure(8, 5)

    # Dot radius in data coords (for side-by-side placement)
    dot_spacing = 0.073  # horizontal offset between same-rate dots

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
                        color=palette[0], markersize=6.5,
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
    y_min, y_max = 2.50, 4.75
    ax.set_ylim(y_min, y_max)
    yticks_major = np.arange(2.50, 4.51, 0.50)
    ax.set_yticks(yticks_major)
    ax.set_yticklabels([f'{y:.1f}\\%' for y in yticks_major], fontsize=11)

    # Minor ticks at every 0.25% for finer grid
    yticks_minor = np.arange(2.50, 4.76, 0.25)
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
               markersize=6.5, markeredgecolor='white', markeredgewidth=0.5,
               label='Projection individuelle'),
        Line2D([0], [0], color=palette[2], linewidth=2.5,
               label=r'Médiane'),
    ]
    ax.legend(handles=legend_elements, frameon=False, fontsize=9,
              loc='upper right', bbox_to_anchor=(1.0, 1.0))

    style_axes(ax, xgrid=False)
    add_source(ax, r"Source : Réserve fédérale, SEP de septembre 2026")
    save(fig, 'fed_dot_plot.pdf')


# =====================================================================
# Figure 10: Gross vs Net Debt (bar chart, 2025)
# =====================================================================
def gross_vs_net_debt():
    """Grouped bar chart: gross vs net debt as % of GDP (2025, IMF WEO)."""
    print('Figure 10: Gross vs net debt comparison')

    countries = ['CAN', 'DEU', 'GBR', r'É.-U.', 'FRA', 'ITA', 'JPN']
    names = ['Canada', 'Allemagne', 'Royaume-Uni', 'États-Unis', 'France', 'Italie', 'Japon']
    gross = [_DEBT_GROSS[country] for country in names]
    net = [10.429, 47.12, 93.609, 96.702, 108.357, 127.704, 132.358]

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
    add_source(ax, f'Source : FMI, WEO d’octobre 2026 (données de {_DEBT_YEAR})')
    save(fig, 'gross_vs_net_debt.pdf')


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
    save(fig, 'interest_expense.pdf')


# =====================================================================
# Figure 12: Overnight rate — last 12 months (conjoncture)
# =====================================================================
def overnight_rate_recent():
    """Bank of Canada overnight target rate, last 12 months."""
    print('Figure 12: Taux directeur (12 derniers mois)')

    rate = get_valet_series('V39079', start='2025-01-01')
    rate = rate.dropna()

    fig, ax = new_figure(9, 4.5)

    ax.plot(rate.index, rate.values, color=palette[0], linewidth=2.5)

    # Horizontal dashed line at latest value with annotation
    latest_val = rate.iloc[-1]
    ax.axhline(latest_val, color=palette[0], linewidth=1, linestyle='--',
               alpha=0.5)
    ax.annotate(f'{latest_val:.2f}\\%',
                xy=(rate.index[-1], latest_val),
                xytext=(-15, 12), textcoords='offset points',
                fontsize=11, color=palette[2], fontweight='bold')

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(rate.index.min(), rate.index.max())
    # Monthly ticks with French abbreviations
    monthly = pd.date_range(rate.index.min().replace(day=1),
                            rate.index.max(), freq='MS')
    ax.set_xticks(monthly)
    ax.set_xticklabels([french_date_label(d) for d in monthly], fontsize=10)

    ymin = max(0, int(rate.min()) - 1)
    ymax = int(rate.max()) + 2
    ax.set_ylim(ymin, ymax)
    ax.set_yticks(np.arange(ymin, ymax + 0.5, 0.5))
    ax.set_yticklabels([f'{y:.1f}\\%' for y in np.arange(ymin, ymax + 0.5, 0.5)],
                       fontsize=11)
    ax.set_ylabel(r"Taux directeur (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Source: Banque du Canada (Valet)")
    save(fig, 'overnight_rate_recent.pdf')


# =====================================================================
# Figure 13: Canada unemployment rate — last 12 months (conjoncture)
# =====================================================================
def unemployment_rate_recent():
    """Canada unemployment rate, last 12 months."""
    print('Figure 13: Taux de chômage (12 derniers mois)')

    # Try FRED first, then Valet fallback
    try:
        unemp = get_fred_data('LRUNTTTTCAM156S', observation_start='2025-01-01')
        unemp = unemp.dropna()
        if len(unemp) == 0:
            raise ValueError('Empty series')
        source_text = r"Source: FRED / Statistique Canada"
    except Exception:
        unemp = get_valet_series('V2062815', start='2025-01-01')
        unemp = unemp.dropna()
        source_text = r"Source: Banque du Canada (Valet)"

    fig, ax = new_figure(9, 4.5)

    ax.plot(unemp.index, unemp.values, color=palette[2], linewidth=2.5)

    # Annotate most recent data point
    latest_val = unemp.iloc[-1]
    ax.annotate(f'{latest_val:.1f}\\%',
                xy=(unemp.index[-1], latest_val),
                xytext=(-15, 12), textcoords='offset points',
                fontsize=11, color=palette[2], fontweight='bold')

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(unemp.index.min(), unemp.index.max())
    monthly = pd.date_range(unemp.index.min().replace(day=1),
                            unemp.index.max(), freq='MS')
    ax.set_xticks(monthly)
    ax.set_xticklabels([french_date_label(d) for d in monthly], fontsize=10)

    ymin = max(0, int(unemp.min()) - 1)
    ymax = int(unemp.max()) + 2
    ax.set_ylim(ymin, ymax)
    ax.set_yticks(range(ymin, ymax + 1))
    ax.set_yticklabels([f'{y}\\%' for y in range(ymin, ymax + 1)], fontsize=11)
    ax.set_ylabel(r"Taux de chômage (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, source_text)
    save(fig, 'unemployment_rate_recent.pdf')


# =====================================================================
# Figure 14: CPI inflation — last 12 months (conjoncture)
# =====================================================================
def inflation_recent():
    """CPI inflation (year-over-year) in Canada, last 12 months."""
    print('Figure 14: Inflation IPC (12 derniers mois)')

    # Fetch CPI level starting from Dec 2023 to compute YoY from Jan 2025
    cpi_level = get_valet_series('V41690973', start='2023-12-01')
    cpi_level = cpi_level.dropna()

    # Compute year-over-year inflation
    inflation = cpi_level.pct_change(periods=12) * 100
    inflation = inflation.dropna()
    inflation = inflation.loc['2025-01-01':]

    fig, ax = new_figure(9, 4.5)

    # Target band (1%–3%)
    ax.axhspan(1, 3, color=palette[1], alpha=0.1, linewidth=0)

    # Target line at 2%
    ax.axhline(2, color=palette[1], linewidth=1.5, linestyle='--',
               label=r"Cible (2\%)")

    ax.plot(inflation.index, inflation.values, color=palette[0],
            linewidth=2.5, label='Inflation IPC (a/a)', zorder=3)

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(inflation.index.min(), inflation.index.max())
    monthly = pd.date_range(inflation.index.min().replace(day=1),
                            inflation.index.max(), freq='MS')
    ax.set_xticks(monthly)
    ax.set_xticklabels([french_date_label(d) for d in monthly], fontsize=10)

    ax.set_ylim(0, 4)
    ax.set_yticks(range(0, 5))
    ax.set_yticklabels([f'{y}\\%' for y in range(0, 5)], fontsize=11)
    ax.set_ylabel(r"Inflation IPC (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, r"Source: Banque du Canada (Valet)")
    save(fig, 'inflation_recent.pdf')


# =====================================================================
# Figure 15: Combined Canada conjoncture (single plot)
# =====================================================================
def conjoncture_canada():
    """Single chart: overnight rate, unemployment, CPI inflation."""
    print('Figure 15: Conjoncture Canada')

    from stats_can import vectors_to_df

    rate = get_valet_series('V39079', start='2025-01-01').resample('MS').last()
    # Statistics Canada table 14-10-0287-01, age 15+, seasonally adjusted.
    unemp = vectors_to_df(['v2062815'], periods=36)['v2062815'].sort_index().loc['2025-01-01':]
    cpi = get_valet_series('V41690973', start='2024-01-01').asfreq('MS')
    inflation = (cpi.pct_change(12, fill_method=None) * 100).loc['2025-01-01':]

    # Compare the three series through the latest month with all releases.
    last = min(rate.last_valid_index(), unemp.last_valid_index(), inflation.last_valid_index())
    months = pd.date_range('2025-01-01', last, freq='MS')
    rate, unemp, inflation = (series.reindex(months) for series in (rate, unemp, inflation))
    if any(series.isna().any() for series in (rate, unemp, inflation)):
        raise ValueError('Missing observations in the Canadian outlook figures')

    # ── 2. Single-axis plot ───────────────────────────────────────────
    fig, ax = new_figure(9, 4.5)

    ax.plot(rate.index, rate.values, color=palette[0], linewidth=2.5,
            label='Taux directeur', marker='o', markersize=5, clip_on=False)
    ax.plot(unemp.index, unemp.values, color=palette[2], linewidth=2.5,
            label=r'Taux de chômage', marker='o', markersize=5, clip_on=False)
    ax.plot(inflation.index, inflation.values, color=palette[1], linewidth=2.5,
            label='Inflation IPC (a/a)', marker='o', markersize=5, clip_on=False)

    # ── Axis formatting ───────────────────────────────────────────────
    ticks = months[::3]
    if ticks[-1] != last:
        ticks = ticks.append(months[-1:])
    ax.set_xticks(ticks)
    ax.set_xticklabels([french_date_label(date) for date in ticks], fontsize=10)
    ax.set_xlim(months[0], last)

    ax.set_ylim(0, 8)
    ax.set_yticks(range(0, 9))
    ax.set_yticklabels([f'{y}\\%' for y in range(0, 9)], fontsize=11)
    ax.set_ylabel(r"\%", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='lower left',
              bbox_to_anchor=(0.0, 0.0))
    add_source(ax, f'Sources : Statistique Canada et Banque du Canada ({MONTH_FR[last.month]} {last.year})')
    save(fig, 'conjoncture_canada.pdf')


# =====================================================================
# Bank of Canada tightening cycles (restore the original chart generator)
# =====================================================================
def boc_tightening_cycles():
    """Cumulative rate increases relative to the pre-cycle policy rate.

    FRED's monthly central-bank rate dates the 1997/2004 observations to
    the first of each month, as in the original chart. The constant spread
    between the Bank Rate and overnight target cancels in the differences.
    The 2017/2022 cycles use exact business-day observations from Valet.
    """
    print('Figure: Bank of Canada tightening cycles')
    monthly = get_fred_data('IRSTCB01CAM156N',
                            observation_start='1997-01-01',
                            observation_end='2006-06-01').dropna()
    daily = get_valet_series('V39079', start='2017-01-01').dropna()
    cycles = [
        ('1997', monthly, '1997-07-01', '1998-09-01', palette[4]),
        ('2004', monthly, '2004-09-01', '2006-05-01', palette[2]),
        ('2017', daily, '2017-07-12', '2018-10-24', palette[1]),
        ('2022', daily, '2022-03-02', '2023-07-12', palette[0]),
    ]
    fig, ax = new_figure(9, 5)
    for label, rates, start, end, color in cycles:
        start = pd.Timestamp(start)
        baseline = rates.loc[rates.index < start].iloc[-1]
        cycle = rates.loc[start:pd.Timestamp(end) + pd.Timedelta(days=7)]
        # Valet records the effective business day after an announcement.
        cycle = cycle.loc[cycle.ne(cycle.shift()) & (cycle > baseline)]
        if cycle.empty:
            raise ValueError(f'No observations for tightening cycle {label}')
        days = (cycle.index - cycle.index[0]).days
        ax.step(days, cycle.values - baseline, where='post',
                color=color, linewidth=3, label=label)
    # Plain text keeps both axes in Fira Sans instead of TeX's math font.
    xticks = range(0, 651, 50)
    yticks = range(0, 6)
    ax.set_xlim(0, 650)
    ax.set_xticks(xticks, labels=[str(value) for value in xticks], fontsize=11)
    ax.set_ylim(0, 5)
    ax.set_yticks(yticks, labels=[str(value) for value in yticks], fontsize=11)
    ax.set_xlabel('Nombre de jours depuis la première hausse', fontsize=11)
    ax.set_ylabel('Points de pourcentage', fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, 'Source: Banque du Canada (Valet); FRED (mensuel: 1997/2004)')
    save(fig, 'boc_tightening_cycles.pdf')


# =====================================================================
# Canada's mid-1990s fiscal consolidation and monetary policy
# =====================================================================
def canada_1990s_fiscal_monetary():
    """Federal fiscal balances and end-of-month Bank of Canada policy rates."""
    from io import BytesIO
    import requests

    print('Figure: Canadian fiscal consolidation and policy rates')
    finance_url = ('https://www.canada.ca/en/department-finance/services/publications/'
                   'fiscal-reference-tables/2026/part-1.html')
    response = requests.get(finance_url, timeout=25)
    response.raise_for_status()
    table, = pd.read_html(BytesIO(response.content), attrs={'id': 'tbl2'})
    table.columns = table.columns.str.replace(r'\s+', ' ', regex=True)
    fiscal_years = table['Year'].astype(str)
    fiscal = table.loc[fiscal_years.str.fullmatch(r'\d{4}-\d{2}'),
                       ['Year', 'Budgetary surplus or deficit (-)']].copy()
    fiscal['year_end'] = fiscal['Year'].str[:4].astype(int) + 1
    years = pd.Index(range(1993, 2000))
    balance = pd.to_numeric(fiscal.set_index('year_end')['Budgetary surplus or deficit (-)']).reindex(years)

    fiscal_dates = pd.to_datetime([f'{year}-03-31' for year in years])
    months = pd.period_range('1993-01', fiscal_dates[-1], freq='M')
    # BIS compilation: official Bank Rate through May 1994, then the overnight target.
    response = requests.get(
        'https://stats.bis.org/api/v1/data/BIS,WS_CBPOL,1.0/M.CA',
        params={'startPeriod': str(months[0]), 'endPeriod': str(months[-1]), 'format': 'csv'},
        timeout=25,
    )
    response.raise_for_status()
    policy = pd.read_csv(BytesIO(response.content), usecols=['TIME_PERIOD', 'OBS_VALUE'])
    policy.index = pd.PeriodIndex(policy['TIME_PERIOD'], freq='M')
    policy_rate = pd.to_numeric(policy['OBS_VALUE']).reindex(months)
    if balance.isna().any() or policy_rate.isna().any():
        raise ValueError('Incomplete Canadian historical budget or policy-rate series')

    fig, fiscal_ax = new_figure(11.4, 5.55)
    rates_ax = fiscal_ax.twinx()
    fiscal_ax.axhline(0, color=palette[7], linewidth=1.0, zorder=2)
    fiscal_ax.plot(fiscal_dates, balance,
                   color=palette[0], marker='o', markersize=5, linewidth=2.8, zorder=3)
    rates_ax.plot(months.to_timestamp(how='end').normalize(), policy_rate,
                  color=palette[1], linewidth=2.8, zorder=3)

    year_ticks = pd.to_datetime([f'{year}-01-01' for year in years])
    fiscal_ax.set_xlim(pd.Timestamp('1993-01-01'), fiscal_dates[-1] + pd.Timedelta(days=14))
    fiscal_ax.set_xticks(year_ticks, labels=[str(year) for year in years], fontsize=14)
    fiscal_ax.tick_params(axis='x', color=palette[7], length=3)
    style_axes(fiscal_ax)
    fiscal_ax.grid(axis='y', color=palette[7], alpha=0.25, linestyle='-', linewidth=0.65)
    fiscal_ax.spines['bottom'].set_color(palette[7])
    rates_ax.spines[['left', 'top', 'bottom']].set_visible(False)

    for axis, title, source_note, ticks, color, side, x in [
        (fiscal_ax, r'Solde budgétaire fédéral (\% du PIB)',
         'Finances Canada, exercices clos en mars', range(-6, 3), palette[0], 'left', 0),
        (rates_ax, r'Taux directeur (\%)',
         'Banque du Canada via la BRI, données de fin de mois', range(2, 10), '#147d4c', 'right', 1),
    ]:
        axis.set_ylim(ticks[0], ticks[-1])
        axis.set_yticks(ticks, labels=[rf'\textminus{{}}{abs(tick)}' if tick < 0 else str(tick)
                                     for tick in ticks], fontsize=14)
        axis.tick_params(axis='y', colors=color, length=3)
        axis.spines[side].set_color(color)
        axis.set_title(rf'\textbf{{{title}}}', loc=side, fontsize=16, color=color, pad=20)
        axis.text(x, 1.01, source_note, transform=axis.transAxes, ha=side, va='bottom', fontsize=10)
    save(fig, 's5_canada_1990s_fiscal_monetary.pdf')


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
        boc_tightening_cycles,
        canada_1990s_fiscal_monetary,
        boc_balance_sheet,
        debt_to_gdp,
        federal_debt_gdp_ca,
        phillips_curve_decades,
        fed_dot_plot,
        gross_vs_net_debt,
        interest_expense,
        overnight_rate_recent,
        unemployment_rate_recent,
        inflation_recent,
        conjoncture_canada,
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
