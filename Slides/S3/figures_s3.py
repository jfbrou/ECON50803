"""
ECON50803 — Session 3 : Figure Generation
============================================

Generates all matplotlib figures for Session 3 slides (labor market,
inequality, AI). All figure labels, axis titles, legends, and annotations
are in French.

Run from Slides/S3/:
    python3 figures_s3.py
"""

import os
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from plot_utils import *


# =====================================================================
# Figure 1: US labor market indicators (1950–2024)
# =====================================================================
def labor_market_indicators_us():
    print('Figure 1: US labor market indicators')

    civpart = get_fred_data('CIVPART', frequency='a', aggregation_method='avg')
    emratio = get_fred_data('EMRATIO', frequency='a', aggregation_method='avg')
    unrate = get_fred_data('UNRATE', frequency='a', aggregation_method='avg')

    fig, ax = new_figure(9, 4.5)

    ax.plot(civpart.index.year, civpart.values, color=palette[0],
            linewidth=2.5, label='Taux de participation')
    ax.plot(emratio.index.year, emratio.values, color=palette[1],
            linewidth=2.5, label="Taux d'emploi")
    ax.plot(unrate.index.year, unrate.values, color=palette[2],
            linewidth=2, label=r"Taux de chômage")

    ax.set_xlim(1950, 2024)
    ax.set_xticks(range(1950, 2025, 10))
    ax.set_xticklabels(range(1950, 2025, 10), fontsize=11)
    ax.set_ylabel(r"Pourcentage (\%)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 70)
    ax.set_yticks(range(0, 71, 10))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(0, 71, 10)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, r"Source: FRED (CIVPART, EMRATIO, UNRATE) --- États-Unis")
    save(fig, 'labor_market_indicators_us.png')


# =====================================================================
# Figure 1b: Canadian labor market indicators (1976–present, dual axis)
# =====================================================================
def labor_market_indicators_ca():
    print('Figure 1b: Canadian labor market indicators (dual axis)')

    from stats_can import StatsCan
    sc = StatsCan()

    # Table 14-10-0287-01: Labour force characteristics, monthly, SA
    df = sc.table_to_df('14-10-0287-01')
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])

    # Keep seasonally adjusted, both genders, 15+, estimate only
    df = df[df['Data type'] == 'Seasonally adjusted']
    df = df[df['Gender'] == 'Total - Gender']
    df = df[df['Age group'] == '15 years and over']
    df = df[df['Statistics'] == 'Estimate']

    # Extract the three series
    participation = df[df['Labour force characteristics'] ==
                       'Participation rate'].set_index('REF_DATE')['VALUE']
    employment = df[df['Labour force characteristics'] ==
                    'Employment rate'].set_index('REF_DATE')['VALUE']
    unemployment = df[df['Labour force characteristics'] ==
                      'Unemployment rate'].set_index('REF_DATE')['VALUE']

    # Drop duplicates and sort
    participation = participation[~participation.index.duplicated(keep='first')].sort_index()
    employment = employment[~employment.index.duplicated(keep='first')].sort_index()
    unemployment = unemployment[~unemployment.index.duplicated(keep='first')].sort_index()

    fig, ax1 = new_figure(9, 4.5)
    ax2 = ax1.twinx()

    # Left axis: participation & employment rates
    ax1.plot(participation.index, participation.values, color=palette[0],
             linewidth=1.5, label='Taux de participation')
    ax1.plot(employment.index, employment.values, color=palette[1],
             linewidth=1.5, label="Taux d'emploi")

    # Right axis: unemployment rate
    ax2.plot(unemployment.index, unemployment.values, color=palette[2],
             linewidth=1.5, label=r"Taux de chômage")

    # Left axis formatting
    import matplotlib.dates as mdates
    ax1.set_xlim(pd.Timestamp('1976-01-01'), participation.index.max())
    tick_years = range(1980, participation.index.max().year + 1, 10)
    tick_dates = [pd.Timestamp(f'{y}-01-01') for y in tick_years]
    ax1.set_xticks(tick_dates)
    ax1.set_xticklabels([str(y) for y in tick_years], fontsize=11)
    ax1.set_ylabel(r"Participation / emploi (\%)", fontsize=11,
                   rotation=0, ha='left')
    ax1.yaxis.set_label_coords(0, 1.02)
    ax1.set_ylim(50, 70)
    ax1.set_yticks(range(50, 71, 5))
    ax1.set_yticklabels([f'{y}' + r'\%' for y in range(50, 71, 5)],
                         fontsize=11)

    # Right axis formatting
    ax2.set_ylabel(r"Chômage (\%)", fontsize=11,
                   rotation=0, ha='right')
    ax2.yaxis.set_label_coords(1, 1.06)
    ax2.set_ylim(4, 14)
    ax2.set_yticks(range(4, 15, 2))
    ax2.set_yticklabels([f'{y}' + r'\%' for y in range(4, 15, 2)],
                         fontsize=11, color=palette[2])
    ax2.tick_params(axis='y', colors=palette[2])
    ax2.spines['right'].set_color(palette[2])
    ax2.spines['top'].set_visible(False)

    # Recession shading
    for start, end in recessions_ca:
        ax1.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    # Style left axis
    style_axes(ax1)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               frameon=False, fontsize=10, loc='lower left')
    ax1.text(0.99, 0.02, r"Source: Statistique Canada, tableau 14-10-0287-01",
             fontsize=8, color='gray', ha='right', va='bottom',
             transform=ax1.transAxes)
    save(fig, 'labor_market_indicators_ca.png')


# =====================================================================
# Figure 2: Male vs female participation rates (US, 1950–2024)
# =====================================================================
def participation_gender():
    print('Figure 2: Participation rates by gender (US)')

    male = get_fred_data('LNS11300001', frequency='a', aggregation_method='avg')
    female = get_fred_data('LNS11300002', frequency='a', aggregation_method='avg')

    fig, ax = new_figure(9, 4.5)

    ax.plot(male.index.year, male.values, color=palette[0],
            linewidth=2.5, label='Hommes')
    ax.plot(female.index.year, female.values, color=palette[2],
            linewidth=2.5, label='Femmes')

    # Annotate the convergence
    ax.annotate('Convergence',
                xy=(2000, 60), xytext=(1975, 50),
                fontsize=11, color=palette[1], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[1], lw=1.5))

    ax.set_xlim(1950, 2024)
    ax.set_xticks(range(1950, 2025, 10))
    ax.set_xticklabels(range(1950, 2025, 10), fontsize=11)
    ax.set_ylabel(r"Taux de participation (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(20, 90)
    ax.set_yticks(range(20, 91, 10))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(20, 91, 10)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='center right')
    add_source(ax, r"Source: FRED (LNS11300001, LNS11300002) --- États-Unis")
    save(fig, 'participation_gender.png')


# =====================================================================
# Figure 3: Aging population — old-age dependency ratio
# =====================================================================
def aging_population():
    print('Figure 3: Aging population — old-age dependency ratio')

    # Old-age dependency ratio (65+ / 15-64) * 100
    # Source: World Bank API (SP.POP.DPND.OL)
    countries = [
        ('JPN', 'Japon', palette[0], 2.5),          # HECnavy
        ('ITA', 'Italie', palette[1], 2.5),          # HECgreen
        ('CAN', 'Canada', palette[2], 3.0),          # HECcoral
        ('USA', r"États-Unis", palette[3], 2.0), # yellow
    ]

    fig, ax = new_figure(9, 4.5)

    for iso, label, color, lw in countries:
        s = _get_worldbank('SP.POP.DPND.OL', iso)
        s = s[s.index >= 1960]
        ax.plot(s.index, s.values, color=color, linewidth=lw, label=label)

    ax.set_xlim(1960, 2025)
    ax.set_xticks(range(1960, 2030, 10))
    ax.set_xticklabels(range(1960, 2030, 10), fontsize=11)
    ax.set_ylabel(r"Ratio de dépendance des aînés (\%)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(5, 55)
    ax.set_yticks(range(5, 56, 10))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(5, 56, 10)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0))
    add_source(ax, 'Source: Banque mondiale (SP.POP.DPND.OL)')
    save(fig, 'aging_population.png')


# =====================================================================
# Figure 4: US prime-age male participation decline
# =====================================================================
def participation_decline_us():
    print('Figure 4: US prime-age male participation decline')

    prime_male = get_fred_data('LRAC25MAUSA156N')
    prime_male = prime_male.dropna()

    fig, ax = new_figure(9, 4.5)

    ax.plot(prime_male.index.year, prime_male.values, color=palette[0],
            linewidth=2.5)
    ax.fill_between(prime_male.index.year, prime_male.values,
                    prime_male.values.min() - 1, alpha=0.1, color=palette[0])

    # Trend annotation
    ax.annotate(r"Déclin structurel",
                xy=(2010, 88), xytext=(1980, 92),
                fontsize=12, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    ax.set_xlim(1950, 2024)
    ax.set_xticks(range(1950, 2025, 10))
    ax.set_xticklabels(range(1950, 2025, 10), fontsize=11)
    ax.set_ylabel(r"Taux de participation (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(84, 100)
    ax.set_yticks(range(84, 101, 2))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(84, 101, 2)], fontsize=11)

    style_axes(ax)
    add_source(ax, r"Source: FRED (LNS11300061) --- Hommes 25--54 ans, É.-U.")
    save(fig, 'participation_decline_us.png')


# =====================================================================
# Figure 5: Labor share of GDP decline
# =====================================================================
def labor_share_decline():
    """Labor share of GDP for Canada, 1950-2023 (Penn World Table via FRED)."""
    print('  labor_share_decline ...', end=' ', flush=True)

    # FRED: Share of Labour Compensation in GDP (Canada, PWT)
    ls = get_fred_data('LABSHPCAA156NRUG')
    ls = ls.dropna() * 100  # convert ratio to %

    ls = ls[ls.index.year >= 1960]

    fig, ax = new_figure(9, 4.5)

    ax.plot(ls.index.year, ls.values, color=palette[0], linewidth=2.5)
    ax.fill_between(ls.index.year, ls.values, 61,
                    alpha=0.08, color=palette[0])

    ax.set_xlim(1960, 2024)
    ax.set_xticks(range(1960, 2025, 10))
    ax.set_xticklabels(range(1960, 2025, 10), fontsize=12)
    ax.set_ylim(61, 76)
    ax.set_yticks(range(61, 77, 3))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(61, 77, 3)], fontsize=12)
    ax.set_ylabel(r"Part du travail dans le PIB",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r'Source: Penn World Table 10.01 (via FRED)')
    save(fig, 'labor_share_canada.png')


# =====================================================================
# Figure 6: College/high-school wage premium (US)
# =====================================================================
def inequality_skill_premium():
    print('Figure 6: College wage premium (US)')

    # College/high-school wage ratio over time
    # Source: Autor (2014); Goldin & Katz (2008); CPS data
    years = list(range(1965, 2024, 5)) + [2023]
    premium = [1.45, 1.40, 1.35, 1.38, 1.50, 1.58, 1.65, 1.72, 1.78,
               1.82, 1.85, 1.88, 1.90]

    fig, ax = new_figure(8, 4.5)

    ax.plot(years, premium, 'o-', color=palette[0], linewidth=2.5,
            markersize=6)

    # Annotation for the rise
    ax.annotate("Hausse du rendement\n" + r"de l'éducation",
                xy=(2005, 1.82), xytext=(1975, 1.82),
                fontsize=11, color=palette[1], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[1], lw=1.5))

    ax.set_xlim(1963, 2025)
    ax.set_xticks(range(1965, 2025, 10))
    ax.set_xticklabels(range(1965, 2025, 10), fontsize=11)
    ax.set_ylabel(r"Ratio salarial (université / secondaire)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(1.2, 2.0)
    ax.set_yticks([1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0])
    ax.set_yticklabels([f'{y:.1f}' for y in
                        [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]],
                       fontsize=11)

    ax.axhline(y=1.0, color='gray', linewidth=0.5, linestyle=':')

    style_axes(ax)
    add_source(ax, 'Source: Autor (2014); Goldin \\& Katz (2008); CPS')
    save(fig, 'inequality_skill_premium.png')


# =====================================================================
# Figure 7: R&D as share of GDP — US private vs public (FRED)
# =====================================================================
def rd_gdp_share():
    """Stacked area: private and public R&D as share of US GDP."""
    print('Figure 7: R&D / GDP — US private vs public')

    private = get_fred_data('Y006RC1Q027SBEA') / get_fred_data('GDP')
    public  = get_fred_data('Y057RC1Q027SBEA') / get_fred_data('GDP')

    # Align on common index and drop NaN
    combined = pd.concat([private.rename('priv'), public.rename('pub')],
                         axis=1).dropna()

    fig, ax = new_figure(9, 4.5)

    ax.stackplot(combined.index, 100 * combined['priv'].values,
                 100 * combined['pub'].values,
                 colors=[palette[0], palette[1]],
                 edgecolor='k', linewidth=0.5)

    ax.set_xlim(pd.to_datetime('1950'), combined.index.max())
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(1950, 2021, 10)])
    ax.set_xticklabels(range(1950, 2021, 10), fontsize=11)
    ax.set_ylim(0, 4)
    ax.set_yticks(np.arange(0, 4.1, 0.5))
    ax.set_yticklabels([f'{x:.1f}' + r'\%' for x in np.arange(0, 4.1, 0.5)],
                       fontsize=11)
    ax.set_ylabel(r"Part du PIB américain (\%)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)

    # In-chart labels
    ax.text(pd.to_datetime('2005'), 0.7, r"R\&D privée",
            fontsize=14, color='white', ha='center', va='center')
    ax.text(pd.to_datetime('1970'), 1.6, r"R\&D publique",
            fontsize=14, color='k', ha='center', va='center')

    add_source(ax, r"Source: FRED (Y006RC, Y057RC, GDP) --- États-Unis")
    save(fig, 'rd_gdp_share.png')


# =====================================================================
# Figure 8: Canada GDP/capita growth decomposition by period
# =====================================================================
def canada_gdp_decomposition():
    """Stacked bar: decompose Canadian Y/N growth into A, K/Y, L/N."""
    print('Figure 8: Canada GDP/capita growth decomposition')

    # Load Penn World Tables 10.01 (same source as S2)
    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')
    ca = pwt[pwt['countrycode'] == 'CAN'].set_index('year')

    alpha = 1 / 3
    amp_ky = alpha / (1 - alpha)  # 0.5

    periods = [('1960--80', 1960, 1980),
               ('1980--00', 1980, 2000),
               ('2000--19', 2000, 2019)]

    a_vals, ky_vals, ln_vals, yn_vals = [], [], [], []
    for _, y0, y1 in periods:
        T = y1 - y0
        yn0 = ca.loc[y0, 'rgdpna'] / ca.loc[y0, 'pop']
        yn1 = ca.loc[y1, 'rgdpna'] / ca.loc[y1, 'pop']
        ky0 = ca.loc[y0, 'rkna'] / ca.loc[y0, 'rgdpna']
        ky1 = ca.loc[y1, 'rkna'] / ca.loc[y1, 'rgdpna']
        ln0 = ca.loc[y0, 'emp'] / ca.loc[y0, 'pop']
        ln1 = ca.loc[y1, 'emp'] / ca.loc[y1, 'pop']

        g_yn = ((yn1 / yn0) ** (1 / T) - 1) * 100
        g_ky = ((ky1 / ky0) ** (1 / T) - 1) * 100
        g_ln = ((ln1 / ln0) ** (1 / T) - 1) * 100

        ky_c = amp_ky * g_ky
        ln_c = g_ln
        a_c = g_yn - ky_c - ln_c

        a_vals.append(a_c)
        ky_vals.append(ky_c)
        ln_vals.append(ln_c)
        yn_vals.append(g_yn)

    x = np.arange(len(periods))
    labels = [p[0] for p in periods]
    w = 0.55

    fig, ax = new_figure(9, 4.5)

    # Stacked bars: positive contributions stack upward from 0,
    # negative contributions stack downward from 0
    components = [
        (a_vals, palette[0], r"Productivité ($A$)"),
        (ky_vals, palette[1], r"Capital/PIB ($K/Y$)"),
        (ln_vals, palette[3], r"Taux d'emploi ($L/N$)"),
    ]

    for i in range(len(periods)):
        pos_base = 0
        neg_base = 0
        for j, (vals, color, label) in enumerate(components):
            v = vals[i]
            if v >= 0:
                ax.bar(x[i], v, w, bottom=pos_base, color=color,
                       label=label if i == 0 else None)
                pos_base += v
            else:
                ax.bar(x[i], v, w, bottom=neg_base, color=color,
                       label=label if i == 0 else None)
                neg_base += v

    # Total Y/N markers
    for i in range(len(periods)):
        ax.plot(x[i], yn_vals[i], 'D', color=palette[2], markersize=8,
                zorder=5, label=r'Total $Y/N$' if i == 0 else None)
        ax.annotate(f'{yn_vals[i]:.1f}' + r'\%',
                    xy=(x[i], yn_vals[i]),
                    xytext=(0, 10), textcoords='offset points',
                    ha='center', fontsize=11, fontweight='bold',
                    color=palette[2])

    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=13)
    ax.set_ylabel(r"Contribution à la croissance de $Y/N$ (\%/an)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    ax.set_ylim(0, 3.5)
    ax.set_yticks(np.arange(0, 3.6, 0.5))
    ax.set_yticklabels([f'{y:.1f}' + r'\%' for y in np.arange(0, 3.6, 0.5)],
                       fontsize=12)
    ax.tick_params(axis='x', labelsize=12)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, 'Source: Penn World Tables 10.01 --- Canada')
    save(fig, 'canada_gdp_decomposition.png')


# =====================================================================
# Figure 9: Cross-country GDP/capita decomposition (2000–2019)
# =====================================================================
def canada_gdp_decomposition_countries():
    """Horizontal stacked bar: Y/N decomposition for ~18 countries, 2000-2019."""
    print('Figure 9: Cross-country GDP/capita decomposition (2000-2019)')

    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')

    alpha = 1 / 3
    amp_ky = alpha / (1 - alpha)  # 0.5

    countries = {
        'KOR': r'Corée du Sud',
        'POL': 'Pologne',
        'IRL': 'Irlande',
        'AUS': 'Australie',
        'SWE': r'Suède',
        'USA': r'États-Unis',
        'GBR': 'Royaume-Uni',
        'NZL': r'Nouvelle-Zélande',
        'DEU': 'Allemagne',
        'NOR': r'Norvège',
        'CAN': 'Canada',
        'CHE': 'Suisse',
        'NLD': 'Pays-Bas',
        'JPN': 'Japon',
        'DNK': 'Danemark',
        'FRA': 'France',
        'BEL': 'Belgique',
        'ESP': 'Espagne',
        'ITA': 'Italie',
    }

    y0, y1 = 2000, 2019
    T = y1 - y0
    results = {}

    for iso, name in countries.items():
        c = pwt[pwt['countrycode'] == iso].set_index('year')
        if y0 not in c.index or y1 not in c.index:
            continue

        yn0 = c.loc[y0, 'rgdpna'] / c.loc[y0, 'pop']
        yn1 = c.loc[y1, 'rgdpna'] / c.loc[y1, 'pop']
        ky0 = c.loc[y0, 'rkna'] / c.loc[y0, 'rgdpna']
        ky1 = c.loc[y1, 'rkna'] / c.loc[y1, 'rgdpna']
        ln0 = c.loc[y0, 'emp'] / c.loc[y0, 'pop']
        ln1 = c.loc[y1, 'emp'] / c.loc[y1, 'pop']

        g_yn = ((yn1 / yn0) ** (1 / T) - 1) * 100
        g_ky = ((ky1 / ky0) ** (1 / T) - 1) * 100
        g_ln = ((ln1 / ln0) ** (1 / T) - 1) * 100

        ky_c = amp_ky * g_ky
        ln_c = g_ln
        a_c = g_yn - ky_c - ln_c

        results[iso] = (name, g_yn, a_c, ky_c, ln_c)

    # Sort by total Y/N growth
    sorted_isos = sorted(results.keys(), key=lambda k: results[k][1])

    names = [results[iso][0] for iso in sorted_isos]
    yn_vals = [results[iso][1] for iso in sorted_isos]
    a_vals = [results[iso][2] for iso in sorted_isos]
    ky_vals = [results[iso][3] for iso in sorted_isos]
    ln_vals = [results[iso][4] for iso in sorted_isos]

    y_pos = np.arange(len(names))
    h = 0.6

    fig, ax = new_figure(9, 7)

    # Stacked horizontal bars: positive right of 0, negative left of 0
    components = [
        (a_vals, palette[0], r"Productivité ($A$)"),
        (ky_vals, palette[1], r"Capital/PIB ($K/Y$)"),
        (ln_vals, palette[3], r"Taux d'emploi ($L/N$)"),
    ]

    for i in range(len(names)):
        pos_base = 0
        neg_base = 0
        for j, (vals, color, label) in enumerate(components):
            v = vals[i]
            if v >= 0:
                ax.barh(y_pos[i], v, h, left=pos_base, color=color,
                        label=label if i == 0 else None)
                pos_base += v
            else:
                ax.barh(y_pos[i], v, h, left=neg_base, color=color,
                        label=label if i == 0 else None)
                neg_base += v

    # Total Y/N diamond markers
    for i in range(len(names)):
        ax.plot(yn_vals[i], y_pos[i], 'D', color=palette[2], markersize=6,
                zorder=5, label=r'Total $Y/N$' if i == 0 else None)

    ax.axvline(x=0, color='black', linewidth=0.5)

    # Highlight Canada
    can_idx = sorted_isos.index('CAN')
    ax.get_yticklabels()  # force tick creation

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=11)
    # Bold Canada label
    tick_labels = ax.get_yticklabels()
    for tl in tick_labels:
        if tl.get_text() == 'Canada':
            tl.set_fontweight('bold')
            tl.set_color(palette[2])

    # Subtle highlight band for Canada
    ax.axhspan(can_idx - 0.4, can_idx + 0.4, color=palette[2],
               alpha=0.08, zorder=0)

    ax.set_xlabel(r"Contribution à la croissance de $Y/N$ (\%/an)",
                  fontsize=11)
    ax.set_xlim(-1.0, 4.0)
    ax.set_xticks(np.arange(-1.0, 4.1, 0.5))
    ax.set_xticklabels([f'{x:.1f}' + r'\%' for x in np.arange(-1.0, 4.1, 0.5)],
                       fontsize=10)

    style_axes(ax)
    ax.spines['left'].set_visible(False)
    ax.grid(True, which='major', axis='x', color='gray', linestyle=':', linewidth=0.5)
    ax.grid(False, axis='y')
    ax.tick_params(axis='y', length=0)

    ax.legend(frameon=False, fontsize=9, loc='lower right',
              bbox_to_anchor=(1.0, 0.0))
    add_source(ax, r"Source: Penn World Tables 10.01 --- Période 2000--2019")
    save(fig, 'canada_gdp_decomposition_countries.png')


# =====================================================================
# Figure 10: Breakthrough patents per million people (Kelly et al. 2021)
# =====================================================================
def breakthrough_inventions():
    """Breakthrough patents per million people from Kelly et al. (2021) data."""
    print('Figure 10: Breakthrough patents (Kelly et al. 2021)')

    # ── Load patent-level breakthrough data ──────────────────────────
    data_dir = os.path.join(Path(__file__).resolve().parent.parent, 'Data')
    patent_csv = os.path.join(data_dir, 'PatentSimilarityImportanceBreakthrough_forPost2022.csv')
    df = pd.read_csv(patent_csv, usecols=['issue_year', 'bk_p90_alqsim05'])
    df = df.dropna(subset=['bk_p90_alqsim05'])

    # Count breakthrough patents (top 10% importance) by issue year
    bt_by_year = (df[df['bk_p90_alqsim05'] == 1]
                  .groupby('issue_year').size()
                  .reindex(range(1840, 2017), fill_value=0))

    # ── US population (millions), decennial census + intercensal ─────
    # Source: US Census Bureau historical estimates
    us_pop_m = {
        1840: 17.1, 1850: 23.2, 1860: 31.4, 1870: 38.6, 1880: 50.2,
        1890: 63.0, 1900: 76.2, 1910: 92.2, 1920: 106.0, 1930: 123.2,
        1940: 132.2, 1950: 151.3, 1960: 179.3, 1970: 203.3, 1980: 226.5,
        1990: 248.7, 2000: 281.4, 2010: 308.7, 2016: 323.1,
    }
    pop_years = sorted(us_pop_m.keys())
    pop_vals = [us_pop_m[y] for y in pop_years]
    # Interpolate annual population
    all_years = np.arange(1840, 2017)
    pop_annual = np.interp(all_years, pop_years, pop_vals)
    pop_series = pd.Series(pop_annual, index=all_years)

    # Breakthrough patents per million people
    # (pop_series is in millions, so count / pop_series = per million)
    bt_per_m = bt_by_year / pop_series

    fig, ax = new_figure(9, 4.5)

    ax.plot(bt_per_m.index, bt_per_m.values, color=palette[0], linewidth=1.8)

    # Annotate three waves (text only, no arrows)
    ax.text(1867, 48,
            r"\textbf{1\textsuperscript{re} vague :}" "\n"
            r"2\textsuperscript{e} rév. industrielle" "\n"
            r"(électricité, transport)",
            fontsize=8, color=palette[0], va='bottom', ha='center')

    ax.text(1932, 78,
            r"\textbf{2\textsuperscript{e} vague :}" "\n"
            r"Entre-deux-guerres" "\n"
            r"(chimie, électricité)",
            fontsize=8, color=palette[0], va='bottom', ha='center')

    ax.text(1978, 78,
            r"\textbf{3\textsuperscript{e} vague :}" "\n"
            r"Technologies de l'information" "\n"
            r"(ordinateurs, communications)",
            fontsize=8, color=palette[0], va='bottom', ha='center')

    ax.set_xlim(1840, 2018)
    ax.set_ylim(0, 100)
    ax.set_xticks(range(1840, 2021, 20))
    ax.set_xticklabels([str(y) for y in range(1840, 2021, 20)], fontsize=11)
    ax.set_yticks(range(0, 101, 20))
    ax.set_yticklabels([str(y) for y in range(0, 101, 20)], fontsize=11)
    ax.set_ylabel(r"Brevets majeurs par million d'habitants",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, 'Source: Kelly et al. (2021), AER: Insights')
    save(fig, 'kelly_et_al_2021.png')


# =====================================================================
# Figure 11: Global R&D spending by country (1996–2022)
# =====================================================================
def rd_spending_global():
    """Stacked area: R&D spending in billions of constant 2021 PPP USD."""
    print('Figure 11: Global R&D spending by country')

    # Country codes and French labels (stacking order: bottom to top)
    countries = [
        ('USA', r'États-Unis'),
        ('CHN', 'Chine'),
        ('EUU', 'UE-27'),
        ('JPN', 'Japon'),
        ('KOR', r'Corée du Sud'),
        ('GBR', 'Royaume-Uni'),
    ]

    # Fetch R&D % of GDP and GDP PPP (constant 2021 intl $)
    gerd = {}
    for iso, label in countries:
        rd_pct = _get_worldbank('GB.XPD.RSDV.GD.ZS', iso)
        gdp_ppp = _get_worldbank('NY.GDP.MKTP.PP.KD', iso)
        common = rd_pct.index.intersection(gdp_ppp.index)
        spending = (rd_pct[common] / 100) * gdp_ppp[common] / 1e9  # billions
        gerd[label] = spending

    # Build DataFrame aligned on common years
    df = pd.DataFrame(gerd).dropna()
    df = df.loc[df.index >= 1996]

    colors = [palette[0], palette[1], palette[2], palette[3], palette[4], palette[5]]

    fig, ax = new_figure(9, 4.5)

    labels = list(df.columns)
    values = [df[col].values for col in labels]
    ax.stackplot(df.index, *values, colors=colors, labels=labels,
                 edgecolor='black', linewidth=0.5)

    ax.set_xlim(1996, df.index.max())
    xticks = list(range(2000, int(df.index.max()) + 1, 5))
    if 1996 not in xticks:
        xticks = [1996] + xticks
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)
    ax.set_ylabel(r"Milliards \$US PPA (2021)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 2500)
    ax.set_yticks(range(0, 2501, 500))
    ax.set_yticklabels([f'{y:,}'.replace(',', r'\,') for y in range(0, 2501, 500)],
                       fontsize=11)

    style_axes(ax)

    # Legend: reverse order so it matches visual stacking (top = last)
    handles, leg_labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], leg_labels[::-1], frameon=False, fontsize=9,
              loc='upper left', bbox_to_anchor=(0.0, 1.0))

    add_source(ax, 'Source: Banque mondiale (GERD = R\\&D/PIB $\\times$ PIB PPA)')
    save(fig, 'rd_spending_global.png')


# =====================================================================
# Figure 12: Moore's Law — transistor count (1971–2024)
# =====================================================================
def moores_law():
    """Log-scale scatter of transistor counts over time (Moore's Law)."""
    print("Figure 12: Moore's Law")

    data_dir = os.path.join(Path(__file__).resolve().parent.parent, 'Data')
    df = pd.read_csv(os.path.join(data_dir, 'moores_law.csv'))

    fig, ax = new_figure(9, 5)

    ax.scatter(df['year'], df['transistors'], s=70, color=palette[0],
               alpha=0.7, zorder=3, edgecolors='black', linewidths=0.3)

    # Moore's Law reference line: doubling every 2 years, spanning full x-axis
    ref_years = np.arange(1970, 2026)
    # Anchor at Intel 4004 (1971, 2300) and extend back/forward
    ref_transistors = 2300 * 2 ** ((ref_years - 1971) / 2)
    ax.plot(ref_years, ref_transistors, color=palette[1], linewidth=1.8,
            linestyle='-', alpha=0.8, zorder=2,
            label=r"Loi de Moore (doublement tous les 2 ans)")

    ax.set_yscale('log')
    ax.set_xlim(1970, 2025)
    ax.set_xticks(range(1970, 2026, 5))
    ax.set_xticklabels([str(y) for y in range(1970, 2026, 5)], fontsize=11)

    # Y-axis: powers of 10 (LaTeX-rendered for correct font)
    yticks = [10**i for i in range(3, 13)]
    ylabels = [r'$10^{' + str(i) + r'}$' for i in range(3, 13)]
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=11, usetex=True)
    ax.set_ylim(1e3, 1e12)

    ax.set_ylabel(r"Nombre de transistors par puce",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.grid(True, which='major', axis='y', color='gray', linestyle=':', linewidth=0.5)
    ax.legend(frameon=False, fontsize=9, loc='upper left')
    add_source(ax, 'Source: Karl Rupp (via Wikipedia)')
    save(fig, 'moores_law.png')


# =====================================================================
# Figure 13: Zimbabwe vs Botswana GDP per capita (1960–2019)
# =====================================================================
def zimbabwe_botswana():
    """GDP per capita comparison: institutions matter."""
    print('Figure 13: Zimbabwe vs Botswana')

    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')

    zwe = pwt[pwt['countrycode'] == 'ZWE'].set_index('year')['rgdpna'] / \
          pwt[pwt['countrycode'] == 'ZWE'].set_index('year')['pop']
    bwa = pwt[pwt['countrycode'] == 'BWA'].set_index('year')['rgdpna'] / \
          pwt[pwt['countrycode'] == 'BWA'].set_index('year')['pop']

    fig, ax = new_figure(9, 4.5)

    ax.plot(zwe.index, zwe.values, color=palette[0], linewidth=2.5,
            label='Zimbabwe')
    ax.plot(bwa.index, bwa.values, color=palette[1], linewidth=2.5,
            label='Botswana')

    ax.set_xlim(1960, 2020)
    ax.set_xticks(range(1960, 2021, 10))
    ax.set_xticklabels(range(1960, 2021, 10), fontsize=11)
    ax.set_ylabel(r"PIB réel par habitant (\$US)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 17500)
    ax.set_yticks(range(0, 17501, 2500))
    ax.set_yticklabels([f'{y:,}'.replace(',', r'\,') for y in range(0, 17501, 2500)],
                       fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'zimbabwe_botswana.png')


# =====================================================================
# Figure 14: Education plateau — average years of schooling
# =====================================================================
def education_plateau():
    """Average years of schooling for advanced economies (1880–2040)."""
    print('Figure 14: Education plateau')

    # Barro-Lee / Our World in Data — average years of schooling (25+)
    years = [1880, 1900, 1920, 1940, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2040]
    data = {
        r'États-Unis': [3.0, 4.5, 6.5, 8.0, 9.5, 10.5, 12.0, 12.5, 13.0, 13.2, 13.4, 13.5],
        'Canada':          [2.8, 4.0, 5.5, 7.5, 8.8, 10.0, 11.5, 12.0, 12.5, 13.0, 13.2, 13.3],
        'Australie':       [3.2, 4.8, 6.0, 7.5, 9.0, 10.0, 11.0, 12.0, 12.5, 12.8, 12.9, 13.0],
        'Royaume-Uni':     [2.0, 3.5, 5.0, 6.5, 8.5, 9.5, 10.5, 11.0, 12.0, 12.5, 13.0, 13.1],
        'France':          [1.0, 2.0, 4.0, 5.0, 6.0, 7.0, 8.5, 9.5, 10.5, 11.5, 12.0, 12.5],
        'Allemagne':       [3.0, 4.5, 6.0, 7.0, 6.5, 8.0, 9.5, 10.0, 12.5, 13.5, 14.1, 14.5],
    }
    colors = [palette[0], palette[2], palette[1], palette[3], palette[5], palette[7]]

    fig, ax = new_figure(9, 4.5)

    for (label, vals), color in zip(data.items(), colors):
        ax.plot(years, vals, 'o-', color=color, linewidth=2, markersize=3,
                label=label)

    # Annotation
    ax.annotate('Plateau?',
                xy=(2020, 13.4), xytext=(1985, 14.5),
                fontsize=12, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    ax.set_xlim(1875, 2045)
    ax.set_xticks(range(1880, 2041, 20))
    ax.set_xticklabels(range(1880, 2041, 20), fontsize=10)
    ax.set_ylabel(r"Années moyennes de scolarité (25+)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 16)
    ax.set_yticks(range(0, 17, 2))
    ax.set_yticklabels([str(y) for y in range(0, 17, 2)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=9, loc='center left',
              bbox_to_anchor=(0.0, 0.45))
    add_source(ax, 'Source: Barro-Lee; Our World in Data')
    save(fig, 'education_plateau.png')


# =====================================================================
# Figure 15: Development accounting — human capital
# =====================================================================
def development_accounting_human_capital():
    """Scatter: human capital vs GDP/capita relative to US."""
    print('Figure 15: Development accounting — human capital')

    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')
    yr = 2019
    dat = pwt[pwt['year'] == yr].dropna(subset=['rgdpna', 'pop', 'hc']).copy()
    dat['yn'] = dat['rgdpna'] / dat['pop']

    us_yn = dat.loc[dat['countrycode'] == 'USA', 'yn'].values[0]
    us_hc = dat.loc[dat['countrycode'] == 'USA', 'hc'].values[0]
    dat['yn_rel'] = dat['yn'] / us_yn
    dat['hc_rel'] = dat['hc'] / us_hc

    fig, ax = new_figure(9, 5)

    ax.scatter(dat['yn_rel'], dat['hc_rel'], s=50, color=palette[0],
               alpha=0.7, zorder=3)

    # 45-degree line
    ax.plot([1/90, 4], [1/90, 4], color=palette[1], linewidth=1.5, zorder=2)

    ax.set_xscale('log', base=2)
    ax.set_yscale('log', base=2)
    ax.set_xlim(1/90, 2)
    ax.set_ylim(1/90, 2)

    ticks = [1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2]
    tick_labels = ['1/64', '1/32', '1/16', '1/8', '1/4', '1/2', '1', '2']
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels, fontsize=11)
    ax.set_yticks(ticks)
    ax.set_yticklabels(tick_labels, fontsize=11)

    ax.set_xlabel(r"PIB réel par habitant relatif aux É.-U. (2019)",
                  fontsize=11)
    ax.set_ylabel(r"Capital humain relatif aux É.-U. (2019)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'development_accounting_human_capital.png')


# =====================================================================
# Figure 16: Tropics map — GDP per capita choropleth
# =====================================================================
def tropics_map():
    """World choropleth: GDP/capita in 3 tiers + tropic lines."""
    print('Figure 16: Tropics map')

    import geopandas as gpd
    from matplotlib.colors import ListedColormap

    # ── Load geometries (Natural Earth 110m) ─────────────────────────
    world = gpd.read_file(
        'https://naciscdn.org/naturalearth/110m/cultural/'
        'ne_110m_admin_0_countries.zip')
    world = world[world['NAME'] != 'Antarctica']

    # ── Load PWT 10.01 for GDP per capita ────────────────────────────
    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')
    pwt = pwt[pwt['year'] == 2019].copy()
    pwt['gdp_pc'] = pwt['rgdpna'] / pwt['pop']
    pwt = pwt[['countrycode', 'gdp_pc']].dropna()

    # ── Merge (ISO_A3 ↔ countrycode) ────────────────────────────────
    # Natural Earth uses -99 for missing ISO codes; also try ISO_A3_EH
    world['iso'] = world['ISO_A3'].where(
        world['ISO_A3'] != '-99', world['ISO_A3_EH'])
    world = world.merge(pwt, left_on='iso', right_on='countrycode',
                        how='left')

    # ── Classify into terciles ──────────────────────────────────────
    valid = world['gdp_pc'].dropna()
    t1 = valid.quantile(1 / 3)
    t2 = valid.quantile(2 / 3)
    world['tier'] = pd.cut(
        world['gdp_pc'], bins=[-np.inf, t1, t2, np.inf],
        labels=[0, 1, 2])
    world['tier'] = world['tier'].astype(float)  # NaN for missing data

    # ── Colours: coral (poor), yellow (mid), green (rich) ─────────────
    cmap = ListedColormap([palette[2], palette[3], palette[1]])

    # ── Plot ─────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    # Countries with data
    world[world['tier'].notna()].plot(
        column='tier', cmap=cmap, ax=ax, linewidth=0.3,
        edgecolor='black')
    # Countries without data: light gray
    world[world['tier'].isna()].plot(
        ax=ax, color='#d9d9d9', linewidth=0.3, edgecolor='black')

    # ── Tropic lines ────────────────────────────────────────────────
    for lat, label in [(23.4364, r'Tropique du Cancer'),
                       (-23.4364, r'Tropique du Capricorne')]:
        ax.axhline(lat, color='black', linewidth=0.8, linestyle='--',
                   zorder=4)

    # ── Equator (subtle) ────────────────────────────────────────────
    ax.axhline(0, color='black', linewidth=0.4, linestyle=':', zorder=4)

    # ── Legend ───────────────────────────────────────────────────────
    from matplotlib.patches import Patch
    legend_items = [
        Patch(facecolor=palette[1], edgecolor='white',
              label=r'PIB/hab. élevé'),
        Patch(facecolor=palette[3], edgecolor='white',
              label=r'PIB/hab. moyen'),
        Patch(facecolor=palette[2], edgecolor='white',
              label=r'PIB/hab. faible'),
    ]
    ax.legend(handles=legend_items, loc='lower left',
              fontsize=9, frameon=False,
              bbox_to_anchor=(0.0, -0.02))

    # ── Clean up axes ───────────────────────────────────────────────
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.axis('off')

    add_source(ax, 'Source: Penn World Tables 10.01 (2019)')
    save(fig, 'tropics.png')


# =====================================================================
# Figure 17: Education and prosperity — years of schooling vs GDP/capita
# =====================================================================
def education_prosperity():
    """Scatter: average years of schooling vs real GDP per capita."""
    print('Figure 17: Education and prosperity')

    # Fetch Our World in Data (average years of schooling vs GDP per capita)
    url = ("https://ourworldindata.org/grapher/"
           "average-years-of-schooling-vs-gdp-per-capita"
           ".csv?v=1&csvType=full&useColumnShortNames=true")
    df = pd.read_csv(url,
                      storage_options={'User-Agent':
                                       'Our World In Data data fetch/1.0'})

    # Keep 2022 with complete data, drop world aggregate
    df = df[(df['year'] == 2022)
            & df['mys__sex_total'].notna()
            & df['ny_gdp_pcap_pp_kd'].notna()
            & df['population_historical'].notna()
            & df['code'].notna()
            & (df['code'] != 'OWID_WRL')]

    fig, ax = new_figure(9, 4.5)

    ax.scatter(df['ny_gdp_pcap_pp_kd'], df['mys__sex_total'],
               s=df['population_historical'] / 5e5,
               alpha=0.6, facecolors=palette[0], edgecolors='k',
               linewidths=0.3, zorder=3)

    # X-axis: log scale
    ax.set_xscale('log')
    ax.set_xlim(1000, 150000)
    ax.set_xticks([1e3, 1e4, 1e5])
    ax.set_xticklabels([r'\$1\,000', r'\$10\,000', r'\$100\,000'],
                       fontsize=11)
    ax.set_xlabel(r"PIB réel par habitant, PPA (\$US 2017)",
                  fontsize=11)

    # Y-axis
    ax.set_ylim(0, 16)
    ax.set_yticks(range(0, 17, 2))
    ax.set_yticklabels([str(y) for y in range(0, 17, 2)], fontsize=11)
    ax.set_ylabel(r"Années moyennes de scolarité",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.grid(True, which='major', axis='both', color='gray',
            linestyle=':', linewidth=0.5)
    add_source(ax, 'Source: Our World in Data (2022)')
    save(fig, 'schooling.png')


# =====================================================================
# Figure 18: Digital Adoption Index vs GDP per capita
# =====================================================================
def digital_adoption_index():
    """Scatter: DAI vs real GDP per capita (log scale)."""
    print('Figure 16: Digital Adoption Index vs GDP/capita')

    # Load PWT 10.01 for real GDP per capita (2016)
    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')
    pwt = pwt[pwt['year'] == 2016].copy()
    pwt['rgdpe_pc'] = pwt['rgdpe'] / pwt['pop']

    # Load DAI data
    dai = pd.read_excel(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/DAIforweb.xlsx'
    ).rename(columns={'Year': 'year'})
    dai = dai.loc[dai['year'] == 2016, ['country', 'Digital Adoption Index']]

    # Merge
    df = pwt.merge(dai, on='country')

    fig, ax = new_figure(9, 4.5)

    ax.scatter(df['rgdpe_pc'], df['Digital Adoption Index'],
               s=70, color=palette[0], alpha=0.7, edgecolors='black',
               linewidths=0.3, zorder=3)

    # X-axis: log scale
    ax.set_xscale('log')
    ax.set_xlim(700, 120000)
    ax.set_xticks([1e3, 1e4, 1e5])
    ax.set_xticklabels([r'\$1\,000', r'\$10\,000', r'\$100\,000'],
                       fontsize=11)
    ax.set_xlabel(r"PIB réel par habitant (\$US)", fontsize=11)

    # Y-axis
    ax.set_ylim(0, 1)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_yticklabels([f'{x:.1f}' for x in np.arange(0, 1.01, 0.2)],
                       fontsize=11)
    ax.set_ylabel(r"Indice d'adoption numérique",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, 'Source: Banque mondiale (DAI) et Penn World Tables 10.01')
    save(fig, 'dai.png')


# =====================================================================
# Figure 19: Canada GDP/capita decomposition — 5-year periods
# =====================================================================
def canada_gdp_decomposition_5y():
    """Stacked bar: decompose Canadian Y/N growth into A, K/Y, L/N (5-yr)."""
    print('Figure 19: Canada GDP/capita decomposition (5-year periods)')

    pwt = pd.read_stata(
        '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')
    ca = pwt[pwt['countrycode'] == 'CAN'].set_index('year')

    alpha = 1 / 3
    amp_ky = alpha / (1 - alpha)  # 0.5

    # 5-year periods from 1970 to 2019
    periods = []
    for y1 in range(1975, 2020, 5):
        y0 = y1 - 5
        periods.append((str(y1), y0, y1))

    a_vals, ky_vals, ln_vals, yn_vals = [], [], [], []
    for label, y0, y1 in periods:
        T = y1 - y0
        yn0 = ca.loc[y0, 'rgdpna'] / ca.loc[y0, 'pop']
        yn1 = ca.loc[y1, 'rgdpna'] / ca.loc[y1, 'pop']
        ky0 = ca.loc[y0, 'rkna'] / ca.loc[y0, 'rgdpna']
        ky1 = ca.loc[y1, 'rkna'] / ca.loc[y1, 'rgdpna']
        ln0 = ca.loc[y0, 'emp'] / ca.loc[y0, 'pop']
        ln1 = ca.loc[y1, 'emp'] / ca.loc[y1, 'pop']

        g_yn = ((yn1 / yn0) ** (1 / T) - 1) * 100
        g_ky = ((ky1 / ky0) ** (1 / T) - 1) * 100
        g_ln = ((ln1 / ln0) ** (1 / T) - 1) * 100

        ky_c = amp_ky * g_ky
        ln_c = g_ln
        a_c = g_yn - ky_c - ln_c

        a_vals.append(a_c)
        ky_vals.append(ky_c)
        ln_vals.append(ln_c)
        yn_vals.append(g_yn)

    x = np.arange(len(periods))
    labels = [p[0] for p in periods]
    w = 0.6

    fig, ax = new_figure(10, 5)

    components = [
        (ln_vals, palette[2], r"Taux d'emploi ($L/N$)"),
        (a_vals, palette[0], r"Productivité ($A$)"),
        (ky_vals, palette[1], r"Capital/PIB ($K/Y$)"),
    ]

    # Track L/N bar positions for circling
    ln_bars = []  # (x_center, bottom, top) for each bar

    for i in range(len(periods)):
        pos_base = 0
        neg_base = 0
        for j, (vals, color, label) in enumerate(components):
            v = vals[i]
            if v >= 0:
                ax.bar(x[i], v, w, bottom=pos_base, color=color,
                       label=label if i == 0 else None)
                if j == 0:  # L/N
                    ln_bars.append((x[i], pos_base, pos_base + v))
                pos_base += v
            else:
                ax.bar(x[i], v, w, bottom=neg_base, color=color,
                       label=label if i == 0 else None)
                if j == 0:  # L/N
                    ln_bars.append((x[i], neg_base + v, neg_base))
                neg_base += v

    # Circle the 1975 and 1980 L/N bars (indices 0 and 1)
    from matplotlib.patches import Ellipse
    for idx in [0, 1]:
        cx, bot, top = ln_bars[idx]
        h = top - bot
        ell = Ellipse((cx, bot + h / 2), width=w + 0.3, height=h + 0.25,
                      fill=False, edgecolor=palette[3], linewidth=2.5,
                      zorder=10)
        ax.add_patch(ell)

    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_xlabel(r"Période de 5 ans se terminant en\ldots", fontsize=11)
    ax.set_ylabel(r"Contribution à la croissance de $Y/N$ (\%/an)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    ax.set_ylim(-1.0, 3.5)
    ax.set_yticks(np.arange(-1.0, 3.6, 0.5))
    ax.set_yticklabels([f'{y:.1f}' + r'\%' for y in np.arange(-1.0, 3.6, 0.5)],
                       fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, 'Source: Penn World Tables 10.01 --- Canada')
    save(fig, 'canada_gdp_decomposition_5y.png')


# =====================================================================
# Figure 20: Participation rate by gender (Canada, 1976–present)
# =====================================================================
def participation_gender_ca():
    """Participation rate by gender + total employment rate — Canada."""
    print('Figure 20: Participation & employment by gender (Canada)')

    from stats_can import StatsCan
    sc = StatsCan()

    df = sc.table_to_df('14-10-0287-01')
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])

    # Keep seasonally adjusted, 15+, estimate only
    df = df[df['Data type'] == 'Seasonally adjusted']
    df = df[df['Age group'] == '15 years and over']
    df = df[df['Statistics'] == 'Estimate']

    # Participation rates by gender
    part = df[df['Labour force characteristics'] == 'Participation rate']
    male = part[part['Gender'] == 'Men+'].set_index('REF_DATE')['VALUE']
    female = part[part['Gender'] == 'Women+'].set_index('REF_DATE')['VALUE']
    male = male[~male.index.duplicated(keep='first')].sort_index()
    female = female[~female.index.duplicated(keep='first')].sort_index()

    # Overall employment rate
    emp = df[df['Labour force characteristics'] == 'Employment rate']
    emp_total = emp[emp['Gender'] == 'Total - Gender'].set_index('REF_DATE')['VALUE']
    emp_total = emp_total[~emp_total.index.duplicated(keep='first')].sort_index()

    fig, ax = new_figure(9, 4.5)

    ax.plot(male.index, male.values, color=palette[0],
            linewidth=2, label='Participation --- Hommes')
    ax.plot(female.index, female.values, color=palette[2],
            linewidth=2, label='Participation --- Femmes')
    ax.plot(emp_total.index, emp_total.values, color=palette[1],
            linewidth=2, linestyle='--', label="Emploi --- Total")

    import matplotlib.dates as mdates
    ax.set_xlim(pd.Timestamp('1976-01-01'), pd.Timestamp('2010-12-31'))
    tick_years = range(1980, 2011, 10)
    tick_dates = [pd.Timestamp(f'{y}-01-01') for y in tick_years]
    ax.set_xticks(tick_dates)
    ax.set_xticklabels([str(y) for y in tick_years], fontsize=11)
    ax.set_ylabel(r"Pourcentage (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(45, 80)
    ax.set_yticks(range(45, 81, 5))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(45, 81, 5)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right')
    add_source(ax, r"Source: Statistique Canada, tableau 14-10-0287-01")
    save(fig, 'participation_gender_ca.png')


# =====================================================================
# Figure 22: Unemployment rate (Canada, 1976–present)
# =====================================================================
def unemployment_ca():
    """Unemployment rate — Canada (StatsCan 14-10-0287-01)."""
    print('Figure 22: Unemployment rate (Canada)')

    from stats_can import StatsCan
    sc = StatsCan()

    df = sc.table_to_df('14-10-0287-01')
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])

    df = df[df['Data type'] == 'Seasonally adjusted']
    df = df[df['Gender'] == 'Total - Gender']
    df = df[df['Age group'] == '15 years and over']
    df = df[df['Statistics'] == 'Estimate']
    df = df[df['Labour force characteristics'] == 'Unemployment rate']

    unemp = df.set_index('REF_DATE')['VALUE']
    unemp = unemp[~unemp.index.duplicated(keep='first')].sort_index()

    fig, ax = new_figure(9, 4.5)

    ax.plot(unemp.index, unemp.values, color=palette[2], linewidth=2)

    # Recession shading
    for start, end in recessions_ca:
        ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    # Annotate major peaks
    annotations = [
        (pd.Timestamp('1982-12-01'), 13.1, '1982\n$\\sim$13\\%'),
        (pd.Timestamp('1992-11-01'), 11.8, '1992\n$\\sim$12\\%'),
        (pd.Timestamp('2009-06-01'), 8.7, '2009\n$\\sim$9\\%'),
        (pd.Timestamp('2020-05-01'), 13.7, 'COVID\n$\\sim$14\\%'),
    ]
    for date, peak, label in annotations:
        ax.annotate(label,
                    xy=(date, peak), xytext=(0, 15),
                    textcoords='offset points',
                    fontsize=9, color=palette[0], fontweight='bold',
                    ha='center', va='bottom')

    import matplotlib.dates as mdates
    ax.set_xlim(pd.Timestamp('1976-01-01'), unemp.index.max())
    tick_years = range(1980, unemp.index.max().year + 1, 10)
    tick_dates = [pd.Timestamp(f'{y}-01-01') for y in tick_years]
    ax.set_xticks(tick_dates)
    ax.set_xticklabels([str(y) for y in tick_years], fontsize=11)
    ax.set_ylabel(r"Taux de chômage (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(4, 16)
    ax.set_yticks(range(4, 17, 2))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(4, 17, 2)], fontsize=11)

    style_axes(ax)
    add_source(ax, r"Source: Statistique Canada, tableau 14-10-0287-01")
    save(fig, 'unemployment_ca.png')


# =====================================================================
# Figure 22b: Participation rate decline (Canada, total)
# =====================================================================
def participation_rate_ca():
    """Total participation rate — Canada (StatsCan 14-10-0287-01)."""
    print('Figure 22b: Participation rate decline (Canada)')

    from stats_can import StatsCan
    sc = StatsCan()

    df = sc.table_to_df('14-10-0287-01')
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])

    df = df[df['Data type'] == 'Seasonally adjusted']
    df = df[df['Gender'] == 'Total - Gender']
    df = df[df['Age group'] == '15 years and over']
    df = df[df['Statistics'] == 'Estimate']
    df = df[df['Labour force characteristics'] == 'Participation rate']

    part = df.set_index('REF_DATE')['VALUE']
    part = part[~part.index.duplicated(keep='first')].sort_index()

    fig, ax = new_figure(9, 4.5)

    ax.plot(part.index, part.values, color=palette[0], linewidth=2.5)

    # Recession shading
    for start, end in recessions_ca:
        ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    import matplotlib.dates as mdates
    ax.set_xlim(pd.Timestamp('1976-01-01'), pd.Timestamp('2020-01-01'))
    tick_years = list(range(1980, 2020, 10)) + [2020]
    tick_dates = [pd.Timestamp(f'{y}-01-01') for y in tick_years]
    ax.set_xticks(tick_dates)
    ax.set_xticklabels([str(y) for y in tick_years], fontsize=11)
    ax.set_ylabel(r"Taux de participation (\%)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(60, 68)
    ax.set_yticks(range(60, 69, 2))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(60, 69, 2)], fontsize=11)

    style_axes(ax)
    add_source(ax, r"Source: Statistique Canada, tableau 14-10-0287-01")
    save(fig, 'participation_rate_ca.png')


# =====================================================================
# Figure 23: Immigration to Canada — PR + temporary as % of population
# =====================================================================
def immigration_ca():
    """Stacked area: immigrants (PR) and net non-permanent residents as % of population."""
    print('Figure 23: Immigration to Canada (% of population)')

    from stats_can import StatsCan
    sc = StatsCan()

    # ── Migration data: StatsCan 17-10-0014-01 ───────────────────────
    mig = sc.table_to_df('17-10-0014-01')
    mig = mig[mig['GEO'] == 'Canada']
    mig = mig[mig['Age group'] == 'All ages']
    mig = mig[mig['Gender'] == 'Total - gender']

    # REF_DATE format is '1971/1972' — extract first year
    mig['year'] = mig['REF_DATE'].str.split('/').str[0].astype(int)

    immigrants = (mig[mig['Type of migrant'] == 'Immigrants']
                  .set_index('year')['VALUE'])
    net_npr = (mig[mig['Type of migrant'] == 'Net non-permanent residents']
               .set_index('year')['VALUE'])
    immigrants = immigrants[~immigrants.index.duplicated(keep='first')].sort_index()
    net_npr = net_npr[~net_npr.index.duplicated(keep='first')].sort_index()

    # ── Population: StatsCan 17-10-0005-01 ────────────────────────────
    pop = sc.table_to_df('17-10-0005-01')
    pop = pop[pop['GEO'] == 'Canada']
    pop = pop[pop['Age group'] == 'All ages']
    pop = pop[pop['Gender'] == 'Total - gender']
    pop['REF_DATE'] = pd.to_datetime(pop['REF_DATE'])
    pop['year'] = pop['REF_DATE'].dt.year
    pop = pop.set_index('year')['VALUE']
    pop = pop[~pop.index.duplicated(keep='first')].sort_index()

    # ── Compute as % of population ────────────────────────────────────
    common = immigrants.index.intersection(net_npr.index).intersection(pop.index)
    imm_pct = (immigrants[common] / pop[common]) * 100
    npr_pct = (net_npr[common] / pop[common]) * 100
    # Clip negative NPR values to 0 for stacked area display
    npr_pct_pos = npr_pct.clip(lower=0)

    fig, ax = new_figure(9, 4.5)

    ax.stackplot(imm_pct.index, imm_pct.values, npr_pct_pos.values,
                 colors=[palette[0], palette[1]],
                 labels=[r'Résidents permanents',
                         r'Résidents temporaires (net)'],
                 edgecolor='k', linewidth=0.5)

    ax.set_xlim(imm_pct.index.min(), imm_pct.index.max())
    xticks = list(range(((imm_pct.index.min() // 10) + 1) * 10,
                        imm_pct.index.max() + 1, 10))
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(y) for y in xticks], fontsize=11)
    ax.set_ylabel(r"Immigration (\% de la population)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 3.5)
    ax.set_yticks(np.arange(0, 3.6, 0.5))
    ax.set_yticklabels([f'{y:.1f}' + r'\%' for y in np.arange(0, 3.6, 0.5)],
                       fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0))
    add_source(ax, r"Source: Statistique Canada, tableaux 17-10-0014-01 et 17-10-0005-01")
    save(fig, 'immigration_ca.png')


def elephant_curve():
    """Elephant curve of global inequality, 1980-2020 (WIR 2022)."""
    print('  elephant_curve ...', end=' ', flush=True)

    # ── Data from World Inequality Report 2022, Figure 2.10 ──────────
    url = ('https://wir2022.wid.world/www-site/uploads/2022/03/'
           'WIR2022TablesFigures-Chapter.zip')
    import zipfile, io
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        with zf.open('WIR2022TablesFigures-Chapter/'
                     'WIR2022TablesFigures-Chapter2.xlsx') as f:
            df = pd.read_excel(f, sheet_name='data-F2.10')

    # Values are cumulative growth rates (divided by 100)
    df.columns = ['percentile', 'growth_raw']
    df['growth_pct'] = df['growth_raw'] * 100

    # Keep only the main curve (p10-p99) for clarity on a linear x-axis.
    main = df[df['percentile'] <= 99].copy()

    fig, ax = new_figure(8, 4)

    ax.plot(main['percentile'], main['growth_pct'],
            color=palette[0], linewidth=2.5, zorder=3)
    ax.fill_between(main['percentile'], 50, main['growth_pct'],
                    color=palette[0], alpha=0.08, zorder=2)

    # ── Axes ─────────────────────────────────────────────────────
    ax.set_xlim(10, 100)
    ax.set_xticks(range(10, 101, 10))
    ax.set_xticklabels([str(x) for x in range(10, 101, 10)], fontsize=13)
    ax.set_xlabel(r'Centile de la distribution mondiale du revenu',
                  fontsize=13)

    ax.set_ylim(50, 210)
    yticks = list(range(50, 211, 50))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}' + r'\%' for y in yticks], fontsize=13)
    ax.set_ylabel(r"Croissance cumulée du revenu réel, 1980--2020",
                  fontsize=13, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, r'Source: World Inequality Report 2022 (Chancel et al.)')
    save(fig, 'elephant.png')


def inequality_top1_share():
    """Top 1% pre-tax income share for 8 countries (WID via OWID)."""
    print('  inequality_top1_share ...', end=' ', flush=True)

    df = pd.read_csv(
        "https://ourworldindata.org/grapher/income-share-top-1-before-tax-wid"
        ".csv?v=1&csvType=full&useColumnShortNames=true",
        storage_options={'User-Agent': 'Our World In Data data fetch/1.0'},
    )

    codes    = ['USA', 'AUS', 'CAN', 'GBR', 'CHN', 'FRA', 'IND', 'DEU']
    labels   = [r'États-Unis', 'Australie', 'Canada', 'Royaume-Uni',
                'Chine', 'France', 'Inde', 'Allemagne']
    colors   = [palette[0], palette[1], palette[2], palette[3],
                palette[4], palette[5], palette[6], palette[7]]

    val_col = [c for c in df.columns if c not in ('entity', 'code', 'year')][0]
    df = df[df['code'].isin(codes)]

    fig, ax = new_figure(8, 4)

    for code, label, color in zip(codes, labels, colors):
        sub = df[df['code'] == code].sort_values('year')
        ax.plot(sub['year'], sub[val_col],
                label=label, color=color, linewidth=2)

    latest = int(df['year'].max())
    ax.set_xlim(1950, latest)
    ax.set_xticks(range(1950, 2020 + 1, 10))
    ax.set_xticklabels(range(1950, 2020 + 1, 10), fontsize=12)

    ax.set_ylim(4, 28)
    ax.set_yticks(range(4, 28 + 1, 4))
    ax.set_yticklabels([f'{x}' + r'\%' for x in range(4, 28 + 1, 4)],
                        fontsize=12)
    ax.set_ylabel(r"Part du revenu du 1\% le plus riche (avant impôt)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(-0.01, 1.0))
    add_source(ax, 'Source: World Inequality Database (2025)')
    save(fig, 'inequality_within_countries.png')


# =====================================================================
# Outsourcing: within vs between firm inequality (Song et al. 2019)
# =====================================================================
def outsourcing_inequality():
    """Between- vs within-firm decomposition of earnings inequality growth."""
    print('  outsourcing_inequality ...', end=' ', flush=True)

    # Data from Song, Price, Guvenen, Bloom & von Wachter (QJE, 2019)
    # Change in variance of log earnings, US, 1981-2013
    categories = [r'\textbf{Entre} les' + '\n' + r'entreprises',
                  r'\textbf{Au sein} des' + '\n' + r'entreprises']
    shares = [2/3, 1/3]       # fraction of total increase
    total_increase = 100       # normalised to 100%
    values = [s * total_increase for s in shares]

    fig, ax = new_figure(6, 4.5)

    bars = ax.bar(categories, values, width=0.55,
                  color=[palette[0], palette[1]], edgecolor='none', zorder=3)

    # Value labels on bars
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                f'{v:.0f}' + r'\%', ha='center', va='bottom',
                fontsize=14, fontweight='bold',
                color=palette[0] if v > 50 else palette[1])

    ax.set_ylim(0, 85)
    ax.set_yticks([])
    ax.tick_params(axis='x', labelsize=13)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.set_ylabel(r"Contribution à la hausse des inégalités salariales",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.05)

    add_source(ax, r'Source: Song, Price, Guvenen, Bloom \& von Wachter (QJE, 2019)')
    save(fig, 'outsourcing_inequality.png')


# =====================================================================
# Job polarization: routine vs nonroutine employment (US, 1983-2024)
# =====================================================================
def job_polarization():
    """Employment by occupational group (routine vs nonroutine, US)."""
    print('  job_polarization ...', end=' ', flush=True)

    # FRED series (CPS Table A-13, annual averages)
    nrc = get_fred_data('LNU02032201', frequency='a', aggregation_method='avg')  # Mgmt/Prof
    nrm = get_fred_data('LNU02032204', frequency='a', aggregation_method='avg')  # Service
    rc  = get_fred_data('LNU02032205', frequency='a', aggregation_method='avg')  # Sales/Office
    rm1 = get_fred_data('LNU02032210', frequency='a', aggregation_method='avg')  # Production/Transport
    rm2 = get_fred_data('LNU02032211', frequency='a', aggregation_method='avg')  # Construction
    rm3 = get_fred_data('LNU02032212', frequency='a', aggregation_method='avg')  # Install/Maint/Repair

    # Combine routine manual
    rm = rm1 + rm2 + rm3

    # Convert to millions
    nrc, nrm, rc, rm = nrc / 1000, nrm / 1000, rc / 1000, rm / 1000

    # Drop NaNs and align
    df = pd.DataFrame({'nrc': nrc, 'nrm': nrm, 'rc': rc, 'rm': rm}).dropna()

    # Normalize to 100 at start of series (1983)
    for col in df.columns:
        df[col] = df[col] / df[col].iloc[0] * 100

    years = df.index.year

    fig, ax = new_figure(9, 4.5)

    # Non-routine: solid lines; routine: dotted lines
    # Cognitive: navy; Manual: green
    ax.plot(years, df['nrc'], color=palette[0], linewidth=2.5, linestyle='-',
            label='Non routinier cognitif')
    ax.plot(years, df['nrm'], color=palette[1], linewidth=2.5, linestyle='-',
            label='Non routinier manuel')
    ax.plot(years, df['rc'], color=palette[0], linewidth=2.5, linestyle=':',
            label='Routinier cognitif')
    ax.plot(years, df['rm'], color=palette[1], linewidth=2.5, linestyle=':',
            label='Routinier manuel')

    ax.set_xlim(1983, 2025)
    ax.set_xticks(range(1985, 2026, 5))
    ax.set_xticklabels(range(1985, 2026, 5), fontsize=12)
    ax.set_ylim(100, 260)
    ax.set_yticks(range(100, 261, 20))
    ax.set_yticklabels([f'{y}' for y in range(100, 261, 20)], fontsize=12)
    ax.set_ylabel(r"Indice (1983 = 100)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Recession shading
    for start, end in recessions_us:
        if start >= pd.Timestamp('1983-01-01'):
            ax.axvspan(start.year + start.month / 12,
                       end.year + end.month / 12,
                       color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(-0.01, 1.0))
    add_source(ax, r'Source: BLS, Current Population Survey (via FRED)')
    save(fig, 'job_polarization.png')


# =====================================================================
# Great Gatsby Curve (Corak 2013)
# =====================================================================
def gatsby_curve():
    """Scatter: Gini coefficient vs intergenerational earnings elasticity.

    IGE estimates: Corak (2013), "Inequality from Generation to Generation:
    The United States in Comparison," Figure 1 — exact published values for
    22 countries, derived from a meta-analysis of the literature as described
    in Corak (2006, IZA DP 1993).

    Gini coefficients: World Bank SI.POV.GINI, closest available to ~2005
    (most recent data available when Corak wrote his paper, ~2010).
    NZL and SGP have no World Bank Gini; we use OECD (NZL, ~2004) and
    Singapore Department of Statistics (SGP, ~2000).
    """
    print('Figure: Great Gatsby Curve')

    # ── IGE: exact values from Corak (2013) Figure 1 ──────────────────
    ige_corak = {
        'DNK': 0.15, 'NOR': 0.17, 'FIN': 0.18, 'CAN': 0.19,
        'SWE': 0.27, 'AUS': 0.26, 'NZL': 0.29, 'DEU': 0.32,
        'JPN': 0.34, 'FRA': 0.41, 'ESP': 0.40, 'PAK': 0.46,
        'CHE': 0.46, 'ITA': 0.50, 'GBR': 0.50, 'USA': 0.47,
        'SGP': 0.44, 'ARG': 0.49, 'CHN': 0.60, 'CHL': 0.52,
        'BRA': 0.58, 'PER': 0.67,
    }

    # ── Gini: World Bank API (SI.POV.GINI), closest to ~1995 ─────────
    iso_to_fr = {
        'DNK': 'Danemark', 'NOR': 'Norvège', 'FIN': 'Finlande',
        'CAN': 'Canada', 'SWE': 'Suède', 'AUS': 'Australie',
        'NZL': 'Nlle-Zélande', 'DEU': 'Allemagne', 'JPN': 'Japon',
        'FRA': 'France', 'ESP': 'Espagne', 'PAK': 'Pakistan',
        'CHE': 'Suisse', 'ITA': 'Italie', 'GBR': 'Royaume-Uni',
        'USA': 'États-Unis', 'SGP': 'Singapour', 'ARG': 'Argentine',
        'CHN': 'Chine', 'CHL': 'Chili', 'BRA': 'Brésil',
        'PER': 'Pérou',
    }

    # Fetch from World Bank
    iso_list = ';'.join(iso_to_fr.keys())
    wb_url = (f'https://api.worldbank.org/v2/country/{iso_list}'
              f'/indicator/SI.POV.GINI?date=1985:2005&format=json&per_page=1500')
    from collections import defaultdict
    gini_wb = defaultdict(list)
    try:
        wb = requests.get(wb_url, timeout=30).json()
        if len(wb) > 1 and wb[1]:
            for e in wb[1]:
                if e['value'] is not None:
                    gini_wb[e['countryiso3code']].append(
                        (int(e['date']), e['value']))
    except Exception as exc:
        print(f'  World Bank API failed ({exc}); using fallback Gini')

    # Pick closest year to 2005 for each country
    target_year = 2005
    gini_selected = {}
    for iso in iso_to_fr:
        entries = sorted(gini_wb.get(iso, []),
                         key=lambda x: abs(x[0] - target_year))
        if entries:
            year, val = entries[0]
            gini_selected[iso] = val

    # Fallback / override for countries with no or sparse WB data
    # JPN: OECD Income Distribution Database, ~2006 ≈ 32.1
    # NZL: OECD Income Distribution Database, ~2004 ≈ 33.5
    # SGP: Singapore Dept of Statistics, ~2000 ≈ 42.5
    fallbacks = {'JPN': 32.1, 'NZL': 33.5, 'SGP': 42.5}
    for iso, val in fallbacks.items():
        if iso not in gini_selected:
            gini_selected[iso] = val

    # Build the final data dict  {French name: (Gini, IGE)}
    data = {}
    for iso, fr_name in iso_to_fr.items():
        if iso in gini_selected and iso in ige_corak:
            data[fr_name] = (gini_selected[iso], ige_corak[iso])

    countries = list(data.keys())
    gini = np.array([data[c][0] for c in countries])
    ige  = np.array([data[c][1] for c in countries])

    fig, ax = new_figure(8, 4)

    # Scatter
    ax.scatter(gini, ige, s=90, color=palette[0], alpha=0.75, zorder=5,
               edgecolors=palette[0], linewidth=0.8)

    # Highlight Canada
    idx_ca = countries.index('Canada')
    ax.scatter(gini[idx_ca], ige[idx_ca], s=110, color=palette[1], alpha=0.85, zorder=6,
               edgecolors=palette[0], linewidth=0.8)

    # Trend line — span the full x-axis range
    z = np.polyfit(gini, ige, 1)
    x_line = np.linspace(22, 62, 100)
    ax.plot(x_line, np.polyval(z, x_line), color=palette[2], linewidth=2, zorder=2)

    # Labels — offset logic to avoid collisions (tuned to WB ~2005 Gini)
    offsets = {
        'Danemark':     ( 1,  -0.025),
        'Norvège':      ( 1,  -0.025),
        'Finlande':     (-1,   0.015),
        'Canada':       ( 1,   0.015),
        'Suède':        (-1,   0.015),
        'Australie':    ( 1,  -0.025),
        'Nlle-Zélande': (-1,  -0.025),
        'Allemagne':    (-1,   0.015),
        'Japon':        (-1,  -0.025),
        'France':       (-1,   0.015),
        'Espagne':      ( 1,  -0.025),
        'Pakistan':     (-1,  -0.025),
        'Suisse':       (-1,   0.02),
        'Italie':       (-1,   0.02),
        'Royaume-Uni':  ( 1,   0.015),
        'États-Unis':   ( 1,  -0.025),
        'Singapour':    ( 1,  -0.025),
        'Argentine':    ( 1,   0.015),
        'Chine':        (-1,   0.015),
        'Chili':        ( 1,  -0.025),
        'Brésil':       ( 1,   0.015),
        'Pérou':        ( 0,   0.025),
    }

    for i, c in enumerate(countries):
        dx, dy = offsets.get(c, (1, 0.01))
        ha = 'right' if dx < 0 else 'left' if dx > 0 else 'center'
        color = palette[1] if c == 'Canada' else palette[7]
        weight = 'bold' if c == 'Canada' else 'normal'
        ax.text(gini[i] + dx * 0.5, ige[i] + dy, c, fontsize=8, ha=ha, va='center',
                color=color, fontweight=weight)

    style_axes(ax)
    ax.grid(True, which='major', axis='x', color='gray', linestyle=':', linewidth=0.5)
    ax.set_xlabel(r"Inégalité des revenus (coefficient de Gini)", fontsize=12)
    ax.set_ylabel(r"Élasticité intergénérationnelle", fontsize=12,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.03)
    ax.set_xlim(22, 62)
    ax.set_ylim(0.10, 0.70)
    ax.set_yticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
    ax.set_yticklabels([r'0.1', r'0.2', r'0.3', r'0.4',
                        r'0.5', r'0.6', r'0.7'])
    ax.set_xticks([25, 30, 35, 40, 45, 50, 55, 60])
    ax.set_xticklabels([r'25', r'30', r'35', r'40', r'45', r'50', r'55', r'60'])
    ax.tick_params(labelsize=12)

    add_source(ax, r"Source: Corak (2013); World Bank"
               r" (Gini, c.\,2005)")
    save(fig, 'gatsby_curve.png')


# =====================================================================
# Baumol cost disease — cumulative CPI by sector (Canada, 2000–2025)
# =====================================================================
def baumol_cost_disease_canada():
    """Perry-style 'Chart of the Century' for Canada (2000 = 100).

    Shows 8 CPI sub-categories from Statistics Canada table 18-10-0005-01,
    normalized to 2000 = 100. Labor-intensive services that are hard to
    automate (health care, tuition, restaurants, shelter) soar far above
    the CPI reference line, while tradeable/tech-driven goods (digital
    equipment, telephone, clothing) fall dramatically.

    Inspired by Mark Perry's AEI chart.
    """
    print('  baumol_cost_disease_canada ...', end=' ', flush=True)

    from stats_can import StatsCan
    sc = StatsCan()
    df = sc.table_to_df('18-10-0005-01')

    # Filter: Canada, base 2002 = 100
    ca = df[(df['GEO'] == 'Canada') & (df['UOM'] == '2002=100')].copy()
    ca['year'] = ca['REF_DATE'].dt.year
    ca = ca[ca['year'] >= 2000].sort_values('year')

    # ── Series specification (without colors — assigned by gradient) ──
    # Ordered from highest to lowest final value
    # (eng_name, fr_label, linestyle, linewidth)
    series_spec_no_color = [
        ('Health care services',
         r"Santé", '-', 2.5),
        ('Food purchased from restaurants',
         r"Restaurants", '-', 2.5),
        ('Tuition fees',
         r"Frais de scolarité", '-', 2.5),
        ('Shelter',
         r"Logement", '-', 2.5),
        ('Clothing and footwear',
         r"Vêtements et chaussures", '-', 2.5),
        ('Toys, games (excluding video games) and hobby supplies',
         r"Jouets et jeux", '-', 2.5),
        ('Telephone services',
         r"Téléphone", '-', 2.5),
        ('Home entertainment equipment, parts and services',
         r"Divertissement maison", '-', 2.5),
        ('Video equipment',
         r"Vidéo", '-', 2.5),
        ('Digital computing equipment and devices',
         r"Équipement informatique", '-', 2.5),
    ]

    # ── Colormap gradient: warm (red) → cool (blue) ──────────────────
    from matplotlib.colors import LinearSegmentedColormap
    import matplotlib.cm as cm
    # Custom gradient: saturated red → saturated purple → saturated blue
    # No pale/white midpoint — stays vivid throughout
    from matplotlib.colors import LinearSegmentedColormap as LSC
    custom_cmap = LSC.from_list('warm_cool', [
        '#b5000e',   # deep red
        '#e04530',   # bright red
        '#d4700a',   # orange
        '#8c5fb0',   # muted purple
        '#3a7ebf',   # medium blue
        '#1a4e8a',   # dark blue
        '#0a2f5c',   # navy
    ])
    n = len(series_spec_no_color)
    gradient_colors = [custom_cmap(i / (n - 1)) for i in range(n)]

    # CPI reference stays gray, inserted at its rank position
    c_cpi = palette[7]

    # Build final series_spec with colors
    series_spec = []
    for i, (eng_name, fr_label, ls, lw) in enumerate(series_spec_no_color):
        series_spec.append((eng_name, fr_label, gradient_colors[i], ls, lw))
    # Insert CPI after Shelter (index 4)
    series_spec.insert(4, ('All-items', r"IPC global", c_cpi, ':', 2.5))

    # ── Build data dict {eng_name: Series indexed by year} ─────────────
    series_data = {}
    for eng_name, *_ in series_spec:
        sub = ca[ca['Products and product groups'] == eng_name]
        s = sub.set_index('year')['VALUE'].dropna().sort_index()
        if len(s) == 0:
            print(f'  Warning: no data for "{eng_name}"')
            continue
        base_val = s.loc[2000] if 2000 in s.index else s.iloc[0]
        s = s / base_val * 100
        series_data[eng_name] = s

    # ── Plot ───────────────────────────────────────────────────────────
    fig, ax = new_figure(10, 5.5)

    for eng_name, fr_label, color, ls, lw in series_spec:
        if eng_name not in series_data:
            continue
        s = series_data[eng_name]
        ax.plot(s.index, s.values, color=color, linewidth=lw,
                linestyle=ls, zorder=3)

    # ── End-of-line labels (with repulsion to avoid overlap) ─────────
    last_year = max(s.index[-1] for s in series_data.values())

    # Collect (eng_name, final_value) for all plotted series
    label_items = []
    for eng_name, fr_label, color, ls, lw in series_spec:
        if eng_name not in series_data:
            continue
        s = series_data[eng_name]
        label_items.append((eng_name, fr_label, color, s.iloc[-1]))

    # Sort by final value (descending) and repel labels so they don't overlap
    label_items.sort(key=lambda x: -x[3])
    min_gap = 10.0  # minimum vertical gap in data-units between label centers
    placed_y = []    # list of placed y-positions (descending order)
    label_positions = {}  # eng_name -> placed y

    for eng_name, fr_label, color, raw_y in label_items:
        y = raw_y
        # Push label down if it collides with any already-placed label above
        for py in placed_y:
            if py - y < min_gap:
                y = py - min_gap
        placed_y.append(y)
        label_positions[eng_name] = y

    for eng_name, fr_label, color, raw_y in label_items:
        y_pos = label_positions[eng_name]
        # Draw a thin connector line from the data endpoint to the label
        if abs(y_pos - raw_y) > 3:
            ax.plot([last_year + 0.1, last_year + 0.25],
                    [raw_y, y_pos], color=color, linewidth=0.5,
                    alpha=0.5, clip_on=False)
        ax.text(last_year + 0.3, y_pos, fr_label,
                fontsize=9, color=color, va='center', ha='left',
                fontweight='bold', clip_on=False)

    # ── Reference line at 100 ──────────────────────────────────────────
    ax.axhline(y=100, color='gray', linewidth=0.6, linestyle=':', zorder=1)

    # ── Axes ───────────────────────────────────────────────────────────
    ax.set_xlim(2000, last_year)
    xtick_end = last_year + 1
    ax.set_xticks(range(2000, xtick_end, 5))
    ax.set_xticklabels([str(y) for y in range(2000, xtick_end, 5)],
                       fontsize=11)

    ax.set_ylim(0, 250)
    yticks = list(range(0, 251, 50))
    ax.set_yticks(yticks)
    ax.set_yticklabels([str(y) for y in yticks], fontsize=11)
    ax.set_ylabel(r"Indice des prix (2000 = 100)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Extra right margin for end-of-line labels
    fig.subplots_adjust(right=0.65)

    style_axes(ax)
    add_source(ax, r"Source: Statistique Canada, tableau 18-10-0005-01")
    save(fig, 'baumol_cost_disease_canada.png')


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 3 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        labor_market_indicators_us,
        labor_market_indicators_ca,
        participation_gender,
        aging_population,
        participation_decline_us,
        labor_share_decline,
        inequality_skill_premium,
        rd_gdp_share,
        canada_gdp_decomposition,
        canada_gdp_decomposition_countries,
        breakthrough_inventions,
        rd_spending_global,
        moores_law,
        zimbabwe_botswana,
        education_plateau,
        development_accounting_human_capital,
        tropics_map,
        education_prosperity,
        digital_adoption_index,
        canada_gdp_decomposition_5y,
        participation_gender_ca,
        unemployment_ca,
        participation_rate_ca,
        immigration_ca,
        inequality_top1_share,
        elephant_curve,
        gatsby_curve,
        baumol_cost_disease_canada,
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
