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
# Figure 3: Gross saving rates — China, US, Japan, Germany
# =====================================================================
def saving_rates_divergence():
    """Gross saving as % of GNI for four major economies."""
    print('Figure 3: Saving rates divergence')

    countries = {
        'CHN': ('Chine',       palette[2], 2.5),
        'USA': (r'États-Unis', palette[0], 2.5),
        'JPN': ('Japon',       palette[3], 2),
        'DEU': ('Allemagne',   palette[4], 2),
    }

    fig, ax = new_figure(9, 4.5)

    # Manual vertical offsets to avoid label overlap (Japan ≈ Allemagne ≈ 27-29%)
    label_offsets = {'JPN': 1.5, 'DEU': -1.5}

    for iso, (label, color, lw) in countries.items():
        s = _get_worldbank('NY.GNS.ICTR.ZS', iso, start=1970, end=2024)
        s = s.dropna()
        if len(s) == 0:
            print(f'  ! No data for {iso}. Skipping.')
            continue
        ax.plot(s.index, s.values, color=color, linewidth=lw)

        # End-of-line label (with offset to avoid overlap)
        last_year = s.index[-1]
        last_val = s.iloc[-1] + label_offsets.get(iso, 0)
        ax.text(last_year + 0.5, last_val, label, fontsize=9,
                color=color, fontweight='bold', va='center')

    # ── Axis formatting ─────────────────────────────────────────────
    ax.set_xlim(1970, 2028)
    xticks = list(range(1970, 2030, 10))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)

    ax.set_ylim(10, 55)
    yticks = list(range(10, 56, 5))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}\\%' for y in yticks], fontsize=11)
    ax.set_ylabel(r"(\% du PIB)", fontsize=11, rotation=0, ha='left')
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
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 6 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        trade_openness,
        us_nx_vs_ca,
        saving_rates_divergence,
        us_ca_balance_gdp,
        ca_ca_balance_gdp,
        us_twin_deficits,
        ca_nx_vs_ca,
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
