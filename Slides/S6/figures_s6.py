"""
ECON50803 — Session 6 : Figure Generation
============================================

Generates all matplotlib figures for Session 6 slides (commerce
international et economie ouverte). All figure labels, axis titles,
legends, and annotations are in French.

Run from Slides/S6/:
    python3 figures_s6.py
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
# Figure 1: Trade openness (X+M)/Y — Canada, US, China, India
# =====================================================================
def trade_openness():
    """Trade openness (exports + imports as % of GDP) for four countries."""
    print('Figure 1: Trade openness')

    countries = {
        'CAN': ('Canada',      palette[1], 2.5),
        'USA': (r'États-Unis', palette[0], 2.5),
        'CHN': ('Chine',       palette[2], 2),
        'IND': ('Inde',        palette[3], 2),
    }

    fig, ax = new_figure(9, 4.5)

    last_year = 1960
    for iso, (label, color, lw) in countries.items():
        s = _get_worldbank('NE.TRD.GNFS.ZS', iso, start=1960, end=2024)
        s = s.dropna()
        if len(s) == 0:
            print(f'  ! No data for {iso}. Skipping.')
            continue
        ax.plot(s.index, s.values, color=color, linewidth=lw, label=label)
        last_year = max(last_year, s.index[-1])

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(1960, last_year)
    xticks = list(range(1960, last_year + 1, 10))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)

    ax.set_ylim(0, 90)
    yticks = list(range(0, 91, 10))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}\\%' for y in yticks], fontsize=11)
    ax.set_ylabel(r"$(X + M) / Y$ (\%)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0))
    add_source(ax, r"Source: Banque mondiale")
    save(fig, 'trade_openness.png')


# =====================================================================
# Figure 2: US trade balance (goods & services) vs current account
# =====================================================================
def us_nx_vs_ca():
    """US trade balance (goods & services) and current account as % of GDP."""
    print('Figure 2: US trade balance vs current account')

    # World Bank: external balance on goods & services (% of GDP)
    nx = _get_worldbank('NE.RSB.GNFS.ZS', 'USA', start=1970, end=2024)
    nx = nx.dropna()

    # World Bank: current account balance (% of GDP)
    ca = _get_worldbank('BN.CAB.XOKA.GD.ZS', 'USA', start=1970, end=2024)
    ca = ca.dropna()

    fig, ax = new_figure(9, 4.5)

    ax.plot(nx.index, nx.values, color=palette[0], linewidth=2,
            label='Balance commerciale (biens et services)')
    ax.plot(ca.index, ca.values, color=palette[2], linewidth=2,
            label='Compte courant')
    ax.axhline(0, color='black', linewidth=0.5)

    # Shading below zero (deficit)
    ax.fill_between(ca.index, ca.values, 0,
                    where=ca.values < 0, interpolate=True,
                    color=palette[2], alpha=0.1, linewidth=0)

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(1970, ca.index.max() + 2)
    xticks = list(range(1970, 2030, 10))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)

    ax.set_ylim(-7, 2)
    yticks = list(range(-7, 3, 1))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'$-${abs(y)}\\%' if y < 0
                        else f'{y}\\%' for y in yticks], fontsize=11)
    ax.set_ylabel(r"(\% du PIB)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=9, loc='lower left',
              bbox_to_anchor=(0.0, 0.0))
    add_source(ax, r"Source: Banque mondiale")
    save(fig, 'us_nx_vs_ca.png')


# =====================================================================
# Figure 3: Global imbalances — CA balances as % of world GDP (stacked)
# =====================================================================
def current_accounts_divergence():
    """Stacked bar chart of current account balances / world GDP by group."""
    print('Figure 3: Global imbalances (stacked bars)')

    # ── Country groups ────────────────────────────────────────────
    groups = {
        'Exportateurs de pétrole': {
            'iso': ['SAU', 'RUS', 'NOR', 'ARE', 'KWT', 'QAT', 'IRN',
                    'IRQ', 'NGA', 'DZA', 'KAZ', 'AGO', 'VEN'],
            'color': '#b8f0d4', 'sign': 'surplus',   # lightest green
        },
        'Europe du Nord': {
            'iso': ['DEU', 'NLD', 'CHE', 'SWE', 'DNK'],
            'color': '#6ee0a8', 'sign': 'surplus',   # light green
        },
        'Chine': {
            'iso': ['CHN'],
            'color': '#1a9e5a', 'sign': 'surplus',   # dark green
        },
        'Asie de l\'Est': {
            'iso': ['JPN', 'KOR', 'SGP', 'MYS', 'THA', 'HKG'],
            'color': palette[1], 'sign': 'surplus',   # HECgreen #26d07c
        },
        'Anglosphère': {
            'iso': ['USA', 'GBR', 'AUS'],
            'color': '#cc2f33', 'sign': 'deficit',    # dark coral/red
        },
        'Europe périphérique': {
            'iso': ['ESP', 'ITA', 'GRC', 'PRT', 'TUR'],
            'color': '#ff9a9d', 'sign': 'deficit',    # light coral/pink
        },
    }

    ca_indicator = 'BN.CAB.XOKA.CD'   # Current account balance (BoP, current US$)
    gdp_indicator = 'NY.GDP.MKTP.CD'  # GDP (current US$)
    start, end = 1995, 2024

    # ── Fetch world GDP ───────────────────────────────────────────
    world_gdp = _get_worldbank(gdp_indicator, 'WLD', start=start, end=end)
    world_gdp = world_gdp.dropna()

    # ── Fetch and aggregate CA balances by group ──────────────────
    group_data = {}
    for gname, ginfo in groups.items():
        total = pd.Series(0.0, index=range(start, end + 1))
        for iso in ginfo['iso']:
            try:
                s = _get_worldbank(ca_indicator, iso, start=start, end=end)
                s = s.reindex(range(start, end + 1)).fillna(0)
                total = total.add(s, fill_value=0)
            except Exception:
                pass
        # Convert to % of world GDP
        common = total.index.intersection(world_gdp.index)
        pct = (total.loc[common] / world_gdp.loc[common]) * 100
        group_data[gname] = pct

    # ── Build stacked bar chart ───────────────────────────────────
    fig, ax = new_figure(10, 5)

    years = sorted(world_gdp.index)
    years = [y for y in years if start <= y <= end]
    bar_width = 0.75

    # Surplus groups (stack upward from 0)
    surplus_groups = [(g, d) for g, d in groups.items() if d['sign'] == 'surplus']
    pos_bottom = np.zeros(len(years))
    for gname, ginfo in surplus_groups:
        vals = np.array([group_data[gname].get(y, 0) for y in years])
        ax.bar(years, vals, bottom=pos_bottom, width=bar_width,
               color=ginfo['color'], label=gname, edgecolor='white', linewidth=0.3)
        pos_bottom += vals

    # Deficit groups (stack downward from 0)
    deficit_groups = [(g, d) for g, d in groups.items() if d['sign'] == 'deficit']
    neg_bottom = np.zeros(len(years))
    for gname, ginfo in deficit_groups:
        vals = np.array([group_data[gname].get(y, 0) for y in years])
        ax.bar(years, vals, bottom=neg_bottom, width=bar_width,
               color=ginfo['color'], label=gname, edgecolor='white', linewidth=0.3)
        neg_bottom += vals

    # ── Zero line ─────────────────────────────────────────────────
    ax.axhline(0, color='black', linewidth=0.7)

    # ── Axis formatting ───────────────────────────────────────────
    ax.set_xlim(start - 0.8, max(years) + 0.8)
    xticks = list(range(start, max(years) + 1, 2))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=10)

    ax.set_ylim(-2.5, 2.5)
    from matplotlib.ticker import FixedLocator
    yticks_vals = [v / 2 for v in range(-5, 6)]  # -2.5, -2.0, ..., 2.5
    ax.yaxis.set_major_locator(FixedLocator(yticks_vals))
    ax.set_yticklabels([f'{y:.1f}\\%' for y in yticks_vals], fontsize=11)
    ax.set_ylabel(r"(\% du PIB mondial)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # ── Legend ─────────────────────────────────────────────────────
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, fontsize=8, ncol=3, loc='lower right',
              frameon=False, handlelength=1.2, handletextpad=0.4,
              columnspacing=1.0)

    style_axes(ax)
    add_source(ax, r"Source: Banque mondiale")
    save(fig, 'current_accounts_divergence.png')


# =====================================================================
# Figure 3b: Gross saving rates — China, East Asia, Norway, Middle East, US
# =====================================================================
def saving_rates_divergence():
    """Gross saving as % of GDP for key surplus/deficit economies."""
    print('Figure 3b: Saving rates divergence')

    # Individual countries and aggregates
    countries = {
        'CHN': ('Chine',            palette[0], 2.5),   # navy
        'USA': (r'États-Unis',      palette[2], 2.5),   # coral
        'NOR': ('Norvège',          palette[1], 2),     # green
        'SAU': ('Arabie saoudite',  palette[3], 2),     # yellow
        'KOR': ('Corée du Sud',     palette[4], 2),     # blue
    }

    fig, ax = new_figure(9, 4.5)

    label_offsets = {}

    import time

    def _fetch_saving(iso, retries=3):
        """Fetch gross saving with retry logic for flaky API."""
        for attempt in range(retries):
            url = (f'https://api.worldbank.org/v2/country/{iso}/'
                   f'indicator/NY.GNS.ICTR.ZS?format=json&per_page=100'
                   f'&date=1980:2024')
            resp = requests.get(url, timeout=60)
            if resp.status_code == 200:
                payload = resp.json()
                if len(payload) < 2 or payload[1] is None:
                    return pd.Series(dtype=float)
                data = [(int(r['date']), r['value']) for r in payload[1]
                        if r['value'] is not None]
                s = pd.Series(dict(data)).sort_index()
                s.index.name = 'year'
                return s
            time.sleep(5)
        resp.raise_for_status()  # raise on final failure

    for iso, (label, color, lw) in countries.items():
        try:
            time.sleep(2)
            s = _fetch_saving(iso)
            s = s.dropna()
        except Exception as e:
            print(f'  ! Error fetching {iso}: {e}. Skipping.')
            continue
        if len(s) == 0:
            print(f'  ! No data for {iso}. Skipping.')
            continue
        ax.plot(s.index, s.values, color=color, linewidth=lw, label=label)

    # ── Axis formatting ─────────────────────────────────────────────
    last_year = max(ax.get_lines()[-1].get_xdata())
    ax.set_xlim(1980, last_year)
    xticks = list(range(1980, int(last_year) + 1, 5))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)

    ax.legend(fontsize=9, loc='upper left', frameon=False,
              bbox_to_anchor=(0.05, 1.0))

    ax.set_ylim(10, 60)
    yticks = list(range(10, 61, 10))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}\\%' for y in yticks], fontsize=11)
    ax.set_ylabel(r"Épargne brute (\% du PIB)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Source: Banque mondiale")
    save(fig, 'saving_rates_divergence.png')


# =====================================================================
# Figure 4: US current account balance as % of GDP
# =====================================================================
def us_ca_balance_gdp():
    """US current account balance as % of GDP, with fill coloring."""
    print('Figure 4: US current account balance (% GDP)')

    ca = _get_worldbank('BN.CAB.XOKA.GD.ZS', 'USA', start=1970, end=2024)
    ca = ca.dropna()

    if len(ca) == 0:
        print('  ! No current account data. Skipping.')
        return

    fig, ax = new_figure(9, 4.5)

    ax.plot(ca.index, ca.values, color=palette[0], linewidth=2)
    ax.axhline(0, color='black', linewidth=0.5)

    # Fill: red below zero (deficit), green above zero (surplus)
    ax.fill_between(ca.index, ca.values, 0,
                    where=ca.values < 0, interpolate=True,
                    color=palette[2], alpha=0.25, linewidth=0)
    ax.fill_between(ca.index, ca.values, 0,
                    where=ca.values >= 0, interpolate=True,
                    color=palette[1], alpha=0.25, linewidth=0)

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(ca.index.min(), ca.index.max())
    start_tick = ca.index.min() + (10 - ca.index.min() % 10) % 10
    xticks = list(range(start_tick, ca.index.max() + 1, 10))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)

    ax.set_ylim(-6, 2)
    yticks = list(range(-6, 3, 1))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'$-${abs(y)}\\%' if y < 0
                        else f'{y}\\%' for y in yticks], fontsize=11)
    ax.set_ylabel(r"(\% du PIB)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Source: Banque mondiale")
    save(fig, 'us_ca_balance_gdp.png')


# =====================================================================
# Figure 5: Canada current account balance as % of GDP
# =====================================================================
def ca_ca_balance_gdp():
    """Canada current account balance as % of GDP, with fill coloring."""
    print('Figure 5: Canada current account balance (% GDP)')

    ca = _get_worldbank('BN.CAB.XOKA.GD.ZS', 'CAN', start=1970, end=2024)
    ca = ca.dropna()

    if len(ca) == 0:
        print('  ! No current account data. Skipping.')
        return

    fig, ax = new_figure(9, 4.5)

    ax.plot(ca.index, ca.values, color=palette[0], linewidth=2)
    ax.axhline(0, color='black', linewidth=0.5)

    # Fill: red below zero (deficit), green above zero (surplus)
    ax.fill_between(ca.index, ca.values, 0,
                    where=ca.values < 0, interpolate=True,
                    color=palette[2], alpha=0.25, linewidth=0)
    ax.fill_between(ca.index, ca.values, 0,
                    where=ca.values >= 0, interpolate=True,
                    color=palette[1], alpha=0.25, linewidth=0)

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(ca.index.min(), ca.index.max())
    start_tick = ca.index.min() + (10 - ca.index.min() % 10) % 10
    xticks = list(range(start_tick, ca.index.max() + 1, 10))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)

    ax.set_ylim(-5, 3)
    yticks = list(range(-5, 4, 1))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'$-${abs(y)}\\%' if y < 0
                        else f'{y}\\%' for y in yticks], fontsize=11)
    ax.set_ylabel(r"(\% du PIB)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Source: Banque mondiale")
    save(fig, 'ca_ca_balance_gdp.png')


# =====================================================================
# Figure 6b: US twin deficits — CA balance + government budget balance
# =====================================================================
def us_twin_deficits():
    """US current account and government budget balance as % of GDP."""
    print('Figure 6b: US twin deficits')

    # Current account balance (% of GDP)
    ca = _get_worldbank('BN.CAB.XOKA.GD.ZS', 'USA', start=1970, end=2024)
    ca = ca.dropna()

    # Government net lending/borrowing (% of GDP) — FRED: FYFSGDA188S
    budget = get_fred_data('FYFSGDA188S', observation_start='1970-01-01')
    budget = budget.dropna()
    # Convert to annual series keyed by integer year
    budget.index = budget.index.year
    budget = budget.groupby(budget.index).last()
    budget.index.name = 'year'

    # Align on common years
    common = ca.index.intersection(budget.index)
    ca = ca.loc[common]
    budget = budget.loc[common]

    fig, ax = new_figure(9, 4.5)

    ax.plot(ca.index, ca.values, color=palette[0], linewidth=2,
            label='Compte courant')
    ax.plot(budget.index, budget.values, color=palette[2], linewidth=2,
            label='Solde budgétaire')
    ax.axhline(0, color='black', linewidth=0.5)

    # ── Axis formatting ─────────────────────────────────────────────
    last_year = max(ca.index.max(), budget.index.max())
    ax.set_xlim(1970, last_year)
    xticks = list(range(1970, last_year + 1, 10))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)

    ax.set_ylim(-12, 4)
    yticks = list(range(-12, 5, 2))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'$-${abs(y)}\\%' if y < 0
                        else f'{y}\\%' for y in yticks], fontsize=11)
    ax.set_ylabel(r"(\% du PIB)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='lower left',
              bbox_to_anchor=(0.0, 0.0))
    add_source(ax, r"Source: Banque mondiale, FRED")
    save(fig, 'us_twin_deficits.png')


# =====================================================================
# Figure 6: Canada NX vs CA (two lines, no fill)
# =====================================================================
def ca_nx_vs_ca():
    """Canada trade balance and current account in billions USD (lines only)."""
    print('Figure 6: Canada NX vs CA')

    # World Bank: external balance on goods & services (current US$)
    nx = _get_worldbank('NE.RSB.GNFS.CD', 'CAN', start=1970, end=2024)
    nx = nx.dropna() / 1e9  # convert to billions

    # World Bank: current account balance (BoP, current US$)
    ca = _get_worldbank('BN.CAB.XOKA.CD', 'CAN', start=1970, end=2024)
    ca = ca.dropna() / 1e9

    fig, ax = new_figure(9, 4.5)

    ax.plot(nx.index, nx.values, color=palette[0], linewidth=2,
            label='Balance commerciale ($NX$)')
    ax.plot(ca.index, ca.values, color=palette[2], linewidth=2,
            label='Compte courant ($CA$)')
    ax.axhline(0, color='black', linewidth=0.5)

    # ── Axis formatting ─────────────────────────────────────────────
    last_year = max(nx.index.max(), ca.index.max())
    ax.set_xlim(1970, last_year)
    xticks = list(range(1970, last_year + 1, 10))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)

    # Auto y-axis range
    all_vals = pd.concat([nx, ca])
    ymin = int(np.floor(all_vals.min() / 10) * 10)
    ymax = int(np.ceil(all_vals.max() / 10) * 10)
    ax.set_ylim(ymin, ymax)
    step = 10
    yticks = list(range(ymin, ymax + 1, step))
    ax.set_yticks(yticks)
    ax.set_yticklabels([str(y) for y in yticks], fontsize=11)
    ax.set_ylabel(r"Milliards USD", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='lower left',
              bbox_to_anchor=(0.0, 0.0))
    add_source(ax, r"Source: Banque mondiale")
    save(fig, 'ca_nx_vs_ca.png')


# =====================================================================
# Figure 7: US gross fixed capital formation as % of GDP
# =====================================================================
def us_investment_gdp():
    """US gross fixed capital formation as % of GDP, highlighting tech boom."""
    print('Figure 7: US investment / GDP')

    inv = _get_worldbank('NE.GDI.FTOT.ZS', 'USA', start=1970, end=2024)
    inv = inv.dropna()

    if len(inv) == 0:
        print('  ! No investment data. Skipping.')
        return

    fig, ax = new_figure(9, 4.5)

    ax.plot(inv.index, inv.values, color=palette[0], linewidth=2.5)

    # Highlight tech boom period (1995-2000)
    ax.axvspan(1995, 2000, color=palette[1], alpha=0.15, linewidth=0)
    # Label
    boom_peak = inv.loc[1995:2000].max()
    ax.annotate('Boom\ntechnologique',
                xy=(1997.5, boom_peak + 0.3), fontsize=9,
                color=palette[1], fontweight='bold', ha='center', va='bottom')

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(1970, inv.index.max())
    xticks = list(range(1970, inv.index.max() + 1, 10))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)

    ymin = int(np.floor(inv.min())) - 1
    ymax = int(np.ceil(inv.max())) + 1
    ax.set_ylim(ymin, ymax)
    yticks = list(range(ymin, ymax + 1, 1))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}\\%' for y in yticks], fontsize=11)
    ax.set_ylabel(r"Investissement (\% du PIB)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Source: Banque mondiale")
    save(fig, 'us_investment_gdp.png')


# =====================================================================
# Figure 8: Laubach-Williams r* estimate (natural rate of interest)
# =====================================================================
def lw_rstar():
    """Laubach-Williams one-sided r* estimate, quarterly, from NY Fed Excel."""
    print('Figure 8: Laubach-Williams r*')

    data_dir = os.path.join(Path(__file__).resolve().parent.parent, 'Data')
    fpath = os.path.join(data_dir, 'Laubach_Williams_current_estimates.xlsx')

    if not os.path.exists(fpath):
        print('  ! LW data file not found. Skipping.')
        return

    df = pd.read_excel(fpath, sheet_name='data', header=5,
                       usecols=['Date', 'rstar'])
    df = df.dropna(subset=['rstar'])
    df['Date'] = pd.to_datetime(df['Date'])

    fig, ax = new_figure(9, 4.5)

    ax.plot(df['Date'], df['rstar'], color=palette[0], linewidth=2)
    ax.axhline(0, color='black', linewidth=0.5)

    # Highlight the decline
    ax.fill_between(df['Date'], df['rstar'], 0,
                    where=df['rstar'] > 0,
                    color=palette[0], alpha=0.08, linewidth=0)

    # ── Axis formatting ─────────────────────────────────────────────
    last_date = df['Date'].iloc[-1]
    ax.set_xlim(df['Date'].iloc[0], last_date)
    xticks = pd.date_range('1970', last_date, freq='10YS')
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y.year) for y in xticks], fontsize=11)

    ax.set_ylim(0, 6)
    yticks = list(range(0, 7, 1))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}\\%' for y in yticks], fontsize=11)
    ax.set_ylabel(r"$r^*$ réel (\%)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r"Source: Laubach \& Williams, Fed de New York")
    save(fig, 'lw_rstar.png')


# =====================================================================
# Figure 9: US federal debt as % of GDP — domestic vs foreign held
# =====================================================================
def us_debt_gdp():
    """US federal debt held by the public as % of GDP, split domestic/foreign."""
    print('Figure 9: US debt-to-GDP (domestic vs foreign)')

    # Total debt held by the public as % of GDP (pre-computed by FRED)
    total_pct = get_fred_data('GFDEGDQ188S', frequency='a',
                              aggregation_method='avg',
                              observation_start='1970-01-01')
    total_pct = total_pct.dropna()
    total_pct.index = total_pct.index.year

    # Foreign-held federal debt (billions $)
    foreign = get_fred_data('FDHBFIN', frequency='a',
                            aggregation_method='avg',
                            observation_start='1970-01-01')
    foreign = foreign.dropna()
    foreign.index = foreign.index.year

    # GDP (billions $) — same denominator basis
    gdp = get_fred_data('GDP', frequency='a',
                        aggregation_method='avg',
                        observation_start='1970-01-01')
    gdp = gdp.dropna()
    gdp.index = gdp.index.year

    # Align on common years
    common = total_pct.index.intersection(foreign.index).intersection(gdp.index)
    total_pct = total_pct.loc[common]
    foreign = foreign.loc[common]
    gdp = gdp.loc[common]

    # Foreign as % of GDP
    foreign_pct = (foreign / gdp) * 100

    fig, ax = new_figure(9, 4.5)

    years = common.values
    ax.fill_between(years, 0, foreign_pct.values,
                    color=palette[2], alpha=0.35, linewidth=0,
                    label='Détenue par des étrangers')
    ax.plot(years, foreign_pct.values, color='#991a1e', linewidth=1.5)
    ax.fill_between(years, foreign_pct.values, total_pct.values,
                    color=palette[0], alpha=0.20, linewidth=0,
                    label='Détenue aux É.-U.')
    ax.plot(years, total_pct.values, color=palette[0], linewidth=2)

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(years.min(), years.max())
    xticks = list(range(1970, years.max() + 1, 10))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)

    ymax = tick_ceil(total_pct.max(), 20)
    ax.set_ylim(0, ymax)
    yticks = list(range(0, ymax + 1, 20))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}\\%' for y in yticks], fontsize=11)
    ax.set_ylabel(r"Dette fédérale (\% du PIB)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0))

    style_axes(ax)
    add_source(ax, r"Source: Federal Reserve Economic Data")
    save(fig, 'us_debt_gdp.png')


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 6 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        trade_openness,
        us_nx_vs_ca,
        saving_rates_divergence,
        current_accounts_divergence,
        us_ca_balance_gdp,
        ca_ca_balance_gdp,
        us_twin_deficits,
        ca_nx_vs_ca,
        us_investment_gdp,
        lw_rstar,
        us_debt_gdp,
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
