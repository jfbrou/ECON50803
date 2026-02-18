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
            linewidth=2, label=r"Taux de ch\^{o}mage")

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
    add_source(ax, r"Source: FRED (CIVPART, EMRATIO, UNRATE) --- \'{E}tats-Unis")
    save(fig, 'labor_market_indicators_us.png')


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
    add_source(ax, r"Source: FRED (LNS11300001, LNS11300002) --- \'{E}tats-Unis")
    save(fig, 'participation_gender.png')


# =====================================================================
# Figure 3: Aging population — old-age dependency ratio
# =====================================================================
def aging_population():
    print('Figure 3: Aging population — old-age dependency ratio')

    # Old-age dependency ratio (65+ / 15-64) * 100
    # Source: World Bank (SP.POP.DPND.OL)
    # Hardcoded representative data points for key countries
    years = [1960, 1970, 1980, 1990, 2000, 2010, 2020, 2023]
    japan = [9.5, 10.3, 13.4, 17.1, 25.2, 35.5, 48.4, 50.4]
    italy = [14.4, 16.9, 20.3, 21.6, 26.8, 31.2, 36.0, 38.3]
    canada = [13.0, 12.4, 14.0, 16.7, 18.2, 20.3, 27.6, 30.1]
    us = [15.4, 15.6, 17.1, 18.9, 18.6, 19.4, 25.6, 27.2]

    fig, ax = new_figure(9, 4.5)

    ax.plot(years, japan, 'o-', color=palette[2], linewidth=2.5,
            markersize=5, label='Japon')
    ax.plot(years, italy, 'o-', color=palette[3], linewidth=2.5,
            markersize=5, label='Italie')
    ax.plot(years, canada, 'o-', color=palette[0], linewidth=2.5,
            markersize=5, label='Canada')
    ax.plot(years, us, 'o-', color=palette[4], linewidth=2,
            markersize=4, label=r"\'{E}tats-Unis")

    ax.set_xlim(1958, 2025)
    ax.set_xticks(range(1960, 2030, 10))
    ax.set_xticklabels(range(1960, 2030, 10), fontsize=11)
    ax.set_ylabel(r"Ratio de d\'{e}pendance des a\^{i}n\'{e}s (\%)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 55)
    ax.set_yticks(range(0, 56, 10))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(0, 56, 10)], fontsize=11)

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
    ax.annotate(r"D\'{e}clin structurel",
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
    add_source(ax, r"Source: FRED (LNS11300061) --- Hommes 25--54 ans, \'{E}.-U.")
    save(fig, 'participation_decline_us.png')


# =====================================================================
# Figure 5: Labor share of GDP decline
# =====================================================================
def labor_share_decline():
    print('Figure 5: Labor share of GDP (US)')

    labor_share = get_fred_data('PRS85006173', frequency='a',
                                aggregation_method='avg')

    fig, ax = new_figure(9, 4.5)

    ax.plot(labor_share.index.year, labor_share.values, color=palette[0],
            linewidth=2.5)
    ax.fill_between(labor_share.index.year, labor_share.values,
                    labor_share.values.min() - 1, alpha=0.08, color=palette[0])

    # Trend line
    valid = labor_share.dropna()
    years_num = valid.index.year.values.astype(float)
    from scipy import stats as sp_stats
    slope, intercept, _, _, _ = sp_stats.linregress(years_num, valid.values)
    ax.plot(years_num, slope * years_num + intercept, color=palette[2],
            linewidth=2, linestyle='--', alpha=0.7, label='Tendance')

    ax.set_xlim(1950, 2024)
    ax.set_xticks(range(1950, 2025, 10))
    ax.set_xticklabels(range(1950, 2025, 10), fontsize=11)
    ax.set_ylabel(r"Part du travail dans le revenu (indice)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right')
    add_source(ax, r"Source: FRED (PRS85006173) --- \'{E}tats-Unis")
    save(fig, 'labor_share_decline.png')


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
    ax.annotate("Hausse du rendement\n" + r"de l'\'{e}ducation",
                xy=(2005, 1.82), xytext=(1975, 1.82),
                fontsize=11, color=palette[1], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[1], lw=1.5))

    ax.set_xlim(1963, 2025)
    ax.set_xticks(range(1965, 2025, 10))
    ax.set_xticklabels(range(1965, 2025, 10), fontsize=11)
    ax.set_ylabel(r"Ratio salarial (universit\'{e} / secondaire)",
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
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 3 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        labor_market_indicators_us,
        participation_gender,
        aging_population,
        participation_decline_us,
        labor_share_decline,
        inequality_skill_premium,
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
